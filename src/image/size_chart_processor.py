"""
尺码表处理模块

提供尺码表检测、解析、生成等功能，支持从OCR结果中提取尺码表信息
并生成符合Temu API要求的尺码表格式。
"""

import re
import json
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass

from ..utils.logger import get_logger
from .ocr_client import OCRClient


@dataclass
class SizeInfo:
    """尺码信息数据类"""
    size: str  # 尺码名称，如 S, M, L, XL
    measurements: Dict[str, str]  # 尺寸信息，如 {"chest": "100", "length": "70"}
    unit: str = "cm"  # 单位


@dataclass
class SizeChartData:
    """尺码表数据类"""
    has_size_chart: bool
    size_infos: List[SizeInfo]
    chart_type: str  # "standard" 或 "detailed"
    raw_text: str = ""


class SizeChartDetector:
    """尺码表检测器"""
    
    def __init__(self):
        self.logger = get_logger("size_chart_detector")
        
        # 尺码表关键词
        self.size_keywords = [
            "尺码", "尺寸", "size", "sizes", "measurement", "measurements",
            "胸围", "腰围", "臀围", "衣长", "袖长", "裤长", "肩宽",
            "chest", "waist", "hip", "length", "sleeve", "shoulder",
            "cm", "inch", "英寸", "厘米"
        ]
        
        # 标准尺码模式
        self.standard_size_patterns = [
            r'\b[XS|S|M|L|XL|XXL|XXXL]\b',
            r'\b\d+[X]+\b',  # 如 2X, 3X
            r'\b\d+\b'  # 纯数字尺码
        ]
        
        # 尺寸测量模式
        self.measurement_patterns = [
            r'(\w+)[:：]\s*(\d+(?:\.\d+)?)\s*(cm|inch|英寸|厘米)',
            r'(\d+(?:\.\d+)?)\s*(cm|inch|英寸|厘米)',
            r'(\w+)\s*(\d+(?:\.\d+)?)'
        ]
    
    def detect_size_chart(self, ocr_text: str) -> bool:
        """
        检测OCR文本中是否包含尺码表
        
        Args:
            ocr_text: OCR识别的文本
            
        Returns:
            bool: 是否包含尺码表
        """
        if not ocr_text:
            return False
        
        text_lower = ocr_text.lower()
        
        # 检查是否包含尺码表关键词
        keyword_count = sum(1 for keyword in self.size_keywords if keyword.lower() in text_lower)
        
        # 检查是否包含标准尺码模式
        size_pattern_count = 0
        for pattern in self.standard_size_patterns:
            if re.search(pattern, ocr_text, re.IGNORECASE):
                size_pattern_count += 1
        
        # 检查是否包含尺寸测量模式
        measurement_count = 0
        for pattern in self.measurement_patterns:
            if re.search(pattern, ocr_text, re.IGNORECASE):
                measurement_count += 1
        
        # 综合判断：至少包含2个关键词，或者包含尺码模式+测量模式
        has_keywords = keyword_count >= 2
        has_size_and_measurement = size_pattern_count > 0 and measurement_count > 0
        
        is_size_chart = has_keywords or has_size_and_measurement
        
        self.logger.debug(f"尺码表检测: 关键词={keyword_count}, 尺码模式={size_pattern_count}, "
                         f"测量模式={measurement_count}, 结果={is_size_chart}")
        
        return is_size_chart


class SizeChartParser:
    """尺码表解析器"""
    
    def __init__(self):
        self.logger = get_logger("size_chart_parser")
        self.detector = SizeChartDetector()
    
    def parse_size_chart(self, ocr_text: str) -> SizeChartData:
        """
        解析尺码表文本
        
        Args:
            ocr_text: OCR识别的文本
            
        Returns:
            SizeChartData: 解析后的尺码表数据
        """
        if not self.detector.detect_size_chart(ocr_text):
            return SizeChartData(
                has_size_chart=False,
                size_infos=[],
                chart_type="none",
                raw_text=ocr_text
            )
        
        self.logger.info("开始解析尺码表")
        
        # 尝试解析标准尺码表
        standard_sizes = self._parse_standard_sizes(ocr_text)
        if standard_sizes:
            return SizeChartData(
                has_size_chart=True,
                size_infos=standard_sizes,
                chart_type="standard",
                raw_text=ocr_text
            )
        
        # 尝试解析详细尺寸表
        detailed_sizes = self._parse_detailed_sizes(ocr_text)
        if detailed_sizes:
            return SizeChartData(
                has_size_chart=True,
                size_infos=detailed_sizes,
                chart_type="detailed",
                raw_text=ocr_text
            )
        
        # 如果都解析失败，返回空结果
        return SizeChartData(
            has_size_chart=True,
            size_infos=[],
            chart_type="unknown",
            raw_text=ocr_text
        )
    
    def _parse_standard_sizes(self, text: str) -> List[SizeInfo]:
        """解析标准尺码（S/M/L/XL等）"""
        sizes = []
        
        # 查找标准尺码
        standard_size_matches = re.findall(r'\b([XS|S|M|L|XL|XXL|XXXL]+)\b', text, re.IGNORECASE)
        
        for size in standard_size_matches:
            if size.upper() not in [s.size.upper() for s in sizes]:
                sizes.append(SizeInfo(
                    size=size.upper(),
                    measurements={},
                    unit="cm"
                ))
        
        return sizes
    
    def _parse_detailed_sizes(self, text: str) -> List[SizeInfo]:
        """解析详细尺寸表"""
        sizes = []
        
        # 按行分割文本
        lines = text.split('\n')
        
        # 查找包含尺码和尺寸的行
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 查找尺码
            size_match = re.search(r'\b([XS|S|M|L|XL|XXL|XXXL]+|\d+[X]*)\b', line, re.IGNORECASE)
            if not size_match:
                continue
            
            size_name = size_match.group(1).upper()
            
            # 查找尺寸信息
            measurements = {}
            measurement_matches = re.findall(r'(\w+)[:：]\s*(\d+(?:\.\d+)?)\s*(cm|inch|英寸|厘米)?', line, re.IGNORECASE)
            
            for measurement_name, value, unit in measurement_matches:
                unit = unit.lower() if unit else "cm"
                if unit in ["inch", "英寸"]:
                    # 转换为厘米
                    value = str(float(value) * 2.54)
                    unit = "cm"
                
                measurements[measurement_name.lower()] = value
            
            if measurements:
                sizes.append(SizeInfo(
                    size=size_name,
                    measurements=measurements,
                    unit="cm"
                ))
        
        return sizes


