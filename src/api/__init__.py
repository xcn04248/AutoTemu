"""
API模块

包含各种API客户端和适配器
"""

from .bg_client import BgGoodsClient, create_bg_client, BgApiException

__all__ = [
    'BgGoodsClient',
    'create_bg_client', 
    'BgApiException'
]
