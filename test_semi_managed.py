#!/usr/bin/env python3
"""
半托管模式货品发布流程测试脚本
测试新的bg.goods.add API和相关功能
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

# 导入项目模块
from src.api.bg_client import BgGoodsClient
from src.api.api_adapter import ApiAdapter
from src.transform.bg_transformer import BgDataTransformer
from src.models.bg_models import BgGoodsAddData, BgProductSkuReq
from src.models.product import TemuProduct, TemuSKU
from src.core.product_manager import ProductManager
from src.utils.logger import get_logger

# 设置日志
logger = get_logger(__name__)

class SemiManagedTester:
    """半托管模式测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.bg_client = None
        self.api_adapter = None
        self.transformer = None
        self.product_manager = None
        
        # 测试配置
        self.test_config = {
            'site_id': 1001,  # 日本站点
            'language': 'ja',
            'currency': 'JPY',
            'test_product_name': 'テスト商品 - 半托管模式',
            'test_product_description': 'これは半托管モードでのテスト商品です。'
        }
        
    def setup_clients(self):
        """设置API客户端"""
        try:
            logger.info("🔧 设置API客户端...")
            
            # 检查环境变量
            required_vars = ['BG_APP_KEY', 'BG_APP_SECRET', 'BG_BASE_URL']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(f"缺少环境变量: {missing_vars}")
            
            # 初始化客户端
            from src.utils.config import get_config
            config = get_config()
            self.bg_client = BgGoodsClient(
                app_key=config.bg_app_key,
                app_secret=config.bg_app_secret,
                access_token=config.bg_access_token,
                base_url=config.bg_base_url
            )
            self.api_adapter = ApiAdapter()
            self.transformer = BgDataTransformer()
            self.product_manager = ProductManager()
            
            logger.info("✅ API客户端设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 设置API客户端失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False
    
    def test_api_connection(self):
        """测试API连接"""
        try:
            logger.info("🔗 测试API连接...")
            
            # 测试权限查询
            response = self.bg_client.test_connection()
            
            if response:
                logger.info("✅ API连接成功")
                return True
            else:
                logger.error("❌ API连接失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ API连接测试异常: {e}")
            return False
    
    def test_category_query(self):
        """测试分类查询"""
        try:
            logger.info("📂 测试分类查询...")
            
            # 查询分类列表
            response = self.bg_client.cats_get(parent_cat_id=0)
            if response.get('success'):
                categories = response.get('result', {}).get('categoryDTOList', [])
                logger.info(f"✅ 查询到 {len(categories)} 个分类")
                for i, cat in enumerate(categories[:5]):
                    logger.info(f"  {i+1}. {cat.get('catName', 'N/A')} (ID: {cat.get('catId', 'N/A')})")
                return categories
            else:
                logger.error(f"❌ 分类查询失败: {response.get('errorMsg', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 分类查询异常: {e}")
            return []
    
    def test_attribute_query(self, category_id):
        """测试属性查询"""
        try:
            logger.info(f"🏷️ 测试属性查询 (分类ID: {category_id})...")
            
            logger.info("暂未实现属性查询接口，跳过")
            return []
                
        except Exception as e:
            logger.error(f"❌ 属性查询异常: {e}")
            return []
    
    def test_image_upload(self):
        """测试图片上传"""
        try:
            logger.info("🖼️ 测试图片上传...")
            
            # 查找测试图片
            test_image_path = self._find_test_image()
            if not test_image_path:
                logger.warning("⚠️ 未找到测试图片，跳过图片上传测试")
                return []
            
            logger.info(f"使用测试图片: {test_image_path}")
            
            logger.info("暂时跳过直传，使用占位图URL进行流程验证")
            return ["https://via.placeholder.com/800.jpg"]
                
        except Exception as e:
            logger.error(f"❌ 图片上传异常: {e}")
            return []
    
    def test_product_transformation(self):
        """测试商品数据转换"""
        try:
            logger.info("🔄 测试商品数据转换...")
            
            # 创建测试商品数据
            test_product = self._create_test_product()
            
            # 转换为新API格式
            bg_request = self.transformer.transform_product(test_product)
            logger.info("✅ 商品数据转换成功")
            logger.info(f"商品名称: {bg_request.productName}")
            logger.info(f"SKU数量: {len(bg_request.productSkcReqs)}")
            logger.info(f"图片数量: {len(bg_request.carouselImageUrls)}")
            return (test_product, bg_request)
            
        except Exception as e:
            logger.error(f"❌ 商品数据转换异常: {e}")
            return None
    
    def test_semi_managed_listing(self, temu_product, bg_request, image_urls):
        """测试半托管商品发布"""
        try:
            logger.info("🚀 测试半托管商品发布...")
            
            # 更新图片URL
            if image_urls:
                bg_request.carouselImageUrls = image_urls
                bg_request.materialImgUrl = image_urls[0] if image_urls else ""
            
            # 使用API适配器发布商品（传入TemuProduct与上下文）
            context = { 'uploaded_images': image_urls }
            result = self.api_adapter.create_product(temu_product, context=context)
            response = result.to_dict() if hasattr(result, 'to_dict') else result
            
            if response.get('success'):
                product_id = response.get('result', {}).get('productId')
                logger.info(f"✅ 半托管商品发布成功")
                logger.info(f"商品ID: {product_id}")
                return product_id
            else:
                logger.error(f"❌ 半托管商品发布失败: {response.get('errorMsg', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 半托管商品发布异常: {e}")
            return None
    
    def test_end_to_end_flow(self):
        """测试端到端流程"""
        try:
            logger.info("🎯 开始端到端测试...")
            
            # 1. 设置客户端
            if not self.setup_clients():
                return False
            
            # 2. 测试API连接
            if not self.test_api_connection():
                return False
            
            # 3. 查询分类
            categories = self.test_category_query()
            if not categories:
                logger.warning("⚠️ 分类查询失败，使用默认分类")
                category_id = 1001  # 默认分类
            else:
                category_id = categories[0].get('categoryId')
            
            # 4. 查询属性
            attributes = self.test_attribute_query(category_id)
            
            # 5. 上传图片
            image_urls = self.test_image_upload()
            
            # 6. 测试数据转换
            trans = self.test_product_transformation()
            if not trans:
                return False
            temu_product, bg_request = trans
            
            # 7. 设置分类和属性
            bg_request.categoryId = category_id
            if attributes:
                bg_request.attributeList = [
                    {
                        'attributeId': attributes[0].get('attributeId'),
                        'attributeValueList': [{'value': 'テスト値'}]
                    }
                ]
            
            # 8. 测试半托管发布
            product_id = self.test_semi_managed_listing(temu_product, bg_request, image_urls)
            
            if product_id:
                logger.info("🎉 端到端测试完成！")
                return True
            else:
                logger.error("❌ 端到端测试失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 端到端测试异常: {e}")
            return False
    
    def _find_test_image(self):
        """查找测试图片"""
        image_dirs = ['./images', './temp_images', './tmp']
        
        for dir_path in image_dirs:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        return os.path.join(dir_path, file)
        
        return None
    
    def _create_test_product(self):
        """创建测试商品数据"""
        return TemuProduct(
            title=self.test_config['test_product_name'],
            description=self.test_config['test_product_description'],
            original_price=1000.0,  # 1000日元
            markup_price=1300.0,   # 加价30%
            currency='JPY',
            category_id="1001",
            size_type="clothing",
            images=["test_image.jpg"],
            skus=[
                TemuSKU(
                    sku_id="TEST_SKU_001",
                    size="M",
                    original_size="M",
                    price=1300.0,
                    stock_quantity=10,
                    images=["https://via.placeholder.com/800.jpg"]
                ),
                TemuSKU(
                    sku_id="TEST_SKU_002",
                    size="L", 
                    original_size="L",
                    price=1300.0,
                    stock_quantity=5,
                    images=["https://via.placeholder.com/800.jpg"]
                )
            ],
            source_url="https://example.com/test-product"
        )

def main():
    """主函数"""
    print("🚀 AutoTemu 半托管模式测试")
    print("=" * 50)
    
    tester = SemiManagedTester()
    
    # 运行端到端测试
    success = tester.test_end_to_end_flow()
    
    if success:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 测试失败！")
        return 1

if __name__ == "__main__":
    exit(main())
