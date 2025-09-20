#!/usr/bin/env python3
"""
测试 SKU 要求

验证 sku_list 是否必须包含至少一个 SKU
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_sku_requirement():
    """测试 SKU 要求"""
    print("🔍 测试 SKU 要求")
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
    
    # 2. 测试不同的 SKU 配置
    print("2️⃣ 测试不同的 SKU 配置")
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
    
    # 测试1: 空 SKU 列表
    print("测试1: 空 SKU 列表")
    try:
        result1 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=[]
        )
        print(f"  📊 结果: {result1}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 单个 SKU，最小参数
    print("测试2: 单个 SKU，最小参数")
    try:
        result2 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=[{
                "skuId": "test_sku_001",
                "specIdList": [spec_id],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }]
        )
        print(f"  📊 结果: {result2}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 单个 SKU，完整参数
    print("测试3: 单个 SKU，完整参数")
    try:
        result3 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=[{
                "skuId": "test_sku_001",
                "skuName": "M",
                "specIdList": [spec_id],
                "skuImageList": [],
                "skuAttributeList": [],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }]
        )
        print(f"  📊 结果: {result3}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 多个 SKU
    print("测试4: 多个 SKU")
    try:
        result4 = client.product.goods_add(
            goods_basic=base_goods_basic,
            goods_service_promise=base_goods_service_promise,
            goods_property=base_goods_property,
            sku_list=[
                {
                    "skuId": "test_sku_001",
                    "skuName": "S",
                    "specIdList": [spec_id],
                    "price": 10.0,
                    "currency": "USD",
                    "inventory": 100,
                    "skuStatus": 1
                },
                {
                    "skuId": "test_sku_002",
                    "skuName": "M",
                    "specIdList": [spec_id],
                    "price": 10.0,
                    "currency": "USD",
                    "inventory": 100,
                    "skuStatus": 1
                }
            ]
        )
        print(f"  📊 结果: {result4}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试5: 检查 SKU 参数类型
    print("5️⃣ 检查 SKU 参数类型")
    print("-" * 40)
    
    # 测试不同的数据类型
    test_cases = [
        ("字符串价格", {"price": "10.0"}),
        ("整数价格", {"price": 10}),
        ("浮点价格", {"price": 10.0}),
        ("字符串库存", {"inventory": "100"}),
        ("整数库存", {"inventory": 100}),
        ("字符串状态", {"skuStatus": "1"}),
        ("整数状态", {"skuStatus": 1}),
    ]
    
    for test_name, test_params in test_cases:
        print(f"测试: {test_name}")
        try:
            sku_data = {
                "skuId": f"test_sku_{test_name}",
                "specIdList": [spec_id],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1,
                **test_params
            }
            
            result = client.product.goods_add(
                goods_basic=base_goods_basic,
                goods_service_promise=base_goods_service_promise,
                goods_property=base_goods_property,
                sku_list=[sku_data]
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
    
    # 测试6: 检查必需字段
    print("6️⃣ 检查必需字段")
    print("-" * 40)
    
    required_sku_fields = ["skuId", "specIdList", "price", "currency", "inventory", "skuStatus"]
    
    for field in required_sku_fields:
        print(f"测试缺少字段: {field}")
        try:
            sku_data = {
                "skuId": "test_sku_001",
                "specIdList": [spec_id],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }
            # 删除要测试的字段
            if field in sku_data:
                del sku_data[field]
            
            result = client.product.goods_add(
                goods_basic=base_goods_basic,
                goods_service_promise=base_goods_service_promise,
                goods_property=base_goods_property,
                sku_list=[sku_data]
            )
            print(f"  📊 结果: {result}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()


if __name__ == "__main__":
    test_sku_requirement()
