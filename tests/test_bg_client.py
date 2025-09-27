"""
BgClient 单元测试
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from src.api.bg_client import BgClient
from src.models.bg_models import (
    BgGoodsAddRequest, BgImageUploadRequest, BgCatsGetRequest,
    BgPropertyGetRequest, BgSpecIdGetRequest
)


class TestBgClient:
    """BgClient测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.client = BgClient(
            app_key="test_app_key",
            app_secret="test_app_secret", 
            access_token="test_access_token",
            base_url="https://test-api.temu.com",
            debug=True
        )
    
    def test_init(self):
        """测试初始化"""
        assert self.client.app_key == "test_app_key"
        assert self.client.app_secret == "test_app_secret"
        assert self.client.access_token == "test_access_token"
        assert self.client.base_url == "https://test-api.temu.com"
        assert self.client.debug == True
    
    @patch('src.api.bg_client.requests.post')
    def test_send_request_success(self, mock_post):
        """测试成功发送请求"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {"productId": 12345},
            "requestId": "test_request_id"
        }
        mock_post.return_value = mock_response
        
        # 测试请求
        request_data = {"test": "data"}
        response = self.client._send_request("bg.goods.add", request_data, Mock)
        
        # 验证
        assert mock_post.called
        assert response.success == True
        assert response.result["productId"] == 12345
    
    @patch('src.api.bg_client.requests.post')
    def test_send_request_api_error(self, mock_post):
        """测试API业务错误"""
        # 模拟API业务错误
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "errorCode": "INVALID_PARAMETER",
            "errorMsg": "参数无效"
        }
        mock_post.return_value = mock_response
        
        # 测试请求
        request_data = {"test": "data"}
        
        with pytest.raises(Exception):  # 应该抛出APIException
            self.client._send_request("bg.goods.add", request_data, Mock)
    
    @patch('src.api.bg_client.requests.post')
    def test_send_request_network_error(self, mock_post):
        """测试网络错误"""
        # 模拟网络错误
        mock_post.side_effect = Exception("网络连接失败")
        
        # 测试请求
        request_data = {"test": "data"}
        
        with pytest.raises(Exception):  # 应该抛出NetworkException
            self.client._send_request("bg.goods.add", request_data, Mock)
    
    @patch('src.api.bg_client.BgClient._send_request')
    def test_goods_add(self, mock_send_request):
        """测试商品添加"""
        # 模拟响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.productId = 12345
        mock_send_request.return_value = mock_response
        
        # 测试请求
        request = BgGoodsAddRequest(
            productName="测试商品",
            cat1Id=1,
            cat2Id=2,
            cat3Id=3
        )
        
        response = self.client.goods_add(request)
        
        # 验证
        assert response.success == True
        assert response.result.productId == 12345
        mock_send_request.assert_called_once()
    
    @patch('src.api.bg_client.BgClient._send_request')
    def test_image_upload(self, mock_send_request):
        """测试图片上传"""
        # 模拟响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.url = "https://test-image-url.com/image.jpg"
        mock_send_request.return_value = mock_response
        
        # 测试请求
        request = BgImageUploadRequest(
            file_url="https://test-source.com/image.jpg",
            scaling_type=1
        )
        
        response = self.client.image_upload(request)
        
        # 验证
        assert response.success == True
        assert response.result.url == "https://test-image-url.com/image.jpg"
        mock_send_request.assert_called_once()
    
    @patch('src.api.bg_client.BgClient._send_request')
    def test_cats_get(self, mock_send_request):
        """测试分类获取"""
        # 模拟响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.goodsCatsList = [
            {"catId": 1, "catName": "服装", "catType": 0},
            {"catId": 2, "catName": "电子产品", "catType": 1}
        ]
        mock_send_request.return_value = mock_response
        
        # 测试请求
        request = BgCatsGetRequest(parent_cat_id=0)
        
        response = self.client.cats_get(request)
        
        # 验证
        assert response.success == True
        assert len(response.result.goodsCatsList) == 2
        mock_send_request.assert_called_once()
    
    @patch('src.api.bg_client.BgClient._send_request')
    def test_property_get(self, mock_send_request):
        """测试属性获取"""
        # 模拟响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.properties = [
            {"pid": 1, "name": "颜色", "required": True},
            {"pid": 2, "name": "尺码", "required": True}
        ]
        mock_send_request.return_value = mock_response
        
        # 测试请求
        request = BgPropertyGetRequest(cat_id=123)
        
        response = self.client.property_get(request)
        
        # 验证
        assert response.success == True
        assert len(response.result.properties) == 2
        mock_send_request.assert_called_once()
    
    @patch('src.api.bg_client.BgClient._send_request')
    def test_spec_id_get(self, mock_send_request):
        """测试规格ID获取"""
        # 模拟响应
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = Mock()
        mock_response.result.specId = 1001
        mock_response.result.specName = "M"
        mock_send_request.return_value = mock_response
        
        # 测试请求
        request = BgSpecIdGetRequest(
            cat_id=123,
            parent_spec_id=3001,
            child_spec_name="M"
        )
        
        response = self.client.spec_id_get(request)
        
        # 验证
        assert response.success == True
        assert response.result.specId == 1001
        assert response.result.specName == "M"
        mock_send_request.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
