"""
ApiAdapter 单元测试
"""

import pytest
from unittest.mock import Mock, patch
from src.api.api_adapter import ApiAdapter
from src.models.product import ScrapedProduct
from src.models.bg_models import (
    BgGoodsAddResponse, BgImageUploadResponse, BgCatsGetResponse,
    BgPropertyGetResponse, BgSpecIdGetResponse
)


class TestApiAdapter:
    """ApiAdapter测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.bg_client = Mock()
        self.bg_transformer = Mock()
        self.adapter = ApiAdapter(self.bg_client, self.bg_transformer)
    
    def test_init(self):
        """测试初始化"""
        assert self.adapter.bg_client == self.bg_client
        assert self.adapter.bg_transformer == self.bg_transformer
    
    def test_create_product_success(self):
        """测试成功创建商品"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        category_info = {"catIdList": [1, 2, 3]}
        property_template = {"properties": []}
        spec_id_map = {"M": 1001, "L": 1002}
        uploaded_image_urls = ["https://uploaded1.jpg", "https://uploaded2.jpg"]
        
        # 模拟转换器
        mock_request = Mock()
        self.bg_transformer.transform_product.return_value = mock_request
        
        # 模拟客户端响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.productId = 12345
        self.bg_client.goods_add.return_value = mock_response
        
        # 测试创建商品
        result = self.adapter.create_product(
            scraped_product=scraped_product,
            category_info=category_info,
            property_template=property_template,
            spec_id_map=spec_id_map,
            uploaded_image_urls=uploaded_image_urls
        )
        
        # 验证结果
        assert result.success == True
        assert result.product_id == "12345"
        self.bg_transformer.transform_product.assert_called_once()
        self.bg_client.goods_add.assert_called_once_with(mock_request)
    
    def test_create_product_failure(self):
        """测试创建商品失败"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        category_info = {"catIdList": [1, 2, 3]}
        property_template = {"properties": []}
        spec_id_map = {"M": 1001, "L": 1002}
        uploaded_image_urls = ["https://uploaded1.jpg", "https://uploaded2.jpg"]
        
        # 模拟转换器
        mock_request = Mock()
        self.bg_transformer.transform_product.return_value = mock_request
        
        # 模拟客户端响应失败
        mock_response = Mock()
        mock_response.success = False
        mock_response.errorMsg = "API错误"
        self.bg_client.goods_add.return_value = mock_response
        
        # 测试创建商品
        result = self.adapter.create_product(
            scraped_product=scraped_product,
            category_info=category_info,
            property_template=property_template,
            spec_id_map=spec_id_map,
            uploaded_image_urls=uploaded_image_urls
        )
        
        # 验证结果
        assert result.success == False
        assert "API错误" in result.errors
    
    def test_upload_image_success(self):
        """测试成功上传图片"""
        # 模拟客户端响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.url = "https://uploaded-image.jpg"
        self.bg_client.image_upload.return_value = mock_response
        
        # 测试上传图片
        result = self.adapter.upload_image("https://source-image.jpg", 1)
        
        # 验证结果
        assert result == "https://uploaded-image.jpg"
        self.bg_client.image_upload.assert_called_once()
    
    def test_upload_image_failure(self):
        """测试上传图片失败"""
        # 模拟客户端响应失败
        mock_response = Mock()
        mock_response.success = False
        mock_response.errorMsg = "上传失败"
        self.bg_client.image_upload.return_value = mock_response
        
        # 测试上传图片
        result = self.adapter.upload_image("https://source-image.jpg", 1)
        
        # 验证结果
        assert result is None
    
    def test_get_categories_success(self):
        """测试成功获取分类"""
        # 模拟客户端响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.goodsCatsList = [
            Mock(catId=1, catName="服装"),
            Mock(catId=2, catName="电子产品")
        ]
        self.bg_client.cats_get.return_value = mock_response
        
        # 测试获取分类
        result = self.adapter.get_categories(0)
        
        # 验证结果
        assert result is not None
        assert len(result) == 2
        assert result[0].catId == 1
        assert result[0].catName == "服装"
    
    def test_get_categories_failure(self):
        """测试获取分类失败"""
        # 模拟客户端响应失败
        mock_response = Mock()
        mock_response.success = False
        mock_response.errorMsg = "获取失败"
        self.bg_client.cats_get.return_value = mock_response
        
        # 测试获取分类
        result = self.adapter.get_categories(0)
        
        # 验证结果
        assert result is None
    
    def test_get_property_template_success(self):
        """测试成功获取属性模板"""
        # 模拟客户端响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.properties = [
            Mock(pid=1, name="颜色", required=True),
            Mock(pid=2, name="尺码", required=True)
        ]
        self.bg_client.property_get.return_value = mock_response
        
        # 测试获取属性模板
        result = self.adapter.get_property_template(123)
        
        # 验证结果
        assert result is not None
        assert result.success == True
        assert len(result.result.properties) == 2
    
    def test_get_property_template_failure(self):
        """测试获取属性模板失败"""
        # 模拟客户端响应失败
        mock_response = Mock()
        mock_response.success = False
        mock_response.errorMsg = "获取失败"
        self.bg_client.property_get.return_value = mock_response
        
        # 测试获取属性模板
        result = self.adapter.get_property_template(123)
        
        # 验证结果
        assert result is None
    
    def test_get_spec_id_success(self):
        """测试成功获取规格ID"""
        # 模拟客户端响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.specId = 1001
        self.bg_client.spec_id_get.return_value = mock_response
        
        # 测试获取规格ID
        result = self.adapter.get_spec_id(123, 3001, "M")
        
        # 验证结果
        assert result == 1001
        self.bg_client.spec_id_get.assert_called_once()
    
    def test_get_spec_id_failure(self):
        """测试获取规格ID失败"""
        # 模拟客户端响应失败
        mock_response = Mock()
        mock_response.success = False
        mock_response.errorMsg = "获取失败"
        self.bg_client.spec_id_get.return_value = mock_response
        
        # 测试获取规格ID
        result = self.adapter.get_spec_id(123, 3001, "M")
        
        # 验证结果
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
