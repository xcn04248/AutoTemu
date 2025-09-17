"""
尺码映射模块

负责将原始尺码信息转换为Temu SKU系统格式
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import SizeMappingException

logger = get_logger(__name__)


class SizeType(Enum):
    """尺码类型枚举"""
    CLOTHING = "clothing"  # 服装
    SHOES = "shoes"        # 鞋子
    ACCESSORIES = "accessories"  # 配饰
    UNKNOWN = "unknown"    # 未知


@dataclass
class SizeInfo:
    """尺码信息数据类"""
    original_size: str
    size_type: SizeType
    mapped_size: Optional[str] = None
    size_chart_element: Optional[str] = None
    confidence: float = 0.0
    notes: Optional[str] = None


class SizeMapper:
    """尺码映射器"""

    def __init__(self):
        """初始化尺码映射器"""
        # 服装尺码映射表
        self.clothing_size_map = {
            # 国际尺码
            'XS': 'XS', 'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL', 'XXL': 'XXL', 'XXXL': 'XXXL',
            'xs': 'XS', 's': 'S', 'm': 'M', 'l': 'L', 'xl': 'XL', 'xxl': 'XXL', 'xxxl': 'XXXL',
            
            # 数字尺码
            '0': 'XS', '1': 'S', '2': 'M', '3': 'L', '4': 'XL', '5': 'XXL', '6': 'XXXL',
            '00': 'XS', '01': 'S', '02': 'M', '03': 'L', '04': 'XL', '05': 'XXL', '06': 'XXXL',
            
            # 日本尺码
            'SS': 'XS', 'S': 'S', 'M': 'M', 'L': 'L', 'LL': 'XL', 'LLL': 'XXL',
            'ss': 'XS', 's': 'S', 'm': 'M', 'l': 'L', 'll': 'XL', 'lll': 'XXL',
            
            # 胸围尺码 (cm) - 移除，避免与腰围尺码冲突
            '80cm': 'XS', '85cm': 'S', '90cm': 'M', '95cm': 'L', '100cm': 'XL', '105cm': 'XXL', '110cm': 'XXXL',
            
            # 腰围尺码 (cm)
            '60': 'XS', '65': 'S', '70': 'M', '75': 'L', '80': 'XL', '85': 'XXL', '90': 'XXXL',
            '60cm': 'XS', '65cm': 'S', '70cm': 'M', '75cm': 'L', '80cm': 'XL', '85cm': 'XXL', '90cm': 'XXXL',
        }
        
        # 鞋子尺码映射表
        self.shoes_size_map = {
            # 国际尺码
            '35': '35', '36': '36', '37': '37', '38': '38', '39': '39', '40': '40', '41': '41', '42': '42', '43': '43', '44': '44', '45': '45',
            '35.5': '35.5', '36.5': '36.5', '37.5': '37.5', '38.5': '38.5', '39.5': '39.5', '40.5': '40.5', '41.5': '41.5', '42.5': '42.5', '43.5': '43.5', '44.5': '44.5',
            
            # 美国尺码 - 移除，避免与英国尺码冲突
            '5US': '35', '5.5US': '35.5', '6US': '36', '6.5US': '36.5', '7US': '37', '7.5US': '37.5', '8US': '38', '8.5US': '38.5', '9US': '39', '9.5US': '39.5', '10US': '40', '10.5US': '40.5', '11US': '41', '11.5US': '41.5', '12US': '42',
            
            # 英国尺码
            '3': '35', '3.5': '35.5', '4': '36', '4.5': '36.5', '5': '37', '5.5': '37.5', '6': '38', '6.5': '38.5', '7': '39', '7.5': '39.5', '8': '40', '8.5': '40.5', '9': '41', '9.5': '41.5', '10': '42',
        }
        
        # 配饰尺码映射表
        self.accessories_size_map = {
            # 帽子尺码
            'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL',
            '54': 'S', '55': 'M', '56': 'L', '57': 'XL', '58': 'XXL',
            '54cm': 'S', '55cm': 'M', '56cm': 'L', '57cm': 'XL', '58cm': 'XXL',
            
            # 手套尺码
            'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL',
            '6': 'S', '7': 'M', '8': 'L', '9': 'XL', '10': 'XXL',
            
            # 腰带尺码
            'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL',
            '80': 'S', '85': 'M', '90': 'L', '95': 'XL', '100': 'XXL',
            '80cm': 'S', '85cm': 'M', '90cm': 'L', '95cm': 'XL', '100cm': 'XXL',
        }
        
        # 尺码类型识别关键词
        self.size_type_keywords = {
            SizeType.CLOTHING: ['shirt', 'dress', 'pants', 'jeans', 'jacket', 'coat', 'sweater', 'hoodie', 't-shirt', 'blouse', 'skirt', 'shorts', 'trousers', 'top', 'bottom', '服装', '衣服', '上衣', '下装', '连衣裙', '衬衫', '裤子', '外套'],
            SizeType.SHOES: ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats', 'loafers', 'slippers', '鞋子', '运动鞋', '靴子', '凉鞋', '高跟鞋', '平底鞋', '拖鞋'],
            SizeType.ACCESSORIES: ['hat', 'cap', 'gloves', 'belt', 'scarf', 'bag', 'purse', 'wallet', 'watch', '帽子', '手套', '腰带', '围巾', '包', '钱包', '手表', '配饰']
        }

    def detect_size_type(self, product_title: str, product_description: str = "") -> SizeType:
        """
        检测尺码类型
        
        Args:
            product_title: 商品标题
            product_description: 商品描述（可选）
            
        Returns:
            尺码类型
        """
        text = f"{product_title} {product_description}".lower()
        
        # 统计各类型关键词出现次数
        type_scores = {}
        for size_type, keywords in self.size_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            type_scores[size_type] = score
        
        # 返回得分最高的类型
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return SizeType.UNKNOWN

    def normalize_size(self, size: str) -> str:
        """
        标准化尺码字符串
        
        Args:
            size: 原始尺码字符串
            
        Returns:
            标准化后的尺码字符串
        """
        if not size:
            return ""
        
        # 去除前后空格
        size = size.strip()
        
        # 去除多余的空格
        size = re.sub(r'\s+', ' ', size)
        
        # 转换为大写（保留小数点）
        size = size.upper()
        
        # 去除常见的单位后缀
        size = re.sub(r'\s*(CM|INCH|IN|MM)\s*$', '', size, flags=re.IGNORECASE)
        
        return size

    def map_size(self, original_size: str, size_type: SizeType, product_title: str = "", product_description: str = "") -> SizeInfo:
        """
        映射尺码
        
        Args:
            original_size: 原始尺码
            size_type: 尺码类型
            product_title: 商品标题（可选）
            product_description: 商品描述（可选）
            
        Returns:
            尺码信息对象
        """
        try:
            # 标准化尺码
            normalized_size = self.normalize_size(original_size)
            
            if not normalized_size:
                return SizeInfo(
                    original_size=original_size,
                    size_type=size_type,
                    confidence=0.0,
                    notes="空尺码"
                )
            
            # 根据尺码类型选择映射表
            if size_type == SizeType.CLOTHING:
                mapped_size, confidence = self._map_clothing_size(normalized_size)
            elif size_type == SizeType.SHOES:
                mapped_size, confidence = self._map_shoes_size(normalized_size)
            elif size_type == SizeType.ACCESSORIES:
                mapped_size, confidence = self._map_accessories_size(normalized_size)
            else:
                # 未知类型，尝试所有映射表
                mapped_size, confidence = self._map_unknown_size(normalized_size)
            
            return SizeInfo(
                original_size=original_size,
                size_type=size_type,
                mapped_size=mapped_size,
                confidence=confidence,
                notes=f"映射到: {mapped_size}" if mapped_size else "无法映射"
            )
            
        except Exception as e:
            logger.error(f"尺码映射失败: {original_size}, 错误: {str(e)}")
            return SizeInfo(
                original_size=original_size,
                size_type=size_type,
                confidence=0.0,
                notes=f"映射错误: {str(e)}"
            )

    def _map_clothing_size(self, size: str) -> Tuple[Optional[str], float]:
        """映射服装尺码"""
        # 直接匹配
        if size in self.clothing_size_map:
            return self.clothing_size_map[size], 1.0
        
        # 模糊匹配 - 智能匹配条件
        for key, value in self.clothing_size_map.items():
            # 对于单字符键，要求完全匹配或作为单词边界匹配
            if len(key) == 1:
                if key == size or f' {key} ' in f' {size} ' or size.startswith(key + ' ') or size.endswith(' ' + key):
                    return value, 0.8
            # 对于多字符键，允许包含匹配
            elif len(key) >= 2 and (key in size or size in key):
                return value, 0.8
        
        # 数字范围匹配
        if size.isdigit():
            size_num = int(size)
            if 0 <= size_num <= 6:
                return self.clothing_size_map[str(size_num)], 0.9
        
        return None, 0.0

    def _map_shoes_size(self, size: str) -> Tuple[Optional[str], float]:
        """映射鞋子尺码"""
        # 直接匹配
        if size in self.shoes_size_map:
            return self.shoes_size_map[size], 1.0
        
        # 模糊匹配 - 智能匹配条件
        for key, value in self.shoes_size_map.items():
            # 对于单字符键，要求完全匹配或作为单词边界匹配
            if len(key) == 1:
                if key == size or f' {key} ' in f' {size} ' or size.startswith(key + ' ') or size.endswith(' ' + key):
                    return value, 0.8
            # 对于多字符键，允许包含匹配
            elif len(key) >= 2 and (key in size or size in key):
                return value, 0.8
        
        # 数字范围匹配
        if size.replace('.', '').isdigit():
            try:
                size_num = float(size)
                if 35 <= size_num <= 45:
                    return str(size_num), 0.9
            except ValueError:
                pass
        
        return None, 0.0

    def _map_accessories_size(self, size: str) -> Tuple[Optional[str], float]:
        """映射配饰尺码"""
        # 直接匹配
        if size in self.accessories_size_map:
            return self.accessories_size_map[size], 1.0
        
        # 模糊匹配 - 智能匹配条件
        for key, value in self.accessories_size_map.items():
            # 对于单字符键，要求完全匹配或作为单词边界匹配
            if len(key) == 1:
                if key == size or f' {key} ' in f' {size} ' or size.startswith(key + ' ') or size.endswith(' ' + key):
                    return value, 0.8
            # 对于多字符键，允许包含匹配
            elif len(key) >= 2 and (key in size or size in key):
                return value, 0.8
        
        return None, 0.0

    def _map_unknown_size(self, size: str) -> Tuple[Optional[str], float]:
        """映射未知类型尺码"""
        # 尝试所有映射表
        for mapper in [self._map_clothing_size, self._map_shoes_size, self._map_accessories_size]:
            mapped_size, confidence = mapper(size)
            if mapped_size:
                return mapped_size, confidence * 0.7  # 降低置信度
        
        return None, 0.0

    def batch_map_sizes(self, sizes: List[str], size_type: SizeType, product_title: str = "", product_description: str = "") -> List[SizeInfo]:
        """
        批量映射尺码
        
        Args:
            sizes: 尺码列表
            size_type: 尺码类型
            product_title: 商品标题（可选）
            product_description: 商品描述（可选）
            
        Returns:
            尺码信息列表
        """
        results = []
        
        for size in sizes:
            try:
                size_info = self.map_size(size, size_type, product_title, product_description)
                results.append(size_info)
            except Exception as e:
                logger.error(f"批量映射尺码失败: {size}, 错误: {str(e)}")
                results.append(SizeInfo(
                    original_size=size,
                    size_type=size_type,
                    confidence=0.0,
                    notes=f"映射错误: {str(e)}"
                ))
        
        return results

    def get_size_chart_elements(self, size_type: SizeType) -> List[str]:
        """
        获取尺码表元素
        
        Args:
            size_type: 尺码类型
            
        Returns:
            尺码表元素列表
        """
        # 这里应该调用Temu API获取尺码表元素
        # 目前返回模拟数据
        if size_type == SizeType.CLOTHING:
            return ['chest', 'waist', 'length', 'sleeve']
        elif size_type == SizeType.SHOES:
            return ['length', 'width', 'heel_height']
        elif size_type == SizeType.ACCESSORIES:
            return ['circumference', 'length', 'width']
        else:
            return ['size']

    def validate_size_mapping(self, size_info: SizeInfo) -> bool:
        """
        验证尺码映射结果
        
        Args:
            size_info: 尺码信息对象
            
        Returns:
            是否有效
        """
        if not size_info.mapped_size:
            return False
        
        if size_info.confidence < 0.5:
            return False
        
        return True

    def get_mapping_statistics(self, size_infos: List[SizeInfo]) -> Dict[str, Any]:
        """
        获取映射统计信息
        
        Args:
            size_infos: 尺码信息列表
            
        Returns:
            统计信息字典
        """
        total = len(size_infos)
        if total == 0:
            return {
                'total': 0,
                'mapped': 0,
                'unmapped': 0,
                'success_rate': 0.0,
                'average_confidence': 0.0,
                'type_distribution': {}
            }
        
        mapped = sum(1 for info in size_infos if info.mapped_size)
        unmapped = total - mapped
        success_rate = mapped / total
        
        confidences = [info.confidence for info in size_infos if info.mapped_size]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        type_distribution = {}
        for info in size_infos:
            type_name = info.size_type.value
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
        
        return {
            'total': total,
            'mapped': mapped,
            'unmapped': unmapped,
            'success_rate': success_rate,
            'average_confidence': average_confidence,
            'type_distribution': type_distribution
        }
