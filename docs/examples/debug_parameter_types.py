#!/usr/bin/env python3
"""
调试参数类型错误

分析 goods_add API 的参数类型问题
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def debug_parameter_types():
    """调试参数类型错误"""
    print("🔍 调试参数类型错误")
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
    
    # 获取分类推荐
    category_result = client.product.category_recommend(
        goods_name="测试商品",
        goods_desc="测试描述"
    )
    recommended_cat_id = str(category_result.get("result", {}).get("catId", "26579"))
    print(f"  📊 推荐分类ID: {recommended_cat_id}")
    
    # 获取规格ID
    spec_result = client.product.spec_id_get(
        cat_id=recommended_cat_id,
        parent_spec_id="1001",
        child_spec_name="颜色"
    )
    spec_id = spec_result.get("result", {}).get("specId")
    print(f"  📊 规格ID: {spec_id}")
    print()
    
    # 2. 测试不同的参数格式
    print("2️⃣ 测试不同的参数格式")
    print("-" * 40)
    
    # 测试1: 最简参数
    print("测试1: 最简参数")
    try:
        simple_result = client.product.goods_add(
            goods_basic={
                "goodsName": "测试商品",
                "catId": recommended_cat_id,
                "specIdList": [spec_id]
            },
            goods_service_promise={},
            goods_property={},
            sku_list=[]
        )
        print(f"  📊 结果: {simple_result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试2: 添加必需字段
    print("测试2: 添加必需字段")
    try:
        basic_result = client.product.goods_add(
            goods_basic={
                "goodsName": "测试商品",
                "goodsDesc": "测试描述",
                "catId": recommended_cat_id,
                "specIdList": [spec_id],
                "goodsType": 1,
                "goodsStatus": 1
            },
            goods_service_promise={
                "servicePromise": []
            },
            goods_property={
                "material": "Cotton"
            },
            sku_list=[]
        )
        print(f"  📊 结果: {basic_result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试3: 添加SKU
    print("测试3: 添加SKU")
    try:
        sku_result = client.product.goods_add(
            goods_basic={
                "goodsName": "测试商品",
                "goodsDesc": "测试描述",
                "catId": recommended_cat_id,
                "specIdList": [spec_id],
                "goodsType": 1,
                "goodsStatus": 1
            },
            goods_service_promise={
                "servicePromise": []
            },
            goods_property={
                "material": "Cotton"
            },
            sku_list=[{
                "skuId": "test_sku_001",
                "specIdList": [spec_id],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }]
        )
        print(f"  📊 结果: {sku_result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()
    
    # 测试4: 检查官方库的方法签名
    print("4️⃣ 检查官方库的方法签名")
    print("-" * 40)
    
    import inspect
    print(f"  📊 goods_add 方法签名:")
    print(f"  {inspect.signature(client.product.goods_add)}")
    print()
    
    # 测试5: 查看官方库的源码
    print("5️⃣ 查看官方库的源码")
    print("-" * 40)
    
    try:
        import temu_api.api.product
        source_file = temu_api.api.product.__file__
        print(f"  📊 源码文件: {source_file}")
        
        # 读取 goods_add 方法
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'def goods_add' in content:
                start = content.find('def goods_add')
                end = content.find('\n    def ', start + 1)
                if end == -1:
                    end = content.find('\nclass ', start + 1)
                if end == -1:
                    end = start + 1000
                
                method_code = content[start:end]
                print(f"  📊 goods_add 方法代码:")
                print(f"  {method_code[:500]}...")
        
    except Exception as e:
        print(f"  ❌ 无法读取源码: {e}")
    print()
    
    # 测试6: 检查参数验证
    print("6️⃣ 检查参数验证")
    print("-" * 40)
    
    # 检查 goods_basic 的必需字段
    required_fields = [
        "goodsName", "catId", "specIdList", "goodsType", "goodsStatus"
    ]
    
    print("  📊 goods_basic 必需字段:")
    for field in required_fields:
        print(f"    - {field}")
    print()
    
    # 检查 sku_list 的必需字段
    sku_required_fields = [
        "skuId", "specIdList", "price", "currency", "inventory", "skuStatus"
    ]
    
    print("  📊 sku_list 必需字段:")
    for field in sku_required_fields:
        print(f"    - {field}")
    print()
    
    # 测试7: 使用完整的参数
    print("7️⃣ 使用完整的参数")
    print("-" * 40)
    
    try:
        complete_result = client.product.goods_add(
            goods_basic={
                "goodsName": "测试商品",
                "goodsDesc": "测试描述",
                "catId": recommended_cat_id,
                "specIdList": [spec_id],
                "brandId": None,
                "trademarkId": None,
                "goodsType": 1,
                "goodsStatus": 1,
                "goodsWeight": 0.1,
                "goodsLength": 10,
                "goodsWidth": 10,
                "goodsHeight": 10,
                "packageLength": 15,
                "packageWidth": 15,
                "packageHeight": 15,
                "packageWeight": 0.2,
                "goodsImageList": [],
                "goodsVideoList": [],
                "goodsAttributeList": []
            },
            goods_service_promise={
                "shippingTemplateId": None,
                "warrantyTemplateId": None,
                "returnTemplateId": None,
                "servicePromise": []
            },
            goods_property={
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
                "careInstructions": "Machine Wash"
            },
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
        print(f"  📊 结果: {complete_result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    print()


if __name__ == "__main__":
    debug_parameter_types()