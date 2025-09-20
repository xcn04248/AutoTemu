#!/usr/bin/env python3
"""
调试Temu API调用

详细测试API调用过程
"""

import sys
import json
import hashlib
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config


def debug_api_call():
    """调试API调用"""
    print("🔍 调试Temu API调用...")
    
    config = get_config()
    
    # 手动构建API请求
    method = "bg.local.goods.category.recommend"
    params = {
        "goodsName": "test product",
        "language": "en"
    }
    
    # 基础参数
    request_params = {
        "type": method,
        "app_key": config.temu_app_key,
        "access_token": config.temu_access_token,
        "timestamp": round(time.time()),
        "data_type": "JSON",
    }
    
    # 添加业务参数
    request_params.update(params)
    
    print(f"📋 请求参数: {json.dumps(request_params, indent=2)}")
    
    # 生成签名
    sorted_params = dict(sorted(request_params.items()))
    result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
    result_str = result_str.replace(" ", "").replace("'", '"')
    concatenated_str = f'{config.temu_app_secret}{result_str}{config.temu_app_secret}'
    signature = hashlib.md5(concatenated_str.encode('utf-8')).hexdigest().upper()
    
    print(f"🔐 签名字符串: {concatenated_str}")
    print(f"🔐 签名结果: {signature}")
    
    request_params["sign"] = signature
    
    # 发送请求
    api_url = config.temu_base_url + '/openapi/router'
    print(f"🌐 API URL: {api_url}")
    
    try:
        response = requests.post(
            api_url,
            json=request_params,
            timeout=30,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "AutoTemu/1.0"
            }
        )
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON解析成功: {json.dumps(data, indent=2)}")
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_official_client():
    """测试官方TemuClient"""
    print("\n🧪 测试官方TemuClient...")
    
    try:
        from temu_api import TemuClient
        
        config = get_config()
        client = TemuClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url,
            debug=True
        )
        
        print("✅ 官方TemuClient初始化成功")
        
        # 测试API调用
        response = client.product.category_recommend(
            goods_name="test product",
            language="en"
        )
        
        print(f"📋 官方客户端响应: {response}")
        
    except Exception as e:
        print(f"❌ 官方客户端测试失败: {e}")


def main():
    """主函数"""
    print("🧪 Temu API调试工具")
    print("=" * 50)
    
    debug_api_call()
    test_official_client()


if __name__ == "__main__":
    main()
