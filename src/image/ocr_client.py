"""
OCR客户端模块

封装百度OCR API，提供图片文字识别和中文检测功能。
"""

import os
import base64
import urllib.parse
import re
import time
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

import requests

from ..utils.config import get_config
from ..utils.logger import get_logger
from ..utils.retry import network_retry
from ..utils.exceptions import OCRException, NetworkException


class OCRClient:
    """百度OCR客户端"""
    
    def __init__(self):
        """初始化OCR客户端"""
        self.config = get_config()
        self.logger = get_logger("ocr")
        
        # OCR API配置
        self.api_key = self.config.baidu_api_key
        self.secret_key = self.config.baidu_secret_key
        self.base_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
        
        # Token缓存
        self._access_token = None
        self._token_expires_at = None
        
        self.logger.info("OCR客户端初始化成功")
    
    def _get_access_token(self) -> str:
        """
        获取百度OCR access_token
        
        Returns:
            str: access_token
            
        Raises:
            OCRException: 获取token失败
        """
        # 检查缓存的token是否有效
        if (self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        self.logger.info("获取新的access_token")
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            access_token = result.get("access_token")
            
            if not access_token:
                error_msg = result.get("error_description", "未知错误")
                raise OCRException(f"获取access_token失败: {error_msg}")
            
            # 缓存token（提前5分钟过期）
            self._access_token = access_token
            expires_in = result.get("expires_in", 2592000)  # 默认30天
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            self.logger.info("access_token获取成功")
            return access_token
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取access_token网络错误: {e}")
            raise OCRException(f"网络请求失败: {e}")
        except Exception as e:
            self.logger.error(f"获取access_token失败: {e}")
            raise OCRException(f"获取access_token失败: {e}")
    
    def _get_file_content_as_base64(self, file_path: str, urlencoded: bool = False) -> str:
        """
        获取文件base64编码
        
        Args:
            file_path: 文件路径
            urlencoded: 是否对结果进行urlencoded
            
        Returns:
            str: base64编码的字符串
            
        Raises:
            OCRException: 文件读取失败
        """
        try:
            with open(file_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf8")
                if urlencoded:
                    content = urllib.parse.quote_plus(content)
                return content
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
            raise OCRException(f"文件读取失败: {e}")
    
    def _check_for_chinese(self, text: str) -> bool:
        """
        检查字符串是否包含中文字符
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 是否包含中文
        """
        return bool(re.search(r'[\u4e00-\u9fa5]', text))
    
    @network_retry()
    def recognize_text(self, image_path: str) -> Tuple[bool, List[str]]:
        """
        识别图片中的文字并检查是否包含中文
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Tuple[bool, List[str]]: (是否包含中文, 识别出的文字列表)
            
        Raises:
            OCRException: OCR识别失败
        """
        self.logger.info(f"开始OCR识别: {os.path.basename(image_path)}")
        
        try:
            # 获取access_token
            access_token = self._get_access_token()
            
            # 准备请求数据
            image_base64 = self._get_file_content_as_base64(image_path, urlencoded=True)
            payload = f'image={image_base64}&detect_language=false&detect_direction=false'
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            # 发送OCR请求
            url = f"{self.base_url}?access_token={access_token}"
            response = requests.post(url, headers=headers, data=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查API错误
            if "error_code" in result:
                error_msg = result.get("error_msg", "未知错误")
                raise OCRException(f"OCR API错误: {error_msg}", api_error=error_msg)
            
            # 解析识别结果
            words_list = []
            has_chinese = False
            
            if result.get("words_result_num", 0) > 0:
                for item in result["words_result"]:
                    words = item.get("words", "")
                    if words:
                        words_list.append(words)
                        if self._check_for_chinese(words):
                            has_chinese = True
            
            self.logger.info(f"OCR识别完成: {os.path.basename(image_path)}, "
                           f"文字数: {len(words_list)}, 包含中文: {has_chinese}")
            
            return has_chinese, words_list
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OCR API网络错误 {image_path}: {e}")
            raise OCRException(f"网络请求失败: {e}")
        except OCRException:
            raise
        except Exception as e:
            self.logger.error(f"OCR识别失败 {image_path}: {e}")
            raise OCRException(f"识别失败: {e}")
    
    def batch_recognize(self, image_paths: List[str]) -> Dict[str, Tuple[bool, List[str]]]:
        """
        批量识别多张图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            Dict[str, Tuple[bool, List[str]]]: 图片路径到识别结果的映射
        """
        self.logger.info(f"开始批量OCR识别，共 {len(image_paths)} 张图片")
        
        results = {}
        success_count = 0
        failed_count = 0
        
        for image_path in image_paths:
            try:
                has_chinese, words = self.recognize_text(image_path)
                results[image_path] = (has_chinese, words)
                success_count += 1
                
                # 添加小延迟避免API频率限制
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"图片识别失败 {image_path}: {e}")
                results[image_path] = (False, [])
                failed_count += 1
        
        self.logger.log_data_processing("OCR识别", len(image_paths), 
                                      success=success_count, failed=failed_count)
        
        return results
    
    def is_image_supported(self, file_path: str) -> bool:
        """
        检查图片格式是否支持
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否支持
        """
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        _, ext = os.path.splitext(file_path.lower())
        return ext in supported_extensions
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的图片格式列表
        
        Returns:
            List[str]: 支持的格式列表
        """
        return ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    def validate_image_file(self, file_path: str) -> bool:
        """
        验证图片文件是否有效
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否有效
        """
        if not os.path.exists(file_path):
            return False
        
        if not os.path.isfile(file_path):
            return False
        
        if not self.is_image_supported(file_path):
            return False
        
        # 检查文件大小（百度OCR限制4MB）
        file_size = os.path.getsize(file_path)
        if file_size > 4 * 1024 * 1024:  # 4MB
            self.logger.warning(f"图片文件过大: {file_path} ({file_size} bytes)")
            return False
        
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "api_key": self.api_key[:8] + "..." if self.api_key else None,
            "has_token": self._access_token is not None,
            "token_expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
            "supported_formats": self.get_supported_formats()
        }


# 便捷函数
def recognize_image_text(image_path: str) -> Tuple[bool, List[str]]:
    """
    识别图片文字的便捷函数
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        Tuple[bool, List[str]]: (是否包含中文, 识别出的文字列表)
    """
    client = OCRClient()
    return client.recognize_text(image_path)


def batch_recognize_images(image_paths: List[str]) -> Dict[str, Tuple[bool, List[str]]]:
    """
    批量识别图片的便捷函数
    
    Args:
        image_paths: 图片路径列表
        
    Returns:
        Dict[str, Tuple[bool, List[str]]]: 图片路径到识别结果的映射
    """
    client = OCRClient()
    return client.batch_recognize(image_paths)


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python ocr_client.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        client = OCRClient()
        
        if not client.validate_image_file(image_path):
            print(f"图片文件无效: {image_path}")
            sys.exit(1)
        
        print(f"开始识别图片: {image_path}")
        has_chinese, words = client.recognize_text(image_path)
        
        print(f"识别结果:")
        print(f"  包含中文: {has_chinese}")
        print(f"  识别文字: {words}")
        
        # 显示使用统计
        stats = client.get_usage_stats()
        print(f"\n使用统计:")
        print(f"  API Key: {stats['api_key']}")
        print(f"  有Token: {stats['has_token']}")
        print(f"  Token过期时间: {stats['token_expires_at']}")
        
    except Exception as e:
        print(f"OCR识别失败: {e}")
        sys.exit(1)
