"""
重试机制的单元测试
"""

import time
import pytest
from unittest.mock import Mock, patch, call

from src.utils.retry import (
    RetryPolicy,
    retry,
    RetryManager,
    with_retry,
    network_retry,
    api_retry,
    quick_retry
)
from src.utils.exceptions import NetworkException, RetryException, ParseException
import src.utils.config as config_module


class TestRetryPolicy:
    """重试策略测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        # 清理全局配置
        config_module._config = None
        
        # 设置必需的环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("MAX_RETRY_ATTEMPTS", "3")
        monkeypatch.setenv("RETRY_INITIAL_DELAY", "1.0")
        monkeypatch.setenv("RETRY_MAX_DELAY", "10.0")
    
    def test_default_policy(self):
        """测试默认策略"""
        policy = RetryPolicy()
        
        assert policy.max_attempts == 3
        assert policy.initial_delay == 1.0
        assert policy.max_delay == 10.0
        assert policy.exponential_base == 2.0
        assert policy.jitter is True
        assert policy.exceptions is None
    
    def test_custom_policy(self):
        """测试自定义策略"""
        policy = RetryPolicy(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False,
            exceptions=(NetworkException,)
        )
        
        assert policy.max_attempts == 5
        assert policy.initial_delay == 0.5
        assert policy.max_delay == 30.0
        assert policy.exponential_base == 3.0
        assert policy.jitter is False
        assert policy.exceptions == (NetworkException,)
    
    def test_calculate_delay_exponential(self):
        """测试指数退避延迟计算"""
        policy = RetryPolicy(initial_delay=1.0, exponential_base=2.0, jitter=False)
        
        # 第1次尝试：1.0 * 2^0 = 1.0
        assert policy.calculate_delay(1) == 1.0
        
        # 第2次尝试：1.0 * 2^1 = 2.0
        assert policy.calculate_delay(2) == 2.0
        
        # 第3次尝试：1.0 * 2^2 = 4.0
        assert policy.calculate_delay(3) == 4.0
        
        # 第4次尝试：1.0 * 2^3 = 8.0
        assert policy.calculate_delay(4) == 8.0
    
    def test_calculate_delay_max_limit(self):
        """测试最大延迟限制"""
        policy = RetryPolicy(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )
        
        # 超过最大延迟时应该被限制
        assert policy.calculate_delay(10) == 5.0
    
    def test_calculate_delay_with_jitter(self):
        """测试带抖动的延迟计算"""
        policy = RetryPolicy(initial_delay=1.0, jitter=True)
        
        # 多次计算应该得到不同的结果（由于抖动）
        delays = [policy.calculate_delay(2) for _ in range(10)]
        assert len(set(delays)) > 1  # 应该有多个不同的值
        
        # 所有值应该在合理范围内（基础值2.0的±25%）
        for delay in delays:
            assert 1.5 <= delay <= 2.5
    
    def test_should_retry_default(self):
        """测试默认的重试判断"""
        policy = RetryPolicy()
        
        # 可重试的异常
        assert policy.should_retry(NetworkException("网络错误"))
        
        # 不可重试的异常
        assert not policy.should_retry(ParseException("解析错误"))
        assert not policy.should_retry(ValueError("值错误"))
    
    def test_should_retry_custom(self):
        """测试自定义的重试判断"""
        policy = RetryPolicy(exceptions=(ValueError, TypeError))
        
        # 指定的异常类型应该重试
        assert policy.should_retry(ValueError("值错误"))
        assert policy.should_retry(TypeError("类型错误"))
        
        # 其他异常不应该重试
        assert not policy.should_retry(NetworkException("网络错误"))
        assert not policy.should_retry(Exception("其他错误"))


class TestRetryDecorator:
    """重试装饰器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        # 设置必需的环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
        
        # 使用mock来加速测试
        self.sleep_patch = patch('time.sleep')
        self.sleep_mock = self.sleep_patch.start()
    
    def teardown_method(self):
        """清理"""
        self.sleep_patch.stop()
    
    def test_retry_success_first_attempt(self):
        """测试第一次就成功的情况"""
        mock_func = Mock(return_value="成功")
        
        @retry(max_attempts=3)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 1
        assert not self.sleep_mock.called
    
    def test_retry_success_after_failures(self):
        """测试失败后重试成功的情况"""
        mock_func = Mock(side_effect=[
            NetworkException("第一次失败"),
            NetworkException("第二次失败"),
            "成功"
        ])
        
        @retry(max_attempts=3, initial_delay=1.0)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 3
        assert self.sleep_mock.call_count == 2  # 失败两次，延迟两次
    
    def test_retry_exhausted(self):
        """测试重试次数耗尽的情况"""
        mock_func = Mock(side_effect=NetworkException("总是失败"))
        
        @retry(max_attempts=3)
        def test_func():
            return mock_func()
        
        with pytest.raises(RetryException) as exc_info:
            test_func()
        
        assert "重试次数已耗尽" in str(exc_info.value)
        assert exc_info.value.attempts == 3
        assert exc_info.value.max_attempts == 3
        assert mock_func.call_count == 3
    
    def test_retry_non_retryable_exception(self):
        """测试不可重试的异常"""
        mock_func = Mock(side_effect=ParseException("解析错误"))
        
        @retry(max_attempts=3)
        def test_func():
            return mock_func()
        
        with pytest.raises(ParseException):
            test_func()
        
        # 不可重试的异常应该立即抛出，不进行重试
        assert mock_func.call_count == 1
        assert not self.sleep_mock.called
    
    def test_retry_with_custom_exceptions(self):
        """测试指定特定异常类型重试"""
        mock_func = Mock(side_effect=[
            ValueError("第一次"),
            ValueError("第二次"),
            "成功"
        ])
        
        @retry(max_attempts=3, exceptions=(ValueError,))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 3
    
    def test_retry_callback(self):
        """测试重试回调"""
        callback_mock = Mock()
        mock_func = Mock(side_effect=[
            NetworkException("失败1"),
            NetworkException("失败2"),
            "成功"
        ])
        
        @retry(max_attempts=3, on_retry=callback_mock)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert callback_mock.call_count == 2  # 失败两次，回调两次
        
        # 验证回调参数
        calls = callback_mock.call_args_list
        assert isinstance(calls[0][0][0], NetworkException)
        assert calls[0][0][1] == 1  # 第一次尝试
        assert isinstance(calls[1][0][0], NetworkException)
        assert calls[1][0][1] == 2  # 第二次尝试
    
    def test_retry_with_arguments(self):
        """测试带参数的函数重试"""
        mock_func = Mock(side_effect=[
            NetworkException("失败"),
            "成功"
        ])
        
        @retry(max_attempts=2)
        def test_func(a, b, c=None):
            return mock_func(a, b, c)
        
        result = test_func(1, 2, c=3)
        
        assert result == "成功"
        assert mock_func.call_count == 2
        # 验证参数传递正确
        mock_func.assert_called_with(1, 2, 3)


