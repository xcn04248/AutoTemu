#!/usr/bin/env python3
"""
基于参考信息测试商品创建

使用从现有商品获取的参考信息来测试商品创建
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def test_goods_add_with_reference():
    """基于参考信息测试商品创建"""
    print("🔍 基于参考信息测试商品创建")
    print("=" * 60)
    
    try:
        # 获取配置
        config = get_config()
        
        # 创建Temu客户端
        temu_client = TemuClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url,
            debug=False
        )
        
        print(f"📋 配置信息:")
        print(f"  - API端点: {config.temu_base_url}")
        print(f"  - App Key: {config.temu_app_key[:8]}...")
        print()
        
        # 1. 获取分类推荐
        print("1️⃣ 获取分类推荐")
        print("-" * 40)
        try:
            category_result = temu_client.product.category_recommend(
                goods_name="测试商品",
                goods_desc="测试描述"
            )
            
            if category_result.get("success"):
                cat_id = category_result.get("result", {}).get("catId")
                print(f"  ✅ 推荐分类ID: {cat_id}")
            else:
                print(f"  ❌ 获取分类推荐失败: {category_result.get('errorMsg')}")
                return
                
        except Exception as e:
            print(f"  ❌ 获取分类推荐异常: {e}")
            return
        print()
        
        # 2. 获取规格ID
        print("2️⃣ 获取规格ID")
        print("-" * 40)
        try:
            spec_result = temu_client.product.spec_id_get(
                cat_id=str(cat_id),
                parent_spec_id="1001",  # 颜色规格
                child_spec_name="颜色"
            )
            
            if spec_result.get("success"):
                spec_id = spec_result.get("result", {}).get("specId")
                print(f"  ✅ 获取到规格ID: {spec_id}")
            else:
                print(f"  ❌ 获取规格ID失败: {spec_result.get('errorMsg')}")
                return
                
        except Exception as e:
            print(f"  ❌ 获取规格ID异常: {e}")
            return
        print()
        
        # 3. 基于参考信息构建商品创建参数
        print("3️⃣ 基于参考信息构建商品创建参数")
        print("-" * 40)
        
        # 使用从现有商品获取的参考格式
        goods_basic = {
            "goodsName": "测试商品",
            "goodsDesc": "测试描述",
            "catId": str(cat_id),
            "specIdList": [spec_id],  # 使用获取到的规格ID
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
            "specIdList": [spec_id],  # 使用获取到的规格ID
            "skuImageList": [],
            "skuAttributeList": [],
            "price": 10.0,
            "currency": "USD",
            "inventory": 100,
            "skuStatus": 1
        }]
        
        print("  📊 商品基础信息:")
        print(json.dumps(goods_basic, indent=2, ensure_ascii=False))
        print()
        
        print("  📊 SKU列表:")
        print(json.dumps(sku_list, indent=2, ensure_ascii=False))
        print()
        
        # 4. 测试商品创建
        print("4️⃣ 测试商品创建")
        print("-" * 40)
        try:
            result = temu_client.product.goods_add(
                goods_basic=goods_basic,
                goods_service_promise=goods_service_promise,
                goods_property=goods_property,
                sku_list=sku_list
            )
            
            print(f"  📊 结果: {result.get('success')}")
            print(f"  📊 错误信息: {result.get('errorMsg')}")
            print(f"  📊 错误码: {result.get('errorCode')}")
            
            if result.get("success"):
                print("  ✅ 商品创建成功！")
                print(f"  📊 商品ID: {result.get('result', {}).get('goodsId')}")
            else:
                print("  ❌ 商品创建失败")
                
        except Exception as e:
            print(f"  ❌ 商品创建异常: {e}")
        print()
        
        # 5. 分析结果
        print("5️⃣ 分析结果")
        print("-" * 40)
        print("  🔍 分析:")
        print("  1. 使用了从现有商品获取的参考格式")
        print("  2. specIdList 包含了正确的规格ID")
        print("  3. 参数格式与现有商品保持一致")
        print("  4. 如果仍然失败，可能是其他参数问题")
        print()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_goods_add_with_reference()
