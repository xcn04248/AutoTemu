#!/usr/bin/env python3
"""
Temu API 综合测试

参考 https://github.com/XIE7654/temu_api/blob/main/tests/test_product.py
对 Temu API 的各个接口进行测试
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient


def test_auth_apis(temu_client):
    """测试认证相关API"""
    print("🔐 测试认证相关API")
    print("=" * 50)
    
    try:
        # 获取访问令牌信息
        print("📋 测试 get_access_token_info...")
        res = temu_client.auth.get_access_token_info()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    try:
        # 创建访问令牌信息
        print("📋 测试 create_access_token_info...")
        res = temu_client.auth.create_access_token_info()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_product_apis(temu_client):
    """测试商品相关API"""
    print("🛍️ 测试商品相关API")
    print("=" * 50)
    
    # 测试分类获取
    try:
        print("📋 测试 cats_get (获取分类)...")
        res = temu_client.product.cats_get(parent_cat_id=0)
        print(f"  ✅ 结果: 成功获取 {len(res.get('result', {}).get('goodsCatsList', []))} 个分类")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试分类推荐
    try:
        print("📋 测试 category_recommend (分类推荐)...")
        res = temu_client.product.category_recommend(
            goods_name="测试商品",
            goods_desc="测试描述"
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试尺码表元素获取
    try:
        print("📋 测试 size_element_get (尺码表元素)...")
        res = temu_client.product.size_element_get(
            cat_id="30847",
            size_type="clothing"
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试商品列表查询
    try:
        print("📋 测试 goods_list_query (商品列表查询)...")
        res = temu_client.product.goods_list_query(
            goods_search_type="ACTIVE",
            page_size=10,
            order_field="create_time",
            order_type=0
        )
        print(f"  ✅ 结果: 成功获取商品列表")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试商品列表检索
    try:
        print("📋 测试 goods_list_retrieve (商品列表检索)...")
        res = temu_client.product.goods_list_retrieve(
            goods_search_type="ACTIVE",
            page_size=10,
            order_field="create_time",
            order_type=0
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试SKU列表检索
    try:
        print("📋 测试 sku_list_retrieve (SKU列表检索)...")
        res = temu_client.product.sku_list_retrieve(
            sku_search_type="ACTIVE",
            page_size=10,
            order_field="create_time",
            order_type=0
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试违规词检查
    try:
        print("📋 测试 illegal_vocabulary_check (违规词检查)...")
        res = temu_client.product.illegal_vocabulary_check(
            goods_name="测试商品",
            goods_desc="测试描述"
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试商品属性获取
    try:
        print("📋 测试 property_get (商品属性获取)...")
        res = temu_client.product.property_get(cat_id="30847")
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()
    
    # 测试商品创建（简化版本）
    try:
        print("📋 测试 goods_add (商品创建)...")
        res = temu_client.product.goods_add(
            goods_basic={
                "goodsName": "测试商品",
                "goodsDesc": "测试描述",
                "catId": "30847",
                "goodsType": 1,
                "goodsStatus": 1
            },
            goods_service_promise={},
            goods_property={},
            sku_list=[{
                "skuId": "test_sku_001",
                "skuName": "M"
            }]
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_order_apis(temu_client):
    """测试订单相关API"""
    print("📦 测试订单相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 list_orders_v2 (订单列表)...")
        res = temu_client.order.list_orders_v2()
        print(f"  ✅ 结果: 成功获取订单列表")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_logistics_apis(temu_client):
    """测试物流相关API"""
    print("🚚 测试物流相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 logistics_track (物流跟踪)...")
        res = temu_client.logistics.logistics_track()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_promotion_apis(temu_client):
    """测试促销相关API"""
    print("🎯 测试促销相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 promotion_list (促销列表)...")
        res = temu_client.promotion.promotion_list()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_price_apis(temu_client):
    """测试价格相关API"""
    print("💰 测试价格相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 price_list (价格列表)...")
        res = temu_client.price.price_list()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_aftersales_apis(temu_client):
    """测试售后服务相关API"""
    print("🔧 测试售后服务相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 aftersales_list (售后服务列表)...")
        res = temu_client.aftersales.aftersales_list(
            parent_after_sales_sn_list=['PO-128-01453433636470441']
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_ads_apis(temu_client):
    """测试广告相关API"""
    print("📢 测试广告相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 roas_pred (广告ROAS预测)...")
        res = temu_client.ads.roas_pred(
            goods_info_list=[{"goodsId": 123456789}]
        )
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def test_fulfillment_apis(temu_client):
    """测试履约相关API"""
    print("📋 测试履约相关API")
    print("=" * 50)
    
    try:
        print("📋 测试 fulfillment_list (履约列表)...")
        res = temu_client.fulfillment.fulfillment_list()
        print(f"  ✅ 结果: {res}")
        print()
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        print()


def main():
    """主测试函数"""
    print("🧪 Temu API 综合测试")
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
        
        # 测试各个模块
        test_auth_apis(temu_client)
        test_product_apis(temu_client)
        test_order_apis(temu_client)
        test_logistics_apis(temu_client)
        test_promotion_apis(temu_client)
        test_price_apis(temu_client)
        test_aftersales_apis(temu_client)
        test_ads_apis(temu_client)
        test_fulfillment_apis(temu_client)
        
        print("=" * 60)
        print("✅ 所有API测试完成")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
