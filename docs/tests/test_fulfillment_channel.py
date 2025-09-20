#!/usr/bin/env python3
"""
测试 fulfillment channel 参数

尝试添加 fulfillment 相关参数来解决 Invalid fulfillment channel 错误
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_fulfillment_channel():
    """测试 fulfillment channel 参数"""
    print("🔍 测试 fulfillment channel 参数")
    print("=" * 60)
    
    # 创建客户端
    client = TemuClient(
        app_key=os.getenv("TEMU_APP_KEY"),
        app_secret=os.getenv("TEMU_APP_SECRET"),
        access_token=os.getenv("TEMU_ACCESS_TOKEN"),
        base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
        debug=False
    )
    
    # 1. 获取分类和规格ID
    print("1️⃣ 获取分类和规格ID")
    print("-" * 40)
    
    category_result = client.product.category_recommend(
        goods_name="测试商品",
        goods_desc="测试描述"
    )
    recommended_cat_id = str(category_result.get("result", {}).get("catId", "26579"))
    print(f"  📊 推荐分类ID: {recommended_cat_id}")
    
    spec_result = client.product.spec_id_get(
        cat_id=recommended_cat_id,
        parent_spec_id="1001",
        child_spec_name="颜色"
    )
    spec_id = spec_result.get("result", {}).get("specId")
    print(f"  📊 规格ID: {spec_id}")
    print()
    
    # 2. 测试不同的 fulfillment 配置
    print("2️⃣ 测试不同的 fulfillment 配置")
    print("-" * 40)
    
    # 基础参数
    base_goods_basic = {
        "goodsName": "测试商品",
        "goodsDesc": "测试描述",
        "catId": recommended_cat_id,
        "specIdList": [spec_id],
        "goodsType": 1,
        "goodsStatus": 1
    }
    
    base_goods_service_promise = {
        "servicePromise": []
    }
    
    base_goods_property = {
        "material": "Cotton"
    }
    
    base_sku_list = [{
        "skuId": "test_sku_001",
        "specIdList": [spec_id],
        "price": 10.0,
        "currency": "USD",
        "inventory": 100,
        "skuStatus": 1
    }]
    
    # 测试1: 添加 fulfillment 相关参数到 goods_basic
    print("测试1: 添加 fulfillment 相关参数到 goods_basic")
    try:
        goods_basic_with_fulfillment = {
            **base_goods_basic,
            "fulfillmentChannel": "TEMU",
            "fulfillmentType": "FBM"
        }
        
        result1 = client.product.goods_add(
            goods_basic=goods_basic_with_fulfillment,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 添加 fulfillment 相关参数到 goods_service_promise
    print("测试2: 添加 fulfillment 相关参数到 goods_service_promise")
    try:
        goods_service_promise_with_fulfillment = {
            **base_goods_service_promise,
            "fulfillmentChannel": "TEMU",
            "fulfillmentType": "FBM"
        }
        
        result2 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=goods_service_promise_with_fulfillment,
            goods_property=base_goods_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 添加 fulfillment 相关参数到 SKU
    print("测试3: 添加 fulfillment 相关参数到 SKU")
    try:
        sku_list_with_fulfillment = [{
            **base_sku_list[0],
            "fulfillmentChannel": "TEMU",
            "fulfillmentType": "FBM"
        }]
        
        result3 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_fulfillment
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 添加 shipping 相关参数
    print("测试4: 添加 shipping 相关参数")
    try:
        goods_service_promise_with_shipping = {
            **base_goods_service_promise,
            "shippingTemplateId": "default",
            "warrantyTemplateId": "default",
            "returnTemplateId": "default"
        }
        
        result4 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=goods_service_promise_with_shipping,
            goods_property=base_goods_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 检查是否有其他必需的模板ID
    print("5️⃣ 检查是否有其他必需的模板ID")
    print("-" * 40)
    
    # 尝试获取可用的模板
    try:
        # 这里可能需要调用其他API来获取模板ID
        print("  📊 尝试获取可用的模板...")
        # 由于我们不知道具体的API，先跳过
        print("  ⚠️  需要查找获取模板ID的API")
    except Exception as e:
        print(f"  ❌ 获取模板失败: {e}")
    print()
    
    # 测试6: 尝试不同的商品类型
    print("6️⃣ 尝试不同的商品类型")
    print("-" * 40)
    
    goods_types = [1, 2, 3, 4, 5]  # 不同的商品类型
    
    for goods_type in goods_types:
        print(f"测试商品类型: {goods_type}")
        try:
            goods_basic_with_type = {
                **base_goods_basic,
                "goodsType": goods_type
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_type,
                goods_service_promise=base_goods_service_promise,
                goods_property=base_goods_property,
                sku_list=base_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试7: 尝试不同的商品状态
    print("7️⃣ 尝试不同的商品状态")
    print("-" * 40)
    
    goods_statuses = [1, 2, 3, 4, 5]  # 不同的商品状态
    
    for goods_status in goods_statuses:
        print(f"测试商品状态: {goods_status}")
        try:
            goods_basic_with_status = {
                **base_goods_basic,
                "goodsStatus": goods_status
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_status,
                goods_service_promise=base_goods_service_promise,
                goods_property=base_goods_property,
                sku_list=base_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()


if __name__ == "__main__":
    test_fulfillment_channel()