class TestRetryManager:
    """重试管理器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
        
        self.sleep_patch = patch('time.sleep')
        self.sleep_mock = self.sleep_patch.start()
    
    def teardown_method(self):
        """清理"""
        self.sleep_patch.stop()
    
    def test_retry_manager_context(self):
        """测试重试管理器上下文管理"""
        with RetryManager() as rm:
            assert rm.attempt == 0
            assert rm.start_time is not None
            assert rm.elapsed_time >= 0
    
    def test_retry_manager_execute_success(self):
        """测试重试管理器执行成功"""
        mock_func = Mock(return_value="结果")
        
        with RetryManager() as rm:
            result = rm.execute(mock_func, 1, 2, key="value")
        
        assert result == "结果"
        assert mock_func.call_count == 1
        mock_func.assert_called_once_with(1, 2, key="value")
    
    def test_retry_manager_execute_with_retry(self):
        """测试重试管理器执行重试"""
        mock_func = Mock(side_effect=[
            NetworkException("失败"),
            "成功"
        ])
        
        with RetryManager() as rm:
            result = rm.execute(mock_func)
        
        assert result == "成功"
        assert mock_func.call_count == 2
        assert rm.attempt == 2
    
    def test_with_retry_helper(self):
        """测试with_retry辅助函数"""
        mock_func = Mock(side_effect=[
            NetworkException("失败"),
            "成功"
        ])
        
        result = with_retry(mock_func, "arg1", key="value")
        
        assert result == "成功"
        assert mock_func.call_count == 2
        mock_func.assert_called_with("arg1", key="value")


class TestPredefinedRetryDecorators:
    """预定义重试装饰器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
        
        self.sleep_patch = patch('time.sleep')
        self.sleep_mock = self.sleep_patch.start()
    
    def teardown_method(self):
        """清理"""
        self.sleep_patch.stop()
    
    def test_network_retry(self):
        """测试网络重试装饰器"""
        mock_func = Mock(side_effect=[
            NetworkException("网络错误"),
            "成功"
        ])
        
        @network_retry()
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 2
    
    def test_api_retry(self):
        """测试API重试装饰器"""
        mock_func = Mock(side_effect=[
            NetworkException("API错误"),
            NetworkException("API错误"),
            "成功"
        ])
        
        @api_retry()
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 3
    
    def test_quick_retry(self):
        """测试快速重试装饰器"""
        mock_func = Mock(side_effect=[
            NetworkException("网络错误"),
            "成功"
        ])
        
        @quick_retry()
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "成功"
        assert mock_func.call_count == 2
