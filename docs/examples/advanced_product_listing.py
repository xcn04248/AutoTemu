#!/usr/bin/env python3
"""
高级版 Temu 商品上架流程

解决叶子分类问题，实现完整的商品上架功能
"""

import os
import sys
import time
import json
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

class AdvancedTemuProductLister:
    """高级版 Temu 商品上架器"""
    
    def __init__(self):
        """初始化商品上架器"""
        self.client = TemuClient(
            app_key=os.getenv("TEMU_APP_KEY"),
            app_secret=os.getenv("TEMU_APP_SECRET"),
            access_token=os.getenv("TEMU_ACCESS_TOKEN"),
            base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
            debug=True
        )
        
        # 缓存数据
        self.categories_cache = {}
        self.leaf_categories_cache = {}
        self.templates_cache = {}
        self.compliance_rules_cache = {}
        self.spec_ids_cache = {}
        self.uploaded_images_cache = {}
        
    def test_connection(self) -> bool:
        """测试API连接"""
        print("🔍 测试 Temu API 连接...")
        try:
            result = self.client.product.cats_get(parent_cat_id=0)
            if result.get("success"):
                print("✅ API 连接成功")
                return True
            else:
                print(f"❌ API 连接失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"❌ API 连接异常: {e}")
            return False
    
    def find_leaf_categories(self, parent_cat_id: int = 0, max_depth: int = 3) -> List[Dict[str, Any]]:
        """递归查找叶子分类"""
        print(f"🔍 查找分类 {parent_cat_id} 的子分类...")
        
        try:
            result = self.client.product.cats_get(parent_cat_id=parent_cat_id)
            if not result.get("success"):
                print(f"❌ 获取分类失败: {result.get('errorMsg')}")
                return []
            
            categories = result.get("result", {}).get("goodsCatsList", [])
            if not categories:
                print(f"✅ 分类 {parent_cat_id} 是叶子分类")
                return [{"catId": parent_cat_id, "catName": "Leaf Category"}]
            
            leaf_categories = []
            for cat in categories:
                cat_id = cat.get("catId")
                cat_name = cat.get("catName")
                print(f"  📁 发现子分类: {cat_name} (ID: {cat_id})")
                
                # 递归查找子分类
                sub_leafs = self.find_leaf_categories(cat_id, max_depth - 1)
                if sub_leafs:
                    leaf_categories.extend(sub_leafs)
                else:
                    # 如果没有子分类，说明这是叶子分类
                    leaf_categories.append(cat)
            
            return leaf_categories
        except Exception as e:
            print(f"❌ 查找分类异常: {e}")
            return []
    
    def get_leaf_categories(self) -> List[Dict[str, Any]]:
        """获取所有叶子分类"""
        print("📋 获取所有叶子分类")
        print("-" * 40)
        
        if self.leaf_categories_cache:
            print(f"  ✅ 从缓存获取到 {len(self.leaf_categories_cache)} 个叶子分类")
            return list(self.leaf_categories_cache.values())
        
        leaf_categories = self.find_leaf_categories()
        self.leaf_categories_cache = {cat.get("catId"): cat for cat in leaf_categories}
        
        print(f"  ✅ 找到 {len(leaf_categories)} 个叶子分类")
        
        # 显示前几个叶子分类
        for i, cat in enumerate(leaf_categories[:5]):
            print(f"    {i+1}. {cat.get('catName')} (ID: {cat.get('catId')})")
        
        return leaf_categories
    
    def step1_get_categories(self) -> bool:
        """步骤1: 获取商品分类"""
        print("📋 步骤1: 获取商品分类")
        print("-" * 40)
        
        try:
            result = self.client.product.cats_get(parent_cat_id=0)
            if result.get("success"):
                categories = result.get("result", {}).get("goodsCatsList", [])
                self.categories_cache = {cat.get("catId"): cat for cat in categories}
                print(f"  ✅ 获取到 {len(categories)} 个分类")
                
                # 显示前几个分类作为示例
                for i, cat in enumerate(categories[:5]):
                    print(f"    {i+1}. {cat.get('catName')} (ID: {cat.get('catId')})")
                
                return True
            else:
                print(f"  ❌ 获取分类失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 获取分类异常: {e}")
            return False
    
    def step2_get_category_template(self, cat_id: str) -> bool:
        """步骤2: 获取分类属性模板"""
        print(f"📋 步骤2: 获取分类 {cat_id} 的属性模板")
        print("-" * 40)
        
        try:
            result = self.client.product.template_get(cat_id=cat_id)
            if result.get("success"):
                template = result.get("result", {})
                self.templates_cache[cat_id] = template
                print(f"  ✅ 获取到分类模板")
                
                # 解析模板中的属性信息
                properties = template.get("propertyList", [])
                required_properties = [p for p in properties if p.get("required", False)]
                print(f"  📊 找到 {len(properties)} 个属性，其中 {len(required_properties)} 个必填")
                
                # 显示必填属性
                if required_properties:
                    print("  📝 必填属性:")
                    for prop in required_properties[:5]:  # 只显示前5个
                        print(f"    - {prop.get('propertyName')} ({prop.get('propertyType')})")
                
                return True
            else:
                print(f"  ❌ 获取模板失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 获取模板异常: {e}")
            return False
    
    def step3_get_compliance_rules(self, cat_id: str) -> bool:
        """步骤3: 获取合规规则"""
        print(f"📋 步骤3: 获取分类 {cat_id} 的合规规则")
        print("-" * 40)
        
        try:
            result = self.client.product.compliance_rules_get(cat_id=cat_id)
            if result.get("success"):
                rules = result.get("result", {})
                self.compliance_rules_cache[cat_id] = rules
                print(f"  ✅ 获取到合规规则")
                return True
            else:
                print(f"  ❌ 获取合规规则失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 获取合规规则异常: {e}")
            return False
    
    def step4_generate_spec_ids(self, cat_id: str, spec_requirements: Dict[str, str]) -> Optional[Dict[str, str]]:
        """步骤4: 生成规格ID"""
        print(f"📋 步骤4: 为分类 {cat_id} 生成规格ID")
        print("-" * 40)
        
        spec_ids = {}
        try:
            for spec_name, spec_value in spec_requirements.items():
                result = self.client.product.spec_id_get(
                    cat_id=cat_id,
                    parent_spec_id="1001",  # 示例父规格ID
                    child_spec_name=spec_value
                )
                if result.get("success"):
                    spec_id = result.get("result", {}).get("specId")
                    spec_ids[spec_name] = spec_id
                    print(f"  ✅ 生成 {spec_name} 规格ID: {spec_id}")
                else:
                    print(f"  ❌ 生成 {spec_name} 规格ID失败: {result.get('errorMsg')}")
                    # 使用默认规格ID
                    spec_ids[spec_name] = f"spec_{spec_name}_{int(time.time())}"
                    print(f"  🔄 使用默认规格ID: {spec_ids[spec_name]}")
            
            self.spec_ids_cache[cat_id] = spec_ids
            return spec_ids
        except Exception as e:
            print(f"  ❌ 生成规格ID异常: {e}")
            return None
    
    def step5_check_illegal_vocabulary(self, goods_name: str, goods_desc: str) -> bool:
        """步骤5: 检查违规词汇"""
        print("📋 步骤5: 检查违规词汇")
        print("-" * 40)
        
        try:
            result = self.client.product.illegal_vocabulary_check(
                goods_name=goods_name,
                goods_desc=goods_desc
            )
            if result.get("success"):
                print(f"  ✅ 词汇检查通过")
                return True
            else:
                print(f"  ❌ 词汇检查失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 词汇检查异常: {e}")
            return False
    
    def step6_upload_images(self, image_paths: List[str]) -> List[str]:
        """步骤6: 上传商品图片"""
        print("📋 步骤6: 上传商品图片")
        print("-" * 40)
        
        uploaded_images = []
        try:
            for image_path in image_paths:
                if os.path.exists(image_path):
                    result = self.client.product.image_upload(image_path=image_path)
                    if result.get("success"):
                        image_id = result.get("result", {}).get("imageId")
                        uploaded_images.append(image_id)
                        print(f"  ✅ 上传图片成功: {image_path} -> {image_id}")
                    else:
                        print(f"  ❌ 上传图片失败: {image_path}, {result.get('errorMsg')}")
                else:
                    print(f"  ⚠️ 图片文件不存在: {image_path}")
            
            self.uploaded_images_cache = uploaded_images
            return uploaded_images
        except Exception as e:
            print(f"  ❌ 上传图片异常: {e}")
            return []
    
    def step7_check_compliance(self, goods_data: Dict[str, Any]) -> bool:
        """步骤7: 检查合规性"""
        print("📋 步骤7: 检查商品合规性")
        print("-" * 40)
        
        try:
            result = self.client.product.compliance_property_check(
                goods_data=goods_data
            )
            if result.get("success"):
                print(f"  ✅ 合规性检查通过")
                return True
            else:
                print(f"  ❌ 合规性检查失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 合规性检查异常: {e}")
            return False
    
    def step8_get_tax_code(self, cat_id: str) -> Optional[str]:
        """步骤8: 获取税码"""
        print(f"📋 步骤8: 获取分类 {cat_id} 的税码")
        print("-" * 40)
        
        try:
            result = self.client.product.tax_code_get(cat_id=cat_id)
            if result.get("success"):
                tax_code = result.get("result", {}).get("taxCode")
                print(f"  ✅ 获取到税码: {tax_code}")
                return tax_code
            else:
                print(f"  ❌ 获取税码失败: {result.get('errorMsg')}")
                return None
        except Exception as e:
            print(f"  ❌ 获取税码异常: {e}")
            return None
    
    def step9_get_freight_templates(self) -> List[Dict[str, Any]]:
        """步骤9: 获取运费模板"""
        print("📋 步骤9: 获取运费模板")
        print("-" * 40)
        
        try:
            result = self.client.product.freight_template_list_query()
            if result.get("success"):
                templates = result.get("result", {}).get("templateList", [])
                print(f"  ✅ 获取到 {len(templates)} 个运费模板")
                return templates
            else:
                print(f"  ❌ 获取运费模板失败: {result.get('errorMsg')}")
                return []
        except Exception as e:
            print(f"  ❌ 获取运费模板异常: {e}")
            return []
    
    def step10_create_product(self, product_data: Dict[str, Any]) -> Optional[str]:
        """步骤10: 创建商品"""
        print("📋 步骤10: 创建商品")
        print("-" * 40)
        
        try:
            # 打印商品数据用于调试
            print(f"  📊 商品数据:")
            print(f"    - 商品名称: {product_data.get('goods_basic', {}).get('goodsName')}")
            print(f"    - 分类ID: {product_data.get('goods_basic', {}).get('catId')}")
            print(f"    - SKU数量: {len(product_data.get('sku_list', []))}")
            
            result = self.client.product.goods_add(
                goods_basic=product_data["goods_basic"],
                goods_service_promise=product_data["goods_service_promise"],
                goods_property=product_data["goods_property"],
                sku_list=product_data["sku_list"]
            )
            
            if result.get("success"):
                product_id = result.get("result", {}).get("goodsId")
                print(f"  ✅ 商品创建成功: {product_id}")
                return product_id
            else:
                print(f"  ❌ 商品创建失败: {result.get('errorMsg')}")
                print(f"  📋 错误详情: {result}")
                return None
        except Exception as e:
            print(f"  ❌ 商品创建异常: {e}")
            return None
    
    def _build_product_data(self, product_info: Dict[str, Any], spec_ids: Dict[str, str], 
                          uploaded_images: List[str], tax_code: Optional[str]) -> Dict[str, Any]:
        """构建商品数据 - 基于官方文档的准确格式"""
        
        # 获取分类模板中的属性信息
        cat_id = product_info.get("cat_id")
        template = self.templates_cache.get(cat_id, {})
        properties = template.get("propertyList", [])
        
        # 构建商品属性 - 基于模板中的必填属性
        goods_properties = []
        for prop in properties:
            if prop.get("required", False):
                # 根据属性类型构建属性数据
                prop_data = {
                    "vid": prop.get("vid", 0),
                    "value": self._get_property_value(prop, product_info),
                    "valueUnit": prop.get("valueUnit", ""),
                    "valueUnitId": prop.get("valueUnitId", 0),
                    "templatePid": prop.get("templatePid", 0),
                    "parentSpecId": prop.get("parentSpecId", 0),
                    "specId": prop.get("specId", 0),
                    "note": "",
                    "imgUrl": "",
                    "groupId": prop.get("groupId", 0),
                    "refPid": prop.get("refPid", 0),
                    "numberInputValue": ""
                }
                goods_properties.append(prop_data)
        
        # 构建SKU列表
        sku_list = []
        for i, sku_info in enumerate(product_info.get("sku_list", [])):
            sku_data = {
                "outSkuSn": sku_info.get("out_sku_sn", f"sku_{product_info.get('goods_name', 'test')}_{i+1:03d}"),
                "specIdList": list(spec_ids.values()),
                "price": {
                    "basePrice": {
                        "amount": str(sku_info.get("price", product_info.get("price", 1000))),
                        "currency": "JPY"
                    }
                },
                "quantity": sku_info.get("quantity", product_info.get("quantity", 100)),
                "images": uploaded_images[:5],  # 限制图片数量
                "weight": sku_info.get("weight", product_info.get("weight", "0.1")),
                "weightUnit": sku_info.get("weight_unit", product_info.get("weight_unit", "kg")),
                "length": sku_info.get("length", product_info.get("length", "10")),
                "width": sku_info.get("width", product_info.get("width", "10")),
                "height": sku_info.get("height", product_info.get("height", "10")),
                "volumeUnit": sku_info.get("volume_unit", product_info.get("volume_unit", "cm"))
            }
            sku_list.append(sku_data)
        
        return {
            "goods_basic": {
                "goodsName": product_info.get("goods_name"),
                "goodsDesc": product_info.get("goods_desc", ""),
                "catId": product_info.get("cat_id"),
                "outGoodsSn": product_info.get("out_goods_sn", f"goods_{int(time.time())}"),
                "specIdList": list(spec_ids.values()),
                "goodsType": 1,
                "goodsStatus": 1,
                "weight": product_info.get("weight", "0.1"),
                "weightUnit": product_info.get("weight_unit", "kg"),
                "length": product_info.get("length", "10"),
                "width": product_info.get("width", "10"),
                "height": product_info.get("height", "10"),
                "volumeUnit": product_info.get("volume_unit", "cm"),
                "currencyCode": "JPY"
            },
            "goods_service_promise": {
                "shipmentLimitDay": product_info.get("shipment_limit_day", 2),
                "fulfillmentType": 1,  # 固定为1，代表"自行履约"
                "costTemplateId": product_info.get("cost_template_id", "default")
            },
            "goods_property": {
                "goodsProperties": goods_properties
            },
            "sku_list": sku_list
        }
    
    def _get_property_value(self, prop: Dict[str, Any], product_info: Dict[str, Any]) -> str:
        """根据属性类型获取属性值"""
        prop_name = prop.get("propertyName", "").lower()
        
        # 年龄组属性特殊处理
        if "age" in prop_name or "applicable" in prop_name:
            return "Adult"  # 默认成人
        
        # 材质属性
        if "material" in prop_name:
            return product_info.get("material", "Cotton")
        
        # 颜色属性
        if "color" in prop_name:
            return product_info.get("color", "Multi")
        
        # 尺寸属性
        if "size" in prop_name:
            return product_info.get("size", "M")
        
        # 默认值
        return prop.get("defaultValue", "Default")
    
    def list_product(self, product_info: Dict[str, Any]) -> bool:
        """完整的商品上架流程"""
        print("🚀 开始 Temu 商品上架流程")
        print("=" * 60)
        
        # 测试连接
        if not self.test_connection():
            return False
        
        # 步骤1: 获取分类
        if not self.step1_get_categories():
            return False
        
        # 获取叶子分类
        leaf_categories = self.get_leaf_categories()
        if not leaf_categories:
            print("❌ 无法获取叶子分类")
            return False
        
        # 使用第一个叶子分类
        leaf_cat = leaf_categories[0]
        cat_id = str(leaf_cat.get("catId"))
        print(f"🎯 使用叶子分类: {leaf_cat.get('catName')} (ID: {cat_id})")
        
        # 更新商品信息中的分类ID
        product_info["cat_id"] = cat_id
        
        # 步骤2: 获取分类模板
        if not self.step2_get_category_template(cat_id):
            return False
        
        # 步骤3: 获取合规规则
        if not self.step3_get_compliance_rules(cat_id):
            return False
        
        # 步骤4: 生成规格ID
        spec_requirements = product_info.get("spec_requirements", {})
        spec_ids = self.step4_generate_spec_ids(cat_id, spec_requirements)
        if not spec_ids:
            return False
        
        # 步骤5: 检查违规词汇
        if not self.step5_check_illegal_vocabulary(
            product_info.get("goods_name"),
            product_info.get("goods_desc")
        ):
            return False
        
        # 步骤6: 上传图片
        image_paths = product_info.get("image_paths", [])
        uploaded_images = self.step6_upload_images(image_paths)
        
        # 步骤7: 检查合规性
        if not self.step7_check_compliance(product_info):
            return False
        
        # 步骤8: 获取税码
        tax_code = self.step8_get_tax_code(cat_id)
        
        # 步骤9: 获取运费模板
        freight_templates = self.step9_get_freight_templates()
        
        # 步骤10: 创建商品
        product_data = self._build_product_data(product_info, spec_ids, uploaded_images, tax_code)
        product_id = self.step10_create_product(product_data)
        
        if product_id:
            print(f"\n🎉 商品上架成功！商品ID: {product_id}")
            return True
        else:
            print(f"\n❌ 商品上架失败")
            return False


def test_advanced_listing_flow():
    """测试高级版商品上架流程"""
    print("🔍 测试高级版商品上架流程")
    print("=" * 60)
    
    # 创建商品上架器
    lister = AdvancedTemuProductLister()
    
    # 测试商品信息
    product_info = {
        # 基础信息
        "goods_name": "テスト商品 - 高品質Tシャツ",
        "goods_desc": "高品質なコットン素材を使用した快適なTシャツです。",
        "out_goods_sn": f"TEST_GOODS_{int(time.time())}",
        
        # 规格要求
        "spec_requirements": {
            "color": "色",
            "size": "サイズ"
        },
        
        # 物理属性
        "weight": "0.3",
        "weight_unit": "kg",
        "length": "30",
        "width": "25",
        "height": "2",
        "volume_unit": "cm",
        
        # 价格和库存
        "price": 2000,
        "quantity": 50,
        
        # 服务承诺
        "shipment_limit_day": 2,
        "cost_template_id": "default",
        
        # 商品属性
        "material": "Cotton",
        "color": "Blue",
        "size": "M",
        
        # SKU列表
        "sku_list": [
            {
                "out_sku_sn": f"sku_blue_m_{int(time.time())}",
                "price": 2000,
                "quantity": 25,
                "color": "Blue",
                "size": "M"
            },
            {
                "out_sku_sn": f"sku_blue_l_{int(time.time())}",
                "price": 2000,
                "quantity": 25,
                "color": "Blue",
                "size": "L"
            }
        ],
        
        # 媒体资源
        "image_paths": [],  # 暂时没有图片
        "carousel_video": [],
        "detail_video": [],
        
        # 其他信息
        "bullet_points": ["高品質", "快適", "ファッション"],
        "certification_info": {},
        "size_chart": {},
        "trademark_info": {}
    }
    
    # 执行上架流程
    success = lister.list_product(product_info)
    
    if success:
        print("\n✅ 商品上架流程测试成功！")
    else:
        print("\n❌ 商品上架流程测试失败！")


if __name__ == "__main__":
    test_advanced_listing_flow()
