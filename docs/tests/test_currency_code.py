#!/usr/bin/env python3
"""
测试 currencyCode 参数

添加 currencyCode 参数来解决 Invalid Request Parameters [currencyCode] 错误
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_currency_code():
    """测试 currencyCode 参数"""
    print("🔍 测试 currencyCode 参数")
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
    
    # 2. 测试不同的 currencyCode 配置
    print("2️⃣ 测试不同的 currencyCode 配置")
    print("-" * 40)
    
    # 基础参数
    base_goods_basic = {
        "goodsName": "测试商品",
        "goodsDesc": "测试描述",
        "catId": recommended_cat_id,
        "specIdList": [spec_id],
        "goodsType": 1,
        "goodsStatus": 1,
        "weight": "0.1",
        "weightUnit": "kg",
        "length": "10",
        "width": "10",
        "height": "10",
        "volumeUnit": "cm"
    }
    
    base_goods_service_promise = {
        "servicePromise": []
    }
    
    base_goods_property = {
        "material": "Cotton"
    }
    
    # 正确的 SKU 格式
    correct_sku_list = [{
        "outSkuSn": "test_sku_001",
        "specIdList": [spec_id],
        "price": {
            "basePrice": {
                "amount": "10.00",
                "currency": "USD"
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
    
    # 测试1: 添加 currencyCode 到 goods_basic
    print("测试1: 添加 currencyCode 到 goods_basic")
    try:
        goods_basic_with_currency = {
            **base_goods_basic,
            "currencyCode": "USD"
        }
        
        result1 = client.product.goods_add(
            goods_basic=goods_basic_with_currency,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=correct_sku_list
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 添加 currencyCode 到 SKU
    print("测试2: 添加 currencyCode 到 SKU")
    try:
        sku_list_with_currency = [{
            **correct_sku_list[0],
            "currencyCode": "USD"
        }]
        
        result2 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_currency
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 添加 currencyCode 到 price 对象
    print("测试3: 添加 currencyCode 到 price 对象")
    try:
        sku_list_with_price_currency = [{
            **correct_sku_list[0],
            "price": {
                "basePrice": {
                    "amount": "10.00",
                    "currency": "USD"
                },
                "currencyCode": "USD"
            }
        }]
        
        result3 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_price_currency
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 添加 currencyCode 到 goods_service_promise
    print("测试4: 添加 currencyCode 到 goods_service_promise")
    try:
        goods_service_promise_with_currency = {
            **base_goods_service_promise,
            "currencyCode": "USD"
        }
        
        result4 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=goods_service_promise_with_currency,
            goods_property=base_goods_property,
            sku_list=correct_sku_list
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 尝试不同的货币代码
    print("5️⃣ 尝试不同的货币代码")
    print("-" * 40)
    
    currency_codes = ["USD", "EUR", "GBP", "JPY", "CNY"]
    
    for currency_code in currency_codes:
        print(f"测试货币代码: {currency_code}")
        try:
            goods_basic_with_currency = {
                **base_goods_basic,
                "currencyCode": currency_code
            }
            
            # 更新 SKU 中的货币
            sku_list_with_currency = [{
                **correct_sku_list[0],
                "price": {
                    "basePrice": {
                        "amount": "10.00",
                        "currency": currency_code
                    }
                }
            }]
            
            result = client.product.goods_add(
                goods_basic=goods_basic_with_currency,
                goods_service_promise=base_goods_service_promise,
                goods_property=base_goods_property,
                sku_list=sku_list_with_currency
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试6: 检查其他可能缺少的参数
    print("6️⃣ 检查其他可能缺少的参数")
    print("-" * 40)
    
    # 尝试添加其他可能缺少的参数
    try:
        complete_goods_basic = {
            **base_goods_basic,
            "currencyCode": "USD",
            "listPriceType": 1,
            "brandId": None,
            "trademarkId": None
        }
        
        complete_goods_service_promise = {
            **base_goods_service_promise,
            "shippingTemplateId": None,
            "warrantyTemplateId": None,
            "returnTemplateId": None
        }
        
        result6 = client.product.goods_add(
            goods_basic=complete_goods_basic,
            goods_service_promise=complete_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=correct_sku_list
        )
        print(f"  📊 结果: {result6}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()


if __name__ == "__main__":
    test_currency_code()
