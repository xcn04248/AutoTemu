#!/usr/bin/env python3
"""
调试商品创建 API 参数问题

分析 specIdList 参数的要求
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def debug_goods_add_params():
    """调试商品创建参数"""
    print("🔍 调试商品创建 API 参数问题")
    print("=" * 60)
    
    try:
        # 获取配置
        config = get_config()
        
        # 创建Temu客户端
        temu_client = TemuClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url,
            debug=False
        )
        
        print(f"📋 配置信息:")
        print(f"  - API端点: {config.temu_base_url}")
        print(f"  - App Key: {config.temu_app_key[:8]}...")
        print()
        
        # 1. 先获取 specId
        print("1️⃣ 获取 specId")
        print("-" * 40)
        try:
            # 尝试获取 specId
            result = temu_client.product.spec_id_get(
                cat_id="30847",
                parent_spec_id="1001",  # 颜色规格
                child_spec_name="颜色"
            )
            print(f"  📊 结果: {result}")
            if result.get("success"):
                spec_id = result.get("result", {}).get("specId")
                print(f"  ✅ 获取到 specId: {spec_id}")
            else:
                print(f"  ❌ 获取 specId 失败: {result.get('errorMsg')}")
        except Exception as e:
            print(f"  ❌ 获取 specId 异常: {e}")
        print()
        
        # 2. 尝试不同的商品创建参数格式
        print("2️⃣ 尝试不同的商品创建参数格式")
        print("-" * 40)
        
        # 格式1: 最简参数
        print("  格式1: 最简参数")
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847"
                },
                goods_service_promise={},
                goods_property={},
                sku_list=[]
            )
            print(f"    📊 结果: {result.get('success')} - {result.get('errorMsg')}")
        except Exception as e:
            print(f"    ❌ 异常: {e}")
        
        # 格式2: 带 SKU 但无 specIdList
        print("  格式2: 带 SKU 但无 specIdList")
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847"
                },
                goods_service_promise={},
                goods_property={},
                sku_list=[{
                    "skuId": "test_sku_001",
                    "skuName": "M",
                    "price": 10.0,
                    "currency": "USD",
                    "inventory": 100,
                    "skuStatus": 1
                }]
            )
            print(f"    📊 结果: {result.get('success')} - {result.get('errorMsg')}")
        except Exception as e:
            print(f"    ❌ 异常: {e}")
        
        # 格式3: 带 specIdList
        print("  格式3: 带 specIdList")
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847",
                    "specIdList": ["1001"]  # 添加 specIdList
                },
                goods_service_promise={},
                goods_property={},
                sku_list=[{
                    "skuId": "test_sku_001",
                    "skuName": "M",
                    "price": 10.0,
                    "currency": "USD",
                    "inventory": 100,
                    "skuStatus": 1,
                    "specIdList": ["1001"]  # SKU 也添加 specIdList
                }]
            )
            print(f"    📊 结果: {result.get('success')} - {result.get('errorMsg')}")
        except Exception as e:
            print(f"    ❌ 异常: {e}")
        print()
        
        # 3. 检查商品创建 API 的文档要求
        print("3️⃣ 分析问题")
        print("-" * 40)
        print("  问题分析:")
        print("  1. 签名验证实际上是成功的（没有 'sign is invalid' 错误）")
        print("  2. 真正的问题是参数验证：'Invalid Request Parameters [specIdList]'")
        print("  3. 商品创建 API 要求提供 specIdList 参数")
        print("  4. specIdList 需要先通过 spec_id_get API 获取")
        print("  5. 其他 API 不需要 specIdList，所以能成功")
        print()
        
        # 4. 解决方案
        print("4️⃣ 解决方案")
        print("-" * 40)
        print("  解决步骤:")
        print("  1. 先调用 spec_id_get 获取规格 ID")
        print("  2. 在 goods_basic 中添加 specIdList")
        print("  3. 在 sku_list 的每个 SKU 中添加 specIdList")
        print("  4. 确保 specIdList 格式正确")
        print()
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_goods_add_params()
