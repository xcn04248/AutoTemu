#!/usr/bin/env python3
"""
详细调试Temu API签名

逐步对比我们的实现与官方实现
"""

import sys
import json
import hashlib
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config


def debug_detailed_signature():
    """详细调试签名算法"""
    print("🔍 详细调试Temu API签名...")
    
    config = get_config()
    
    # 测试参数
    params = {
        "type": "bg.local.goods.cats.get",
        "app_key": config.temu_app_key,
        "access_token": config.temu_access_token,
        "timestamp": round(time.time()),
        "data_type": "JSON",
        "parent_cat_id": 0
    }
    
    print(f"📋 测试参数: {json.dumps(params, indent=2)}")
    
    # 我们的实现
    print("\n🔐 我们的实现:")
    sorted_params = dict(sorted(params.items()))
    print(f"  排序后参数: {sorted_params}")
    
    result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
    print(f"  连接字符串: {result_str}")
    
    result_str_cleaned = result_str.replace(" ", "").replace("'", '"')
    print(f"  清理后字符串: {result_str_cleaned}")
    
    concatenated_str = f'{config.temu_app_secret}{result_str_cleaned}{config.temu_app_secret}'
    print(f"  最终签名字符串: {concatenated_str}")
    
    our_signature = hashlib.md5(concatenated_str.encode('utf-8')).hexdigest().upper()
    print(f"  我们的签名: {our_signature}")
    
    # 官方实现
    print("\n🔐 官方实现:")
    try:
        from temu_api.utils.base_client import BaseClient
        
        official_client = BaseClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url
        )
        
        # 使用官方方法
        official_signature = official_client._get_sign(params)
        print(f"  官方签名: {official_signature}")
        
        # 对比
        if our_signature == official_signature:
            print("  ✅ 签名完全匹配！")
        else:
            print("  ❌ 签名不匹配！")
            print(f"  差异: 我们的={our_signature}, 官方的={official_signature}")
            
        # 测试官方API调用
        print("\n🌐 测试官方API调用:")
        try:
            from temu_api import TemuClient
            
            client = TemuClient(
                app_key=config.temu_app_key,
                app_secret=config.temu_app_secret,
                access_token=config.temu_access_token,
                base_url=config.temu_base_url,
                debug=True
            )
            
            response = client.product.cats_get(parent_cat_id=0)
            print(f"  官方API响应: {response}")
            
        except Exception as e:
            print(f"  官方API调用失败: {e}")
        
    except Exception as e:
        print(f"  ❌ 官方客户端测试失败: {e}")


def test_manual_request():
    """测试手动请求"""
    print("\n🌐 测试手动请求...")
    
    config = get_config()
    
    # 构建请求参数
    params = {
        "type": "bg.local.goods.cats.get",
        "app_key": config.temu_app_key,
        "access_token": config.temu_access_token,
        "timestamp": round(time.time()),
        "data_type": "JSON",
        "parent_cat_id": 0
    }
    
    # 生成签名
    sorted_params = dict(sorted(params.items()))
    result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
    result_str = result_str.replace(" ", "").replace("'", '"')
    concatenated_str = f'{config.temu_app_secret}{result_str}{config.temu_app_secret}'
    signature = hashlib.md5(concatenated_str.encode('utf-8')).hexdigest().upper()
    
    params['sign'] = signature
    
    print(f"📋 最终请求参数: {json.dumps(params, indent=2)}")
    
    # 发送请求
    import requests
    try:
        response = requests.post(
            config.temu_base_url + '/openapi/router',
            json=params,
            headers={'Content-Type': 'application/json;charset=UTF-8'}
        )
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def main():
    """主函数"""
    print("🧪 详细Temu API签名调试")
    print("=" * 50)
    
    debug_detailed_signature()
    test_manual_request()


if __name__ == "__main__":
    main()
