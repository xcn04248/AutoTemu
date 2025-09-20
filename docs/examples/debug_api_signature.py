#!/usr/bin/env python3
"""
调试 Temu API 签名问题

分析为什么其他 API 成功，但商品创建 API 失败
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def debug_api_calls():
    """调试 API 调用"""
    print("🔍 调试 Temu API 签名问题")
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
            debug=True  # 开启调试模式
        )
        
        print(f"📋 配置信息:")
        print(f"  - API端点: {config.temu_base_url}")
        print(f"  - App Key: {config.temu_app_key[:8]}...")
        print()
        
        # 1. 测试成功的 API - 分类获取
        print("1️⃣ 测试分类获取 API (成功)")
        print("-" * 40)
        try:
            result = temu_client.product.cats_get(parent_cat_id=0)
            print(f"  ✅ 成功: {result.get('success')}")
            print(f"  📊 结果: 获取到 {len(result.get('result', {}).get('goodsCatsList', []))} 个分类")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
        print()
        
        # 2. 测试成功的 API - 分类推荐
        print("2️⃣ 测试分类推荐 API (成功)")
        print("-" * 40)
        try:
            result = temu_client.product.category_recommend(
                goods_name="测试商品",
                goods_desc="测试描述"
            )
            print(f"  ✅ 成功: {result.get('success')}")
            print(f"  📊 结果: 推荐分类ID {result.get('result', {}).get('catId')}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
        print()
        
        # 3. 测试成功的 API - 尺码表元素
        print("3️⃣ 测试尺码表元素 API (成功)")
        print("-" * 40)
        try:
            result = temu_client.product.size_element_get(
                cat_id="30847",
                size_type="clothing"
            )
            print(f"  ✅ 成功: {result.get('success')}")
            print(f"  📊 结果: 获取到 {len(result.get('result', {}).get('sizeElementList', []))} 个尺码元素")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
        print()
        
        # 4. 测试失败的 API - 商品创建 (简化版本)
        print("4️⃣ 测试商品创建 API (失败)")
        print("-" * 40)
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847",
                    "goodsType": 1,
                    "goodsStatus": 1
                },
                goods_service_promise={},
                goods_property={},
                sku_list=[{
                    "skuId": "test_sku_001",
                    "skuName": "M"
                }]
            )
            print(f"  ❌ 失败: {result.get('success')}")
            print(f"  📊 错误: {result.get('errorMsg')}")
            print(f"  📊 错误码: {result.get('errorCode')}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
        
        # 5. 分析可能的原因
        print("5️⃣ 分析可能的原因")
        print("-" * 40)
        print("  可能的原因:")
        print("  1. 商品创建 API 需要特殊的权限")
        print("  2. 商品创建 API 的参数格式要求更严格")
        print("  3. 商品创建 API 需要额外的认证信息")
        print("  4. 商品创建 API 的签名算法可能不同")
        print("  5. 商品创建 API 需要特定的参数组合")
        print()
        
        # 6. 检查 API 权限
        print("6️⃣ 检查 API 权限")
        print("-" * 40)
        try:
            result = temu_client.auth.get_access_token_info()
            if result.get("success"):
                api_scope_list = result.get("result", {}).get("apiScopeList", [])
                goods_add_permission = "bg.local.goods.add" in api_scope_list
                print(f"  📊 商品创建权限: {'✅ 有' if goods_add_permission else '❌ 无'}")
                print(f"  📊 总权限数: {len(api_scope_list)}")
                if goods_add_permission:
                    print("  ✅ 权限检查通过")
                else:
                    print("  ❌ 缺少商品创建权限")
            else:
                print("  ❌ 无法获取权限信息")
        except Exception as e:
            print(f"  ❌ 权限检查失败: {e}")
        print()
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api_calls()
