#!/usr/bin/env python3
"""
测试年龄组属性位置

尝试将年龄组信息放在不同的位置和属性名
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_age_group_attributes():
    """测试年龄组属性位置"""
    print("🔍 测试年龄组属性位置")
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
    
    # 测试1: 在 goods_basic 中添加不同的年龄组属性名
    print("1️⃣ 在 goods_basic 中添加不同的年龄组属性名")
    print("-" * 40)
    
    age_attributes = [
        "ageGroup",
        "applicableAgeGroup", 
        "ApplicableAgeGroup",
        "age_group",
        "applicable_age_group",
        "targetAgeGroup",
        "targetAge",
        "ageRange",
        "ageCategory"
    ]
    
    for attr_name in age_attributes:
        print(f"测试属性名: {attr_name}")
        try:
            goods_basic_with_age = {
                **base_goods_basic,
                attr_name: "Adult"
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_age,
                goods_service_promise=base_goods_service_promise,
                goods_property={"material": "Cotton"},
                sku_list=base_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试2: 在 goods_property 中添加不同的年龄组属性名
    print("2️⃣ 在 goods_property 中添加不同的年龄组属性名")
    print("-" * 40)
    
    for attr_name in age_attributes:
        print(f"测试属性名: {attr_name}")
        try:
            goods_property_with_age = {
                "material": "Cotton",
                "style": "Casual",
                "season": "All Season",
                "gender": "Unisex",
                "color": "Multi",
                "pattern": "Solid",
                attr_name: "Adult"
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
    
    # 测试3: 在 SKU 中添加年龄组属性
    print("3️⃣ 在 SKU 中添加年龄组属性")
    print("-" * 40)
    
    for attr_name in age_attributes:
        print(f"测试属性名: {attr_name}")
        try:
            sku_list_with_age = [{
                **base_sku_list[0],
                attr_name: "Adult"
            }]
            
            result = client.product.goods_add(
                goods_basic=base_goods_basic,
                goods_service_promise=base_goods_service_promise,
                goods_property={"material": "Cotton"},
                sku_list=sku_list_with_age
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试4: 尝试使用 goodsAttributeList
    print("4️⃣ 尝试使用 goodsAttributeList")
    print("-" * 40)
    
    try:
        goods_basic_with_attributes = {
            **base_goods_basic,
            "goodsAttributeList": [
                {
                    "attributeName": "Applicable Age Group",
                    "attributeValue": "Adult"
                },
                {
                    "attributeName": "Age Group",
                    "attributeValue": "Adult"
                },
                {
                    "attributeName": "Target Age",
                    "attributeValue": "Adult"
                }
            ]
        }
        
        result4 = client.product.goods_add(
            goods_basic=goods_basic_with_attributes,
            goods_service_promise=base_goods_service_promise,
            goods_property={"material": "Cotton"},
            sku_list=base_sku_list
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 尝试使用 skuAttributeList
    print("5️⃣ 尝试使用 skuAttributeList")
    print("-" * 40)
    
    try:
        sku_list_with_attributes = [{
            **base_sku_list[0],
            "skuAttributeList": [
                {
                    "attributeName": "Applicable Age Group",
                    "attributeValue": "Adult"
                },
                {
                    "attributeName": "Age Group",
                    "attributeValue": "Adult"
                }
            ]
        }]
        
        result5 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property={"material": "Cotton"},
            sku_list=sku_list_with_attributes
        )
        print(f"  📊 结果: {result5}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试6: 尝试不同的年龄组值
    print("6️⃣ 尝试不同的年龄组值")
    print("-" * 40)
    
    age_values = [
        "Adult",
        "18+",
        "18 and above",
        "Adults only",
        "For adults",
        "Adult only",
        "18 years and above",
        "18+ years",
        "Adult (18+)",
        "18+ Adult"
    ]
    
    for age_value in age_values:
        print(f"测试年龄值: {age_value}")
        try:
            goods_basic_with_age = {
                **base_goods_basic,
                "goodsAttributeList": [
                    {
                        "attributeName": "Applicable Age Group",
                        "attributeValue": age_value
                    }
                ]
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_age,
                goods_service_promise=base_goods_service_promise,
                goods_property={"material": "Cotton"},
                sku_list=base_sku_list
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()


if __name__ == "__main__":
    test_age_group_attributes()
