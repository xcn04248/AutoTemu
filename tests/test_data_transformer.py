"""
数据转换模块测试
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.transform.data_transformer import DataTransformer, TransformResult
from src.transform.size_mapper import SizeMapper, SizeType
from src.models.product import ScrapedProduct, TemuProduct, TemuSKU


class TestDataTransformer:
    """数据转换器测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.transformer = DataTransformer()

    def test_init(self):
        """测试初始化"""
        assert self.transformer is not None
        assert self.transformer.size_mapper is not None
        assert self.transformer.price_markup == 1.3

    def test_clean_title(self):
        """测试清理标题"""
        # 基本清理
        assert self.transformer._clean_title("  Test  Title  ") == "Test Title"
        
        # 特殊字符清理
        assert self.transformer._clean_title("Test@#$%Title") == "TestTitle"
        
        # 长度限制
        long_title = "A" * 250
        cleaned = self.transformer._clean_title(long_title)
        assert len(cleaned) == 200
        assert cleaned.endswith("...")
        
        # 空标题
        assert self.transformer._clean_title("") == ""
        assert self.transformer._clean_title(None) == ""

    def test_clean_description(self):
        """测试清理描述"""
        # HTML标签清理
        html_desc = "<p>Test <b>description</b></p>"
        assert self.transformer._clean_description(html_desc) == "Test description"
        
        # 特殊字符清理
        special_desc = "Test@#$%description"
        assert self.transformer._clean_description(special_desc) == "Testdescription"
        
        # 长度限制
        long_desc = "A" * 2500
        cleaned = self.transformer._clean_description(long_desc)
        assert len(cleaned) == 2000
        assert cleaned.endswith("...")
        
        # 空描述
        assert self.transformer._clean_description("") == ""
        assert self.transformer._clean_description(None) == ""

    def test_validate_scraped_product_valid(self):
        """测试验证有效的爬取商品数据"""
        product = ScrapedProduct(
            title="Test Product",
            price=100.0,
            description="Test description",
            images=["image1.jpg", "image2.jpg"],
            sizes=["S", "M", "L"],
            url="https://example.com/product"
        )
        
        result = TransformResult(success=False)
        self.transformer._validate_scraped_product(product, result)
        
        assert result.success == True
        assert len(result.errors) == 0

    def test_validate_scraped_product_invalid_title(self):
        """测试验证无效标题的爬取商品数据"""
        # 创建有效的数据对象，然后修改属性
        product = ScrapedProduct(
            title="Valid Title",
            price=100.0,
            description="Test description",
            images=["image1.jpg"],
            sizes=["S"],
            url="https://example.com/product"
        )
        product.title = ""  # 修改为无效标题
        
        result = TransformResult(success=False)
        self.transformer._validate_scraped_product(product, result)
        
        assert result.success == False
        assert "商品标题不能为空" in result.errors

    def test_validate_scraped_product_invalid_price(self):
        """测试验证无效价格的爬取商品数据"""
        # 创建有效的数据对象，然后修改属性
        product = ScrapedProduct(
            title="Test Product",
            price=100.0,
            description="Test description",
            images=["image1.jpg"],
            sizes=["S"],
            url="https://example.com/product"
        )
        product.price = 0  # 修改为无效价格
        
        result = TransformResult(success=False)
        self.transformer._validate_scraped_product(product, result)
        
        assert result.success == False
        assert "商品价格必须大于0" in result.errors

    def test_validate_scraped_product_warnings(self):
        """测试验证带警告的爬取商品数据"""
        product = ScrapedProduct(
            title="Test Product",
            price=100.0,
            description="",
            images=[],
            sizes=[],
            url="https://example.com/product"
        )
        
        result = TransformResult(success=False)
        self.transformer._validate_scraped_product(product, result)
        
        assert result.success == True  # 只有警告，没有错误
        assert len(result.warnings) == 3
        assert "商品描述为空" in result.warnings
        assert "商品图片为空" in result.warnings
        assert "商品尺码为空" in result.warnings

    def test_transform_basic_info(self):
        """测试转换基本信息"""
        product = ScrapedProduct(
            title="  Test@Product  ",
            price=100.0,
            description="<p>Test description</p>",
            images=["image1.jpg"],
            sizes=["S"],
            url="https://example.com/product",
            currency="JPY"
        )
        
        result = TransformResult(success=True)
        temu_product = self.transformer._transform_basic_info(product, result)
        
        assert temu_product.title == "TestProduct"
        assert temu_product.description == "Test description"
        assert temu_product.original_price == 100.0
        assert temu_product.markup_price == 130.0
        assert temu_product.currency == "JPY"
        assert temu_product.source_url == "https://example.com/product"

    def test_transform_skus(self):
        """测试转换SKU数据"""
        product = ScrapedProduct(
            title="Test Shirt",
            price=100.0,
            description="Test description",
            images=["image1.jpg"],
            sizes=["S", "M", "L"],
            url="https://example.com/product"
        )
        
        result = TransformResult(success=True)
        skus = self.transformer._transform_skus(product, result)
        
        assert len(skus) == 3
        assert all(sku.price == 130.0 for sku in skus)
        assert all(sku.sku_id.startswith("SKU_") for sku in skus)
        assert skus[0].size == "S"
        assert skus[1].size == "M"
        assert skus[2].size == "L"

    def test_transform_skus_no_valid_sizes(self):
        """测试转换SKU数据 - 无有效尺码"""
        product = ScrapedProduct(
            title="Test Product",
            price=100.0,
            description="Test description",
            images=["image1.jpg"],
            sizes=["INVALID_SIZE"],
            url="https://example.com/product"
        )
        
        result = TransformResult(success=True)
        skus = self.transformer._transform_skus(product, result)
        
        assert result.success == False
        assert "没有有效的SKU数据" in result.errors
        assert len(skus) == 0

    def test_transform_product_success(self):
        """测试成功转换商品"""
        product = ScrapedProduct(
            title="Test Shirt",
            price=100.0,
            description="Test description",
            images=["image1.jpg", "image2.jpg"],
            sizes=["S", "M", "L"],
            url="https://example.com/product",
            currency="JPY"
        )
        
        result = self.transformer.transform_product(product)
        
        assert result.success == True
        assert result.temu_product is not None
        assert len(result.skus) == 3
        assert len(result.errors) == 0

    def test_transform_product_failure(self):
        """测试转换商品失败"""
        # 创建有效的数据对象，然后修改属性
        product = ScrapedProduct(
            title="Valid Title",
            price=100.0,
            description="Test description",
            images=["image1.jpg"],
            sizes=["S"],
            url="https://example.com/product"
        )
        product.title = ""  # 修改为无效标题
        product.price = 0   # 修改为无效价格
        
        result = self.transformer.transform_product(product)
        
        assert result.success == False
        assert result.temu_product is None
        assert len(result.skus) == 0
        assert len(result.errors) > 0

    def test_validate_temu_product_valid(self):
        """测试验证有效的Temu商品"""
        product = TemuProduct(
            title="Test Product",
            description="Test description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["image1.jpg"],
            source_url="https://example.com/product"
        )
        
        is_valid, errors = self.transformer.validate_temu_product(product)
        
        assert is_valid == True
        assert len(errors) == 0

    def test_validate_temu_product_invalid_title(self):
        """测试验证无效标题的Temu商品"""
        # 创建有效的数据对象，然后修改属性
        product = TemuProduct(
            title="Valid Title",
            description="Test description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["image1.jpg"],
            source_url="https://example.com/product"
        )
        product.title = ""  # 修改为无效标题
        
        is_valid, errors = self.transformer.validate_temu_product(product)
        
        assert is_valid == False
        assert "商品标题不能为空" in errors

    def test_validate_temu_product_invalid_price(self):
        """测试验证无效价格的Temu商品"""
        # 创建有效的数据对象，然后修改属性
        product = TemuProduct(
            title="Test Product",
            description="Test description",
            original_price=100.0,
            markup_price=130.0,
            currency="JPY",
            size_type="clothing",
            images=["image1.jpg"],
            source_url="https://example.com/product"
        )
        product.markup_price = 0  # 修改为无效价格
        
        is_valid, errors = self.transformer.validate_temu_product(product)
        
        assert is_valid == False
        assert "商品价格必须大于0" in errors

    def test_validate_temu_sku_valid(self):
        """测试验证有效的Temu SKU"""
        sku = TemuSKU(
            sku_id="SKU_001",
            size="M",
            original_size="M",
            price=130.0,
            stock_quantity=100,
            images=["image1.jpg"]
        )
        
        is_valid, errors = self.transformer.validate_temu_sku(sku)
        
        assert is_valid == True
        assert len(errors) == 0

    def test_validate_temu_sku_invalid_id(self):
        """测试验证无效ID的Temu SKU"""
        # 创建有效的数据对象，然后修改属性
        sku = TemuSKU(
            sku_id="SKU_001",
            size="M",
            original_size="M",
            price=130.0,
            stock_quantity=100,
            images=["image1.jpg"]
        )
        sku.sku_id = ""  # 修改为无效ID
        
        is_valid, errors = self.transformer.validate_temu_sku(sku)
        
        assert is_valid == False
        assert "SKU ID不能为空" in errors

    def test_validate_temu_sku_invalid_price(self):
        """测试验证无效价格的Temu SKU"""
        # 创建有效的数据对象，然后修改属性
        sku = TemuSKU(
            sku_id="SKU_001",
            size="M",
            original_size="M",
            price=130.0,
            stock_quantity=100,
            images=["image1.jpg"]
        )
        sku.price = 0  # 修改为无效价格
        
        is_valid, errors = self.transformer.validate_temu_sku(sku)
        
        assert is_valid == False
        assert "SKU价格必须大于0" in errors

    def test_transform_images(self):
        """测试转换图片数据"""
        images = ["image1.jpg", "image2.jpg"]
        image_processor_result = {
            'main': ["path/to/main1.jpg"],
            'detail': ["path/to/detail1.jpg", "path/to/detail2.jpg"],
            'other': ["path/to/other1.jpg"]
        }
        
        processed_images = self.transformer.transform_images(images, image_processor_result)
        
        assert len(processed_images) == 4
        assert "path/to/main1.jpg" in processed_images
        assert "path/to/detail1.jpg" in processed_images
        assert "path/to/detail2.jpg" in processed_images
        assert "path/to/other1.jpg" in processed_images

    def test_get_transform_statistics(self):
        """测试获取转换统计信息"""
        # 创建测试结果
        results = [
            TransformResult(success=True, skus=[Mock(), Mock()]),  # 2个SKU
            TransformResult(success=True, skus=[Mock()]),  # 1个SKU
            TransformResult(success=False, errors=["Error 1"]),  # 失败
        ]
        
        stats = self.transformer.get_transform_statistics(results)
        
        assert stats['total'] == 3
        assert stats['successful'] == 2
        assert stats['failed'] == 1
        assert stats['success_rate'] == 2/3
        assert stats['total_skus'] == 3
        assert stats['average_skus_per_product'] == 1.5
        assert stats['total_errors'] == 1
        assert stats['total_warnings'] == 0

    def test_get_transform_statistics_empty(self):
        """测试空列表的转换统计信息"""
        stats = self.transformer.get_transform_statistics([])
        
        assert stats['total'] == 0
        assert stats['successful'] == 0
        assert stats['failed'] == 0
        assert stats['success_rate'] == 0.0
        assert stats['total_skus'] == 0
        assert stats['average_skus_per_product'] == 0.0
        assert stats['total_errors'] == 0
        assert stats['total_warnings'] == 0

    def test_batch_transform(self):
        """测试批量转换"""
        products = [
            ScrapedProduct(
                title="Product 1",
                price=100.0,
                description="Description 1",
                images=["image1.jpg"],
                sizes=["S", "M"],
                url="https://example.com/product1"
            ),
            ScrapedProduct(
                title="Product 2",
                price=200.0,
                description="Description 2",
                images=["image2.jpg"],
                sizes=["L", "XL"],
                url="https://example.com/product2"
            )
        ]
        
        results = self.transformer.batch_transform(products)
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all(len(result.skus) == 2 for result in results)

    def test_transform_result_creation(self):
        """测试TransformResult数据类"""
        result = TransformResult(
            success=True,
            temu_product=Mock(),
            skus=[Mock(), Mock()],
            errors=["Error 1"],
            warnings=["Warning 1"]
        )
        
        assert result.success == True
        assert result.temu_product is not None
        assert len(result.skus) == 2
        assert len(result.errors) == 1
        assert len(result.warnings) == 1

    def test_transform_result_post_init(self):
        """测试TransformResult的__post_init__方法"""
        result = TransformResult(success=True)
        
        assert result.skus == []
        assert result.errors == []
        assert result.warnings == []
