#!/usr/bin/env python3
"""
测试日本市场配置

专门针对日本 Temu 网店的配置测试
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_japan_market():
    """测试日本市场配置"""
    print("🔍 测试日本市场配置")
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
        goods_name="テスト商品",
        goods_desc="テスト商品の説明"
    )
    recommended_cat_id = str(category_result.get("result", {}).get("catId", "26579"))
    print(f"  📊 推荐分类ID: {recommended_cat_id}")
    
    spec_result = client.product.spec_id_get(
        cat_id=recommended_cat_id,
        parent_spec_id="1001",
        child_spec_name="色"
    )
    spec_id = spec_result.get("result", {}).get("specId")
    print(f"  📊 规格ID: {spec_id}")
    print()
    
    # 2. 测试日本市场配置
    print("2️⃣ 测试日本市场配置")
    print("-" * 40)
    
    # 日本市场基础参数
    japan_goods_basic = {
        "goodsName": "テスト商品",
        "goodsDesc": "テスト商品の説明",
        "catId": recommended_cat_id,
        "specIdList": [spec_id],
        "goodsType": 1,
        "goodsStatus": 1,
        "weight": "0.1",
        "weightUnit": "kg",
        "length": "10",
        "width": "10",
        "height": "10",
        "volumeUnit": "cm",
        "currencyCode": "JPY"
    }
    
    japan_goods_service_promise = {
        "servicePromise": []
    }
    
    japan_goods_property = {
        "material": "Cotton",
        "style": "Casual",
        "season": "All Season",
        "gender": "Unisex",
        "ageGroup": "Adult",
        "color": "Multi",
        "pattern": "Solid"
    }
    
    # 日本市场 SKU 配置
    japan_sku_list = [{
        "outSkuSn": "test_sku_jp_001",
        "specIdList": [spec_id],
        "price": {
            "basePrice": {
                "amount": "1000",  # 1000 日元
                "currency": "JPY"
            }
        },
        "quantity": 100,
        "images": [],
        "weight": "0.1",
        "weightUnit": "kg",
        "length": "10",
        "width": "10",
        "height": "10",
        "volumeUnit": "cm"
    }]
    
    # 测试1: 基础日本配置
    print("测试1: 基础日本配置")
    try:
        result1 = client.product.goods_add(
            goods_basic=japan_goods_basic,
            goods_service_promise=japan_goods_service_promise,
            goods_property=japan_goods_property,
            sku_list=japan_sku_list
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 添加 fulfillment 相关参数
    print("测试2: 添加 fulfillment 相关参数")
    try:
        japan_goods_basic_with_fulfillment = {
            **japan_goods_basic,
            "fulfillmentChannel": "TEMU",
            "fulfillmentType": "FBM"
        }
        
        result2 = client.product.goods_add(
            goods_basic=japan_goods_basic_with_fulfillment,
            goods_service_promise=japan_goods_service_promise,
            goods_property=japan_goods_property,
            sku_list=japan_sku_list
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 添加 shipping 模板
    print("测试3: 添加 shipping 模板")
    try:
        japan_goods_service_promise_with_shipping = {
            **japan_goods_service_promise,
            "shippingTemplateId": "default",
            "warrantyTemplateId": "default",
            "returnTemplateId": "default"
        }
        
        result3 = client.product.goods_add(
            goods_basic=japan_goods_basic,
            goods_service_promise=japan_goods_service_promise_with_shipping,
            goods_property=japan_goods_property,
            sku_list=japan_sku_list
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 尝试不同的商品类型
    print("4️⃣ 尝试不同的商品类型")
    print("-" * 40)
    
    goods_types = [1, 2, 3, 4, 5]
    
    for goods_type in goods_types:
        print(f"测试商品类型: {goods_type}")
        try:
            goods_basic_with_type = {
                **japan_goods_basic,
                "goodsType": goods_type
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_type,
                goods_service_promise=japan_goods_service_promise,
                goods_property=japan_goods_property,
                sku_list=japan_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试5: 尝试不同的商品状态
    print("5️⃣ 尝试不同的商品状态")
    print("-" * 40)
    
    goods_statuses = [1, 2, 3, 4, 5]
    
    for goods_status in goods_statuses:
        print(f"测试商品状态: {goods_status}")
        try:
            goods_basic_with_status = {
                **japan_goods_basic,
                "goodsStatus": goods_status
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_status,
                goods_service_promise=japan_goods_service_promise,
                goods_property=japan_goods_property,
                sku_list=japan_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试6: 检查是否需要特定的日本市场参数
    print("6️⃣ 检查是否需要特定的日本市场参数")
    print("-" * 40)
    
    try:
        japan_specific_goods_basic = {
            **japan_goods_basic,
            "market": "JP",
            "region": "JP",
            "country": "JP",
            "language": "ja"
        }
        
        result6 = client.product.goods_add(
            goods_basic=japan_specific_goods_basic,
            goods_service_promise=japan_goods_service_promise,
            goods_property=japan_goods_property,
            sku_list=japan_sku_list
        )
        print(f"  📊 结果: {result6}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试7: 检查是否需要特定的 fulfillment 配置
    print("7️⃣ 检查是否需要特定的 fulfillment 配置")
    print("-" * 40)
    
    fulfillment_configs = [
        {"fulfillmentChannel": "TEMU", "fulfillmentType": "FBM"},
        {"fulfillmentChannel": "TEMU", "fulfillmentType": "FBA"},
        {"fulfillmentChannel": "SELLER", "fulfillmentType": "FBM"},
        {"fulfillmentChannel": "SELLER", "fulfillmentType": "FBA"}
    ]
    
    for config in fulfillment_configs:
        print(f"测试 fulfillment 配置: {config}")
        try:
            goods_basic_with_fulfillment = {
                **japan_goods_basic,
                **config
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_fulfillment,
                goods_service_promise=japan_goods_service_promise,
                goods_property=japan_goods_property,
                sku_list=japan_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()


if __name__ == "__main__":
    test_japan_market()
