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
        
        # 图片下载记录文件
        self.download_record_file = self.image_save_path / "download_records.json"
        self.downloaded_urls = self._load_download_records()

        # OCR结果记录文件与缓存
        self.ocr_record_file = self.image_save_path / "ocr_records.json"
        self.ocr_results = self._load_ocr_records()

    def _load_download_records(self) -> Dict[str, str]:
        """加载图片下载记录"""
        if not self.download_record_file.exists():
            return {}
        
        try:
            import json
            with open(self.download_record_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载下载记录失败: {e}")
            return {}

    def _save_download_records(self):
        """保存图片下载记录"""
        try:
            import json
            with open(self.download_record_file, 'w', encoding='utf-8') as f:
                json.dump(self.downloaded_urls, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存下载记录失败: {e}")

    def _load_ocr_records(self) -> Dict[str, Dict[str, str]]:
        """加载OCR结果缓存记录: {url: {"has_chinese": bool, "text": str}}"""
        if not self.ocr_record_file.exists():
            return {}
        try:
            import json
            with open(self.ocr_record_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载OCR记录失败: {e}")
            return {}

    def _save_ocr_records(self):
        """保存OCR结果缓存记录"""
        try:
            import json
            with open(self.ocr_record_file, 'w', encoding='utf-8') as f:
                json.dump(self.ocr_results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存OCR记录失败: {e}")

    def _get_cached_ocr(self, url: str) -> Optional[Tuple[bool, str]]:
        """获取已缓存的OCR结果"""
        record = self.ocr_results.get(url)
        if not record:
            return None
        try:
            has_chinese = bool(record.get("has_chinese", False))
            text = record.get("text", "")
            return has_chinese, text
        except Exception:
            return None

    def _record_ocr_result(self, url: str, has_chinese: bool, text: str):
        """记录OCR结果到缓存"""
        self.ocr_results[url] = {"has_chinese": has_chinese, "text": text}
        self._save_ocr_records()

    def _is_image_downloaded(self, url: str) -> Optional[Path]:
        """检查图片是否已经下载过（仅依据URL，不校验本地文件）"""
        if url in self.downloaded_urls:
            return Path(self.downloaded_urls[url])
        return None

    def _record_downloaded_image(self, url: str, file_path: Path):
        """记录已下载的图片"""
        self.downloaded_urls[url] = str(file_path)
        self._save_download_records()

    @retry()
    def download_image(self, url: str, filename: Optional[str] = None, force_scrape: bool = False) -> Path:
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
            # 首先检查是否已经下载过（除非强制抓取）
            if not force_scrape:
                existing_path = self._is_image_downloaded(url)
                if existing_path:
                    logger.info(f"图片已下载过，跳过下载: {url} -> {existing_path}")
                    return existing_path

            # 解析URL获取原始文件名
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"image_{hash(url) % 100000}.jpg"

            # 确保文件名有扩展名
            if not any(filename.lower().endswith(ext) for ext in self.supported_formats):
                filename += '.jpg'

            # 构建保存路径（不重命名，保持原始文件名）
            save_path = self.image_save_path / filename

            # 下载图片
            logger.info(f"开始下载图片: {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 记录已下载的图片
            self._record_downloaded_image(url, save_path)
            
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
            has_chinese, words_list = self.ocr_client.recognize_text(str(image_path))
            
            # 将识别出的文字列表合并为字符串
            ocr_text = " ".join(words_list) if words_list else ""
            
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

    def process_images(self, image_urls: List[str], force_scrape: bool = False) -> Dict[str, List[Path]]:
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
                # 生成文件名（仅用于首次下载时保存）
                filename = f"image_{i+1:03d}_{hash(url) % 10000}"

                # 基于URL的去重逻辑：
                # 1) 如果URL已存在记录且本地文件存在，则直接使用该文件，避免重复下载（除非强制抓取）
                # 2) 如果URL已存在记录但本地文件不存在，则按需跳过（不重新下载）
                # 3) 如果URL未记录，则执行下载
                if not force_scrape:
                    recorded_path_str = self.downloaded_urls.get(url)
                    if recorded_path_str:
                        recorded_path = Path(recorded_path_str)
                        if recorded_path.exists():
                            logger.info(f"URL已记录，使用已存在文件，跳过下载: {url} -> {recorded_path}")
                            image_path = recorded_path
                        else:
                            logger.info(f"URL已记录但本地文件缺失，按要求跳过下载与处理: {url}")
                            continue
                    else:
                        # 首次下载
                        image_path = self.download_image(url, filename, force_scrape=force_scrape)
                else:
                    # 强制抓取，重新下载
                    image_path = self.download_image(url, filename, force_scrape=force_scrape)
                
                # 检查图片是否包含中文（优先使用缓存，除非强制抓取）
                if not force_scrape:
                    cached = self._get_cached_ocr(url)
                    if cached is not None:
                        has_chinese, ocr_text = cached
                        logger.info(f"使用缓存OCR结果: {image_path.name}, 包含中文: {has_chinese}")
                    else:
                        has_chinese, ocr_text = self.check_image_for_chinese(image_path)
                        # 记录OCR结果
                        self._record_ocr_result(url, has_chinese, ocr_text)
                else:
                    # 强制抓取，跳过缓存
                    has_chinese, ocr_text = self.check_image_for_chinese(image_path)
                    # 记录OCR结果
                    self._record_ocr_result(url, has_chinese, ocr_text)
                
                if has_chinese:
                    # 包含中文，直接删除图片
                    image_path.unlink()  # 删除文件
                    # 不移除URL记录，确保后续运行依旧不会重复下载该URL
                    result['filtered'].append(image_path)  # 记录已删除的图片
                    logger.info(f"图片包含中文，已删除: {image_path.name}")
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

    def validate_image_requirements(self, image_paths: List[Path], cat_type: int = 0) -> Dict[str, List[Path]]:
        """
        验证图片是否符合Temu要求

        Args:
            image_paths: 图片路径列表
            cat_type: 分类类型，0=服装，1=非服装

        Returns:
            验证结果: {
                'valid': [Path, ...],     # 符合要求的图片
                'invalid': [Path, ...]    # 不符合要求的图片
            }
        """
        result = {'valid': [], 'invalid': []}
        
        # 根据分类类型设置不同的要求
        if cat_type == 0:  # 服装类
            min_width, min_height = 1340, 1785
            expected_ratio = 3 / 4
            max_size = 3 * 1024 * 1024  # 3MB
        else:  # 非服装类
            min_width, min_height = 800, 800
            expected_ratio = 1.0
            max_size = 3 * 1024 * 1024  # 3MB
        
        for image_path in image_paths:
            try:
                with Image.open(image_path) as img:
                    # 检查图片格式
                    if img.format not in ['JPEG', 'JPG', 'PNG']:
                        result['invalid'].append(image_path)
                        logger.warning(f"图片格式不支持: {image_path.name} ({img.format})")
                        continue
                    
                    # 检查尺寸要求
                    if img.width < min_width or img.height < min_height:
                        result['invalid'].append(image_path)
                        logger.warning(f"图片尺寸不符合要求: {image_path.name} ({img.width}x{img.height}, 最小: {min_width}x{min_height})")
                        continue
                    
                    # 检查文件大小
                    file_size = image_path.stat().st_size
                    if file_size > max_size:
                        result['invalid'].append(image_path)
                        logger.warning(f"图片文件过大: {image_path.name} ({file_size / 1024 / 1024:.2f}MB, 最大: {max_size / 1024 / 1024:.2f}MB)")
                        continue
                    
                    # 检查宽高比
                    ratio = img.width / img.height
                    if abs(ratio - expected_ratio) > 0.1:  # 允许10%的误差
                        result['invalid'].append(image_path)
                        logger.warning(f"图片宽高比不符合要求: {image_path.name} ({ratio:.2f}, 期望: {expected_ratio:.2f})")
                        continue
                    
                    # 检查图片质量（避免模糊或低质量图片）
                    if img.width < min_width * 1.2 or img.height < min_height * 1.2:
                        logger.warning(f"图片分辨率较低: {image_path.name} ({img.width}x{img.height})")
                    
                    result['valid'].append(image_path)
                    logger.debug(f"图片验证通过: {image_path.name} ({img.width}x{img.height})")
                    
            except Exception as e:
                result['invalid'].append(image_path)
                logger.error(f"验证图片失败: {image_path}, 错误: {str(e)}")
        
        return result

    def optimize_image_for_upload(self, image_path: Path, cat_type: int = 0) -> Optional[Path]:
        """
        优化图片以符合上传要求
        
        Args:
            image_path: 原始图片路径
            cat_type: 分类类型，0=服装，1=非服装
            
        Returns:
            优化后的图片路径，如果优化失败返回None
        """
        try:
            with Image.open(image_path) as img:
                # 根据分类类型设置目标尺寸
                if cat_type == 0:  # 服装类
                    target_width, target_height = 1350, 1800
                else:  # 非服装类
                    target_width, target_height = 800, 800
                
                # 计算缩放比例，保持宽高比
                width_ratio = target_width / img.width
                height_ratio = target_height / img.height
                scale_ratio = min(width_ratio, height_ratio)
                
                # 计算新尺寸
                new_width = int(img.width * scale_ratio)
                new_height = int(img.height * scale_ratio)
                
                # 如果图片已经符合要求，直接返回
                if (img.width >= target_width and img.height >= target_height and 
                    abs(img.width / img.height - target_width / target_height) < 0.1):
                    return image_path
                
                # 调整图片尺寸
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 创建目标尺寸的白色背景
                if cat_type == 0:  # 服装类
                    final_img = Image.new('RGB', (target_width, target_height), 'white')
                    # 居中放置图片
                    x_offset = (target_width - new_width) // 2
                    y_offset = (target_height - new_height) // 2
                    final_img.paste(resized_img, (x_offset, y_offset))
                else:  # 非服装类
                    final_img = Image.new('RGB', (target_width, target_height), 'white')
                    # 居中放置图片
                    x_offset = (target_width - new_width) // 2
                    y_offset = (target_height - new_height) // 2
                    final_img.paste(resized_img, (x_offset, y_offset))
                
                # 保存优化后的图片
                optimized_path = image_path.parent / f"optimized_{image_path.name}"
                final_img.save(optimized_path, 'JPEG', quality=90, optimize=True)
                
                logger.info(f"图片优化完成: {image_path.name} -> {optimized_path.name}")
                return optimized_path
                
        except Exception as e:
            logger.error(f"优化图片失败: {image_path}, 错误: {str(e)}")
            return None

    def select_best_images(self, image_paths: List[Path], max_count: int = 5) -> List[Path]:
        """
        智能选择最佳图片
        
        Args:
            image_paths: 图片路径列表
            max_count: 最大选择数量
            
        Returns:
            选择的最佳图片路径列表
        """
        if not image_paths:
            return []
        
        # 按文件大小和质量排序（优先选择大文件）
        scored_images = []
        for image_path in image_paths:
            try:
                with Image.open(image_path) as img:
                    # 计算质量分数
                    file_size = image_path.stat().st_size
                    width, height = img.size
                    
                    # 基础分数：文件大小 + 分辨率
                    score = file_size + (width * height * 0.1)
                    
                    # 宽高比加分
                    ratio = width / height
                    if 0.7 <= ratio <= 0.8:  # 接近3:4的比例
                        score += 1000000
                    
                    # 分辨率加分
                    if width >= 1500 and height >= 2000:
                        score += 500000
                    elif width >= 1340 and height >= 1785:
                        score += 200000
                    
                    scored_images.append((score, image_path))
                    
            except Exception as e:
                logger.warning(f"评估图片失败: {image_path}, 错误: {str(e)}")
                continue
        
        # 按分数降序排序
        scored_images.sort(key=lambda x: x[0], reverse=True)
        
        # 选择前max_count张图片
        selected = [img_path for _, img_path in scored_images[:max_count]]
        
        logger.info(f"从 {len(image_paths)} 张图片中选择了 {len(selected)} 张最佳图片")
        return selected
