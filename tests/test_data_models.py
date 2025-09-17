"""
数据模型的单元测试
"""

import json
import pytest
from datetime import datetime

from src.models.data_models import (
    ProductStatus,
    ImageStatus,
    SizeInfo,
    ImageInfo,
    ProductData,
    ProcessedImages,
    TemuSKU,
    TemuProductData,
    CreateProductResult,
    ProcessingResult,
    SIZE_MAPPING,
    normalize_size
)


class TestEnums:
    """枚举类测试"""
    
    def test_product_status_enum(self):
        """测试商品状态枚举"""
        assert ProductStatus.SCRAPED.value == "scraped"
        assert ProductStatus.SUCCESS.value == "success"
        assert ProductStatus.FAILED.value == "failed"
    
    def test_image_status_enum(self):
        """测试图片状态枚举"""
        assert ImageStatus.PENDING.value == "pending"
        assert ImageStatus.PASSED.value == "passed"
        assert ImageStatus.REJECTED.value == "rejected"


class TestSizeInfo:
    """尺码信息测试"""
    
    def test_size_info_creation(self):
        """测试尺码信息创建"""
        size = SizeInfo(
            size_name="M",
            size_image_url="https://example.com/m.jpg",
            measurements={"chest": 100, "length": 70}
        )
        
        assert size.size_name == "M"
        assert size.size_image_url == "https://example.com/m.jpg"
        assert size.measurements["chest"] == 100
    
    def test_size_info_to_dict(self):
        """测试尺码信息转字典"""
        size = SizeInfo(size_name="L")
        data = size.to_dict()
        
        assert data["size_name"] == "L"
        assert data["size_image_url"] is None
        assert data["measurements"] is None


class TestImageInfo:
    """图片信息测试"""
    
    def test_image_info_creation(self):
        """测试图片信息创建"""
        image = ImageInfo(
            url="https://example.com/image.jpg",
            local_path="/tmp/image.jpg",
            status=ImageStatus.DOWNLOADED,
            width=800,
            height=600
        )
        
        assert image.url == "https://example.com/image.jpg"
        assert image.status == ImageStatus.DOWNLOADED
        assert image.width == 800
    
    def test_image_info_to_dict(self):
        """测试图片信息转字典"""
        image = ImageInfo(url="https://example.com/image.jpg")
        data = image.to_dict()
        
        assert data["url"] == "https://example.com/image.jpg"
        assert data["status"] == "pending"
        assert data["local_path"] is None
    
    def test_image_info_from_dict(self):
        """测试从字典创建图片信息"""
        data = {
            "url": "https://example.com/image.jpg",
            "status": "passed",
            "has_chinese": False
        }
        
        image = ImageInfo.from_dict(data)
        
        assert image.url == "https://example.com/image.jpg"
        assert image.status == ImageStatus.PASSED
        assert image.has_chinese is False


class TestProductData:
    """商品数据测试"""
    
    def test_product_data_creation(self):
        """测试商品数据创建"""
        product = ProductData(
            url="https://example.com/product",
            name="测试商品",
            price=100.0,
            description="这是一个测试商品",
            main_image_url="https://example.com/main.jpg",
            detail_images=["https://example.com/detail1.jpg"],
            sizes=[SizeInfo(size_name="M")]
        )
        
        assert product.name == "测试商品"
        assert product.price == 100.0
        assert len(product.sizes) == 1
        assert product.sizes[0].size_name == "M"
    
    def test_product_data_to_dict(self):
        """测试商品数据转字典"""
        product = ProductData(
            url="https://example.com/product",
            name="商品",
            price=100,
            description="描述",
            main_image_url="https://example.com/main.jpg"
        )
        
        data = product.to_dict()
        
        assert data["name"] == "商品"
        assert data["price"] == 100
        assert isinstance(data["scraped_at"], str)  # 时间转为字符串
    
    def test_product_data_json_serialization(self):
        """测试商品数据JSON序列化"""
        product = ProductData(
            url="https://example.com/product",
            name="商品",
            price=100,
            description="描述",
            main_image_url="https://example.com/main.jpg",
            sizes=[SizeInfo(size_name="S"), SizeInfo(size_name="M")]
        )
        
        # 转为JSON
        json_str = product.to_json()
        
        # 从JSON恢复
        restored = ProductData.from_json(json_str)
        
        assert restored.name == product.name
        assert restored.price == product.price
        assert len(restored.sizes) == 2
        assert restored.sizes[0].size_name == "S"


