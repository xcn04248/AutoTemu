"""
OCR客户端模块的单元测试
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import os
import tempfile
from datetime import datetime, timedelta

from src.image.ocr_client import OCRClient, recognize_image_text, batch_recognize_images
from src.utils.exceptions import OCRException
import src.utils.config as config_module


class TestOCRClient:
    """OCR客户端测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        # 清理全局配置
        config_module._config = None
        
        # 设置必需的环境变量
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
    
    @pytest.fixture
    def mock_token_response(self):
        """模拟token响应"""
        return {
            "access_token": "test_access_token_12345",
            "expires_in": 2592000,
            "scope": "public"
        }
    
    @pytest.fixture
    def mock_ocr_response(self):
        """模拟OCR响应"""
        return {
            "words_result_num": 2,
            "words_result": [
                {"words": "Pure Cotton"},
                {"words": "100% Quality"}
            ]
        }
    
    @pytest.fixture
    def mock_ocr_response_with_chinese(self):
        """模拟包含中文的OCR响应"""
        return {
            "words_result_num": 2,
            "words_result": [
                {"words": "Pure Cotton"},
                {"words": "纯棉材质"}
            ]
        }
    
    def test_ocr_client_initialization(self):
        """测试OCR客户端初始化"""
        client = OCRClient()
        
        assert client.api_key == "test_key"
        assert client.secret_key == "test_secret"
        assert client.base_url == "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
        assert client._access_token is None
        assert client._token_expires_at is None
    
    @patch('src.image.ocr_client.requests.post')
    def test_get_access_token_success(self, mock_post, mock_token_response):
        """测试成功获取access_token"""
        mock_response = Mock()
        mock_response.json.return_value = mock_token_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = OCRClient()
        token = client._get_access_token()
        
        assert token == "test_access_token_12345"
        assert client._access_token == "test_access_token_12345"
        assert client._token_expires_at is not None
        
        # 验证请求参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "oauth/2.0/token" in call_args[0][0]
        assert call_args[1]["params"]["client_id"] == "test_key"
    
    @patch('src.image.ocr_client.requests.post')
    def test_get_access_token_api_error(self, mock_post):
        """测试API返回错误"""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "invalid_client"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = OCRClient()
        
        with pytest.raises(OCRException) as exc_info:
            client._get_access_token()
        
        assert "获取access_token失败" in str(exc_info.value)
    
    @patch('src.image.ocr_client.requests.post')
    def test_get_access_token_network_error(self, mock_post):
        """测试网络错误"""
        mock_post.side_effect = Exception("网络超时")
        
        client = OCRClient()
        
        with pytest.raises(OCRException) as exc_info:
            client._get_access_token()
        
        assert "获取access_token失败" in str(exc_info.value)
    
    def test_check_for_chinese(self):
        """测试中文检测"""
        client = OCRClient()
        
        # 包含中文
        assert client._check_for_chinese("纯棉材质") is True
        assert client._check_for_chinese("Pure Cotton 纯棉") is True
        
        # 不包含中文
        assert client._check_for_chinese("Pure Cotton") is False
        assert client._check_for_chinese("100% Quality") is False
        assert client._check_for_chinese("") is False
    
    def test_get_file_content_as_base64(self):
        """测试文件base64编码"""
        client = OCRClient()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # 测试不URL编码
            result = client._get_file_content_as_base64(temp_file, urlencoded=False)
            assert isinstance(result, str)
            assert len(result) > 0
            
            # 测试URL编码
            result_encoded = client._get_file_content_as_base64(temp_file, urlencoded=True)
            assert isinstance(result_encoded, str)
            # 对于简单的ASCII内容，URL编码可能不会改变结果
            # 这里只验证返回的是字符串即可
            
        finally:
            os.unlink(temp_file)
    
    def test_get_file_content_as_base64_file_not_found(self):
        """测试文件不存在的情况"""
        client = OCRClient()
        
        with pytest.raises(OCRException) as exc_info:
            client._get_file_content_as_base64("nonexistent_file.txt")
        
        assert "文件读取失败" in str(exc_info.value)
    
    @patch('src.image.ocr_client.requests.post')
    def test_recognize_text_success(self, mock_post, mock_token_response, mock_ocr_response):
        """测试成功识别文字"""
        # 模拟token请求
        token_response = Mock()
        token_response.json.return_value = mock_token_response
        token_response.raise_for_status.return_value = None
        
        # 模拟OCR请求
        ocr_response = Mock()
        ocr_response.json.return_value = mock_ocr_response
        ocr_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [token_response, ocr_response]
        
        client = OCRClient()
        
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_file = f.name
        
        try:
            has_chinese, words = client.recognize_text(temp_file)
            
            assert has_chinese is False
            assert words == ["Pure Cotton", "100% Quality"]
            
            # 验证OCR请求
            assert mock_post.call_count == 2
            ocr_call = mock_post.call_args_list[1]
            assert "webimage" in ocr_call[0][0]
            
        finally:
            os.unlink(temp_file)
    
    @patch('src.image.ocr_client.requests.post')
    def test_recognize_text_with_chinese(self, mock_post, mock_token_response, mock_ocr_response_with_chinese):
        """测试识别包含中文的文字"""
        # 模拟token请求
        token_response = Mock()
        token_response.json.return_value = mock_token_response
        token_response.raise_for_status.return_value = None
        
        # 模拟OCR请求
        ocr_response = Mock()
        ocr_response.json.return_value = mock_ocr_response_with_chinese
        ocr_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [token_response, ocr_response]
        
        client = OCRClient()
        
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_file = f.name
        
        try:
            has_chinese, words = client.recognize_text(temp_file)
            
            assert has_chinese is True
            assert "纯棉材质" in words
            
        finally:
            os.unlink(temp_file)
    
    @patch('src.image.ocr_client.requests.post')
    def test_recognize_text_api_error(self, mock_post, mock_token_response):
        """测试OCR API返回错误"""
        # 模拟token请求
        token_response = Mock()
        token_response.json.return_value = mock_token_response
        token_response.raise_for_status.return_value = None
        
        # 模拟OCR错误响应
        error_response = Mock()
        error_response.json.return_value = {
            "error_code": "17",
            "error_msg": "Open api daily request limit reached"
        }
        error_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [token_response, error_response]
        
        client = OCRClient()
        
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_file = f.name
        
        try:
            # 由于有重试机制，最终会抛出RetryException
            from src.utils.exceptions import RetryException
            with pytest.raises(RetryException):
                client.recognize_text(temp_file)
            
        finally:
            os.unlink(temp_file)
    
    def test_is_image_supported(self):
        """测试图片格式支持检查"""
        client = OCRClient()
        
        # 支持的格式
        assert client.is_image_supported("test.jpg") is True
        assert client.is_image_supported("test.JPEG") is True
        assert client.is_image_supported("test.png") is True
        assert client.is_image_supported("test.bmp") is True
        assert client.is_image_supported("test.gif") is True
        
        # 不支持的格式
        assert client.is_image_supported("test.txt") is False
        assert client.is_image_supported("test.pdf") is False
        assert client.is_image_supported("test") is False
    
    def test_get_supported_formats(self):
        """测试获取支持的格式列表"""
        client = OCRClient()
        
        formats = client.get_supported_formats()
        
        assert isinstance(formats, list)
        assert '.jpg' in formats
        assert '.jpeg' in formats
        assert '.png' in formats
        assert '.bmp' in formats
        assert '.gif' in formats
    
    def test_validate_image_file(self):
        """测试图片文件验证"""
        client = OCRClient()
        
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image data")
            temp_file = f.name
        
        try:
            # 有效文件
            assert client.validate_image_file(temp_file) is True
            
            # 不存在的文件
            assert client.validate_image_file("nonexistent.jpg") is False
            
            # 不支持的格式
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b"text data")
                txt_file = f.name
            
            try:
                assert client.validate_image_file(txt_file) is False
            finally:
                os.unlink(txt_file)
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_image_file_large_file(self):
        """测试大文件验证"""
        client = OCRClient()
        
        # 创建大文件（超过4MB）
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # 写入5MB数据
            f.write(b"x" * (5 * 1024 * 1024))
            large_file = f.name
        
        try:
            assert client.validate_image_file(large_file) is False
        finally:
            os.unlink(large_file)
    
    @patch('src.image.ocr_client.requests.post')
    def test_batch_recognize(self, mock_post, mock_token_response, mock_ocr_response):
        """测试批量识别"""
        # 模拟token请求
        token_response = Mock()
        token_response.json.return_value = mock_token_response
        token_response.raise_for_status.return_value = None
        
        # 模拟OCR请求
        ocr_response = Mock()
        ocr_response.json.return_value = mock_ocr_response
        ocr_response.raise_for_status.return_value = None
        
        # 为每个图片创建响应
        mock_post.side_effect = [token_response] + [ocr_response] * 3
        
        client = OCRClient()
        
        # 创建临时图片文件
        temp_files = []
        try:
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                    f.write(b"fake image data")
                    temp_files.append(f.name)
            
            results = client.batch_recognize(temp_files)
            
            assert len(results) == 3
            for file_path in temp_files:
                assert file_path in results
                has_chinese, words = results[file_path]
                assert has_chinese is False
                assert words == ["Pure Cotton", "100% Quality"]
            
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_get_usage_stats(self):
        """测试获取使用统计"""
        client = OCRClient()
        
        stats = client.get_usage_stats()
        
        assert "api_key" in stats
        assert "has_token" in stats
        assert "token_expires_at" in stats
        assert "supported_formats" in stats
        
        assert stats["api_key"] == "test_key..."
        assert stats["has_token"] is False
        assert stats["token_expires_at"] is None
        assert isinstance(stats["supported_formats"], list)
    
    def test_token_caching(self):
        """测试token缓存"""
        client = OCRClient()
        
        # 设置缓存的token
        client._access_token = "cached_token"
        client._token_expires_at = datetime.now() + timedelta(hours=1)
        
        # 应该返回缓存的token
        token = client._get_access_token()
        assert token == "cached_token"
    
    def test_token_expired(self):
        """测试token过期"""
        client = OCRClient()
        
        # 设置过期的token
        client._access_token = "expired_token"
        client._token_expires_at = datetime.now() - timedelta(hours=1)
        
        # 应该重新获取token
        with patch('src.image.ocr_client.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "new_token",
                "expires_in": 2592000
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            token = client._get_access_token()
            assert token == "new_token"
            assert client._access_token == "new_token"


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """设置测试环境"""
        monkeypatch.setenv("FIRECRAWL_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_API_KEY", "test_key")
        monkeypatch.setenv("BAIDU_SECRET_KEY", "test_secret")
        monkeypatch.setenv("TEMU_APP_KEY", "test_key")
        monkeypatch.setenv("TEMU_APP_SECRET", "test_secret")
        monkeypatch.setenv("TEMU_ACCESS_TOKEN", "test_token")
    
    @patch('src.image.ocr_client.OCRClient')
    def test_recognize_image_text(self, mock_client_class):
        """测试便捷函数recognize_image_text"""
        mock_client = Mock()
        mock_client.recognize_text.return_value = (False, ["test"])
        mock_client_class.return_value = mock_client
        
        result = recognize_image_text("test.jpg")
        
        assert result == (False, ["test"])
        mock_client_class.assert_called_once()
        mock_client.recognize_text.assert_called_once_with("test.jpg")
    
    @patch('src.image.ocr_client.OCRClient')
    def test_batch_recognize_images(self, mock_client_class):
        """测试便捷函数batch_recognize_images"""
        mock_client = Mock()
        mock_client.batch_recognize.return_value = {"test.jpg": (False, ["test"])}
        mock_client_class.return_value = mock_client
        
        result = batch_recognize_images(["test.jpg"])
        
        assert result == {"test.jpg": (False, ["test"])}
        mock_client_class.assert_called_once()
        mock_client.batch_recognize.assert_called_once_with(["test.jpg"])
