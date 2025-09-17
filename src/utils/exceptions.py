"""
自定义异常类

定义系统中使用的各种异常类型。
"""


class AutoTemuException(Exception):
    """AutoTemu系统的基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 额外的错误详情
        """
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        """返回异常的字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {super().__str__()}"
        return super().__str__()


# 爬虫相关异常

class ScraperException(AutoTemuException):
    """爬虫异常基类"""
    pass


class NetworkException(ScraperException):
    """网络相关异常"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details["url"] = url
        if status_code:
            self.details["status_code"] = status_code


class ParseException(ScraperException):
    """数据解析异常"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, error_code="PARSE_ERROR", **kwargs)
        self.field = field
        if field:
            self.details["field"] = field


# 图片处理相关异常

class ImageProcessException(AutoTemuException):
    """图片处理异常基类"""
    pass


class ImageDownloadException(ImageProcessException):
    """图片下载异常"""
    
    def __init__(self, message: str, image_url: str = None, **kwargs):
        super().__init__(message, error_code="IMAGE_DOWNLOAD_ERROR", **kwargs)
        self.image_url = image_url
        if image_url:
            self.details["image_url"] = image_url


class ImageFormatException(ImageProcessException):
    """图片格式异常"""
    
    def __init__(self, message: str, expected_format: str = None, actual_format: str = None, **kwargs):
        super().__init__(message, error_code="IMAGE_FORMAT_ERROR", **kwargs)
        self.expected_format = expected_format
        self.actual_format = actual_format
        if expected_format:
            self.details["expected_format"] = expected_format
        if actual_format:
            self.details["actual_format"] = actual_format


class OCRException(ImageProcessException):
    """OCR识别异常"""
    
    def __init__(self, message: str, api_error: str = None, **kwargs):
        super().__init__(message, error_code="OCR_ERROR", **kwargs)
        self.api_error = api_error
        if api_error:
            self.details["api_error"] = api_error


# 数据转换相关异常

class TransformException(AutoTemuException):
    """数据转换异常基类"""
    pass


class DataValidationException(TransformException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: str = None, expected_type: str = None, **kwargs):
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", **kwargs)
        self.field = field
        self.expected_type = expected_type
        if field:
            self.details["field"] = field
        if expected_type:
            self.details["expected_type"] = expected_type


class SizeMappingException(TransformException):
    """尺码映射异常"""
    
    def __init__(self, message: str, original_size: str = None, **kwargs):
        super().__init__(message, error_code="SIZE_MAPPING_ERROR", **kwargs)
        self.original_size = original_size
        if original_size:
            self.details["original_size"] = original_size


# Temu API相关异常

class TemuAPIException(AutoTemuException):
    """Temu API异常基类"""
    pass


class AuthenticationException(TemuAPIException):
    """认证异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class RateLimitException(TemuAPIException):
    """限流异常"""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, error_code="RATE_LIMIT", **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class APIResponseException(TemuAPIException):
    """API响应异常"""
    
    def __init__(self, message: str, api_code: str = None, api_message: str = None, **kwargs):
        super().__init__(message, error_code="API_RESPONSE_ERROR", **kwargs)
        self.api_code = api_code
        self.api_message = api_message
        if api_code:
            self.details["api_code"] = api_code
        if api_message:
            self.details["api_message"] = api_message


# 重试相关异常

class RetryException(AutoTemuException):
    """重试异常"""
    
    def __init__(self, message: str, attempts: int = None, max_attempts: int = None, **kwargs):
        super().__init__(message, error_code="RETRY_EXHAUSTED", **kwargs)
        self.attempts = attempts
        self.max_attempts = max_attempts
        if attempts:
            self.details["attempts"] = attempts
        if max_attempts:
            self.details["max_attempts"] = max_attempts


# 用于判断是否应该重试的异常类型
RETRYABLE_EXCEPTIONS = (
    NetworkException,
    ImageDownloadException,
    OCRException,
    RateLimitException,
    # 可以添加其他可重试的异常类型
)


def is_retryable_exception(exception: Exception) -> bool:
    """
    判断异常是否可以重试
    
    Args:
        exception: 异常实例
        
    Returns:
        是否可以重试
    """
    return isinstance(exception, RETRYABLE_EXCEPTIONS)
