#!/usr/bin/env python3
"""
调试Temu API签名算法

比较我们的签名与官方TemuClient的签名
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


def debug_signature():
    """调试签名算法"""
    print("🔍 调试Temu API签名算法...")
    
    config = get_config()
    
    # 测试参数
    params = {
        "type": "bg.local.goods.category.recommend",
        "app_key": config.temu_app_key,
        "access_token": config.temu_access_token,
        "timestamp": round(time.time()),
        "data_type": "JSON",
        "goodsName": "test product",
        "language": "en"
    }
    
    print(f"📋 原始参数: {json.dumps(params, indent=2)}")
    
    # 我们的签名算法
    print("\n🔐 我们的签名算法:")
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
    
    # 官方TemuClient的签名算法
    print("\n🔐 官方TemuClient签名算法:")
    try:
        from temu_api.utils.base_client import BaseClient
        
        # 创建官方客户端实例
        official_client = BaseClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url
        )
        
        # 使用官方方法生成签名
        official_signature = official_client._get_sign(params)
        print(f"  官方签名: {official_signature}")
        
        # 比较签名
        if our_signature == official_signature:
            print("  ✅ 签名匹配！")
        else:
            print("  ❌ 签名不匹配！")
            print(f"  差异: 我们的={our_signature}, 官方的={official_signature}")
            
            # 调试官方签名过程
            print("\n🔍 官方签名过程:")
            sorted_params_official = dict(sorted(params.items()))
            print(f"  排序后参数: {sorted_params_official}")
            
            result_str_official = ''.join([f"{key}{value}" for key, value in sorted_params_official.items()])
            print(f"  连接字符串: {result_str_official}")
            
            result_str_official_cleaned = result_str_official.replace(" ", "").replace("'", '"')
            print(f"  清理后字符串: {result_str_official_cleaned}")
            
            concatenated_str_official = f'{config.temu_app_secret}{result_str_official_cleaned}{config.temu_app_secret}'
            print(f"  最终签名字符串: {concatenated_str_official}")
            
            # 检查是否有差异
            if concatenated_str != concatenated_str_official:
                print("  ❌ 签名字符串不匹配！")
                print(f"  我们的: {concatenated_str}")
                print(f"  官方的: {concatenated_str_official}")
                
                # 逐字符比较
                for i, (c1, c2) in enumerate(zip(concatenated_str, concatenated_str_official)):
                    if c1 != c2:
                        print(f"  差异位置 {i}: 我们的='{c1}' (ASCII {ord(c1)}), 官方的='{c2}' (ASCII {ord(c2)})")
                        break
            else:
                print("  ✅ 签名字符串匹配")
        
    except Exception as e:
        print(f"  ❌ 官方客户端测试失败: {e}")


def main():
    """主函数"""
    print("🧪 Temu API签名调试工具")
    print("=" * 50)
    
    debug_signature()


if __name__ == "__main__":
    main()
