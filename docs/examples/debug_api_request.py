#!/usr/bin/env python3
"""
调试Temu API请求

查看API请求的详细信息和签名计算
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient


def debug_api_request():
    """调试API请求"""
    print("🔍 调试Temu API请求")
    print("=" * 50)
    
    try:
        config = get_config()
        
        # 创建官方客户端
        client = TemuClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url,
            debug=True  # 启用调试模式
        )
        
        print(f"📋 配置信息:")
        print(f"  - API端点: {config.temu_base_url}")
        print(f"  - App Key: {config.temu_app_key[:8]}...")
        print(f"  - App Secret: {config.temu_app_secret[:8]}...")
        print(f"  - Access Token: {config.temu_access_token[:8]}...")
        print()
        
        # 测试简单的API调用
        print("🔌 测试分类获取API...")
        try:
            result = client.product.cats_get(parent_cat_id=0)
            print(f"  ✅ 分类获取成功: {result}")
        except Exception as e:
            print(f"  ❌ 分类获取失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试商品创建API（使用最简单的参数）
        print("\n🚀 测试商品创建API...")
        try:
            # 最简单的商品创建参数
            goods_basic = {
                "goodsName": "测试商品",
                "goodsDesc": "测试描述",
                "catId": "30847",
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
                "skuImageList": [],
                "skuAttributeList": [],
                "price": 35.1,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }]
            
            result = client.product.goods_add(
                goods_basic=goods_basic,
                goods_service_promise=goods_service_promise,
                goods_property=goods_property,
                sku_list=sku_list
            )
            print(f"  ✅ 商品创建成功: {result}")
        except Exception as e:
            print(f"  ❌ 商品创建失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("✅ API调试完成")
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api_request()
