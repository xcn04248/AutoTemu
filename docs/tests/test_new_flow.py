#!/usr/bin/env python3
"""
测试新流程是否能解决Applicable Age Group问题
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from complete_product_listing import TemuProductLister

def test_new_flow_with_age_group():
    """测试新流程是否能正确处理Applicable Age Group"""
    print("🔍 测试新流程的Applicable Age Group处理")
    print("=" * 60)
    
    # 创建商品上架器
    lister = TemuProductLister()
    
    # 测试商品信息 - 包含年龄组相关属性
    product_info = {
        # 基础信息
        "goods_name": "Test Product for Age Group",
        "goods_desc": "Test product description",
        "out_goods_sn": "TEST_AGE_GROUP_001",
        "cat_id": "25478",  # 使用之前获取的分类ID
        
        # 规格要求
        "spec_requirements": {
            "color": "色",
            "size": "サイズ"
        },
        
        # 物理属性
        "weight": "0.5",
        "weight_unit": "kg",
        "length": "20",
        "width": "15",
        "height": "10",
        "volume_unit": "cm",
        
        # 价格和库存
        "price": 1500,
        "quantity": 100,
        
        # 服务承诺
        "shipment_limit_day": 2,
        "cost_template_id": "default",
        
        # 商品属性 - 包含年龄组信息
        "material": "Cotton",
        "color": "Blue",
        "size": "M",
        "age_group": "Adult",  # 明确指定年龄组
        
        # 媒体资源
        "image_paths": [],
        "carousel_video": [],
        "detail_video": [],
        
        # 其他信息
        "bullet_points": ["高质量", "舒适", "时尚"],
        "certification_info": {},
        "size_chart": {},
        "trademark_info": {}
    }
    
    print("📋 步骤1: 获取商品分类")
    print("-" * 40)
    if not lister.step1_get_categories():
        print("❌ 获取分类失败")
        return False
    
    print("\n📋 步骤2: 获取分类属性模板")
    print("-" * 40)
    if not lister.step2_get_category_template(product_info["cat_id"]):
        print("❌ 获取模板失败")
        return False
    
    # 检查模板中是否包含年龄组属性
    template = lister.templates_cache.get(product_info["cat_id"], {})
    properties = template.get("propertyList", [])
    
    print(f"\n📊 分类模板分析:")
    print(f"  总属性数量: {len(properties)}")
    
    age_group_props = []
    required_props = []
    
    for prop in properties:
        prop_name = prop.get("propertyName", "").lower()
        is_required = prop.get("required", False)
        
        if is_required:
            required_props.append(prop)
        
        if "age" in prop_name or "applicable" in prop_name:
            age_group_props.append(prop)
            print(f"  🎯 找到年龄组属性: {prop.get('propertyName')} (必填: {is_required})")
    
    print(f"  必填属性数量: {len(required_props)}")
    print(f"  年龄组属性数量: {len(age_group_props)}")
    
    if age_group_props:
        print(f"\n✅ 发现年龄组属性，新流程应该能正确处理")
        
        # 测试属性值映射
        print(f"\n🔍 测试属性值映射:")
        for prop in age_group_props:
            mapped_value = lister._get_property_value(prop, product_info)
            print(f"  属性: {prop.get('propertyName')} -> 值: {mapped_value}")
    else:
        print(f"\n⚠️  未发现年龄组属性，可能需要检查分类ID")
    
    print(f"\n📋 步骤3: 获取合规规则")
    print("-" * 40)
    if not lister.step3_get_compliance_rules(product_info["cat_id"]):
        print("❌ 获取合规规则失败")
        return False
    
    print(f"\n📋 步骤4: 检查违规词汇")
    print("-" * 40)
    if not lister.step5_check_illegal_vocabulary(product_info["goods_name"], product_info["goods_desc"]):
        print("❌ 违规词汇检查失败")
        return False
    
    print(f"\n📋 步骤5: 生成规格ID")
    print("-" * 40)
    spec_ids = {}
    if not lister.step4_generate_spec_ids(product_info["cat_id"], product_info["spec_requirements"]):
        print("❌ 生成规格ID失败")
        return False
    
    print(f"\n📋 步骤6: 上传图片")
    print("-" * 40)
    uploaded_images = []
    if not lister.step6_upload_images(product_info["image_paths"]):
        print("❌ 上传图片失败")
        return False
    
    print(f"\n📋 步骤7: 检查合规性")
    print("-" * 40)
    if not lister.step7_check_compliance(product_info):
        print("❌ 合规性检查失败")
        return False
    
    print(f"\n📋 步骤8: 获取税码信息")
    print("-" * 40)
    if not lister.step8_get_tax_code(product_info["cat_id"], product_info["goods_name"]):
        print("❌ 获取税码失败")
        return False
    
    print(f"\n📋 步骤9: 获取运费模板")
    print("-" * 40)
    if not lister.step9_get_freight_templates():
        print("❌ 获取运费模板失败")
        return False
    
    print(f"\n📋 步骤10: 创建商品")
    print("-" * 40)
    
    # 构建商品数据
    uploaded_images = []  # 暂时没有图片
    tax_code = lister.tax_codes_cache.get(product_info["cat_id"], {})
    
    product_data = lister._build_product_data(
        product_info, 
        spec_ids, 
        uploaded_images, 
        tax_code
    )
    
    print(f"📊 构建的商品数据:")
    print(f"  商品名称: {product_data['goods_basic']['goodsName']}")
    print(f"  分类ID: {product_data['goods_basic']['catId']}")
    print(f"  规格ID列表: {product_data['goods_basic']['specIdList']}")
    print(f"  商品属性数量: {len(product_data['goods_property']['goodsProperties'])}")
    
    # 检查是否包含年龄组属性
    age_group_found = False
    for prop in product_data['goods_property']['goodsProperties']:
        if "age" in str(prop.get("value", "")).lower() or "adult" in str(prop.get("value", "")).lower():
            age_group_found = True
            print(f"  🎯 找到年龄组属性: {prop}")
            break
    
    if age_group_found:
        print(f"\n✅ 新流程成功处理了年龄组属性！")
    else:
        print(f"\n⚠️  未在商品属性中找到年龄组信息")
    
    print(f"\n📋 尝试创建商品...")
    if lister.step10_create_product(product_data):
        print(f"\n✅ 商品创建成功！新流程解决了Applicable Age Group问题")
        return True
    else:
        print(f"\n❌ 商品创建失败")
        return False

if __name__ == "__main__":
    test_new_flow_with_age_group()
