"""
ProductManager 集成测试 - 验证新旧API切换
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.core.product_manager import ProductManager
from src.models.data_models import ProductData, SizeInfo


class TestProductManagerIntegration:
    """ProductManager集成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 模拟环境变量
        self.env_patches = patch.dict(os.environ, {
            'TEMU_APP_KEY': 'test_app_key',
            'TEMU_APP_SECRET': 'test_app_secret',
            'TEMU_ACCESS_TOKEN': 'test_access_token',
            'TEMU_BASE_URL': 'https://test-api.temu.com',
            'PRICE_MARKUP': '1.3',
            'TEMU_CNY_TO_JPY_RATE': '20.0',
            'DEFAULT_PARENT_SPEC_ID': '3001',
            'DEFAULT_WAREHOUSE_ID': 'WHS-TEST',
            'DEFAULT_SKU_STOCK': '100',
            'PRODUCT_NAME_MAX_LENGTH': '250'
        })
        self.env_patches.start()
    
    def teardown_method(self):
        """测试后清理"""
        self.env_patches.stop()
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_init_with_new_api(self, mock_size_mapper, mock_data_transformer, 
                              mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试使用新版API初始化"""
        # 测试新版API初始化
        manager = ProductManager(use_new_api=True)
        
        assert manager.use_new_api == True
        assert hasattr(manager, 'bg_client')
        assert hasattr(manager, 'bg_transformer')
        assert hasattr(manager, 'api_adapter')
        assert not hasattr(manager, 'temu_client')
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_init_with_old_api(self, mock_size_mapper, mock_data_transformer,
                              mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试使用旧版API初始化"""
        # 测试旧版API初始化
        manager = ProductManager(use_new_api=False)
        
        assert manager.use_new_api == False
        assert hasattr(manager, 'temu_client')
        assert not hasattr(manager, 'bg_client')
        assert not hasattr(manager, 'bg_transformer')
        assert not hasattr(manager, 'api_adapter')
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_workflow_steps_new_api(self, mock_size_mapper, mock_data_transformer,
                                   mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试新版API工作流程步骤"""
        manager = ProductManager(use_new_api=True)
        
        # 验证工作流程步骤
        workflow_steps = [
            ("抓取商品信息", manager._scrape_product),
            ("处理商品图片", manager._process_images),
            ("处理尺码表", manager._process_size_chart),
            ("转换数据格式", manager._transform_data),
            ("获取商品分类", manager._get_categories_new),
            ("获取分类推荐", manager._get_category_recommendation_new),
            ("获取分类模板", manager._get_category_template_new),
            ("生成规格ID", manager._generate_spec_ids_new),
            ("上传商品图片", manager._upload_images_new),
            ("添加商品", manager._create_product_new)
        ]
        
        assert len(workflow_steps) == 10
        for step_name, step_func in workflow_steps:
            assert callable(step_func)
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_workflow_steps_old_api(self, mock_size_mapper, mock_data_transformer,
                                  mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试旧版API工作流程步骤"""
        manager = ProductManager(use_new_api=False)
        
        # 验证工作流程步骤
        workflow_steps = [
            ("抓取商品信息", manager._scrape_product),
            ("处理商品图片", manager._process_images),
            ("处理尺码表", manager._process_size_chart),
            ("转换数据格式", manager._transform_data),
            ("获取商品分类", manager._get_categories),
            ("获取分类推荐", manager._get_category_recommendation),
            ("获取分类模板", manager._get_category_template),
            ("生成规格ID", manager._generate_spec_ids),
            ("上传商品图片", manager._upload_images),
            ("添加商品", manager._create_product)
        ]
        
        assert len(workflow_steps) == 10
        for step_name, step_func in workflow_steps:
            assert callable(step_func)
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_scrape_product_method(self, mock_size_mapper, mock_data_transformer,
                                  mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试商品抓取方法"""
        manager = ProductManager(use_new_api=True)
        
        # 模拟抓取结果
        mock_product_data = ProductData(
            url="https://test.com",
            name="测试商品",
            price=100.0,
            description="测试描述",
            main_image_url="https://main.jpg",
            detail_images=["https://detail1.jpg", "https://detail2.jpg"],
            sizes=[
                SizeInfo(size_name="M", stock_quantity=10),
                SizeInfo(size_name="L", stock_quantity=15)
            ]
        )
        
        mock_scraper.return_value.scrape_product.return_value = mock_product_data
        
        # 测试抓取
        result = manager._scrape_product("https://test.com")
        
        assert result == True
        assert manager.scraped_product == mock_product_data
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_process_images_method(self, mock_size_mapper, mock_data_transformer,
                                  mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试图片处理方法"""
        manager = ProductManager(use_new_api=True)
        
        # 设置抓取的商品数据
        manager.scraped_product = ProductData(
            url="https://test.com",
            name="测试商品",
            price=100.0,
            description="测试描述",
            main_image_url="https://main.jpg",
            detail_images=["https://detail1.jpg", "https://detail2.jpg"],
            sizes=[]
        )
        
        # 模拟图片处理结果
        mock_image_processor.return_value.process_images.return_value = {
            'main': ['processed_main.jpg'],
            'detail': ['processed_detail1.jpg', 'processed_detail2.jpg'],
            'other': []
        }
        
        # 测试图片处理
        result = manager._process_images()
        
        assert result == True
        mock_image_processor.return_value.process_images.assert_called_once()
    
    @patch('src.core.product_manager.ProductScraper')
    @patch('src.core.product_manager.ImageProcessor')
    @patch('src.core.product_manager.SizeChartProcessor')
    @patch('src.core.product_manager.DataTransformer')
    @patch('src.core.product_manager.SizeMapper')
    def test_transform_data_method(self, mock_size_mapper, mock_data_transformer,
                                  mock_size_chart_processor, mock_image_processor, mock_scraper):
        """测试数据转换方法"""
        manager = ProductManager(use_new_api=True)
        
        # 设置抓取的商品数据
        manager.scraped_product = ProductData(
            url="https://test.com",
            name="测试商品",
            price=100.0,
            description="测试描述",
            main_image_url="https://main.jpg",
            detail_images=["https://detail1.jpg", "https://detail2.jpg"],
            sizes=[
                SizeInfo(size_name="M", stock_quantity=10),
                SizeInfo(size_name="L", stock_quantity=15)
            ]
        )
        
        # 模拟转换结果
        mock_result = Mock()
        mock_result.success = True
        mock_result.temu_product = Mock()
        mock_result.temu_product.title = "测试商品"
        mock_result.temu_product.category_id = "123"
        mock_data_transformer.return_value.transform_product.return_value = mock_result
        
        # 测试数据转换
        result = manager._transform_data()
        
        assert result == True
        assert manager.temu_product == mock_result.temu_product
        mock_data_transformer.return_value.transform_product.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
