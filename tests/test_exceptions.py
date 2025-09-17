"""
异常类的单元测试
"""

import pytest
from src.utils.exceptions import (
    AutoTemuException,
    NetworkException,
    ParseException,
    ImageDownloadException,
    ImageFormatException,
    OCRException,
    DataValidationException,
    SizeMappingException,
    AuthenticationException,
    RateLimitException,
    APIResponseException,
    RetryException,
    is_retryable_exception
)


class TestExceptions:
    """异常类测试"""
    
    def test_base_exception(self):
        """测试基础异常类"""
        # 基本用法
        exc = AutoTemuException("测试错误")
        assert str(exc) == "测试错误"
        assert exc.error_code is None
        assert exc.details == {}
        
        # 带错误代码
        exc = AutoTemuException("测试错误", error_code="TEST_ERROR")
        assert str(exc) == "[TEST_ERROR] 测试错误"
        assert exc.error_code == "TEST_ERROR"
        
        # 带详情
        exc = AutoTemuException("测试错误", details={"key": "value"})
        assert exc.details == {"key": "value"}
    
    def test_network_exception(self):
        """测试网络异常"""
        exc = NetworkException("连接超时", url="https://example.com", status_code=504)
        
        assert str(exc) == "[NETWORK_ERROR] 连接超时"
        assert exc.error_code == "NETWORK_ERROR"
        assert exc.url == "https://example.com"
        assert exc.status_code == 504
        assert exc.details["url"] == "https://example.com"
        assert exc.details["status_code"] == 504
    
    def test_parse_exception(self):
        """测试解析异常"""
        exc = ParseException("字段缺失", field="price")
        
        assert exc.error_code == "PARSE_ERROR"
        assert exc.field == "price"
        assert exc.details["field"] == "price"
    
    def test_image_download_exception(self):
        """测试图片下载异常"""
        exc = ImageDownloadException("下载失败", image_url="https://example.com/image.jpg")
        
        assert exc.error_code == "IMAGE_DOWNLOAD_ERROR"
        assert exc.image_url == "https://example.com/image.jpg"
        assert exc.details["image_url"] == "https://example.com/image.jpg"
    
    def test_image_format_exception(self):
        """测试图片格式异常"""
        exc = ImageFormatException(
            "格式不支持",
            expected_format="JPEG",
            actual_format="BMP"
        )
        
        assert exc.error_code == "IMAGE_FORMAT_ERROR"
        assert exc.expected_format == "JPEG"
        assert exc.actual_format == "BMP"
        assert exc.details["expected_format"] == "JPEG"
        assert exc.details["actual_format"] == "BMP"
    
    def test_ocr_exception(self):
        """测试OCR异常"""
        exc = OCRException("识别失败", api_error="Rate limit exceeded")
        
        assert exc.error_code == "OCR_ERROR"
        assert exc.api_error == "Rate limit exceeded"
        assert exc.details["api_error"] == "Rate limit exceeded"
    
    def test_data_validation_exception(self):
        """测试数据验证异常"""
        exc = DataValidationException(
            "类型错误",
            field="price",
            expected_type="float"
        )
        
        assert exc.error_code == "DATA_VALIDATION_ERROR"
        assert exc.field == "price"
        assert exc.expected_type == "float"
    
    def test_size_mapping_exception(self):
        """测试尺码映射异常"""
        exc = SizeMappingException("未知尺码", original_size="XXL")
        
        assert exc.error_code == "SIZE_MAPPING_ERROR"
        assert exc.original_size == "XXL"
        assert exc.details["original_size"] == "XXL"
    
    def test_authentication_exception(self):
        """测试认证异常"""
        exc = AuthenticationException("Token过期")
        
        assert exc.error_code == "AUTH_ERROR"
        assert str(exc) == "[AUTH_ERROR] Token过期"
    
    def test_rate_limit_exception(self):
        """测试限流异常"""
        exc = RateLimitException("请求过于频繁", retry_after=60)
        
        assert exc.error_code == "RATE_LIMIT"
        assert exc.retry_after == 60
        assert exc.details["retry_after"] == 60
    
    def test_api_response_exception(self):
        """测试API响应异常"""
        exc = APIResponseException(
            "商品创建失败",
            api_code="GOODS_001",
            api_message="商品名称重复"
        )
        
        assert exc.error_code == "API_RESPONSE_ERROR"
        assert exc.api_code == "GOODS_001"
        assert exc.api_message == "商品名称重复"
        assert exc.details["api_code"] == "GOODS_001"
        assert exc.details["api_message"] == "商品名称重复"
    
    def test_retry_exception(self):
        """测试重试异常"""
        exc = RetryException("重试失败", attempts=3, max_attempts=3)
        
        assert exc.error_code == "RETRY_EXHAUSTED"
        assert exc.attempts == 3
        assert exc.max_attempts == 3
        assert exc.details["attempts"] == 3
        assert exc.details["max_attempts"] == 3
    
    def test_is_retryable_exception(self):
        """测试异常是否可重试的判断"""
        # 可重试的异常
        assert is_retryable_exception(NetworkException("网络错误"))
        assert is_retryable_exception(ImageDownloadException("下载失败"))
        assert is_retryable_exception(OCRException("OCR失败"))
        assert is_retryable_exception(RateLimitException("限流"))
        
        # 不可重试的异常
        assert not is_retryable_exception(ParseException("解析错误"))
        assert not is_retryable_exception(DataValidationException("验证失败"))
        assert not is_retryable_exception(AuthenticationException("认证失败"))
        assert not is_retryable_exception(Exception("普通异常"))
    
    def test_exception_inheritance(self):
        """测试异常继承关系"""
        # 所有自定义异常都应该是AutoTemuException的子类
        exc = NetworkException("测试")
        assert isinstance(exc, AutoTemuException)
        assert isinstance(exc, Exception)
        
        # 检查继承链
        assert issubclass(NetworkException, AutoTemuException)
        assert issubclass(ImageDownloadException, AutoTemuException)
        assert issubclass(OCRException, AutoTemuException)
