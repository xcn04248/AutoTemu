#!/usr/bin/env python3
"""
基于官方文档格式测试

使用官方文档中的正确参数格式
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_official_documentation_format():
    """基于官方文档格式测试"""
    print("🔍 基于官方文档格式测试")
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
    
    # 2. 使用官方文档格式
    print("2️⃣ 使用官方文档格式")
    print("-" * 40)
    
    # 基础商品信息
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
    
    # 商家服务承诺 - 使用官方文档格式
    goods_service_promise = {
        "shipmentLimitDay": 2,  # 必需：发货时间限制（天）
        "fulfillmentType": 1,   # 必需：配送方式 1-自配送
        "costTemplateId": "default"  # 必需：配送配置ID
    }
    
    # 商品属性 - 使用官方文档格式
    goods_property = {
        "goodsProperties": [  # 使用 goodsProperties 数组
            {
                "vid": 1001,  # 属性ID
                "value": "Adult",  # 年龄组值
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
            },
            {
                "vid": 1002,  # 材质属性ID
                "value": "Cotton",
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
    
    # SKU列表 - 使用官方文档格式
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
    
    # 测试1: 使用官方文档格式
    print("测试1: 使用官方文档格式")
    try:
        result1 = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise,
            goods_property=goods_property,
            sku_list=sku_list
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 尝试不同的 costTemplateId
    print("测试2: 尝试不同的 costTemplateId")
    try:
        goods_service_promise_v2 = {
            **goods_service_promise,
            "costTemplateId": "1"  # 尝试数字ID
        }
        
        result2 = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise_v2,
            goods_property=goods_property,
            sku_list=sku_list
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 尝试不同的 fulfillmentType
    print("测试3: 尝试不同的 fulfillmentType")
    try:
        goods_service_promise_v3 = {
            **goods_service_promise,
            "fulfillmentType": 2  # 尝试其他配送方式
        }
        
        result3 = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise_v3,
            goods_property=goods_property,
            sku_list=sku_list
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 尝试不同的 shipmentLimitDay
    print("测试4: 尝试不同的 shipmentLimitDay")
    try:
        goods_service_promise_v4 = {
            **goods_service_promise,
            "shipmentLimitDay": 1  # 尝试1天
        }
        
        result4 = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise_v4,
            goods_property=goods_property,
            sku_list=sku_list
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 尝试不同的年龄组属性
    print("测试5: 尝试不同的年龄组属性")
    try:
        goods_property_v5 = {
            "goodsProperties": [
                {
                    "vid": 1001,
                    "value": "18+",  # 尝试不同的年龄组值
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
        
        result5 = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise,
            goods_property=goods_property_v5,
            sku_list=sku_list
        )
        print(f"  📊 结果: {result5}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试6: 检查是否需要获取正确的属性ID
    print("6️⃣ 检查是否需要获取正确的属性ID")
    print("-" * 40)
    
    try:
        # 尝试获取分类属性
        property_result = client.product.property_get(cat_id=recommended_cat_id)
        print(f"  📊 分类属性: {property_result}")
        
        if property_result.get("success"):
            properties = property_result.get("result", {}).get("propertyList", [])
            print(f"  📊 可用属性数量: {len(properties)}")
            
            # 查找年龄组相关属性
            for prop in properties:
                if "age" in prop.get("propertyName", "").lower() or "age" in prop.get("propertyDesc", "").lower():
                    print(f"  📊 找到年龄组属性: {prop}")
        
    except Exception as e:
        print(f"  ❌ 获取属性失败: {e}")
    print()


if __name__ == "__main__":
    test_official_documentation_format()
