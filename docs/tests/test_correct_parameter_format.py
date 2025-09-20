#!/usr/bin/env python3
"""
测试正确的参数格式

使用正确的参数名称格式测试商品创建 API
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def test_correct_parameter_format():
    """测试正确的参数格式"""
    print("🔍 测试正确的参数格式")
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
        
        # 1. 获取 specId
        print("1️⃣ 获取 specId")
        print("-" * 40)
        try:
            result = temu_client.product.spec_id_get(
                cat_id="30847",
                parent_spec_id="1001",
                child_spec_name="颜色"
            )
            if result.get("success"):
                spec_id = result.get("result", {}).get("specId")
                print(f"  ✅ 获取到 specId: {spec_id}")
            else:
                print(f"  ❌ 获取 specId 失败: {result.get('errorMsg')}")
                return
        except Exception as e:
            print(f"  ❌ 获取 specId 异常: {e}")
            return
        print()
        
        # 2. 使用正确的参数格式
        print("2️⃣ 使用正确的参数格式")
        print("-" * 40)
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847",
                    "specIdList": [spec_id]  # 使用获取到的 specId
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
                    "price": 10.0,
                    "currency": "USD",
                    "inventory": 100,
                    "skuStatus": 1,
                    "specIdList": [spec_id]  # 使用获取到的 specId
                }]
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
            print(f"  ❌ 异常: {e}")
        print()
        
        # 3. 分析问题
        print("3️⃣ 分析问题")
        print("-" * 40)
        print("  问题分析:")
        print("  1. 签名验证成功（没有 'sign is invalid' 错误）")
        print("  2. 参数验证失败：'parameters type is error'")
        print("  3. 可能是参数结构不正确")
        print("  4. 需要检查官方库的参数格式要求")
        print()
        
        # 4. 检查参数格式
        print("4️⃣ 检查参数格式")
        print("-" * 40)
        print("  官方库期望的参数格式:")
        print("  - goods_basic -> goodsBasic")
        print("  - goods_service_promise -> goodsServicePromise")
        print("  - goods_property -> goodsProperty")
        print("  - sku_list -> skuList")
        print("  - specIdList 需要在 goods_basic 和 sku_list 中")
        print()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_correct_parameter_format()
