"""
图片处理模块测试
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
from PIL import Image

from src.image.image_processor import ImageProcessor
from src.image.ocr_client import OCRClient
from src.utils.exceptions import ImageProcessingError


class TestImageProcessor:
    """图片处理器测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建模拟的OCR客户端
        self.mock_ocr_client = Mock(spec=OCRClient)
        
        # 创建图片处理器实例
        with patch('src.image.image_processor.get_config') as mock_config:
            mock_config.return_value.image_save_path = str(self.temp_path)
            self.processor = ImageProcessor(ocr_client=self.mock_ocr_client)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """测试初始化"""
        assert self.processor.ocr_client == self.mock_ocr_client
        assert self.processor.image_save_path == self.temp_path
        assert self.processor.supported_formats == {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}

    def test_is_chinese_text(self):
        """测试中文字符检测"""
        # 包含中文
        assert self.processor.is_chinese_text("Hello 世界") == True
        assert self.processor.is_chinese_text("测试") == True
        assert self.processor.is_chinese_text("商品详情") == True
        
        # 不包含中文
        assert self.processor.is_chinese_text("Hello World") == False
        assert self.processor.is_chinese_text("123456") == False
        assert self.processor.is_chinese_text("") == False

    def test_classify_image_type(self):
        """测试图片类型分类"""
        # 尺码图
        assert self.processor.classify_image_type("size_chart.jpg") == "size"
        assert self.processor.classify_image_type("sizing_guide.png") == "size"
        assert self.processor.classify_image_type("measurement.jpg") == "size"
        
        # 详情图
        assert self.processor.classify_image_type("detail_view.jpg") == "detail"
        assert self.processor.classify_image_type("closeup.png") == "detail"
        assert self.processor.classify_image_type("details.jpg") == "detail"
        
        # 主图
        assert self.processor.classify_image_type("main_image.jpg") == "main"
        assert self.processor.classify_image_type("primary.jpg") == "main"
        assert self.processor.classify_image_type("hero.png") == "main"
        
        # 其他
        assert self.processor.classify_image_type("random.jpg") == "other"
        assert self.processor.classify_image_type("image.png") == "other"

    def test_classify_image_type_with_url(self):
        """测试带URL的图片类型分类"""
        # 尺码图URL
        assert self.processor.classify_image_type("image.jpg", "https://example.com/size-chart") == "size"
        
        # 详情图URL
        assert self.processor.classify_image_type("image.jpg", "https://example.com/detail-view") == "detail"
        
        # 主图URL
        assert self.processor.classify_image_type("image.jpg", "https://example.com/main-image") == "main"

    @patch('requests.get')
    def test_download_image_success(self, mock_get):
        """测试成功下载图片"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 测试下载
        result_path = self.processor.download_image("https://example.com/image.jpg")
        
        # 验证结果
        assert result_path.exists()
        assert result_path.name == "image.jpg"
        mock_get.assert_called_once_with("https://example.com/image.jpg", timeout=30, stream=True)

    @patch('requests.get')
    def test_download_image_with_custom_filename(self, mock_get):
        """测试使用自定义文件名下载图片"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 测试下载
        result_path = self.processor.download_image("https://example.com/image.jpg", "custom.jpg")
        
        # 验证结果
        assert result_path.exists()
        assert result_path.name == "custom.jpg"

    @patch('requests.get')
    def test_download_image_http_error(self, mock_get):
        """测试下载图片HTTP错误"""
        # 模拟HTTP错误
        mock_get.side_effect = requests.RequestException("Network error")
        
        # 测试下载失败
        with pytest.raises(ImageProcessingError) as exc_info:
            self.processor.download_image("https://example.com/image.jpg")
        
        assert "下载图片失败" in str(exc_info.value)

    def test_check_image_for_chinese_with_chinese(self):
        """测试检测包含中文的图片"""
        # 模拟OCR返回包含中文的文本
        self.mock_ocr_client.recognize_text.return_value = "商品详情 测试"
        
        # 创建测试图片
        test_image = self.temp_path / "test.jpg"
        Image.new('RGB', (100, 100), color='white').save(test_image)
        
        # 测试检测
        has_chinese, text = self.processor.check_image_for_chinese(test_image)
        
        # 验证结果
        assert has_chinese == True
        assert text == "商品详情 测试"
        self.mock_ocr_client.recognize_text.assert_called_once_with(str(test_image))

    def test_check_image_for_chinese_without_chinese(self):
        """测试检测不包含中文的图片"""
        # 模拟OCR返回不包含中文的文本
        self.mock_ocr_client.recognize_text.return_value = "Product Details Test"
        
        # 创建测试图片
        test_image = self.temp_path / "test.jpg"
        Image.new('RGB', (100, 100), color='white').save(test_image)
        
        # 测试检测
        has_chinese, text = self.processor.check_image_for_chinese(test_image)
        
        # 验证结果
        assert has_chinese == False
        assert text == "Product Details Test"

    def test_check_image_for_chinese_ocr_error(self):
        """测试OCR识别错误时的处理"""
        # 模拟OCR抛出异常
        self.mock_ocr_client.recognize_text.side_effect = Exception("OCR error")
        
        # 创建测试图片
        test_image = self.temp_path / "test.jpg"
        Image.new('RGB', (100, 100), color='white').save(test_image)
        
        # 测试检测
        has_chinese, text = self.processor.check_image_for_chinese(test_image)
        
        # 验证结果（OCR失败时假设不包含中文）
        assert has_chinese == False
        assert text == ""

    @patch('requests.get')
    def test_process_images_success(self, mock_get):
        """测试批量处理图片成功"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 模拟OCR返回不包含中文的文本
        self.mock_ocr_client.recognize_text.return_value = "Product Details"
        
        # 测试图片URL列表
        image_urls = [
            "https://example.com/main.jpg",
            "https://example.com/size.jpg",
            "https://example.com/detail.jpg"
        ]
        
        # 处理图片
        result = self.processor.process_images(image_urls)
        
        # 验证结果
        assert len(result['main']) == 1
        assert len(result['size']) == 1
        assert len(result['detail']) == 1
        assert len(result['other']) == 0
        assert len(result['filtered']) == 0

    @patch('requests.get')
    def test_process_images_with_chinese_filter(self, mock_get):
        """测试批量处理图片并过滤中文"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 模拟OCR返回包含中文的文本
        self.mock_ocr_client.recognize_text.return_value = "商品详情"
        
        # 测试图片URL列表
        image_urls = ["https://example.com/chinese.jpg"]
        
        # 处理图片
        result = self.processor.process_images(image_urls)
        
        # 验证结果
        assert len(result['main']) == 0
        assert len(result['size']) == 0
        assert len(result['detail']) == 0
        assert len(result['other']) == 0
        assert len(result['filtered']) == 1

    def test_get_image_info(self):
        """测试获取图片信息"""
        # 创建测试图片
        test_image = self.temp_path / "test.jpg"
        img = Image.new('RGB', (100, 100), color='white')
        img.save(test_image)
        
        # 获取图片信息
        info = self.processor.get_image_info(test_image)
        
        # 验证结果
        assert info['path'] == str(test_image)
        assert info['filename'] == "test.jpg"
        assert info['format'] == "JPEG"
        assert info['mode'] == "RGB"
        assert info['size'] == (100, 100)
        assert info['width'] == 100
        assert info['height'] == 100
        assert 'file_size' in info

    def test_get_image_info_error(self):
        """测试获取图片信息错误"""
        # 使用不存在的文件
        test_image = self.temp_path / "nonexistent.jpg"
        
        # 获取图片信息
        info = self.processor.get_image_info(test_image)
        
        # 验证结果
        assert info['path'] == str(test_image)
        assert info['filename'] == "nonexistent.jpg"
        assert 'error' in info

    def test_validate_image_requirements_valid(self):
        """测试验证符合要求的图片"""
        # 创建符合要求的测试图片 (3:4比例，大于最小尺寸)
        test_image = self.temp_path / "valid.jpg"
        img = Image.new('RGB', (1500, 2000), color='white')  # 3:4比例，大于1340x1785
        img.save(test_image)
        
        # 验证图片
        result = self.processor.validate_image_requirements([test_image])
        
        # 验证结果
        assert len(result['valid']) == 1
        assert len(result['invalid']) == 0

    def test_validate_image_requirements_invalid_size(self):
        """测试验证尺寸不符合要求的图片"""
        # 创建尺寸不符合要求的测试图片
        test_image = self.temp_path / "invalid_size.jpg"
        img = Image.new('RGB', (100, 100), color='white')  # 小于最小尺寸
        img.save(test_image)
        
        # 验证图片
        result = self.processor.validate_image_requirements([test_image])
        
        # 验证结果
        assert len(result['valid']) == 0
        assert len(result['invalid']) == 1

    def test_validate_image_requirements_invalid_ratio(self):
        """测试验证宽高比不符合要求的图片"""
        # 创建宽高比不符合要求的测试图片
        test_image = self.temp_path / "invalid_ratio.jpg"
        img = Image.new('RGB', (2000, 1000), color='white')  # 2:1比例，不符合3:4
        img.save(test_image)
        
        # 验证图片
        result = self.processor.validate_image_requirements([test_image])
        
        # 验证结果
        assert len(result['valid']) == 0
        assert len(result['invalid']) == 1

    def test_cleanup_temp_images(self):
        """测试清理临时图片"""
        # 创建临时图片
        temp_image1 = self.temp_path / "temp1.jpg"
        temp_image2 = self.temp_path / "temp2.jpg"
        Image.new('RGB', (100, 100), color='white').save(temp_image1)
        Image.new('RGB', (100, 100), color='white').save(temp_image2)
        
        # 验证图片存在
        assert temp_image1.exists()
        assert temp_image2.exists()
        
        # 清理图片
        self.processor.cleanup_temp_images([temp_image1, temp_image2])
        
        # 验证图片已删除
        assert not temp_image1.exists()
        assert not temp_image2.exists()
