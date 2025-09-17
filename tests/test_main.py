"""
主程序测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.main import AutoTemuApp
from src.models.product import ScrapedProduct, TemuProduct, TemuSKU, TemuListingResult, TemuCategory


class TestAutoTemuApp:
    """AutoTemu主应用程序测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建模拟配置
        self.mock_config = Mock()
        self.mock_config.price_markup = 1.3
        self.mock_config.log_level = "INFO"
        self.mock_config.image_save_path = "./images"
        self.mock_config.max_retry_attempts = 3
        self.mock_config.temu_base_url = "https://api.temu.com"
        self.mock_config.temu_app_key = "test_key"
        self.mock_config.temu_app_secret = "test_secret"
        self.mock_config.temu_access_token = "test_token"

    @patch('src.main.get_config')
    @patch('src.main.OCRClient')
    @patch('src.main.ImageProcessor')
    @patch('src.main.SizeMapper')
    @patch('src.main.DataTransformer')
    @patch('src.main.TemuAPIClient')
    @patch('src.main.ProductScraper')
    def test_init_success(self, mock_scraper, mock_temu_client, mock_data_transformer, 
                         mock_size_mapper, mock_image_processor, mock_ocr_client, mock_get_config):
        """测试成功初始化"""
        mock_get_config.return_value = self.mock_config
        
        app = AutoTemuApp()
        
        assert app.config == self.mock_config
        assert app.ocr_client is not None
        assert app.image_processor is not None
        assert app.size_mapper is not None
        assert app.data_transformer is not None
        assert app.temu_client is not None
        assert app.scraper is not None

    @patch('src.main.get_config')
    def test_init_config_error(self, mock_get_config):
        """测试配置错误"""
        from src.utils.exceptions import AutoTemuException
        mock_get_config.side_effect = Exception("Config error")
        
        with pytest.raises(AutoTemuException):
            AutoTemuApp()

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_process_single_url_success(self, mock_init):
        """测试成功处理单个URL"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.config = self.mock_config
        app.scraper = Mock()
        app.image_processor = Mock()
        app.data_transformer = Mock()
        app.temu_client = Mock()
        
        # 模拟爬取结果
        scraped_product = ScrapedProduct(
            title="Test Product",
            price=100.0,
            description="Test Description",
            images=["image1.jpg", "image2.jpg"],
            sizes=["S", "M", "L"],
            url="https://example.com/product"
        )
        app.scraper.scrape_product.return_value = scraped_product
        
        # 模拟图片处理结果
        image_result = {
            'main': ['path/to/main1.jpg'],
            'detail': ['path/to/detail1.jpg'],
            'size': ['path/to/size1.jpg'],
            'other': [],
            'filtered': []
        }
        app.image_processor.process_images.return_value = image_result
        
        # 模拟数据转换结果
        temu_product = TemuProduct(
            title="Test Product",
            description="Test Description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["image1.jpg", "image2.jpg"]
        )
        skus = [
            TemuSKU("SKU_001", "S", "S", 130.0, 100, ["image1.jpg"]),
            TemuSKU("SKU_002", "M", "M", 130.0, 100, ["image1.jpg"])
        ]
        transform_result = Mock()
        transform_result.success = True
        transform_result.temu_product = temu_product
        transform_result.skus = skus
        app.data_transformer.transform_product.return_value = transform_result
        
        # 模拟分类推荐
        categories = [
            TemuCategory("cat1", "Category 1", level=1, is_leaf=True)
        ]
        app.temu_client.get_category_recommend.return_value = categories
        
        # 模拟尺码表元素
        app.temu_client.get_size_chart_elements.return_value = ["chest", "waist"]
        
        # 模拟上架结果
        listing_result = TemuListingResult(
            success=True,
            product_id="prod123",
            sku_ids=["sku1", "sku2"],
            image_ids=["img1", "img2"]
        )
        app.temu_client.list_product.return_value = listing_result
        
        # 执行测试
        result = app.process_single_url("https://example.com/product")
        
        # 验证结果
        assert result.success == True
        assert result.product_id == "prod123"
        assert len(result.sku_ids) == 2
        assert len(result.image_ids) == 2

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_process_single_url_failure(self, mock_init):
        """测试处理单个URL失败"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.config = self.mock_config
        app.scraper = Mock()
        
        # 模拟爬取失败
        app.scraper.scrape_product.side_effect = Exception("Scrape failed")
        
        # 执行测试
        result = app.process_single_url("https://example.com/product")
        
        # 验证结果
        assert result.success == False
        assert len(result.errors) > 0
        assert "Scrape failed" in result.errors[0]

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_process_batch_urls(self, mock_init):
        """测试批量处理URL"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.config = self.mock_config
        app.scraper = Mock()
        app.image_processor = Mock()
        app.data_transformer = Mock()
        app.temu_client = Mock()
        
        # 模拟处理结果
        def mock_process_single_url(url, output_dir=None):
            if "success" in url:
                return TemuListingResult(success=True, product_id="prod123")
            else:
                return TemuListingResult(success=False, errors=["Failed"])
        
        app.process_single_url = mock_process_single_url
        
        # 执行测试
        urls = ["https://example.com/success", "https://example.com/fail"]
        results = app.process_batch_urls(urls)
        
        # 验证结果
        assert len(results) == 2
        assert results[0].success == True
        assert results[1].success == False

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_test_connection_success(self, mock_init):
        """测试连接测试成功"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.temu_client = Mock()
        app.temu_client.test_connection.return_value = True
        
        # 执行测试
        result = app.test_connection()
        
        # 验证结果
        assert result == True

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_test_connection_failure(self, mock_init):
        """测试连接测试失败"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.temu_client = Mock()
        app.temu_client.test_connection.return_value = False
        
        # 执行测试
        result = app.test_connection()
        
        # 验证结果
        assert result == False

    @patch('src.main.AutoTemuApp.__init__', return_value=None)
    def test_get_system_status(self, mock_init):
        """测试获取系统状态"""
        # 创建应用程序实例
        app = AutoTemuApp()
        app.config = self.mock_config
        app.temu_client = Mock()
        app.temu_client.test_connection.return_value = True
        
        # 执行测试
        status = app.get_system_status()
        
        # 验证结果
        assert "config" in status
        assert "modules" in status
        assert "api_connection" in status
        assert status["api_connection"] == True
        assert status["config"]["price_markup"] == 1.3

    def test_main_test_connection(self):
        """测试主函数 - 测试连接"""
        # 模拟应用程序
        mock_app = Mock()
        mock_app.test_connection.return_value = True
        
        # 直接测试主函数逻辑，不通过命令行
        with patch('src.main.AutoTemuApp', return_value=mock_app):
            with patch('sys.exit') as mock_exit:
                # 模拟args对象
                args = Mock()
                args.test = True
                args.status = False
                args.url = None
                args.urls = None
                args.config = None
                args.output = None
                args.verbose = False
                
                # 直接调用主函数逻辑
                from src.main import main
                
                # 模拟argparse
                with patch('argparse.ArgumentParser.parse_args', return_value=args):
                    main()
                
                # 验证调用
                mock_app.test_connection.assert_called_once()
                # 检查是否调用了exit(0)
                assert mock_exit.called
                # 获取第一次调用的参数（应该是exit(0)）
                first_call = mock_exit.call_args_list[0]
                assert first_call[0][0] == 0

    def test_main_process_single_url(self):
        """测试主函数 - 处理单个URL"""
        # 模拟应用程序
        mock_app = Mock()
        mock_result = TemuListingResult(success=True, product_id="prod123")
        mock_app.process_single_url.return_value = mock_result
        
        with patch('src.main.AutoTemuApp', return_value=mock_app):
            with patch('sys.argv', ['main.py', '--url', 'https://example.com/product']):
                with patch('sys.stdout') as mock_stdout:
                    with patch('sys.exit') as mock_exit:
                        from src.main import main
                        main()
                        
                        # 验证调用
                        mock_app.process_single_url.assert_called_once_with('https://example.com/product', None)
                        mock_exit.assert_called_with(0)

    def test_main_process_batch_urls(self):
        """测试主函数 - 批量处理URL"""
        # 模拟应用程序
        mock_app = Mock()
        mock_results = [
            TemuListingResult(success=True, product_id="prod1"),
            TemuListingResult(success=False, errors=["Failed"])
        ]
        mock_app.process_batch_urls.return_value = mock_results
        
        with patch('src.main.AutoTemuApp', return_value=mock_app):
            with patch('sys.argv', ['main.py', '--urls', 'https://example.com/1', 'https://example.com/2']):
                with patch('sys.stdout') as mock_stdout:
                    with patch('sys.exit') as mock_exit:
                        from src.main import main
                        main()
                        
                        # 验证调用
                        mock_app.process_batch_urls.assert_called_once_with(['https://example.com/1', 'https://example.com/2'], None)
                        mock_exit.assert_called_with(0)

    def test_main_show_status(self):
        """测试主函数 - 显示状态"""
        # 模拟应用程序
        mock_app = Mock()
        mock_status = {"config": {"price_markup": 1.3}, "modules": {}, "api_connection": True}
        mock_app.get_system_status.return_value = mock_status
        
        # 直接测试主函数逻辑，不通过命令行
        with patch('src.main.AutoTemuApp', return_value=mock_app):
            with patch('sys.exit') as mock_exit:
                # 模拟args对象
                args = Mock()
                args.test = False
                args.status = True
                args.url = None
                args.urls = None
                args.config = None
                args.output = None
                args.verbose = False
                
                # 直接调用主函数逻辑
                from src.main import main
                
                # 模拟argparse
                with patch('argparse.ArgumentParser.parse_args', return_value=args):
                    main()
                
                # 验证调用
                mock_app.get_system_status.assert_called_once()
                # 检查是否调用了exit(0)
                assert mock_exit.called
                # 获取第一次调用的参数（应该是exit(0)）
                first_call = mock_exit.call_args_list[0]
                assert first_call[0][0] == 0
