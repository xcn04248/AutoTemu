"""
图片处理模块

负责图片下载、OCR检测、中文过滤和图片分类功能
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import requests
from PIL import Image
import logging

from .ocr_client import OCRClient
from ..utils.config import get_config
from ..utils.exceptions import ImageProcessingError
from ..utils.retry import retry
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """图片处理器"""

    def __init__(self, ocr_client: Optional[OCRClient] = None):
        """
        初始化图片处理器

        Args:
            ocr_client: OCR客户端实例，如果为None则创建新实例
        """
        self.config = get_config()
        self.ocr_client = ocr_client or OCRClient()
        self.image_save_path = Path(self.config.image_save_path)
        self.image_save_path.mkdir(parents=True, exist_ok=True)

        # 支持的图片格式
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}

        # 图片类型分类规则
        self.size_keywords = ['size', 'sizing', '尺码', 'サイズ', 'measurement', 'measure']
        self.detail_keywords = ['detail', 'details', 'close', 'closeup', '详细', '詳細', 'close-up']
        self.main_keywords = ['main', 'primary', 'hero', 'featured', '主要', 'メイン']

    @retry()
    def download_image(self, url: str, filename: Optional[str] = None) -> Path:
        """
        下载图片

        Args:
            url: 图片URL
            filename: 保存的文件名，如果为None则自动生成

        Returns:
            保存的图片文件路径

        Raises:
            ImageProcessingError: 下载失败时抛出
        """
        try:
            # 解析URL获取文件名
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"image_{hash(url) % 100000}.jpg"

            # 确保文件名有扩展名
            if not any(filename.lower().endswith(ext) for ext in self.supported_formats):
                filename += '.jpg'

            # 构建保存路径
            save_path = self.image_save_path / filename

            # 下载图片
            logger.info(f"开始下载图片: {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"图片下载成功: {save_path}")
            return save_path

        except requests.RequestException as e:
            raise ImageProcessingError(f"下载图片失败: {url}, 错误: {str(e)}")
        except Exception as e:
            raise ImageProcessingError(f"保存图片失败: {url}, 错误: {str(e)}")

    def is_chinese_text(self, text: str) -> bool:
        """
        检查文本是否包含中文字符

        Args:
            text: 要检查的文本

        Returns:
            如果包含中文字符返回True，否则返回False
        """
        # 中文字符的Unicode范围
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3300-\u33ff\ufe30-\ufe4f]')
        return bool(chinese_pattern.search(text))

    def check_image_for_chinese(self, image_path: Path) -> Tuple[bool, str]:
        """
        检查图片是否包含中文文字

        Args:
            image_path: 图片文件路径

        Returns:
            (是否包含中文, OCR识别的文本)
        """
        try:
            # 使用OCR识别图片中的文字
            ocr_text = self.ocr_client.recognize_text(str(image_path))
            
            # 检查是否包含中文字符
            has_chinese = self.is_chinese_text(ocr_text)
            
            logger.debug(f"图片OCR结果: {image_path.name}, 包含中文: {has_chinese}, 文本: {ocr_text[:100]}...")
            
            return has_chinese, ocr_text

        except Exception as e:
            logger.warning(f"OCR识别失败: {image_path}, 错误: {str(e)}")
            # OCR失败时，假设不包含中文，避免误删图片
            return False, ""

    def classify_image_type(self, filename: str, url: str = "") -> str:
        """
        根据文件名和URL分类图片类型

        Args:
            filename: 文件名
            url: 图片URL（可选）

        Returns:
            图片类型: 'main', 'size', 'detail', 'other'
        """
        # 转换为小写进行匹配
        filename_lower = filename.lower()
        url_lower = url.lower()

        # 检查尺码图
        for keyword in self.size_keywords:
            if keyword in filename_lower or keyword in url_lower:
                return 'size'

        # 检查详情图
        for keyword in self.detail_keywords:
            if keyword in filename_lower or keyword in url_lower:
                return 'detail'

        # 检查主图
        for keyword in self.main_keywords:
            if keyword in filename_lower or keyword in url_lower:
                return 'main'

        # 默认分类为其他
        return 'other'

    def process_images(self, image_urls: List[str]) -> Dict[str, List[Path]]:
        """
        批量处理图片：下载、OCR检测、中文过滤、分类

        Args:
            image_urls: 图片URL列表

        Returns:
            分类后的图片路径字典: {
                'main': [Path, ...],      # 主图
                'size': [Path, ...],      # 尺码图
                'detail': [Path, ...],    # 详情图
                'other': [Path, ...],     # 其他图片
                'filtered': [Path, ...]   # 被过滤的图片（包含中文）
            }
        """
        result = {
            'main': [],
            'size': [],
            'detail': [],
            'other': [],
            'filtered': []
        }

        logger.info(f"开始处理 {len(image_urls)} 张图片")

        for i, url in enumerate(image_urls):
            try:
                # 生成文件名
                filename = f"image_{i+1:03d}_{hash(url) % 10000}"
                
                # 下载图片
                image_path = self.download_image(url, filename)
                
                # 检查图片是否包含中文
                has_chinese, ocr_text = self.check_image_for_chinese(image_path)
                
                if has_chinese:
                    # 包含中文，移动到过滤目录
                    filtered_path = self.image_save_path / "filtered" / image_path.name
                    filtered_path.parent.mkdir(exist_ok=True)
                    image_path.rename(filtered_path)
                    result['filtered'].append(filtered_path)
                    logger.info(f"图片包含中文，已过滤: {image_path.name}")
                    continue

                # 分类图片
                image_type = self.classify_image_type(image_path.name, url)
                result[image_type].append(image_path)
                
                logger.info(f"图片分类完成: {image_path.name} -> {image_type}")

            except ImageProcessingError as e:
                logger.error(f"处理图片失败: {url}, 错误: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"处理图片时发生未知错误: {url}, 错误: {str(e)}")
                continue

        # 记录处理结果
        total_processed = sum(len(images) for images in result.values())
        logger.info(f"图片处理完成: 总计 {total_processed} 张, 主图 {len(result['main'])} 张, "
                   f"尺码图 {len(result['size'])} 张, 详情图 {len(result['detail'])} 张, "
                   f"其他 {len(result['other'])} 张, 过滤 {len(result['filtered'])} 张")

        return result

    def get_image_info(self, image_path: Path) -> Dict[str, any]:
        """
        获取图片信息

        Args:
            image_path: 图片文件路径

        Returns:
            图片信息字典
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'path': str(image_path),
                    'filename': image_path.name,
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size': image_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"获取图片信息失败: {image_path}, 错误: {str(e)}")
            return {
                'path': str(image_path),
                'filename': image_path.name,
                'error': str(e)
            }

    def cleanup_temp_images(self, image_paths: List[Path]):
        """
        清理临时图片文件

        Args:
            image_paths: 要清理的图片路径列表
        """
        for image_path in image_paths:
            try:
                if image_path.exists():
                    image_path.unlink()
                    logger.debug(f"已删除临时图片: {image_path}")
            except Exception as e:
                logger.warning(f"删除临时图片失败: {image_path}, 错误: {str(e)}")

    def validate_image_requirements(self, image_paths: List[Path]) -> Dict[str, List[Path]]:
        """
        验证图片是否符合Temu要求

        Args:
            image_paths: 图片路径列表

        Returns:
            验证结果: {
                'valid': [Path, ...],     # 符合要求的图片
                'invalid': [Path, ...]    # 不符合要求的图片
            }
        """
        result = {'valid': [], 'invalid': []}
        
        for image_path in image_paths:
            try:
                with Image.open(image_path) as img:
                    # 检查尺寸要求 (最小1340x1785)
                    if img.width < 1340 or img.height < 1785:
                        result['invalid'].append(image_path)
                        logger.warning(f"图片尺寸不符合要求: {image_path.name} ({img.width}x{img.height})")
                        continue
                    
                    # 检查文件大小 (最大2MB)
                    file_size = image_path.stat().st_size
                    if file_size > 2 * 1024 * 1024:  # 2MB
                        result['invalid'].append(image_path)
                        logger.warning(f"图片文件过大: {image_path.name} ({file_size / 1024 / 1024:.2f}MB)")
                        continue
                    
                    # 检查宽高比 (3:4)
                    ratio = img.width / img.height
                    expected_ratio = 3 / 4
                    if abs(ratio - expected_ratio) > 0.1:  # 允许10%的误差
                        result['invalid'].append(image_path)
                        logger.warning(f"图片宽高比不符合要求: {image_path.name} ({ratio:.2f}, 期望: {expected_ratio:.2f})")
                        continue
                    
                    result['valid'].append(image_path)
                    logger.debug(f"图片验证通过: {image_path.name}")
                    
            except Exception as e:
                result['invalid'].append(image_path)
                logger.error(f"验证图片失败: {image_path}, 错误: {str(e)}")
        
        return result