class TestProcessedImages:
    """处理后图片集合测试"""
    
    def test_processed_images_creation(self):
        """测试处理后图片集合创建"""
        images = ProcessedImages()
        
        assert images.main_image is None
        assert len(images.detail_images) == 0
        assert images.total_count == 0
    
    def test_add_images(self):
        """测试添加图片"""
        images = ProcessedImages()
        
        # 添加主图
        main = ImageInfo(url="main.jpg", status=ImageStatus.PASSED)
        images.main_image = main
        images._update_counts()
        
        # 添加详情图
        detail = ImageInfo(url="detail.jpg", status=ImageStatus.REJECTED)
        images.add_detail_image(detail)
        
        # 添加尺码图
        size_img = ImageInfo(url="size.jpg", status=ImageStatus.PASSED)
        images.add_size_image("M", size_img)
        
        assert images.total_count == 3
        assert images.passed_count == 2
        assert images.rejected_count == 1
    
    def test_get_valid_images(self):
        """测试获取有效图片"""
        images = ProcessedImages()
        
        # 添加不同状态的图片
        images.main_image = ImageInfo(url="main.jpg", status=ImageStatus.PASSED)
        images.add_detail_image(ImageInfo(url="detail1.jpg", status=ImageStatus.REJECTED))
        images.add_detail_image(ImageInfo(url="detail2.jpg", status=ImageStatus.PROCESSED))
        
        valid = images.get_valid_images()
        
        assert len(valid) == 2  # 只有PASSED和PROCESSED的图片
        assert valid[0].url == "main.jpg"
        assert valid[1].url == "detail2.jpg"


class TestTemuSKU:
    """Temu SKU测试"""
    
    def test_temu_sku_creation(self):
        """测试Temu SKU创建"""
        sku = TemuSKU(
            spec_list=[{"specId": 123, "specValue": "M"}],
            sku_price=130.0,
            sku_quantity=100
        )
        
        assert sku.spec_list[0]["specValue"] == "M"
        assert sku.sku_price == 130.0
        assert sku.sku_quantity == 100


class TestTemuProductData:
    """Temu商品数据测试"""
    
    def test_temu_product_data_creation(self):
        """测试Temu商品数据创建"""
        product = TemuProductData(
            goods_name="测试商品",
            cat_id=12345,
            hd_thumb_url="https://example.com/thumb.jpg",
            carousel_image_list=["https://example.com/1.jpg"],
            sku_list=[TemuSKU(sku_price=130.0)]
        )
        
        assert product.goods_name == "测试商品"
        assert product.cat_id == 12345
        assert len(product.sku_list) == 1
    
    def test_to_api_format(self):
        """测试转换为API格式"""
        product = TemuProductData(
            goods_name="商品",
            cat_id=12345,
            hd_thumb_url="https://example.com/thumb.jpg",
            goods_desc="描述",
            bullet_points=["卖点1", "卖点2"]
        )
        
        api_data = product.to_api_format()
        
        assert api_data["goodsBasic"]["goodsName"] == "商品"
        assert api_data["goodsBasic"]["catId"] == 12345
        assert api_data["bulletPoints"] == ["卖点1", "卖点2"]
        assert "goodsServicePromise" in api_data


class TestCreateProductResult:
    """商品创建结果测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = CreateProductResult(
            success=True,
            goods_id=123456,
            sku_ids=[1, 2, 3]
        )
        
        assert result.success is True
        assert result.goods_id == 123456
        assert len(result.sku_ids) == 3
        assert result.error_code is None
    
    def test_failed_result(self):
        """测试失败结果"""
        result = CreateProductResult(
            success=False,
            error_code="GOODS_001",
            error_message="商品名称重复"
        )
        
        assert result.success is False
        assert result.goods_id is None
        assert result.error_code == "GOODS_001"


class TestProcessingResult:
    """处理结果测试"""
    
    def test_processing_result_creation(self):
        """测试处理结果创建"""
        result = ProcessingResult(
            product_url="https://example.com/product",
            status=ProductStatus.PROCESSING
        )
        
        assert result.product_url == "https://example.com/product"
        assert result.status == ProductStatus.PROCESSING
        assert result.start_time is not None
        assert result.end_time is None
    
    def test_mark_completed(self):
        """测试标记完成"""
        result = ProcessingResult(
            product_url="https://example.com/product",
            status=ProductStatus.SUCCESS
        )
        
        # 等待一小段时间
        import time
        time.sleep(0.1)
        
        result.mark_completed()
        
        assert result.end_time is not None
        assert result.duration_seconds > 0
    
    def test_to_dict(self):
        """测试转字典"""
        result = ProcessingResult(
            product_url="https://example.com/product",
            status=ProductStatus.FAILED,
            error_message="网络错误"
        )
        
        data = result.to_dict()
        
        assert data["product_url"] == "https://example.com/product"
        assert data["status"] == "failed"
        assert data["error_message"] == "网络错误"


class TestSizeMapping:
    """尺码映射测试"""
    
    def test_size_mapping_data(self):
        """测试尺码映射数据"""
        assert SIZE_MAPPING['S']['temu_size'] == 'S'
        assert SIZE_MAPPING['XXL']['temu_size'] == '2XL'
        assert SIZE_MAPPING['F']['temu_size'] == 'FREE'
        assert SIZE_MAPPING['38']['temu_size'] == 'S'
    
    def test_normalize_size(self):
        """测试尺码标准化"""
        # 标准尺码
        assert normalize_size('s') == 'S'
        assert normalize_size('M') == 'M'
        assert normalize_size(' L ') == 'L'
        
        # 特殊映射
        assert normalize_size('XXL') == '2XL'
        assert normalize_size('XXXL') == '3XL'
        assert normalize_size('F') == 'FREE'
        
        # 数字尺码
        assert normalize_size('38') == 'S'
        assert normalize_size('40') == 'M'
        
        # 未知尺码
        assert normalize_size('UNKNOWN') == 'UNKNOWN'
