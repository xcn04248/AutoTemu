"""
配置模块的单元测试
"""

import os
import pytest
from pathlib import Path
import tempfile

from src.utils.config import Config, ConfigError, get_config, reload_config
import src.utils.config as config_module


class TestConfig:
    """配置类测试"""
    
    def setup_method(self):
        """每个测试方法执行前清理全局配置"""
        config_module._config = None
    
    def test_config_load_from_env_vars(self, monkeypatch):
        """测试从环境变量加载配置"""
        # 设置测试环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_firecrawl_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_baidu_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_baidu_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_temu_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_temu_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_temu_token")
        monkeypatch.setenv("PRICE_MARKUP", "1.5")
        
        # 创建配置实例
        config = Config()
        
        # 验证配置值
        assert config.firecrawl_api_key == "test_firecrawl_key"
        assert config.baidu_api_key == "test_baidu_key"
        assert config.baidu_secret_key == "test_baidu_secret"
        assert config.temu_app_key == "test_temu_key"
        assert config.temu_app_secret == "test_temu_secret"
        assert config.temu_access_token == "test_temu_token"
        assert config.price_markup == 1.5
    
    def test_config_missing_required_env(self, monkeypatch):
        """测试缺少必需环境变量时的异常"""
        # 清除所有环境变量
        for key in ["FIRECRAWL_API_KEY", "BAIDU_API_KEY", "BAIDU_SECRET_KEY",
                   "TEMU_APP_KEY", "TEMU_APP_SECRET", "TEMU_ACCESS_TOKEN"]:
            monkeypatch.delenv(key, raising=False)
        
        # 应该抛出ConfigError
        with pytest.raises(ConfigError) as exc_info:
            Config(load_default_env=False)
        
        assert "必需的环境变量" in str(exc_info.value)
    
    def test_config_default_values(self, monkeypatch):
        """测试默认配置值"""
        # 清除可能已存在的环境变量
        for key in ["PRICE_MARKUP", "TEMU_BASE_URL", "LOG_LEVEL", 
                   "IMAGE_SAVE_PATH", "MAX_RETRY_ATTEMPTS", 
                   "RETRY_INITIAL_DELAY", "RETRY_MAX_DELAY"]:
            monkeypatch.delenv(key, raising=False)
        
        # 设置必需的环境变量
        self._set_required_env_vars(monkeypatch)
        
        config = Config(load_default_env=False)
        
        # 验证默认值
        assert config.temu_base_url == "https://openapi-jp.temu.com"
        assert config.price_markup == 1.3
        assert config.log_level == "INFO"
        assert config.image_save_path == "./images"
        assert config.max_retry_attempts == 3
        assert config.retry_initial_delay == 1.0
        assert config.retry_max_delay == 60.0
    
    def test_config_validate_price_markup(self, monkeypatch):
        """测试价格加价率验证"""
        self._set_required_env_vars(monkeypatch)
        monkeypatch.setenv("PRICE_MARKUP", "0.5")  # 小于1.0
        
        config = Config()
        with pytest.raises(ConfigError) as exc_info:
            config.validate()
        
        assert "价格加价率必须大于等于1.0" in str(exc_info.value)
    
    def test_config_validate_retry_settings(self, monkeypatch):
        """测试重试设置验证"""
        self._set_required_env_vars(monkeypatch)
        
        # 测试负数重试次数
        monkeypatch.setenv("MAX_RETRY_ATTEMPTS", "-1")
        config = Config()
        with pytest.raises(ConfigError) as exc_info:
            config.validate()
        assert "最大重试次数必须大于等于0" in str(exc_info.value)
        
        # 测试无效的初始延迟
        monkeypatch.setenv("MAX_RETRY_ATTEMPTS", "3")
        monkeypatch.setenv("RETRY_INITIAL_DELAY", "0")
        config = Config()
        with pytest.raises(ConfigError) as exc_info:
            config.validate()
        assert "初始重试延迟必须大于0" in str(exc_info.value)
        
        # 测试最大延迟小于初始延迟
        monkeypatch.setenv("RETRY_INITIAL_DELAY", "10.0")
        monkeypatch.setenv("RETRY_MAX_DELAY", "5.0")
        config = Config()
        with pytest.raises(ConfigError) as exc_info:
            config.validate()
        assert "最大重试延迟必须大于等于初始延迟" in str(exc_info.value)
    
    def test_config_load_from_env_file(self, monkeypatch):
        """测试从.env文件加载配置"""
        # 清除可能已经加载的环境变量
        for key in ["FIRECRAWL_API_KEY", "BAIDU_API_KEY", "BAIDU_SECRET_KEY",
                   "TEMU_APP_KEY", "TEMU_APP_SECRET", "TEMU_ACCESS_TOKEN",
                   "PRICE_MARKUP", "TEMU_BASE_URL"]:
            monkeypatch.delenv(key, raising=False)
        
        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("FIRECRAWL_API_KEY=file_firecrawl_key\n")
            f.write("BAIDU_API_KEY=file_baidu_key\n")
            f.write("BAIDU_SECRET_KEY=file_baidu_secret\n")
            f.write("TEMU_APP_KEY=file_temu_key\n")
            f.write("TEMU_APP_SECRET=file_temu_secret\n")
            f.write("TEMU_ACCESS_TOKEN=file_temu_token\n")
            f.write("PRICE_MARKUP=2.0\n")
            env_file = f.name
        
        try:
            config = Config(env_file)
            assert config.firecrawl_api_key == "file_firecrawl_key"
            assert config.price_markup == 2.0
        finally:
            os.unlink(env_file)
    
    def test_get_config_singleton(self, monkeypatch):
        """测试get_config返回单例"""
        self._set_required_env_vars(monkeypatch)
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reload_config(self, monkeypatch):
        """测试重新加载配置"""
        self._set_required_env_vars(monkeypatch)
        
        # 第一次加载
        config1 = get_config()
        
        # 修改环境变量
        monkeypatch.setenv("PRICE_MARKUP", "2.5")
        
        # 重新加载
        config2 = reload_config()
        
        assert config1 is not config2
        assert config2.price_markup == 2.5
        assert get_config() is config2
    
    def test_config_str_representation(self, monkeypatch):
        """测试配置的字符串表示"""
        # 清除可能已存在的PRICE_MARKUP环境变量
        monkeypatch.delenv("PRICE_MARKUP", raising=False)
        
        self._set_required_env_vars(monkeypatch)
        config = Config()
        
        config_str = str(config)
        
        # 应该隐藏敏感信息
        assert "***" in config_str
        assert "test_firecrawl_key" not in config_str
        assert "Price Markup: 1.3" in config_str  # 价格加价率应该显示
    
    def test_ensure_directories(self, monkeypatch, tmp_path):
        """测试目录创建"""
        self._set_required_env_vars(monkeypatch)
        
        # 使用临时目录
        image_path = tmp_path / "test_images"
        monkeypatch.setenv("IMAGE_SAVE_PATH", str(image_path))
        
        # 切换到临时目录以避免在项目中创建logs目录
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            Config()
            
            # 验证目录已创建
            assert image_path.exists()
            assert (tmp_path / "logs").exists()
        finally:
            os.chdir(original_cwd)
    
    def _set_required_env_vars(self, monkeypatch):
        """设置必需的环境变量用于测试"""
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_firecrawl_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_baidu_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_baidu_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_temu_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_temu_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_temu_token")
