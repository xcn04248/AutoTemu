#!/usr/bin/env python3
"""
调试自定义TemuClient

逐步测试客户端的问题
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.temu_client import TemuAPIClient
from src.utils.config import get_config


def debug_client():
    """调试客户端"""
    print("🔍 调试自定义TemuClient...")
    
    config = get_config()
    client = TemuAPIClient()
    
    print(f"📊 客户端配置:")
    print(f"  - Base URL: {client.base_url}")
    print(f"  - App Key: {client.app_key[:10]}...")
    print(f"  - App Secret: {client.app_secret[:10]}...")
    print(f"  - Access Token: {client.access_token[:10]}...")
    
    # 测试直接调用_make_request
    print("\n🧪 测试直接调用_make_request...")
    try:
        result = client._make_request("bg.local.goods.cats.get", {"parent_cat_id": 0})
        print(f"✅ _make_request成功: {result}")
    except Exception as e:
        print(f"❌ _make_request失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试test_connection
    print("\n🧪 测试test_connection...")
    try:
        result = client.test_connection()
        print(f"✅ test_connection结果: {result}")
    except Exception as e:
        print(f"❌ test_connection失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("🧪 自定义TemuClient调试")
    print("=" * 50)
    
    debug_client()


if __name__ == "__main__":
    main()
