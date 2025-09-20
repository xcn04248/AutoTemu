#!/usr/bin/env python3
"""
测试修复后的官方库

验证修复后的签名生成是否解决了商品创建问题
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

def test_fixed_official_library():
    """测试修复后的官方库"""
    print("🔍 测试修复后的官方库")
    print("=" * 60)
    
    # 创建客户端
    client = TemuClient(
        app_key=os.getenv("TEMU_APP_KEY"),
        app_secret=os.getenv("TEMU_APP_SECRET"),
        access_token=os.getenv("TEMU_ACCESS_TOKEN"),
        base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
        debug=False
    )
    
    print("📋 客户端配置:")
    print(f"  App Key: {os.getenv('TEMU_APP_KEY')[:10]}...")
    print(f"  Base URL: {os.getenv('TEMU_BASE_URL', 'https://openapi-b-global.temu.com')}")
    print()
    
    # 1. 测试连接
    print("1️⃣ 测试连接")
    print("-" * 40)
    try:
        result = client.product.cats_get(parent_cat_id=0)
        if result.get("success"):
            print("  ✅ 连接成功")
            print(f"  📊 获取到 {len(result.get('result', {}).get('goodsCatsList', []))} 个分类")
        else:
            print(f"  ❌ 连接失败: {result.get('errorMsg')}")
            return
    except Exception as e:
        print(f"  ❌ 连接异常: {e}")
        return
    print()
    
    # 2. 测试分类推荐
    print("2️⃣ 测试分类推荐")
    print("-" * 40)
    try:
        category_result = client.product.category_recommend(
            goods_name="测试商品",
            goods_desc="测试描述"
        )
        if category_result.get("success"):
            cat_data = category_result.get("result", {})
            recommended_cat_id = None
            
            if "catId" in cat_data:
                recommended_cat_id = str(cat_data["catId"])
            elif "catIdList" in cat_data and cat_data["catIdList"]:
                recommended_cat_id = str(cat_data["catIdList"][0])
            
            print(f"  ✅ 分类推荐成功")
            print(f"  📊 推荐分类ID: {recommended_cat_id}")
        else:
            print(f"  ❌ 分类推荐失败: {category_result.get('errorMsg')}")
            return
    except Exception as e:
        print(f"  ❌ 分类推荐异常: {e}")
        return
    print()
    
    # 3. 测试规格ID获取
    print("3️⃣ 测试规格ID获取")
    print("-" * 40)
    try:
        spec_result = client.product.spec_id_get(
            cat_id=recommended_cat_id,
            parent_spec_id="1001",
            child_spec_name="颜色"
        )
        if spec_result.get("success"):
            spec_id = spec_result.get("result", {}).get("specId")
            print(f"  ✅ 规格ID获取成功")
            print(f"  📊 规格ID: {spec_id}")
        else:
            print(f"  ❌ 规格ID获取失败: {spec_result.get('errorMsg')}")
            return
    except Exception as e:
        print(f"  ❌ 规格ID获取异常: {e}")
        return
    print()
    
    # 4. 测试商品创建（使用修复后的签名）
    print("4️⃣ 测试商品创建（使用修复后的签名）")
    print("-" * 40)
    try:
        # 构建商品创建参数
        goods_basic = {
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
        }
        
        goods_service_promise = {
            "shippingTemplateId": None,
            "warrantyTemplateId": None,
            "returnTemplateId": None,
            "servicePromise": []
        }
        
        goods_property = {
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
        }
        
        sku_list = [{
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
        
        # 调用商品创建API
        create_result = client.product.goods_add(
            goods_basic=goods_basic,
            goods_service_promise=goods_service_promise,
            goods_property=goods_property,
            sku_list=sku_list
        )
        
        print(f"  📊 创建结果: {create_result}")
        
        if create_result.get("success"):
            print("  ✅ 商品创建成功！")
            print(f"  📊 商品ID: {create_result.get('result', {}).get('goodsId')}")
        else:
            print(f"  ❌ 商品创建失败: {create_result.get('errorMsg')}")
            print(f"  📊 错误码: {create_result.get('errorCode')}")
            
    except Exception as e:
        print(f"  ❌ 商品创建异常: {e}")
    print()
    
    # 5. 总结
    print("5️⃣ 修复总结")
    print("-" * 40)
    print("🔧 修复内容:")
    print("  1. 添加了 json 模块导入")
    print("  2. 修复了 _get_sign 方法:")
    print("     - 添加空值过滤 (跳过 None 值)")
    print("     - 改进嵌套对象处理 (使用 JSON 序列化)")
    print("     - 移除不必要的字符串替换")
    print("     - 确保与 Java 代码逻辑一致")
    print()
    print("📁 备份文件:")
    print("  - 原始文件已备份为: base_client.py.backup")
    print()


if __name__ == "__main__":
    test_fixed_official_library()
