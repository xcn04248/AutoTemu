#!/usr/bin/env python3
"""
完整的 Temu 商品上架流程

基于官方文档实现完整的商品上架流程
"""

import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入修复后的官方库
from temu_api import TemuClient

class TemuProductLister:
    """Temu 商品上架器"""
    
    def __init__(self):
        """初始化商品上架器"""
        self.client = TemuClient(
            app_key=os.getenv("TEMU_APP_KEY"),
            app_secret=os.getenv("TEMU_APP_SECRET"),
            access_token=os.getenv("TEMU_ACCESS_TOKEN"),
            base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
            debug=False
        )
        
        # 缓存数据
        self.categories_cache = {}
        self.templates_cache = {}
        self.compliance_rules_cache = {}
    
    def step1_get_categories(self):
        """步骤1: 获取商品分类"""
        print("📋 步骤1: 获取商品分类")
        print("-" * 40)
        
        try:
            result = self.client.product.cats_get(parent_cat_id=0)
            if result.get("success"):
                categories = result.get("result", {}).get("goodsCatsList", [])
                self.categories_cache = {cat.get("catId"): cat for cat in categories}
                print(f"  ✅ 获取到 {len(categories)} 个分类")
                return True
            else:
                print(f"  ❌ 获取分类失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 获取分类异常: {e}")
            return False
    
    def step2_get_category_template(self, cat_id):
        """步骤2: 获取分类属性模板"""
        print(f"📋 步骤2: 获取分类 {cat_id} 的属性模板")
        print("-" * 40)
        
        try:
            # 根据官方文档，获取分类属性模板
            result = self.client.product.template_get(cat_id=cat_id)
            if result.get("success"):
                template = result.get("result", {})
                self.templates_cache[cat_id] = template
                print(f"  ✅ 获取到分类模板")
                
                # 解析模板中的属性信息
                properties = template.get("propertyList", [])
                required_properties = [p for p in properties if p.get("required", False)]
                print(f"  📊 找到 {len(properties)} 个属性，其中 {len(required_properties)} 个必填")
                
                return True
            else:
                print(f"  ❌ 获取模板失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"  ❌ 获取模板异常: {e}")
            return False
    
    def step3_get_compliance_rules(self, cat_id):
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
    
    def step4_generate_spec_ids(self, cat_id, spec_requirements):
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
                    return None
            return spec_ids
        except Exception as e:
            print(f"  ❌ 生成规格ID异常: {e}")
            return None
    
    def step5_check_illegal_vocabulary(self, goods_name, goods_desc):
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
    
    def step6_upload_images(self, image_paths):
        """步骤6: 上传商品图片"""
        print("📋 步骤6: 上传商品图片")
        print("-" * 40)
        
        uploaded_images = []
        try:
            for image_path in image_paths:
                result = self.client.product.image_upload(image_path=image_path)
                if result.get("success"):
                    image_id = result.get("result", {}).get("imageId")
                    uploaded_images.append(image_id)
                    print(f"  ✅ 上传图片成功: {image_path}")
                else:
                    print(f"  ❌ 上传图片失败: {image_path}, {result.get('errorMsg')}")
            return uploaded_images
        except Exception as e:
            print(f"  ❌ 上传图片异常: {e}")
            return []
    
    def step7_check_compliance(self, goods_data):
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
    
    def step8_get_tax_code(self, cat_id):
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
    
    def step9_get_freight_templates(self):
        """步骤9: 获取运费模板"""
        print("📋 步骤9: 获取运费模板")
        print("-" * 40)
        
        try:
            result = self.client.freight.template_list_query()
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
    
    def step10_create_product(self, product_data):
        """步骤10: 创建商品"""
        print("📋 步骤10: 创建商品")
        print("-" * 40)
        
        try:
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
                return None
        except Exception as e:
            print(f"  ❌ 商品创建异常: {e}")
            return None
    
    def list_product(self, product_info):
        """完整的商品上架流程"""
        print("🚀 开始 Temu 商品上架流程")
        print("=" * 60)
        
        # 步骤1: 获取分类
        if not self.step1_get_categories():
            return False
        
        # 步骤2: 获取分类模板
        cat_id = product_info.get("cat_id")
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
    
    def _build_product_data(self, product_info, spec_ids, uploaded_images, tax_code):
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
        
        return {
            "goods_basic": {
                "goodsName": product_info.get("goods_name"),
                "goodsDesc": product_info.get("goods_desc", ""),
                "catId": product_info.get("cat_id"),
                "outGoodsSn": product_info.get("out_goods_sn", ""),
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
            "sku_list": [{
                "outSkuSn": f"sku_{product_info.get('goods_name', 'test')}_001",
                "specIdList": list(spec_ids.values()),
                "price": {
                    "basePrice": {
                        "amount": str(product_info.get("price", 1000)),
                        "currency": "JPY"
                    }
                },
                "quantity": product_info.get("quantity", 100),
                "images": uploaded_images,
                "weight": product_info.get("weight", "0.1"),
                "weightUnit": product_info.get("weight_unit", "kg"),
                "length": product_info.get("length", "10"),
                "width": product_info.get("width", "10"),
                "height": product_info.get("height", "10"),
                "volumeUnit": product_info.get("volume_unit", "cm")
            }],
            # 选填字段
            "goods_gallery": {
                "detailImage": uploaded_images[:49],  # 最多49张
                "carouselVideo": product_info.get("carousel_video", []),
                "detailVideo": product_info.get("detail_video", [])
            },
            "bullet_points": product_info.get("bullet_points", []),
            "certification_info": product_info.get("certification_info", {}),
            "goods_size_chart_list": product_info.get("size_chart", {}),
            "goods_trademark": product_info.get("trademark_info", {}),
            "tax_code_info": tax_code
        }
    
    def _get_property_value(self, prop, product_info):
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


def test_complete_listing_flow():
    """测试完整的商品上架流程"""
    print("🔍 测试完整的商品上架流程")
    print("=" * 60)
    
    # 创建商品上架器
    lister = TemuProductLister()
    
    # 测试商品信息 - 基于官方文档的完整格式
    product_info = {
        # 基础信息
        "goods_name": "テスト商品",
        "goods_desc": "テスト商品の説明",
        "out_goods_sn": "TEST_GOODS_001",
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
        
        # 商品属性
        "material": "Cotton",
        "color": "Blue",
        "size": "M",
        
        # 媒体资源
        "image_paths": [],  # 暂时没有图片
        "carousel_video": [],
        "detail_video": [],
        
        # 其他信息
        "bullet_points": ["高质量", "舒适", "时尚"],
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
    test_complete_listing_flow()