class SizeChartGenerator:
    """尺码表生成器"""
    
    def __init__(self):
        self.logger = get_logger("size_chart_generator")
    
    def generate_temu_size_chart(self, size_chart_data: SizeChartData, cat_type: int) -> Optional[List[Dict]]:
        """
        生成符合Temu API要求的尺码表
        
        Args:
            size_chart_data: 解析后的尺码表数据
            cat_type: 商品分类类型，0=服装，1=非服装
            
        Returns:
            List[Dict]: Temu API格式的尺码表，如果不需要则返回None
        """
        # 非服装类商品不需要尺码表
        if cat_type != 0:
            self.logger.info("非服装类商品，跳过尺码表生成")
            return None
        
        # 如果没有尺码表数据，返回None
        if not size_chart_data.has_size_chart or not size_chart_data.size_infos:
            self.logger.info("没有尺码表数据，跳过尺码表生成")
            return None
        
        self.logger.info(f"开始生成尺码表，尺码数量: {len(size_chart_data.size_infos)}")
        
        # 生成Temu尺码表格式
        size_chart = self._build_temu_size_chart(size_chart_data)
        
        return size_chart
    
    def _build_temu_size_chart(self, size_chart_data: SizeChartData) -> List[Dict]:
        """构建Temu尺码表格式"""
        # 基础尺码表结构
        size_chart = {
            "classId": 128,  # 尺码表类型ID
            "meta": {
                "groups": [
                    {"id": 1, "name": "size"},
                    {"id": 20, "name": "JP"}  # 日本站
                ],
                "elements": [
                    {"id": 10002, "name": "胸围", "unit": 2},  # 胸围
                    {"id": 10003, "name": "衣长", "unit": 2}   # 衣长
                ]
            },
            "records": []
        }
        
        # 生成尺码记录
        for size_info in size_chart_data.size_infos:
            record = {
                "values": [
                    {"id": 1, "value": size_info.size, "unit_value": "cm"},  # 尺码
                    {"id": 20, "value": size_info.size, "unit_value": "cm"},  # 日本尺码
                ]
            }
            
            # 添加尺寸信息
            if "chest" in size_info.measurements:
                record["values"].append({
                    "id": 10002,
                    "value": size_info.measurements["chest"],
                    "unit_value": "cm"
                })
            
            if "length" in size_info.measurements:
                record["values"].append({
                    "id": 10003,
                    "value": size_info.measurements["length"],
                    "unit_value": "cm"
                })
            
            size_chart["records"].append(record)
        
        return [size_chart]


