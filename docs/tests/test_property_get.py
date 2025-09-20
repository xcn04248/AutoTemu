#!/usr/bin/env python3
"""
测试属性获取

获取正确的分类属性ID
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_property_get():
    """测试属性获取"""
    print("🔍 测试属性获取")
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
    
    # 2. 尝试获取分类属性
    print("2️⃣ 尝试获取分类属性")
    print("-" * 40)
    
    try:
        # 尝试不同的参数组合
        property_result = client.product.property_get(
            cat_id=recommended_cat_id,
            goods_prop_list=[],  # 空列表
            goods_name="テスト商品"
        )
        print(f"  📊 分类属性结果: {property_result}")
        
        if property_result.get("success"):
            properties = property_result.get("result", {}).get("propertyList", [])
            print(f"  📊 可用属性数量: {len(properties)}")
            
            # 查找年龄组相关属性
            age_properties = []
            for prop in properties:
                prop_name = prop.get("propertyName", "").lower()
                prop_desc = prop.get("propertyDesc", "").lower()
                if "age" in prop_name or "age" in prop_desc:
                    age_properties.append(prop)
                    print(f"  📊 找到年龄组属性: {prop}")
            
            if not age_properties:
                print("  ⚠️  未找到年龄组相关属性")
                print("  📊 所有属性:")
                for i, prop in enumerate(properties[:10]):  # 只显示前10个
                    print(f"    {i+1}. {prop.get('propertyName', 'N/A')} - {prop.get('propertyDesc', 'N/A')}")
        
    except Exception as e:
        print(f"  ❌ 获取属性失败: {e}")
    print()
    
    # 3. 尝试使用已知的属性ID
    print("3️⃣ 尝试使用已知的属性ID")
    print("-" * 40)
    
    # 常见的年龄组属性ID
    age_property_ids = [1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005]
    
    for prop_id in age_property_ids:
        print(f"测试属性ID: {prop_id}")
        try:
            goods_property = {
                "goodsProperties": [
                    {
                        "vid": prop_id,
                        "value": "Adult",
                        "valueUnit": "",
                        "valueUnitId": 0,
                        "templatePid": 0,
                        "parentSpecId": 0,
                        "specId": 0,
                        "note": "",
                        "imgUrl": "",
                        "groupId": 0,
                        "refPid": 0,
                        "numberInputValue": ""
                    }
                ]
            }
            
            goods_basic = {
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
            
            goods_service_promise = {
                "shipmentLimitDay": 2,
                "fulfillmentType": 1,
                "costTemplateId": "default"
            }
            
            sku_list = [{
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
            
            result = client.product.goods_add(
                goods_basic=goods_basic,
                goods_service_promise=goods_service_promise,
                goods_property=goods_property,
                sku_list=sku_list
            )
            print(f"  📊 结果: {result}")
            
            # 如果成功，跳出循环
            if result.get("success"):
                print(f"  ✅ 成功！属性ID {prop_id} 有效")
                break
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 4. 尝试不同的属性值
    print("4️⃣ 尝试不同的属性值")
    print("-" * 40)
    
    age_values = ["Adult", "18+", "18 and above", "Adults only", "For adults", "Adult only"]
    
    for age_value in age_values:
        print(f"测试年龄值: {age_value}")
        try:
            goods_property = {
                "goodsProperties": [
                    {
                        "vid": 1001,  # 使用第一个属性ID
                        "value": age_value,
                        "valueUnit": "",
                        "valueUnitId": 0,
                        "templatePid": 0,
                        "parentSpecId": 0,
                        "specId": 0,
                        "note": "",
                        "imgUrl": "",
                        "groupId": 0,
                        "refPid": 0,
                        "numberInputValue": ""
                    }
                ]
            }
            
            result = client.product.goods_add(
                goods_basic=goods_basic,
                goods_service_promise=goods_service_promise,
                goods_property=goods_property,
                sku_list=sku_list
            )
            print(f"  📊 结果: {result}")
            
            # 如果成功，跳出循环
            if result.get("success"):
                print(f"  ✅ 成功！年龄值 {age_value} 有效")
                break
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()


if __name__ == "__main__":
    test_property_get()
