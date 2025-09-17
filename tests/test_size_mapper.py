"""
尺码映射模块测试
"""

import pytest
from src.transform.size_mapper import SizeMapper, SizeType, SizeInfo


class TestSizeMapper:
    """尺码映射器测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.mapper = SizeMapper()

    def test_init(self):
        """测试初始化"""
        assert self.mapper is not None
        assert len(self.mapper.clothing_size_map) > 0
        assert len(self.mapper.shoes_size_map) > 0
        assert len(self.mapper.accessories_size_map) > 0

    def test_detect_size_type_clothing(self):
        """测试检测服装尺码类型"""
        # 英文关键词
        assert self.mapper.detect_size_type("T-Shirt") == SizeType.CLOTHING
        assert self.mapper.detect_size_type("Dress") == SizeType.CLOTHING
        assert self.mapper.detect_size_type("Jeans") == SizeType.CLOTHING
        
        # 中文关键词
        assert self.mapper.detect_size_type("衬衫") == SizeType.CLOTHING
        assert self.mapper.detect_size_type("连衣裙") == SizeType.CLOTHING
        assert self.mapper.detect_size_type("裤子") == SizeType.CLOTHING

    def test_detect_size_type_shoes(self):
        """测试检测鞋子尺码类型"""
        # 英文关键词
        assert self.mapper.detect_size_type("Sneakers") == SizeType.SHOES
        assert self.mapper.detect_size_type("Boots") == SizeType.SHOES
        assert self.mapper.detect_size_type("Heels") == SizeType.SHOES
        
        # 中文关键词
        assert self.mapper.detect_size_type("运动鞋") == SizeType.SHOES
        assert self.mapper.detect_size_type("靴子") == SizeType.SHOES
        assert self.mapper.detect_size_type("高跟鞋") == SizeType.SHOES

    def test_detect_size_type_accessories(self):
        """测试检测配饰尺码类型"""
        # 英文关键词
        assert self.mapper.detect_size_type("Hat") == SizeType.ACCESSORIES
        assert self.mapper.detect_size_type("Belt") == SizeType.ACCESSORIES
        assert self.mapper.detect_size_type("Watch") == SizeType.ACCESSORIES
        
        # 中文关键词
        assert self.mapper.detect_size_type("帽子") == SizeType.ACCESSORIES
        assert self.mapper.detect_size_type("腰带") == SizeType.ACCESSORIES
        assert self.mapper.detect_size_type("手表") == SizeType.ACCESSORIES

    def test_detect_size_type_unknown(self):
        """测试检测未知尺码类型"""
        assert self.mapper.detect_size_type("Unknown Product") == SizeType.UNKNOWN
        assert self.mapper.detect_size_type("Random Item") == SizeType.UNKNOWN

    def test_normalize_size(self):
        """测试尺码标准化"""
        # 基本标准化
        assert self.mapper.normalize_size("  S  ") == "S"
        assert self.mapper.normalize_size("m") == "M"
        assert self.mapper.normalize_size("XL") == "XL"
        
        # 去除单位
        assert self.mapper.normalize_size("80cm") == "80"
        assert self.mapper.normalize_size("36 inch") == "36"
        assert self.mapper.normalize_size("42mm") == "42"
        
        # 去除多余空格
        assert self.mapper.normalize_size("  L  L  ") == "L L"
        
        # 空字符串
        assert self.mapper.normalize_size("") == ""
        assert self.mapper.normalize_size("   ") == ""

    def test_map_clothing_size_direct_match(self):
        """测试服装尺码直接匹配"""
        # 字母尺码
        size_info = self.mapper.map_size("S", SizeType.CLOTHING)
        assert size_info.mapped_size == "S"
        assert size_info.confidence == 1.0
        
        # 数字尺码
        size_info = self.mapper.map_size("2", SizeType.CLOTHING)
        assert size_info.mapped_size == "M"
        assert size_info.confidence == 1.0
        
        # 腰围尺码
        size_info = self.mapper.map_size("70", SizeType.CLOTHING)
        assert size_info.mapped_size == "M"
        assert size_info.confidence == 1.0

    def test_map_clothing_size_fuzzy_match(self):
        """测试服装尺码模糊匹配"""
        # 包含匹配
        size_info = self.mapper.map_size("Size S", SizeType.CLOTHING)
        assert size_info.mapped_size == "S"
        assert size_info.confidence == 0.8

    def test_map_shoes_size_direct_match(self):
        """测试鞋子尺码直接匹配"""
        # 数字尺码
        size_info = self.mapper.map_size("38", SizeType.SHOES)
        assert size_info.mapped_size == "38"
        assert size_info.confidence == 1.0
        
        # 英国尺码
        size_info = self.mapper.map_size("6", SizeType.SHOES)
        assert size_info.mapped_size == "38"
        assert size_info.confidence == 1.0

    def test_map_shoes_size_range_match(self):
        """测试鞋子尺码范围匹配"""
        # 在范围内的数字
        size_info = self.mapper.map_size("39.5", SizeType.SHOES)
        assert size_info.mapped_size == "39.5"
        assert size_info.confidence == 1.0  # 直接匹配

    def test_map_accessories_size(self):
        """测试配饰尺码映射"""
        # 帽子尺码
        size_info = self.mapper.map_size("M", SizeType.ACCESSORIES)
        assert size_info.mapped_size == "M"
        assert size_info.confidence == 1.0
        
        # 腰带尺码
        size_info = self.mapper.map_size("85", SizeType.ACCESSORIES)
        assert size_info.mapped_size == "M"
        assert size_info.confidence == 1.0

    def test_map_unknown_size(self):
        """测试未知类型尺码映射"""
        # 尝试映射为服装尺码
        size_info = self.mapper.map_size("S", SizeType.UNKNOWN)
        assert size_info.mapped_size == "S"
        assert size_info.confidence == 0.7  # 降低的置信度

    def test_map_size_unmappable(self):
        """测试无法映射的尺码"""
        size_info = self.mapper.map_size("INVALID_SIZE", SizeType.CLOTHING)
        assert size_info.mapped_size is None
        assert size_info.confidence == 0.0
        assert "无法映射" in size_info.notes

    def test_map_size_empty(self):
        """测试空尺码"""
        size_info = self.mapper.map_size("", SizeType.CLOTHING)
        assert size_info.mapped_size is None
        assert size_info.confidence == 0.0
        assert "空尺码" in size_info.notes

    def test_batch_map_sizes(self):
        """测试批量映射尺码"""
        sizes = ["S", "M", "L", "INVALID"]
        size_infos = self.mapper.batch_map_sizes(sizes, SizeType.CLOTHING)
        
        assert len(size_infos) == 4
        assert size_infos[0].mapped_size == "S"
        assert size_infos[1].mapped_size == "M"
        assert size_infos[2].mapped_size == "L"
        assert size_infos[3].mapped_size is None

    def test_get_size_chart_elements(self):
        """测试获取尺码表元素"""
        # 服装尺码表元素
        elements = self.mapper.get_size_chart_elements(SizeType.CLOTHING)
        assert 'chest' in elements
        assert 'waist' in elements
        
        # 鞋子尺码表元素
        elements = self.mapper.get_size_chart_elements(SizeType.SHOES)
        assert 'length' in elements
        assert 'width' in elements
        
        # 配饰尺码表元素
        elements = self.mapper.get_size_chart_elements(SizeType.ACCESSORIES)
        assert 'circumference' in elements
        
        # 未知类型
        elements = self.mapper.get_size_chart_elements(SizeType.UNKNOWN)
        assert 'size' in elements

    def test_validate_size_mapping(self):
        """测试验证尺码映射"""
        # 有效映射
        valid_info = SizeInfo("S", SizeType.CLOTHING, "S", confidence=0.9)
        assert self.mapper.validate_size_mapping(valid_info) == True
        
        # 无效映射 - 无映射结果
        invalid_info = SizeInfo("INVALID", SizeType.CLOTHING, None, confidence=0.0)
        assert self.mapper.validate_size_mapping(invalid_info) == False
        
        # 无效映射 - 置信度过低
        low_confidence_info = SizeInfo("S", SizeType.CLOTHING, "S", confidence=0.3)
        assert self.mapper.validate_size_mapping(low_confidence_info) == False

    def test_get_mapping_statistics(self):
        """测试获取映射统计信息"""
        size_infos = [
            SizeInfo("S", SizeType.CLOTHING, "S", confidence=1.0),
            SizeInfo("M", SizeType.CLOTHING, "M", confidence=0.9),
            SizeInfo("INVALID", SizeType.CLOTHING, None, confidence=0.0),
        ]
        
        stats = self.mapper.get_mapping_statistics(size_infos)
        
        assert stats['total'] == 3
        assert stats['mapped'] == 2
        assert stats['unmapped'] == 1
        assert stats['success_rate'] == 2/3
        assert stats['average_confidence'] == 0.95
        assert stats['type_distribution']['clothing'] == 3

    def test_get_mapping_statistics_empty(self):
        """测试空列表的映射统计信息"""
        stats = self.mapper.get_mapping_statistics([])
        
        assert stats['total'] == 0
        assert stats['mapped'] == 0
        assert stats['unmapped'] == 0
        assert stats['success_rate'] == 0.0
        assert stats['average_confidence'] == 0.0
        assert stats['type_distribution'] == {}

    def test_size_info_creation(self):
        """测试SizeInfo数据类"""
        size_info = SizeInfo(
            original_size="S",
            size_type=SizeType.CLOTHING,
            mapped_size="S",
            confidence=1.0,
            notes="Test"
        )
        
        assert size_info.original_size == "S"
        assert size_info.size_type == SizeType.CLOTHING
        assert size_info.mapped_size == "S"
        assert size_info.confidence == 1.0
        assert size_info.notes == "Test"

    def test_size_type_enum(self):
        """测试SizeType枚举"""
        assert SizeType.CLOTHING.value == "clothing"
        assert SizeType.SHOES.value == "shoes"
        assert SizeType.ACCESSORIES.value == "accessories"
        assert SizeType.UNKNOWN.value == "unknown"
