"""
日志系统的单元测试
"""

import os
import pytest
import logging
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.utils.logger import Logger, get_logger, ColoredFormatter
from src.utils.config import get_config
import src.utils.config as config_module


class TestLogger:
    """日志系统测试"""
    
    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        """设置测试环境变量"""
        # 清理全局配置
        config_module._config = None
        
        # 设置必需的环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        
        # 清理Logger类的缓存
        Logger._loggers.clear()
    
    @pytest.fixture
    def temp_log_dir(self):
        """创建临时日志目录"""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # 创建logs目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        yield temp_dir
        
        # 清理
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_logger_creation(self, temp_log_dir):
        """测试日志器创建"""
        logger = Logger("test_module")
        
        assert logger.module_name == "test_module"
        assert logger.logger is not None
        assert logger.logger.name == "autotemu.test_module"
    
    def test_logger_singleton(self):
        """测试同一模块的logger是单例"""
        logger1 = get_logger("singleton_test")
        logger2 = get_logger("singleton_test")
        
        assert logger1.logger is logger2.logger
    
    def test_log_levels(self, temp_log_dir):
        """测试不同日志级别"""
        logger = get_logger("level_test")
        
        # 测试各个级别的日志方法
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # 验证日志文件已创建
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_level_test.log"
        assert log_file.exists()
        
        # 读取日志内容
        content = log_file.read_text()
        
        # 根据配置的日志级别，某些消息可能不会出现
        config = get_config()
        if config.log_level == "INFO":
            assert "Debug message" not in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
        assert "Critical message" in content
    
    def test_log_operation(self, temp_log_dir):
        """测试操作日志记录"""
        logger = get_logger("operation_test")
        
        # 记录操作开始
        logger.log_operation("数据处理", "started", items=100)
        
        # 记录操作完成
        logger.log_operation("数据处理", "completed", items=100, duration=5.2)
        
        # 验证日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_operation_test.log"
        content = log_file.read_text()
        
        assert "数据处理 started" in content
        assert "items=100" in content
        assert "数据处理 completed" in content
        assert "duration=5.2" in content
    
    def test_log_api_call(self, temp_log_dir):
        """测试API调用日志记录"""
        logger = get_logger("api_test")
        
        # 成功的API调用
        logger.log_api_call(
            "Test API", "GET", "/api/test", 
            status_code=200, response_time=0.5
        )
        
        # 失败的API调用
        logger.log_api_call(
            "Test API", "POST", "/api/test", 
            error="Connection timeout"
        )
        
        # 验证日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_api_test.log"
        content = log_file.read_text()
        
        assert "API call: Test API GET /api/test" in content
        assert "Status: 200" in content
        assert "Time: 0.50s" in content
        assert "API call failed" in content
        assert "Connection timeout" in content
    
    def test_log_data_processing(self, temp_log_dir):
        """测试数据处理日志记录"""
        logger = get_logger("data_test")
        
        # 记录数据处理结果
        logger.log_data_processing("商品图片", 20, success=15, failed=5)
        
        # 只记录总数
        logger.log_data_processing("商品信息", 10)
        
        # 验证日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_data_test.log"
        content = log_file.read_text()
        
        assert "Processed 商品图片" in content
        assert "Total=20" in content
        assert "Success=15" in content
        assert "Failed=5" in content
        assert "Processing 商品信息" in content
        assert "Count=10" in content
    
    def test_exception_logging(self, temp_log_dir):
        """测试异常日志记录"""
        logger = get_logger("exception_test")
        
        try:
            1 / 0
        except ZeroDivisionError:
            logger.exception("发生除零错误")
        
        # 验证日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_exception_test.log"
        content = log_file.read_text()
        
        assert "发生除零错误" in content
        assert "ZeroDivisionError" in content
        assert "Traceback" in content
    
    def test_custom_log_level(self):
        """测试自定义日志级别"""
        logger = get_logger("custom_level", "DEBUG")
        
        assert logger.logger.level == logging.DEBUG
    
    def test_log_file_format(self, temp_log_dir):
        """测试日志文件格式"""
        logger = get_logger("format_test")
        logger.info("测试消息")
        
        # 读取日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = Path("logs") / f"{date_str}_autotemu_format_test.log"
        content = log_file.read_text()
        
        # 验证格式包含所需元素
        lines = content.strip().split('\n')
        assert len(lines) >= 1
        
        log_line = lines[0]
        # 应包含时间戳
        assert datetime.now().strftime('%Y-%m-%d') in log_line
        # 应包含模块名
        assert "autotemu.format_test" in log_line
        # 应包含日志级别
        assert "INFO" in log_line
        # 应包含函数名和行号（这里会是Logger类的info方法）
        assert "info:" in log_line  # 函数名
        assert " - " in log_line  # 分隔符
        # 应包含消息
        assert "测试消息" in log_line
    
    def test_colored_formatter(self):
        """测试带颜色的格式化器"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        
        # 创建一个日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # 格式化消息
        formatted = formatter.format(record)
        
        # 在非TTY环境下应该没有颜色代码
        if not os.sys.stdout.isatty():
            assert '\033[' not in formatted
    
    def test_multiple_modules_separate_files(self, temp_log_dir):
        """测试不同模块使用不同的日志文件"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        logger1.info("Module 1 message")
        logger2.info("Module 2 message")
        
        # 验证创建了两个不同的日志文件
        date_str = datetime.now().strftime('%Y%m%d')
        log_file1 = Path("logs") / f"{date_str}_autotemu_module1.log"
        log_file2 = Path("logs") / f"{date_str}_autotemu_module2.log"
        
        assert log_file1.exists()
        assert log_file2.exists()
        
        # 验证内容分离
        content1 = log_file1.read_text()
        content2 = log_file2.read_text()
        
        assert "Module 1 message" in content1
        assert "Module 1 message" not in content2
        assert "Module 2 message" in content2
        assert "Module 2 message" not in content1
