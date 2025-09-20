#!/usr/bin/env python3
"""
获取已有商品的 SKU 作为参考

通过 API 获取现有商品的 SKU 信息，了解正确的参数格式
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def get_existing_sku_reference():
    """获取已有商品的 SKU 作为参考"""
    print("🔍 获取已有商品的 SKU 作为参考")
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
        
        # 1. 获取商品列表
        print("1️⃣ 获取商品列表")
        print("-" * 40)
        try:
            result = temu_client.product.goods_list_retrieve(
                goods_search_type="ACTIVE",
                page_size=5,  # 只获取前5个商品
                order_field="create_time",
                order_type=0
            )
            
            if result.get("success"):
                goods_list = result.get("result", {}).get("goodsList", [])
                print(f"  ✅ 成功获取 {len(goods_list)} 个商品")
                
                if goods_list:
                    # 选择第一个商品进行详细分析
                    first_goods = goods_list[0]
                    goods_id = first_goods.get("goodsId")
                    goods_name = first_goods.get("goodsName")
                    print(f"  📊 选择商品: {goods_name} (ID: {goods_id})")
                    
                    # 2. 获取该商品的详细信息
                    print("\n2️⃣ 获取商品详细信息")
                    print("-" * 40)
                    try:
                        detail_result = temu_client.product.goods_detail_query(goods_id=goods_id)
                        if detail_result.get("success"):
                            detail = detail_result.get("result", {})
                            print(f"  ✅ 商品详情获取成功")
                            
                            # 显示商品基本信息
                            print(f"  📊 商品名称: {detail.get('goodsName')}")
                            print(f"  📊 分类ID: {detail.get('catId')}")
                            print(f"  📊 商品状态: {detail.get('goodsStatus')}")
                            print(f"  📊 商品类型: {detail.get('goodsType')}")
                            
                            # 显示规格信息
                            spec_list = detail.get("specList", [])
                            print(f"  📊 规格数量: {len(spec_list)}")
                            for i, spec in enumerate(spec_list):
                                print(f"    {i+1}. 规格ID: {spec.get('specId')}, 父规格ID: {spec.get('parentSpecId')}, 规格名称: {spec.get('specName')}")
                            
                            # 显示 SKU 信息
                            sku_list = detail.get("skuList", [])
                            print(f"  📊 SKU数量: {len(sku_list)}")
                            for i, sku in enumerate(sku_list[:3]):  # 只显示前3个SKU
                                print(f"    {i+1}. SKU ID: {sku.get('skuId')}")
                                print(f"       规格ID列表: {sku.get('specIdList', [])}")
                                print(f"       SKU名称: {sku.get('skuName')}")
                                print(f"       价格: {sku.get('price')}")
                                print(f"       货币: {sku.get('currency')}")
                                print(f"       库存: {sku.get('inventory')}")
                                print(f"       状态: {sku.get('skuStatus')}")
                                print()
                            
                            # 3. 分析参数格式
                            print("3️⃣ 分析参数格式")
                            print("-" * 40)
                            
                            # 分析 goods_basic 格式
                            print("  📊 goods_basic 格式分析:")
                            goods_basic_keys = [
                                "goodsName", "goodsDesc", "catId", "specIdList", 
                                "brandId", "trademarkId", "goodsType", "goodsStatus",
                                "goodsWeight", "goodsLength", "goodsWidth", "goodsHeight",
                                "packageLength", "packageWidth", "packageHeight", "packageWeight",
                                "goodsImageList", "goodsVideoList", "goodsAttributeList"
                            ]
                            
                            for key in goods_basic_keys:
                                value = detail.get(key)
                                if value is not None:
                                    print(f"    {key}: {type(value).__name__} = {value}")
                            
                            print()
                            
                            # 分析 sku_list 格式
                            print("  📊 sku_list 格式分析:")
                            if sku_list:
                                first_sku = sku_list[0]
                                sku_keys = [
                                    "skuId", "skuName", "specIdList", "skuImageList", 
                                    "skuAttributeList", "price", "currency", "inventory", "skuStatus"
                                ]
                                
                                for key in sku_keys:
                                    value = first_sku.get(key)
                                    if value is not None:
                                        print(f"    {key}: {type(value).__name__} = {value}")
                            
                            print()
                            
                            # 4. 生成参考模板
                            print("4️⃣ 生成参考模板")
                            print("-" * 40)
                            
                            # 生成 goods_basic 模板
                            print("  📊 goods_basic 模板:")
                            template_goods_basic = {
                                "goodsName": detail.get("goodsName", "商品名称"),
                                "goodsDesc": detail.get("goodsDesc", "商品描述"),
                                "catId": detail.get("catId", "分类ID"),
                                "specIdList": detail.get("specIdList", []),
                                "brandId": detail.get("brandId"),
                                "trademarkId": detail.get("trademarkId"),
                                "goodsType": detail.get("goodsType", 1),
                                "goodsStatus": detail.get("goodsStatus", 1),
                                "goodsWeight": detail.get("goodsWeight", 0.1),
                                "goodsLength": detail.get("goodsLength", 10),
                                "goodsWidth": detail.get("goodsWidth", 10),
                                "goodsHeight": detail.get("goodsHeight", 10),
                                "packageLength": detail.get("packageLength", 15),
                                "packageWidth": detail.get("packageWidth", 15),
                                "packageHeight": detail.get("packageHeight", 15),
                                "packageWeight": detail.get("packageWeight", 0.2),
                                "goodsImageList": detail.get("goodsImageList", []),
                                "goodsVideoList": detail.get("goodsVideoList", []),
                                "goodsAttributeList": detail.get("goodsAttributeList", [])
                            }
                            
                            print(json.dumps(template_goods_basic, indent=2, ensure_ascii=False))
                            print()
                            
                            # 生成 sku_list 模板
                            print("  📊 sku_list 模板:")
                            if sku_list:
                                template_sku = {
                                    "skuId": sku_list[0].get("skuId", "SKU_ID"),
                                    "skuName": sku_list[0].get("skuName", "SKU名称"),
                                    "specIdList": sku_list[0].get("specIdList", []),
                                    "skuImageList": sku_list[0].get("skuImageList", []),
                                    "skuAttributeList": sku_list[0].get("skuAttributeList", []),
                                    "price": sku_list[0].get("price", 0.0),
                                    "currency": sku_list[0].get("currency", "USD"),
                                    "inventory": sku_list[0].get("inventory", 0),
                                    "skuStatus": sku_list[0].get("skuStatus", 1)
                                }
                                
                                print(json.dumps(template_sku, indent=2, ensure_ascii=False))
                            
                        else:
                            print(f"  ❌ 商品详情获取失败: {detail_result.get('errorMsg')}")
                            
                    except Exception as e:
                        print(f"  ❌ 获取商品详情异常: {e}")
                    
                else:
                    print("  ❌ 没有找到商品")
            else:
                print(f"  ❌ 获取商品列表失败: {result.get('errorMsg')}")
                
        except Exception as e:
            print(f"  ❌ 获取商品列表异常: {e}")
        print()
        
    except Exception as e:
        print(f"❌ 获取参考信息过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    get_existing_sku_reference()
