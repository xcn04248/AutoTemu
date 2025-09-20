#!/usr/bin/env python3
"""
测试增强版商品上架功能
"""

import os
import sys
import time
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 加载环境变量
load_dotenv()

from docs.examples.enhanced_product_listing import EnhancedTemuProductLister

def test_api_connection():
    """测试API连接"""
    print("🔍 测试 API 连接")
    print("=" * 40)
    
    lister = EnhancedTemuProductLister()
    success = lister.test_connection()
    
    if success:
        print("✅ API 连接测试通过")
    else:
        print("❌ API 连接测试失败")
    
    return success

def test_get_categories():
    """测试获取分类"""
    print("\n🔍 测试获取分类")
    print("=" * 40)
    
    lister = EnhancedTemuProductLister()
    success = lister.step1_get_categories()
    
    if success:
        print("✅ 获取分类测试通过")
        print(f"📊 缓存了 {len(lister.categories_cache)} 个分类")
    else:
        print("❌ 获取分类测试失败")
    
    return success

def test_get_category_template():
    """测试获取分类模板"""
    print("\n🔍 测试获取分类模板")
    print("=" * 40)
    
    lister = EnhancedTemuProductLister()
    
    # 先获取分类
    if not lister.step1_get_categories():
        print("❌ 无法获取分类，跳过模板测试")
        return False
    
    # 使用第一个分类进行测试
    cat_id = list(lister.categories_cache.keys())[0]
    success = lister.step2_get_category_template(cat_id)
    
    if success:
        print("✅ 获取分类模板测试通过")
        template = lister.templates_cache.get(cat_id, {})
        properties = template.get("propertyList", [])
        print(f"📊 分类 {cat_id} 有 {len(properties)} 个属性")
    else:
        print("❌ 获取分类模板测试失败")
    
    return success

def test_illegal_vocabulary_check():
    """测试违规词汇检查"""
    print("\n🔍 测试违规词汇检查")
    print("=" * 40)
    
    lister = EnhancedTemuProductLister()
    
    # 测试正常词汇
    success1 = lister.step5_check_illegal_vocabulary(
        "テスト商品",
        "高品質な商品です"
    )
    
    # 测试可能违规的词汇
    success2 = lister.step5_check_illegal_vocabulary(
        "最高級商品",
        "最高品質の商品です"
    )
    
    if success1 and success2:
        print("✅ 违规词汇检查测试通过")
    else:
        print("❌ 违规词汇检查测试失败")
    
    return success1 and success2

def test_complete_flow():
    """测试完整流程（不实际上架）"""
    print("\n🔍 测试完整流程")
    print("=" * 40)
    
    lister = EnhancedTemuProductLister()
    
    # 测试商品信息
    product_info = {
        "goods_name": "テスト商品 - 高品質Tシャツ",
        "goods_desc": "高品質なコットン素材を使用した快適なTシャツです。",
        "out_goods_sn": f"TEST_GOODS_{int(time.time())}",
        "cat_id": "25478",  # 使用测试分类ID
        
        "spec_requirements": {
            "color": "色",
            "size": "サイズ"
        },
        
        "weight": "0.3",
        "weight_unit": "kg",
        "length": "30",
        "width": "25",
        "height": "2",
        "volume_unit": "cm",
        
        "price": 2000,
        "quantity": 50,
        
        "shipment_limit_day": 2,
        "cost_template_id": "default",
        
        "material": "Cotton",
        "color": "Blue",
        "size": "M",
        
        "sku_list": [
            {
                "out_sku_sn": f"sku_blue_m_{int(time.time())}",
                "price": 2000,
                "quantity": 25,
                "color": "Blue",
                "size": "M"
            }
        ],
        
        "image_paths": [],
        "carousel_video": [],
        "detail_video": [],
        
        "bullet_points": ["高品質", "快適", "ファッション"],
        "certification_info": {},
        "size_chart": {},
        "trademark_info": {}
    }
    
    # 只测试前几个步骤，不实际上架
    print("📋 测试步骤1-5（不实际上架）")
    
    # 步骤1: 获取分类
    if not lister.step1_get_categories():
        print("❌ 步骤1失败")
        return False
    
    # 步骤2: 获取分类模板
    if not lister.step2_get_category_template(product_info["cat_id"]):
        print("❌ 步骤2失败")
        return False
    
    # 步骤3: 获取合规规则
    if not lister.step3_get_compliance_rules(product_info["cat_id"]):
        print("❌ 步骤3失败")
        return False
    
    # 步骤4: 生成规格ID
    spec_ids = lister.step4_generate_spec_ids(
        product_info["cat_id"], 
        product_info["spec_requirements"]
    )
    if not spec_ids:
        print("❌ 步骤4失败")
        return False
    
    # 步骤5: 检查违规词汇
    if not lister.step5_check_illegal_vocabulary(
        product_info["goods_name"],
        product_info["goods_desc"]
    ):
        print("❌ 步骤5失败")
        return False
    
    print("✅ 完整流程测试通过（前5步）")
    return True

def main():
    """主测试函数"""
    print("🧪 增强版商品上架功能测试")
    print("=" * 60)
    
    # 检查环境变量
    required_vars = ["TEMU_APP_KEY", "TEMU_APP_SECRET", "TEMU_ACCESS_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件配置")
        return False
    
    # 运行测试
    tests = [
        ("API连接", test_api_connection),
        ("获取分类", test_get_categories),
        ("获取分类模板", test_get_category_template),
        ("违规词汇检查", test_illegal_vocabulary_check),
        ("完整流程", test_complete_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n📊 测试结果汇总")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置和API状态")
        return False

if __name__ == "__main__":
    main()
