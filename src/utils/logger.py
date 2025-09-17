"""
日志系统模块

提供统一的日志记录功能，支持按模块分类、按日期分割日志文件。
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

from .config import get_config


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（用于控制台输出）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """格式化日志记录"""
        # 获取原始格式化的日志
        log_message = super().format(record)
        
        # 如果是终端输出，添加颜色
        if sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, '')
            return f"{color}{log_message}{self.RESET}"
        
        return log_message


class Logger:
    """日志管理器"""
    
    # 存储已创建的logger实例
    _loggers = {}
    
    def __init__(self, module_name: str, log_level: Optional[str] = None):
        """
        初始化日志管理器
        
        Args:
            module_name: 模块名称，用于日志分类
            log_level: 日志级别，不指定则使用配置中的级别
        """
        self.module_name = module_name
        self.logger = self._get_or_create_logger(module_name, log_level)
    
    @classmethod
    def _get_or_create_logger(cls, module_name: str, log_level: Optional[str] = None):
        """
        获取或创建logger实例
        
        Args:
            module_name: 模块名称
            log_level: 日志级别
            
        Returns:
            logger实例
        """
        # 如果已存在，直接返回
        if module_name in cls._loggers:
            return cls._loggers[module_name]
        
        # 创建新的logger
        logger = logging.getLogger(f"autotemu.{module_name}")
        
        # 设置日志级别
        config = get_config()
        level = getattr(logging, log_level or config.log_level)
        logger.setLevel(level)
        
        # 避免日志向上传播
        logger.propagate = False
        
        # 清除已有的处理器（避免重复）
        logger.handlers.clear()
        
        # 添加控制台处理器
        console_handler = cls._create_console_handler()
        logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_handler = cls._create_file_handler(module_name)
        logger.addHandler(file_handler)
        
        # 缓存logger实例
        cls._loggers[module_name] = logger
        
        return logger
    
    @staticmethod
    def _create_console_handler():
        """创建控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        
        # 使用带颜色的格式化器
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def _create_file_handler(module_name: str):
        """
        创建文件处理器
        
        Args:
            module_name: 模块名称
            
        Returns:
            文件处理器
        """
        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 按日期创建日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f"{date_str}_autotemu_{module_name}.log"
        
        handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # 文件使用更详细的格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message, *args, **kwargs)
    
    def log_operation(self, operation: str, status: str = "started", **details):
        """
        记录操作日志
        
        Args:
            operation: 操作名称
            status: 操作状态（started, completed, failed）
            **details: 其他详细信息
        """
        detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
        if detail_str:
            self.info(f"{operation} {status}: {detail_str}")
        else:
            self.info(f"{operation} {status}")
    
    def log_api_call(self, api_name: str, method: str, url: str, 
                     status_code: Optional[int] = None, 
                     response_time: Optional[float] = None,
                     error: Optional[str] = None):
        """
        记录API调用日志
        
        Args:
            api_name: API名称
            method: HTTP方法
            url: 请求URL
            status_code: 响应状态码
            response_time: 响应时间（秒）
            error: 错误信息
        """
        if error:
            self.error(
                f"API call failed: {api_name} {method} {url} - Error: {error}"
            )
        else:
            self.info(
                f"API call: {api_name} {method} {url} - "
                f"Status: {status_code}, Time: {response_time:.2f}s"
            )
    
    def log_data_processing(self, data_type: str, count: int, 
                          success: Optional[int] = None, 
                          failed: Optional[int] = None):
        """
        记录数据处理日志
        
        Args:
            data_type: 数据类型
            count: 总数量
            success: 成功数量
            failed: 失败数量
        """
        if success is not None and failed is not None:
            self.info(
                f"Processed {data_type}: Total={count}, "
                f"Success={success}, Failed={failed}"
            )
        else:
            self.info(f"Processing {data_type}: Count={count}")


def get_logger(module_name: str, log_level: Optional[str] = None) -> Logger:
    """
    获取日志记录器
    
    Args:
        module_name: 模块名称
        log_level: 日志级别
        
    Returns:
        Logger实例
    """
    return Logger(module_name, log_level)


# 默认logger的延迟初始化
_default_logger = None

def get_default_logger():
    """获取默认logger（延迟初始化）"""
    global _default_logger
    if _default_logger is None:
        _default_logger = get_logger("default")
    return _default_logger


if __name__ == "__main__":
    # 测试日志功能
    logger = get_logger("test")
    
    logger.debug("这是调试信息")
    logger.info("这是一般信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    # 测试操作日志
    logger.log_operation("商品抓取", "started", url="https://example.com", count=10)
    logger.log_operation("商品抓取", "completed", success=8, failed=2)
    
    # 测试API日志
    logger.log_api_call("Temu API", "POST", "/api/goods/add", 200, 1.23)
    logger.log_api_call("Temu API", "POST", "/api/goods/add", error="Connection timeout")
    
    # 测试数据处理日志
    logger.log_data_processing("图片", 20, success=15, failed=5)
    
    print("\n日志已写入logs目录，请查看生成的日志文件。")
