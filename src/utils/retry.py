"""
重试机制模块

提供装饰器和工具函数实现自动重试功能。
"""

import time
import random
import functools
from typing import Callable, Type, Tuple, Optional, Union, Any
from datetime import datetime

from .logger import get_logger
from .config import get_config
from .exceptions import RetryException, is_retryable_exception


class RetryPolicy:
    """重试策略类"""
    
    def __init__(
        self,
        max_attempts: int = None,
        initial_delay: float = None,
        max_delay: float = None,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = None,
        logger_name: str = "retry"
    ):
        """
        初始化重试策略
        
        Args:
            max_attempts: 最大重试次数（包含首次尝试）
            initial_delay: 初始延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数退避的基数
            jitter: 是否添加随机抖动
            exceptions: 需要重试的异常类型元组，None表示所有异常
            logger_name: 日志记录器名称
        """
        config = get_config()
        
        self.max_attempts = max_attempts or config.max_retry_attempts
        self.initial_delay = initial_delay or config.retry_initial_delay
        self.max_delay = max_delay or config.retry_max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions
        self.logger = get_logger(logger_name)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数（从1开始）
            
        Returns:
            延迟时间（秒）
        """
        # 指数退避
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        
        # 添加随机抖动（±25%）
        if self.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)  # 确保延迟不为负
    
    def should_retry(self, exception: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            exception: 发生的异常
            
        Returns:
            是否应该重试
        """
        # 如果没有指定异常类型，使用默认的可重试异常判断
        if self.exceptions is None:
            return is_retryable_exception(exception)
        
        # 检查是否是指定的异常类型
        return isinstance(exception, self.exceptions)


def retry(
    max_attempts: int = None,
    initial_delay: float = None,
    max_delay: float = None,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = None,
    on_retry: Callable[[Exception, int], None] = None,
    logger_name: str = None
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        initial_delay: 初始延迟时间
        max_delay: 最大延迟时间
        exponential_base: 指数退避基数
        jitter: 是否添加随机抖动
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数，接收异常和尝试次数
        logger_name: 日志记录器名称
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 使用函数名作为默认的logger名称
            log_name = logger_name or f"retry.{func.__module__}.{func.__name__}"
            policy = RetryPolicy(
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                exceptions=exceptions,
                logger_name=log_name
            )
            
            last_exception = None
            
            for attempt in range(1, policy.max_attempts + 1):
                try:
                    # 记录尝试
                    if attempt > 1:
                        policy.logger.info(
                            f"重试 {func.__name__}，第 {attempt}/{policy.max_attempts} 次尝试"
                        )
                    
                    # 执行函数
                    result = func(*args, **kwargs)
                    
                    # 成功后记录
                    if attempt > 1:
                        policy.logger.info(
                            f"{func.__name__} 在第 {attempt} 次尝试后成功"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # 检查是否应该重试
                    if not policy.should_retry(e):
                        policy.logger.error(
                            f"{func.__name__} 失败，异常不可重试: {type(e).__name__}: {e}"
                        )
                        raise
                    
                    # 检查是否还有重试机会
                    if attempt >= policy.max_attempts:
                        policy.logger.error(
                            f"{func.__name__} 在 {attempt} 次尝试后失败: {type(e).__name__}: {e}"
                        )
                        raise RetryException(
                            f"重试次数已耗尽，共尝试 {attempt} 次",
                            attempts=attempt,
                            max_attempts=policy.max_attempts
                        ) from e
                    
                    # 计算延迟时间
                    delay = policy.calculate_delay(attempt)
                    
                    # 记录错误和延迟
                    policy.logger.warning(
                        f"{func.__name__} 失败 (尝试 {attempt}/{policy.max_attempts}): "
                        f"{type(e).__name__}: {e}，{delay:.2f} 秒后重试"
                    )
                    
                    # 调用重试回调
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            policy.logger.error(
                                f"重试回调函数出错: {callback_error}"
                            )
                    
                    # 延迟重试
                    time.sleep(delay)
            
            # 不应该到达这里，但为了安全起见
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class RetryManager:
    """重试管理器，用于更细粒度的重试控制"""
    
    def __init__(self, policy: RetryPolicy = None):
        """
        初始化重试管理器
        
        Args:
            policy: 重试策略，不指定则使用默认策略
        """
        self.policy = policy or RetryPolicy()
        self.attempt = 0
        self.start_time = None
    
    def __enter__(self):
        """进入上下文"""
        self.attempt = 0
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_val is None:
            # 没有异常，正常退出
            return False
        
        # 有异常，但不处理（让调用者处理）
        return False
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数并自动重试
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            RetryException: 重试次数耗尽
        """
        last_exception = None
        
        for self.attempt in range(1, self.policy.max_attempts + 1):
            try:
                if self.attempt > 1:
                    func_name = getattr(func, '__name__', repr(func))
                    self.policy.logger.info(
                        f"重试 {func_name}，第 {self.attempt}/{self.policy.max_attempts} 次尝试"
                    )
                
                result = func(*args, **kwargs)
                
                if self.attempt > 1:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    func_name = getattr(func, '__name__', repr(func))
                    self.policy.logger.info(
                        f"{func_name} 在第 {self.attempt} 次尝试后成功，"
                        f"总耗时 {elapsed:.2f} 秒"
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.policy.should_retry(e):
                    func_name = getattr(func, '__name__', repr(func))
                    self.policy.logger.error(
                        f"{func_name} 失败，异常不可重试: {type(e).__name__}: {e}"
                    )
                    raise
                
                if self.attempt >= self.policy.max_attempts:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    func_name = getattr(func, '__name__', repr(func))
                    self.policy.logger.error(
                        f"{func_name} 在 {self.attempt} 次尝试后失败，"
                        f"总耗时 {elapsed:.2f} 秒"
                    )
                    raise RetryException(
                        f"重试次数已耗尽，共尝试 {self.attempt} 次",
                        attempts=self.attempt,
                        max_attempts=self.policy.max_attempts
                    ) from e
                
                delay = self.policy.calculate_delay(self.attempt)
                func_name = getattr(func, '__name__', repr(func))
                self.policy.logger.warning(
                    f"{func_name} 失败: {type(e).__name__}: {e}，"
                    f"{delay:.2f} 秒后重试"
                )
                
                time.sleep(delay)
        
        if last_exception:
            raise last_exception
    
    @property
    def elapsed_time(self) -> float:
        """获取已经过的时间（秒）"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0


# 便捷函数

def with_retry(func: Callable, *args, **kwargs) -> Any:
    """
    使用默认重试策略执行函数
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值
    """
    with RetryManager() as rm:
        return rm.execute(func, *args, **kwargs)


# 预定义的重试装饰器

# 网络请求重试装饰器
network_retry = functools.partial(
    retry,
    max_attempts=3,
    initial_delay=1.0,
    max_delay=30.0,
    logger_name="retry.network"
)

# API调用重试装饰器
api_retry = functools.partial(
    retry,
    max_attempts=5,
    initial_delay=2.0,
    max_delay=60.0,
    exponential_base=2.0,
    logger_name="retry.api"
)

# 快速重试装饰器（用于本地操作）
quick_retry = functools.partial(
    retry,
    max_attempts=3,
    initial_delay=0.1,
    max_delay=1.0,
    jitter=False,
    logger_name="retry.quick"
)
