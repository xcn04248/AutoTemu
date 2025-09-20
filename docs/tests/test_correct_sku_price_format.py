#!/usr/bin/env python3
"""
测试正确的 SKU 价格格式

根据官方文档修复 price 字段的格式
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_correct_sku_price_format():
    """测试正确的 SKU 价格格式"""
    print("🔍 测试正确的 SKU 价格格式")
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
    
    # 2. 测试正确的价格格式
    print("2️⃣ 测试正确的价格格式")
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
    
    # 测试1: 使用正确的价格格式
    print("测试1: 使用正确的价格格式")
    try:
        # 根据官方文档，price 应该是复杂对象
        correct_sku_list = [{
            "outSkuSn": "test_sku_001",  # 使用 outSkuSn 而不是 skuId
            "specIdList": [spec_id],
            "price": {
                "basePrice": {
                    "amount": "10.00",  # 字符串格式
                    "currency": "USD"
                }
            },
            "quantity": 100,  # 使用 quantity 而不是 inventory
            "images": [],  # 使用 images 而不是 skuImageList
            "weight": "0.1",
            "weightUnit": "kg",
            "length": "10",
            "width": "10",
            "height": "10",
            "volumeUnit": "cm"
        }]
        
        result1 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=correct_sku_list
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 添加 listPrice
    print("测试2: 添加 listPrice")
    try:
        sku_list_with_list_price = [{
            "outSkuSn": "test_sku_002",
            "specIdList": [spec_id],
            "price": {
                "basePrice": {
                    "amount": "10.00",
                    "currency": "USD"
                },
                "listPrice": {
                    "amount": "15.00",
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
        
        result2 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_list_price
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 添加 listPriceType
    print("测试3: 添加 listPriceType")
    try:
        goods_basic_with_list_price_type = {
            **base_goods_basic,
            "listPriceType": 1
        }
        
        result3 = client.product.goods_add(
            goods_basic=goods_basic_with_list_price_type,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=correct_sku_list
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 添加外部产品信息
    print("测试4: 添加外部产品信息")
    try:
        sku_list_with_external = [{
            "outSkuSn": "test_sku_003",
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
            "volumeUnit": "cm",
            "externalProductType": 1,
            "externalProductId": "EAN123456789"
        }]
        
        result4 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=sku_list_with_external
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 对比新旧格式
    print("5️⃣ 对比新旧格式")
    print("-" * 40)
    
    print("旧格式 (错误):")
    print("  price: 10.0")
    print("  currency: 'USD'")
    print("  inventory: 100")
    print("  skuId: 'test_sku_001'")
    print("  skuImageList: []")
    print()
    
    print("新格式 (正确):")
    print("  price: {")
    print("    basePrice: {")
    print("      amount: '10.00',")
    print("      currency: 'USD'")
    print("    }")
    print("  }")
    print("  quantity: 100")
    print("  outSkuSn: 'test_sku_001'")
    print("  images: []")
    print()
    
    # 测试6: 检查必需字段
    print("6️⃣ 检查必需字段")
    print("-" * 40)
    
    required_sku_fields = [
        "outSkuSn", "specIdList", "price", "quantity", "images",
        "weight", "weightUnit", "length", "width", "height", "volumeUnit"
    ]
    
    print("SKU 必需字段:")
    for field in required_sku_fields:
        print(f"  - {field}")
    print()
    
    print("price 对象必需字段:")
    print("  - basePrice.amount (STRING)")
    print("  - basePrice.currency (STRING)")
    print()
    
    print("物理尺寸必需字段 (STRING 类型):")
    print("  - weight")
    print("  - weightUnit")
    print("  - length")
    print("  - width")
    print("  - height")
    print("  - volumeUnit")


if __name__ == "__main__":
    test_correct_sku_price_format()
