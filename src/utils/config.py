"""
配置管理模块

负责加载和管理应用程序配置，包括API密钥、业务参数等。
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置相关的异常"""
    pass


class Config:
    """应用程序配置类"""
    
    def __init__(self, env_file: Optional[str] = None, load_default_env: bool = True):
        """
        初始化配置
        
        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env文件
            load_default_env: 是否加载默认的.env文件
        """
        # 加载环境变量
        if env_file:
            load_dotenv(env_file, override=True)
        elif load_default_env:
            # 查找项目根目录的.env文件
            root_dir = Path(__file__).parent.parent.parent
            env_path = root_dir / ".env"
            if env_path.exists():
                load_dotenv(env_path)
            else:
                load_dotenv()  # 尝试从默认位置加载
        
        # API配置
        self.firecrawl_api_key = self._get_required_env("FIRECRAWL_API_KEY")
        self.baidu_api_key = self._get_required_env("BAIDU_API_KEY")
        self.baidu_secret_key = self._get_required_env("BAIDU_SECRET_KEY")
        
        # 新BG API配置（优先使用）
        self.bg_app_key = os.getenv("BG_APP_KEY") or self._get_optional_env("TEMU_APP_KEY")
        self.bg_app_secret = os.getenv("BG_APP_SECRET") or self._get_optional_env("TEMU_APP_SECRET")
        # 优先读取 BG_APP_ACCESS_TOKEN，其次 BG_ACCESS_TOKEN，最后回退 TEMU_ACCESS_TOKEN
        self.bg_access_token = (
            os.getenv("BG_APP_ACCESS_TOKEN")
            or os.getenv("BG_ACCESS_TOKEN")
            or self._get_optional_env("TEMU_ACCESS_TOKEN")
        )
        self.bg_base_url = os.getenv("BG_BASE_URL", "https://openapi-b-partner.temu.com/openapi/router")
        
        # 兼容旧配置
        self.temu_app_key = self.bg_app_key
        self.temu_app_secret = self.bg_app_secret
        self.temu_access_token = self.bg_access_token
        self.temu_base_url = self.bg_base_url
        
        # 业务配置
        self.price_markup = float(os.getenv("PRICE_MARKUP", "1.3"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.image_save_path = os.getenv("IMAGE_SAVE_PATH", "./images")
        
        # 重试配置
        self.max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.retry_initial_delay = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
        self.retry_max_delay = float(os.getenv("RETRY_MAX_DELAY", "60.0"))
        
        # 创建必要的目录
        self._ensure_directories()
    
    def _get_required_env(self, key: str) -> str:
        """
        获取必需的环境变量
        
        Args:
            key: 环境变量名
            
        Returns:
            环境变量值
            
        Raises:
            ConfigError: 当环境变量未设置时
        """
        value = os.getenv(key)
        if value is None:
            raise ConfigError(
                f"必需的环境变量 {key} 未设置。"
                f"请检查.env文件或环境变量设置。"
            )
        return value
    
    def _get_optional_env(self, key: str) -> Optional[str]:
        """
        获取可选的环境变量
        
        Args:
            key: 环境变量名
            
        Returns:
            环境变量值，如果未设置则返回None
        """
        return os.getenv(key)
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 创建图片保存目录
        image_path = Path(self.image_save_path)
        image_path.mkdir(parents=True, exist_ok=True)
        
        # 创建日志目录
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        # 检查价格加价率是否合理
        if self.price_markup < 1.0:
            raise ConfigError(f"价格加价率必须大于等于1.0，当前值：{self.price_markup}")
        
        # 检查重试配置
        if self.max_retry_attempts < 0:
            raise ConfigError(f"最大重试次数必须大于等于0，当前值：{self.max_retry_attempts}")
        
        if self.retry_initial_delay <= 0:
            raise ConfigError(f"初始重试延迟必须大于0，当前值：{self.retry_initial_delay}")
        
        if self.retry_max_delay < self.retry_initial_delay:
            raise ConfigError(
                f"最大重试延迟必须大于等于初始延迟，"
                f"当前最大延迟：{self.retry_max_delay}，"
                f"初始延迟：{self.retry_initial_delay}"
            )
        
        return True
    
    def __str__(self) -> str:
        """返回配置的字符串表示（隐藏敏感信息）"""
        return f"""<Config:
    Firecrawl API: {'***' + self.firecrawl_api_key[-4:] if len(self.firecrawl_api_key) > 4 else '***'}
    Baidu API: {'***' + self.baidu_api_key[-4:] if len(self.baidu_api_key) > 4 else '***'}
    Temu API: {'***' + self.temu_app_key[-4:] if len(self.temu_app_key) > 4 else '***'}
    Temu Base URL: {self.temu_base_url}
    Price Markup: {self.price_markup}
    Log Level: {self.log_level}
    Image Save Path: {self.image_save_path}
    Max Retry Attempts: {self.max_retry_attempts}
>"""


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        配置实例
    """
    global _config
    if _config is None:
        _config = Config()
        _config.validate()
    return _config


def reload_config(env_file: Optional[str] = None) -> Config:
    """
    重新加载配置
    
    Args:
        env_file: 环境变量文件路径
        
    Returns:
        新的配置实例
    """
    global _config
    _config = Config(env_file)
    _config.validate()
    return _config


if __name__ == "__main__":
    # 测试配置加载
    try:
        config = get_config()
        print("配置加载成功！")
        print(config)
    except ConfigError as e:
        print(f"配置错误：{e}")
