#!/usr/bin/env python3
"""
获取已有商品的 SKU 作为参考 (版本2)

通过 goods_list_query API 获取现有商品的 SKU 信息
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json


def get_sku_reference_v2():
    """获取已有商品的 SKU 作为参考"""
    print("🔍 获取已有商品的 SKU 作为参考 (版本2)")
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
            result = temu_client.product.goods_list_query(
                page_no=1,
                page_size=5,  # 只获取前5个商品
                goods_search_type="ACTIVE",
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
                    
                    # 2. 分析商品基本信息
                    print("\n2️⃣ 分析商品基本信息")
                    print("-" * 40)
                    
                    print(f"  📊 商品ID: {first_goods.get('goodsId')}")
                    print(f"  📊 商品名称: {first_goods.get('goodsName')}")
                    print(f"  📊 分类ID: {first_goods.get('catId')}")
                    print(f"  📊 商品状态: {first_goods.get('goodsStatus')}")
                    print(f"  📊 商品类型: {first_goods.get('catType')}")
                    print(f"  📊 品牌ID: {first_goods.get('brandId')}")
                    print(f"  📊 商标ID: {first_goods.get('trademarkId')}")
                    print(f"  📊 变体数量: {first_goods.get('variationsCount')}")
                    
                    # 3. 分析 SKU 信息
                    print("\n3️⃣ 分析 SKU 信息")
                    print("-" * 40)
                    
                    sku_info_list = first_goods.get("skuInfoList", [])
                    print(f"  📊 SKU数量: {len(sku_info_list)}")
                    
                    for i, sku_info in enumerate(sku_info_list[:3]):  # 只显示前3个SKU
                        print(f"    {i+1}. SKU ID: {sku_info.get('skuId')}")
                        print(f"       SKU SN: {sku_info.get('skuSn')}")
                        
                        # 分析规格信息
                        spec_list = sku_info.get("specList", [])
                        print(f"       规格数量: {len(spec_list)}")
                        for j, spec in enumerate(spec_list):
                            print(f"         {j+1}. 规格ID: {spec.get('specId')}, 父规格ID: {spec.get('parentSpecId')}")
                    
                    # 4. 获取 SKU 详细信息
                    print("\n4️⃣ 获取 SKU 详细信息")
                    print("-" * 40)
                    try:
                        sku_result = temu_client.product.sku_list_retrieve(
                            sku_search_type="ACTIVE",
                            page_size=10,
                            order_field="create_time",
                            order_type=0
                        )
                        
                        if sku_result.get("success"):
                            sku_list = sku_result.get("result", {}).get("skuList", [])
                            print(f"  ✅ 成功获取 {len(sku_list)} 个 SKU 详情")
                            
                            if sku_list:
                                # 选择第一个 SKU 进行详细分析
                                first_sku = sku_list[0]
                                print(f"  📊 选择 SKU: {first_sku.get('skuName')} (ID: {first_sku.get('skuId')})")
                                
                                # 分析 SKU 详细信息
                                print("\n5️⃣ 分析 SKU 详细信息")
                                print("-" * 40)
                                
                                print(f"  📊 SKU ID: {first_sku.get('skuId')}")
                                print(f"  📊 SKU 名称: {first_sku.get('skuName')}")
                                print(f"  📊 SKU SN: {first_sku.get('skuSn')}")
                                print(f"  📊 外部 SKU SN: {first_sku.get('outSkuSn')}")
                                print(f"  📊 商品 ID: {first_sku.get('goodsId')}")
                                print(f"  📊 分类 ID: {first_sku.get('catId')}")
                                print(f"  📊 SKU 状态: {first_sku.get('skuStatus')}")
                                print(f"  📊 SKU 子状态: {first_sku.get('skuSubStatus')}")
                                print(f"  📊 规格名称: {first_sku.get('specName')}")
                                
                                # 分析规格信息
                                spec_list = first_sku.get("specList", [])
                                print(f"  📊 规格数量: {len(spec_list)}")
                                for i, spec in enumerate(spec_list):
                                    print(f"    {i+1}. 规格ID: {spec.get('specId')}, 父规格ID: {spec.get('parentSpecId')}")
                                
                                # 分析重量和尺寸信息
                                weight_info = first_sku.get("weightInfo", {})
                                volume_info = first_sku.get("volumeInfo", {})
                                
                                print(f"  📊 重量信息: {weight_info}")
                                print(f"  📊 尺寸信息: {volume_info}")
                                
                                # 6. 生成参考模板
                                print("\n6️⃣ 生成参考模板")
                                print("-" * 40)
                                
                                # 生成 goods_basic 模板
                                print("  📊 goods_basic 模板:")
                                template_goods_basic = {
                                    "goodsName": first_goods.get("goodsName", "商品名称"),
                                    "goodsDesc": "商品描述",  # 从商品列表中没有获取到描述
                                    "catId": first_goods.get("catId", "分类ID"),
                                    "specIdList": [spec.get("specId") for spec in spec_list if spec.get("specId")],
                                    "brandId": first_goods.get("brandId"),
                                    "trademarkId": first_goods.get("trademarkId"),
                                    "goodsType": first_goods.get("catType", 1),
                                    "goodsStatus": 1,  # 假设为1（上架状态）
                                    "goodsWeight": weight_info.get("weight", 0.1),
                                    "goodsLength": volume_info.get("length", 10),
                                    "goodsWidth": volume_info.get("width", 10),
                                    "goodsHeight": volume_info.get("height", 10),
                                    "packageLength": volume_info.get("length", 15),
                                    "packageWidth": volume_info.get("width", 15),
                                    "packageHeight": volume_info.get("height", 15),
                                    "packageWeight": weight_info.get("weight", 0.2),
                                    "goodsImageList": [],
                                    "goodsVideoList": [],
                                    "goodsAttributeList": []
                                }
                                
                                print(json.dumps(template_goods_basic, indent=2, ensure_ascii=False))
                                print()
                                
                                # 生成 sku_list 模板
                                print("  📊 sku_list 模板:")
                                template_sku = {
                                    "skuId": first_sku.get("skuId", "SKU_ID"),
                                    "skuName": first_sku.get("skuName", "SKU名称"),
                                    "specIdList": [spec.get("specId") for spec in spec_list if spec.get("specId")],
                                    "skuImageList": [],
                                    "skuAttributeList": [],
                                    "price": 0.0,  # 从 SKU 列表中没有获取到价格
                                    "currency": "USD",
                                    "inventory": 0,  # 从 SKU 列表中没有获取到库存
                                    "skuStatus": 1
                                }
                                
                                print(json.dumps(template_sku, indent=2, ensure_ascii=False))
                                
                        else:
                            print(f"  ❌ 获取 SKU 详情失败: {sku_result.get('errorMsg')}")
                            
                    except Exception as e:
                        print(f"  ❌ 获取 SKU 详情异常: {e}")
                    
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
    get_sku_reference_v2()
