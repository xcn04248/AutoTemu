"""
Temu API客户端测试
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from src.api.temu_client import TemuAPIClient
from src.models.product import TemuProduct, TemuSKU, TemuCategory, TemuListingResult
from src.utils.exceptions import TemuAPIException, AuthenticationException, RateLimitException, APIResponseException


class TestTemuAPIClient:
    """Temu API客户端测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建模拟配置
        self.mock_config = Mock()
        self.mock_config.temu_base_url = "https://api.temu.com"
        self.mock_config.temu_app_key = "test_app_key"
        self.mock_config.temu_app_secret = "test_app_secret"
        self.mock_config.temu_access_token = "test_access_token"
        
        # 创建API客户端
        self.client = TemuAPIClient(self.mock_config)

    def test_init(self):
        """测试初始化"""
        assert self.client.base_url == "https://api.temu.com"
        assert self.client.app_key == "test_app_key"
        assert self.client.app_secret == "test_app_secret"
        assert self.client.access_token == "test_access_token"
        assert self.client.api_version == "1.0"

    def test_generate_signature(self):
        """测试生成签名"""
        params = {
            "app_key": "test_app_key",
            "method": "test_method",
            "timestamp": "1234567890",
            "version": "1.0"
        }
        
        signature = self.client._generate_signature(params)
        
        # 验证签名不为空且长度正确
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex string length

    def test_prepare_request_params(self):
        """测试准备请求参数"""
        method = "test_method"
        params = {"param1": "value1", "param2": "value2"}
        
        request_params = self.client._prepare_request_params(method, params)
        
        # 验证基础参数
        assert request_params["app_key"] == "test_app_key"
        assert request_params["access_token"] == "test_access_token"
        assert request_params["method"] == "test_method"
        assert request_params["version"] == "1.0"
        assert request_params["format"] == "json"
        assert request_params["charset"] == "utf-8"
        assert request_params["sign_method"] == "hmac-sha256"
        
        # 验证业务参数
        assert request_params["param1"] == "value1"
        assert request_params["param2"] == "value2"
        
        # 验证签名
        assert "sign" in request_params
        assert len(request_params["sign"]) == 64

    @patch('requests.post')
    def test_make_request_success(self, mock_post):
        """测试成功发送请求"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {"result": "test_data"}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client._make_request("test_method", {"param": "value"})
        
        assert result == {"result": "test_data"}
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_make_request_auth_error(self, mock_post):
        """测试认证错误"""
        # 模拟认证错误响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "AUTH_ERROR",
            "message": "Authentication failed"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationException) as exc_info:
            self.client._make_request("test_method", {"param": "value"})
        
        assert "认证失败" in str(exc_info.value)

    @patch('requests.post')
    def test_make_request_rate_limit_error(self, mock_post):
        """测试限流错误"""
        # 模拟限流错误响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "RATE_LIMIT",
            "message": "Rate limit exceeded",
            "retry_after": 60
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(RateLimitException) as exc_info:
            self.client._make_request("test_method", {"param": "value"})
        
        assert "请求频率限制" in str(exc_info.value)
        assert exc_info.value.retry_after == 60

    @patch('requests.post')
    def test_make_request_api_error(self, mock_post):
        """测试API错误"""
        # 模拟API错误响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "INVALID_PARAM",
            "message": "Invalid parameter"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with pytest.raises(APIResponseException) as exc_info:
            self.client._make_request("test_method", {"param": "value"})
        
        assert "API请求失败" in str(exc_info.value)
        assert exc_info.value.api_code == "INVALID_PARAM"

    @patch('requests.post')
    def test_make_request_network_error(self, mock_post):
        """测试网络错误"""
        # 模拟网络错误
        mock_post.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(TemuAPIException) as exc_info:
            self.client._make_request("test_method", {"param": "value"})
        
        assert "网络请求失败" in str(exc_info.value)

    @patch.object(TemuAPIClient, '_make_request')
    def test_get_category_recommend(self, mock_make_request):
        """测试获取分类推荐"""
        # 模拟API响应
        mock_make_request.return_value = {
            "categories": [
                {
                    "category_id": "cat1",
                    "category_name": "Category 1",
                    "parent_id": None,
                    "level": 1,
                    "is_leaf": True
                },
                {
                    "category_id": "cat2",
                    "category_name": "Category 2",
                    "parent_id": "cat1",
                    "level": 2,
                    "is_leaf": True
                }
            ]
        }
        
        categories = self.client.get_category_recommend("Test Product", "Test Description")
        
        assert len(categories) == 2
        assert categories[0].category_id == "cat1"
        assert categories[0].name == "Category 1"
        assert categories[1].category_id == "cat2"
        assert categories[1].name == "Category 2"
        assert categories[1].parent_id == "cat1"

    @patch.object(TemuAPIClient, '_make_request')
    def test_get_size_chart_elements(self, mock_make_request):
        """测试获取尺码表元素"""
        # 模拟API响应
        mock_make_request.return_value = {
            "elements": ["chest", "waist", "length", "sleeve"]
        }
        
        elements = self.client.get_size_chart_elements("cat1", "clothing")
        
        assert elements == ["chest", "waist", "length", "sleeve"]

    @patch.object(TemuAPIClient, '_make_request')
    def test_upload_image_success(self, mock_make_request):
        """测试成功上传图片"""
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'fake_image_data')
            temp_path = f.name
        
        try:
            # 模拟API响应
            mock_make_request.return_value = {
                "image_id": "img123"
            }
            
            image_id = self.client.upload_image(temp_path, "main")
            
            assert image_id == "img123"
        finally:
            # 清理临时文件
            os.unlink(temp_path)

    def test_upload_image_file_not_found(self):
        """测试上传不存在的图片文件"""
        with pytest.raises(TemuAPIException) as exc_info:
            self.client.upload_image("nonexistent.jpg", "main")
        
        assert "图片文件不存在" in str(exc_info.value)

    @patch.object(TemuAPIClient, 'upload_image')
    def test_batch_upload_images(self, mock_upload_image):
        """测试批量上传图片"""
        # 创建临时图片文件
        temp_paths = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                f.write(b'fake_image_data')
                temp_paths.append(f.name)
        
        try:
            # 模拟上传成功
            mock_upload_image.side_effect = ["img1", "img2", "img3"]
            
            image_ids = self.client.batch_upload_images(temp_paths, ["main", "detail", "size"])
            
            assert image_ids == ["img1", "img2", "img3"]
            assert mock_upload_image.call_count == 3
        finally:
            # 清理临时文件
            for path in temp_paths:
                os.unlink(path)

    @patch.object(TemuAPIClient, '_make_request')
    def test_create_product(self, mock_make_request):
        """测试创建商品"""
        # 模拟API响应
        mock_make_request.return_value = {
            "product_id": "prod123"
        }
        
        product = TemuProduct(
            title="Test Product",
            description="Test Description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["img1", "img2"]
        )
        
        product_id = self.client.create_product(product, "cat1")
        
        assert product_id == "prod123"

    @patch.object(TemuAPIClient, '_make_request')
    def test_create_sku(self, mock_make_request):
        """测试创建SKU"""
        # 模拟API响应
        mock_make_request.return_value = {
            "sku_id": "sku123"
        }
        
        sku = TemuSKU(
            sku_id="SKU_001",
            size="M",
            original_size="M",
            price=130.0,
            stock_quantity=100,
            images=["img1"]
        )
        
        sku_id = self.client.create_sku("prod123", sku)
        
        assert sku_id == "sku123"

    @patch.object(TemuAPIClient, 'create_sku')
    def test_batch_create_skus(self, mock_create_sku):
        """测试批量创建SKU"""
        # 模拟创建成功
        mock_create_sku.side_effect = ["sku1", "sku2", "sku3"]
        
        skus = [
            TemuSKU("SKU_001", "S", "S", 130.0, 100, ["img1"]),
            TemuSKU("SKU_002", "M", "M", 130.0, 100, ["img1"]),
            TemuSKU("SKU_003", "L", "L", 130.0, 100, ["img1"])
        ]
        
        sku_ids = self.client.batch_create_skus("prod123", skus)
        
        assert sku_ids == ["sku1", "sku2", "sku3"]
        assert mock_create_sku.call_count == 3

    @patch.object(TemuAPIClient, 'batch_upload_images')
    @patch.object(TemuAPIClient, 'create_product')
    @patch.object(TemuAPIClient, 'batch_create_skus')
    def test_list_product_success(self, mock_batch_create_skus, mock_create_product, mock_batch_upload_images):
        """测试成功上架商品"""
        # 模拟成功响应
        mock_batch_upload_images.return_value = ["img1", "img2"]
        mock_create_product.return_value = "prod123"
        mock_batch_create_skus.return_value = ["sku1", "sku2"]
        
        product = TemuProduct(
            title="Test Product",
            description="Test Description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["path1", "path2"]
        )
        
        skus = [
            TemuSKU("SKU_001", "S", "S", 130.0, 100, ["img1"]),
            TemuSKU("SKU_002", "M", "M", 130.0, 100, ["img1"])
        ]
        
        result = self.client.list_product(product, skus, "cat1")
        
        assert result.success == True
        assert result.product_id == "prod123"
        assert result.sku_ids == ["sku1", "sku2"]
        assert result.image_ids == ["img1", "img2"]
        assert len(result.errors) == 0

    @patch.object(TemuAPIClient, 'batch_upload_images')
    def test_list_product_failure(self, mock_batch_upload_images):
        """测试上架商品失败"""
        # 模拟上传失败
        mock_batch_upload_images.side_effect = TemuAPIException("Upload failed")
        
        product = TemuProduct(
            title="Test Product",
            description="Test Description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["path1", "path2"]
        )
        
        skus = [TemuSKU("SKU_001", "S", "S", 130.0, 100, ["img1"])]
        
        result = self.client.list_product(product, skus, "cat1")
        
        assert result.success == False
        assert result.product_id is None
        assert len(result.errors) > 0
        assert "Upload failed" in result.errors[0]

    @patch.object(TemuAPIClient, '_make_request')
    def test_get_product_status(self, mock_make_request):
        """测试获取商品状态"""
        # 模拟API响应
        mock_make_request.return_value = {
            "product_id": "prod123",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        status = self.client.get_product_status("prod123")
        
        assert status["product_id"] == "prod123"
        assert status["status"] == "active"

    @patch.object(TemuAPIClient, '_make_request')
    def test_update_product(self, mock_make_request):
        """测试更新商品"""
        # 模拟API响应
        mock_make_request.return_value = {}
        
        updates = {"title": "Updated Title", "price": 150.0}
        result = self.client.update_product("prod123", updates)
        
        assert result == True

    @patch.object(TemuAPIClient, '_make_request')
    def test_delete_product(self, mock_make_request):
        """测试删除商品"""
        # 模拟API响应
        mock_make_request.return_value = {}
        
        result = self.client.delete_product("prod123")
        
        assert result == True

    @patch.object(TemuAPIClient, '_make_request')
    def test_get_api_quota(self, mock_make_request):
        """测试获取API配额"""
        # 模拟API响应
        mock_make_request.return_value = {
            "daily_limit": 1000,
            "used": 100,
            "remaining": 900
        }
        
        quota = self.client.get_api_quota()
        
        assert quota["daily_limit"] == 1000
        assert quota["used"] == 100
        assert quota["remaining"] == 900

    @patch.object(TemuAPIClient, 'get_api_quota')
    def test_test_connection_success(self, mock_get_quota):
        """测试连接测试成功"""
        mock_get_quota.return_value = {"daily_limit": 1000}
        
        result = self.client.test_connection()
        
        assert result == True

    @patch.object(TemuAPIClient, 'get_api_quota')
    def test_test_connection_failure(self, mock_get_quota):
        """测试连接测试失败"""
        mock_get_quota.side_effect = TemuAPIException("Connection failed")
        
        result = self.client.test_connection()
        
        assert result == False