class SizeChartValidator:
    """尺码表验证器"""
    
    def __init__(self):
        self.logger = get_logger("size_chart_validator")
    
    def validate_size_chart(self, size_chart: List[Dict]) -> bool:
        """
        验证尺码表数据
        
        Args:
            size_chart: Temu API格式的尺码表
            
        Returns:
            bool: 是否有效
        """
        if not size_chart:
            return False
        
        try:
            # 检查基本结构
            chart = size_chart[0]
            if "classId" not in chart or "meta" not in chart or "records" not in chart:
                self.logger.error("尺码表结构不完整")
                return False
            
            # 检查meta结构
            meta = chart["meta"]
            if "groups" not in meta or "elements" not in meta:
                self.logger.error("尺码表meta结构不完整")
                return False
            
            # 检查records结构
            records = chart["records"]
            if not records:
                self.logger.error("尺码表records为空")
                return False
            
            # 检查每个record的结构
            for record in records:
                if "values" not in record:
                    self.logger.error("尺码表record缺少values")
                    return False
                
                values = record["values"]
                if not values:
                    self.logger.error("尺码表record values为空")
                    return False
                
                # 检查必要的字段
                has_size = any(v.get("id") == 1 for v in values)
                if not has_size:
                    self.logger.error("尺码表缺少尺码信息")
                    return False
            
            self.logger.info("尺码表验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"尺码表验证失败: {e}")
            return False


class SizeChartProcessor:
    """尺码表处理器 - 主要接口类"""
    
    def __init__(self):
        self.logger = get_logger("size_chart_processor")
        self.ocr_client = OCRClient()
        self.detector = SizeChartDetector()
        self.parser = SizeChartParser()
        self.generator = SizeChartGenerator()
        self.validator = SizeChartValidator()
    
    def process_size_chart_from_image(self, image_path: Path, cat_type: int) -> Optional[List[Dict]]:
        """
        从图片中处理尺码表
        
        Args:
            image_path: 图片路径
            cat_type: 商品分类类型
            
        Returns:
            List[Dict]: Temu API格式的尺码表，如果不需要则返回None
        """
        try:
            self.logger.info(f"开始处理尺码表: {image_path}")
            
            # OCR识别
            has_chinese, ocr_texts = self.ocr_client.recognize_text(str(image_path))
            ocr_text = " ".join(ocr_texts)
            
            if not ocr_text:
                self.logger.warning("OCR识别结果为空")
                return None
            
            # 检测尺码表
            if not self.detector.detect_size_chart(ocr_text):
                self.logger.info("未检测到尺码表")
                return None
            
            # 解析尺码表
            size_chart_data = self.parser.parse_size_chart(ocr_text)
            
            if not size_chart_data.has_size_chart:
                self.logger.info("解析后未发现尺码表")
                return None
            
            # 生成Temu格式
            temu_size_chart = self.generator.generate_temu_size_chart(size_chart_data, cat_type)
            
            if not temu_size_chart:
                return None
            
            # 验证尺码表
            if not self.validator.validate_size_chart(temu_size_chart):
                self.logger.error("尺码表验证失败")
                return None
            
            self.logger.info(f"尺码表处理成功，尺码数量: {len(size_chart_data.size_infos)}")
            return temu_size_chart
            
        except Exception as e:
            self.logger.error(f"尺码表处理失败: {e}")
            return None
    
    def process_size_chart_from_text(self, ocr_text: str, cat_type: int) -> Optional[List[Dict]]:
        """
        从OCR文本中处理尺码表
        
        Args:
            ocr_text: OCR识别的文本
            cat_type: 商品分类类型
            
        Returns:
            List[Dict]: Temu API格式的尺码表，如果不需要则返回None
        """
        try:
            self.logger.info("开始从文本处理尺码表")
            
            # 检测尺码表
            if not self.detector.detect_size_chart(ocr_text):
                self.logger.info("未检测到尺码表")
                return None
            
            # 解析尺码表
            size_chart_data = self.parser.parse_size_chart(ocr_text)
            
            if not size_chart_data.has_size_chart:
                self.logger.info("解析后未发现尺码表")
                return None
            
            # 生成Temu格式
            temu_size_chart = self.generator.generate_temu_size_chart(size_chart_data, cat_type)
            
            if not temu_size_chart:
                return None
            
            # 验证尺码表
            if not self.validator.validate_size_chart(temu_size_chart):
                self.logger.error("尺码表验证失败")
                return None
            
            self.logger.info(f"尺码表处理成功，尺码数量: {len(size_chart_data.size_infos)}")
            return temu_size_chart
            
        except Exception as e:
            self.logger.error(f"尺码表处理失败: {e}")
            return None


# 便捷函数
def process_size_chart_from_image(image_path: Path, cat_type: int) -> Optional[List[Dict]]:
    """
    从图片中处理尺码表的便捷函数
    
    Args:
        image_path: 图片路径
        cat_type: 商品分类类型
        
    Returns:
        List[Dict]: Temu API格式的尺码表，如果不需要则返回None
    """
    processor = SizeChartProcessor()
    return processor.process_size_chart_from_image(image_path, cat_type)


def process_size_chart_from_text(ocr_text: str, cat_type: int) -> Optional[List[Dict]]:
    """
    从OCR文本中处理尺码表的便捷函数
    
    Args:
        ocr_text: OCR识别的文本
        cat_type: 商品分类类型
        
    Returns:
        List[Dict]: Temu API格式的尺码表，如果不需要则返回None
    """
    processor = SizeChartProcessor()
    return processor.process_size_chart_from_text(ocr_text, cat_type)


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python size_chart_processor.py <图片路径>")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    
    try:
        processor = SizeChartProcessor()
        size_chart = processor.process_size_chart_from_image(image_path, 0)  # 服装类
        
        if size_chart:
            print("尺码表处理成功:")
            print(json.dumps(size_chart, indent=2, ensure_ascii=False))
        else:
            print("未检测到尺码表或处理失败")
        
    except Exception as e:
        print(f"尺码表处理失败: {e}")
        sys.exit(1)

