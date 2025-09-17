"""
商品爬虫模块的单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.scraper.product_scraper import ProductScraper, scrape_product
from src.models.data_models import ProductData, SizeInfo
from src.utils.exceptions import NetworkException, ParseException
import src.utils.config as config_module


class TestProductScraper:
    """商品爬虫测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        # 清理全局配置
        config_module._config = None
        
        # 设置必需的环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_firecrawl_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
    
    @pytest.fixture
    def mock_firecrawl_response(self):
        """模拟Firecrawl响应"""
        mock_response = Mock()
        mock_response.json = {
            "productName": "测试商品",
            "price": "2980",
            "description": "这是一个测试商品",
            "imageLink": "https://example.com/main.jpg",
            "sizes": [
                {"size": "S", "sizeImageLink": "https://example.com/s.jpg"},
                {"size": "M", "sizeImageLink": "https://example.com/m.jpg"},
                {"size": "L", "sizeImageLink": "https://example.com/l.jpg"}
            ],
            "productDetails": {
                "details": "货号: TEST-001\n材质: 纯棉",
                "detailImageLinks": [
                    "https://example.com/detail1.jpg",
                    "https://example.com/detail2.jpg"
                ]
            },
            "brand": "测试品牌",
            "material": "纯棉"
        }
        return mock_response
    
    @patch('src.scraper.product_scraper.Firecrawl')
    def test_scraper_initialization(self, mock_firecrawl_class):
        """测试爬虫初始化"""
        mock_firecrawl_class.return_value = Mock()
        
        scraper = ProductScraper()
        
        assert scraper.config is not None
        assert scraper.logger is not None
        mock_firecrawl_class.assert_called_once_with(api_key="test_firecrawl_key")
    
    @patch('src.scraper.product_scraper.Firecrawl')
    def test_scraper_initialization_failure(self, mock_firecrawl_class):
        """测试爬虫初始化失败"""
        mock_firecrawl_class.side_effect = Exception("API密钥无效")
        
        with pytest.raises(NetworkException) as exc_info:
            ProductScraper()
        
        assert "Firecrawl初始化失败" in str(exc_info.value)
    
    @patch('src.scraper.product_scraper.Firecrawl')
    def test_scrape_product_success(self, mock_firecrawl_class, mock_firecrawl_response):
        """测试成功爬取商品"""
        # 设置mock
        mock_firecrawl = Mock()
        mock_firecrawl.scrape.return_value = mock_firecrawl_response
        mock_firecrawl_class.return_value = mock_firecrawl
        
        scraper = ProductScraper()
        url = "https://www.jp0663.com/detail/test"
        
        # 执行爬取
        product = scraper.scrape_product(url)
        
        # 验证结果
        assert isinstance(product, ProductData)
        assert product.name == "测试商品"
        assert product.price == 2980.0
        assert product.description == "这是一个测试商品"
        assert product.main_image_url == "https://example.com/main.jpg"
        assert len(product.sizes) == 3
        assert len(product.detail_images) == 2
        assert product.product_code == "TEST-001"
        assert product.brand == "测试品牌"
        assert product.material == "纯棉"
        
        # 验证Firecrawl调用
        mock_firecrawl.scrape.assert_called_once()
        call_args = mock_firecrawl.scrape.call_args
        assert call_args[0][0] == url
    
    @patch('src.scraper.product_scraper.Firecrawl')
    def test_scrape_product_network_error(self, mock_firecrawl_class):
        """测试网络错误"""
        mock_firecrawl = Mock()
        mock_firecrawl.scrape.side_effect = Exception("网络超时")
        mock_firecrawl_class.return_value = mock_firecrawl
        
        scraper = ProductScraper()
        url = "https://www.jp0663.com/detail/test"
        
        # 由于有重试机制，最终会抛出RetryException
        from src.utils.exceptions import RetryException
        with pytest.raises(RetryException):
            scraper.scrape_product(url)
    
    @patch('src.scraper.product_scraper.Firecrawl')
    def test_scrape_product_invalid_response(self, mock_firecrawl_class):
        """测试无效响应"""
        mock_firecrawl = Mock()
        mock_response = Mock()
        mock_response.json = None
        mock_firecrawl.scrape.return_value = mock_response
        mock_firecrawl_class.return_value = mock_firecrawl
        
        scraper = ProductScraper()
        url = "https://www.jp0663.com/detail/test"
        
        # 由于有重试机制，最终会抛出RetryException
        from src.utils.exceptions import RetryException
        with pytest.raises(RetryException):
            scraper.scrape_product(url)
    
    def test_extract_price_string(self):
        """测试字符串价格提取"""
        scraper = ProductScraper()
        
        # 测试正常价格
        data = {"price": "2980"}
        assert scraper._extract_price(data, "price") == 2980.0
        
        # 测试带货币符号的价格
        data = {"price": "¥2,980"}
        assert scraper._extract_price(data, "price") == 2980.0
        
        # 测试数字价格
        data = {"price": 2980}
        assert scraper._extract_price(data, "price") == 2980.0
    
    def test_extract_price_invalid(self):
        """测试无效价格"""
        scraper = ProductScraper()
        
        # 测试缺失价格
        data = {}
        with pytest.raises(ParseException) as exc_info:
            scraper._extract_price(data, "price")
        assert "未找到价格信息" in str(exc_info.value)
        
        # 测试无效价格格式
        data = {"price": "invalid"}
        with pytest.raises(ParseException) as exc_info:
            scraper._extract_price(data, "price")
        assert "价格格式无效" in str(exc_info.value)
    
    def test_extract_sizes(self):
        """测试尺码提取"""
        scraper = ProductScraper()
        
        data = {
            "sizes": [
                {"size": "S", "sizeImageLink": "https://example.com/s.jpg"},
                {"size": "M", "sizeImageLink": "https://example.com/m.jpg"},
                {"size": "L", "sizeImageLink": "https://example.com/l.jpg"}
            ]
        }
        
        sizes = scraper._extract_sizes(data)
        
        assert len(sizes) == 3
        assert sizes[0].size_name == "S"
        assert sizes[0].size_image_url == "https://example.com/s.jpg"
        assert sizes[1].size_name == "M"
        assert sizes[2].size_name == "L"
    
    def test_extract_sizes_invalid(self):
        """测试无效尺码数据"""
        scraper = ProductScraper()
        
        # 测试非列表数据
        data = {"sizes": "invalid"}
        sizes = scraper._extract_sizes(data)
        assert len(sizes) == 0
        
        # 测试空列表
        data = {"sizes": []}
        sizes = scraper._extract_sizes(data)
        assert len(sizes) == 0
    
    def test_extract_detail_images(self):
        """测试详情图提取"""
        scraper = ProductScraper()
        
        data = {
            "productDetails": {
                "detailImageLinks": [
                    "https://example.com/detail1.jpg",
                    "https://example.com/detail2.jpg"
                ]
            }
        }
        
        images = scraper._extract_detail_images(data)
        
        assert len(images) == 2
        assert images[0] == "https://example.com/detail1.jpg"
        assert images[1] == "https://example.com/detail2.jpg"
    
    def test_extract_product_code(self):
        """测试商品编码提取"""
        scraper = ProductScraper()
        
        data = {
            "productDetails": {
                "details": "货号: TEST-001\n其他信息"
            }
        }
        
        code = scraper._extract_product_code(data)
        assert code == "TEST-001"
    
    def test_extract_product_code_not_found(self):
        """测试未找到商品编码"""
        scraper = ProductScraper()
        
        data = {
            "productDetails": {
                "details": "没有货号信息"
            }
        }
        
        code = scraper._extract_product_code(data)
        assert code is None
    
    def test_validate_url(self):
        """测试URL验证"""
        scraper = ProductScraper()
        
        # 有效URL
        assert scraper.validate_url("https://www.jp0663.com/detail/test") is True
        assert scraper.validate_url("http://example.com") is True
        
        # 无效URL
        assert scraper.validate_url("invalid-url") is False
        assert scraper.validate_url("") is False
    
    def test_is_supported_url(self):
        """测试支持的URL检查"""
        scraper = ProductScraper()
        
        # 支持的URL
        assert scraper.is_supported_url("https://www.jp0663.com/detail/test") is True
        assert scraper.is_supported_url("https://jp0663.com/detail/test") is True
        
        # 不支持的URL
        assert scraper.is_supported_url("https://example.com/product") is False
        assert scraper.is_supported_url("invalid-url") is False
    
    def test_get_supported_domains(self):
        """测试获取支持的域名"""
        scraper = ProductScraper()
        
        domains = scraper.get_supported_domains()
        
        assert "www.jp0663.com" in domains
        assert "jp0663.com" in domains
        assert isinstance(domains, list)
    
    @patch('src.scraper.product_scraper.ProductScraper')
    def test_scrape_product_convenience_function(self, mock_scraper_class):
        """测试便捷函数"""
        mock_scraper = Mock()
        mock_product = Mock()
        mock_scraper.scrape_product.return_value = mock_product
        mock_scraper_class.return_value = mock_scraper
        
        url = "https://www.jp0663.com/detail/test"
        result = scrape_product(url)
        
        mock_scraper_class.assert_called_once()
        mock_scraper.scrape_product.assert_called_once_with(url)
        assert result == mock_product
    
    def test_parse_product_data_missing_required_fields(self):
        """测试解析缺少必需字段的数据"""
        scraper = ProductScraper()
        
        # 缺少商品名称
        data = {
            "price": "2980",
            "imageLink": "https://example.com/main.jpg"
        }
        
        mock_response = Mock()
        mock_response.json = data
        
        with pytest.raises(ParseException) as exc_info:
            scraper._parse_product_data(mock_response, "https://example.com")
        
        assert "商品名称不能为空" in str(exc_info.value)
    
    def test_parse_product_data_invalid_price(self):
        """测试解析无效价格"""
        scraper = ProductScraper()
        
        data = {
            "productName": "测试商品",
            "price": "0",  # 价格为0
            "imageLink": "https://example.com/main.jpg"
        }
        
        mock_response = Mock()
        mock_response.json = data
        
        with pytest.raises(ParseException) as exc_info:
            scraper._parse_product_data(mock_response, "https://example.com")
        
        assert "商品价格必须大于0" in str(exc_info.value)
