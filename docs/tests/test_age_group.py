#!/usr/bin/env python3
"""
测试年龄组属性

添加 Applicable Age Group 属性来解决必需属性错误
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_age_group():
    """测试年龄组属性"""
    print("🔍 测试年龄组属性")
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
    
    # 2. 测试不同的年龄组配置
    print("2️⃣ 测试不同的年龄组配置")
    print("-" * 40)
    
    # 基础参数
    base_goods_basic = {
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
    
    base_goods_service_promise = {
        "servicePromise": []
    }
    
    base_sku_list = [{
        "outSkuSn": "test_sku_jp_001",
        "specIdList": [spec_id],
        "price": {
            "basePrice": {
                "amount": "1000",
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
    
    # 测试不同的年龄组
    age_groups = [
        "Adult",
        "Teen",
        "Child",
        "Baby",
        "All Ages",
        "18+",
        "16+",
        "12+",
        "6+",
        "3+",
        "0+"
    ]
    
    for age_group in age_groups:
        print(f"测试年龄组: {age_group}")
        try:
            goods_property_with_age = {
                "material": "Cotton",
                "style": "Casual",
                "season": "All Season",
                "gender": "Unisex",
                "ageGroup": age_group,
                "color": "Multi",
                "pattern": "Solid"
            }
            
            result = client.product.goods_add(
                goods_basic=base_goods_basic,
                goods_service_promise=base_goods_service_promise,
                goods_property=goods_property_with_age,
                sku_list=base_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试3: 添加年龄组到 goods_basic
    print("3️⃣ 添加年龄组到 goods_basic")
    print("-" * 40)
    
    try:
        goods_basic_with_age = {
            **base_goods_basic,
            "ageGroup": "Adult"
        }
        
        result3 = client.product.goods_add(
            goods_basic=goods_basic_with_age,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 添加年龄组到 SKU
    print("4️⃣ 添加年龄组到 SKU")
    print("-" * 40)
    
    try:
        sku_list_with_age = [{
            **base_sku_list[0],
            "ageGroup": "Adult"
        }]
        
        result4 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_age
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 添加其他可能缺少的属性
    print("5️⃣ 添加其他可能缺少的属性")
    print("-" * 40)
    
    try:
        complete_goods_property = {
            "material": "Cotton",
            "style": "Casual",
            "season": "All Season",
            "gender": "Unisex",
            "ageGroup": "Adult",
            "color": "Multi",
            "pattern": "Solid",
            "sleeveLength": "Long Sleeve",
            "neckline": "Round Neck",
            "fit": "Regular",
            "occasion": "Daily",
            "careInstructions": "Machine Wash",
            "brand": "Generic",
            "origin": "China",
            "warranty": "1 Year"
        }
        
        result5 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=complete_goods_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result5}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试6: 检查是否需要特定的日本市场属性
    print("6️⃣ 检查是否需要特定的日本市场属性")
    print("-" * 40)
    
    try:
        japan_specific_property = {
            "material": "Cotton",
            "style": "Casual",
            "season": "All Season",
            "gender": "Unisex",
            "ageGroup": "Adult",
            "color": "Multi",
            "pattern": "Solid",
            "country": "Japan",
            "language": "ja",
            "market": "JP"
        }
        
        result6 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=japan_specific_property,
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result6}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()


if __name__ == "__main__":
    test_age_group()
