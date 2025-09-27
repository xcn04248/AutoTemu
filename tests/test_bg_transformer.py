"""
BgTransformer 单元测试
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.transform.bg_transformer import BgTransformer
from src.models.product import ScrapedProduct
from src.models.bg_models import BgGoodsAddRequest


class TestBgTransformer:
    """BgTransformer测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.size_mapper = Mock()
        self.transformer = BgTransformer(self.size_mapper)
        
        # 模拟环境变量
        with patch.dict(os.environ, {
            'PRICE_MARKUP': '1.3',
            'TEMU_CNY_TO_JPY_RATE': '20.0',
            'DEFAULT_PARENT_SPEC_ID': '3001',
            'DEFAULT_WAREHOUSE_ID': 'WHS-TEST',
            'DEFAULT_SKU_STOCK': '100',
            'PRODUCT_NAME_MAX_LENGTH': '250'
        }):
            self.transformer = BgTransformer(self.size_mapper)
    
    def test_init(self):
        """测试初始化"""
        assert self.transformer.size_mapper == self.size_mapper
        assert self.transformer.price_markup == 1.3
        assert self.transformer.cny_to_jpy_rate == 20.0
    
    def test_clean_title(self):
        """测试标题清理"""
        # 测试正常标题
        title = "Premium Cotton T-Shirt"
        cleaned = self.transformer._clean_title(title)
        assert cleaned == "Premium Cotton T-Shirt"
        
        # 测试包含特殊字符的标题
        title = "T恤，高品质，100%棉质"
        cleaned = self.transformer._clean_title(title)
        assert cleaned == "T恤,高品质,100%棉质"
        
        # 测试超长标题
        long_title = "A" * 300
        cleaned = self.transformer._clean_title(long_title)
        assert len(cleaned) <= 250
        assert cleaned.endswith("...")
        
        # 测试空标题
        cleaned = self.transformer._clean_title("")
        assert cleaned == ""
    
    def test_get_category_ids(self):
        """测试分类ID提取"""
        # 测试正常分类信息
        category_info = {
            "catIdList": [1, 2, 3, 4]
        }
        cat_ids = self.transformer._get_category_ids(category_info)
        
        assert cat_ids['cat1Id'] == 1
        assert cat_ids['cat2Id'] == 2
        assert cat_ids['cat3Id'] == 3
        assert cat_ids['cat4Id'] == 4
        
        # 测试空分类信息
        category_info = {"catIdList": []}
        with patch.dict(os.environ, {
            'DEFAULT_CAT1_ID': '100',
            'DEFAULT_CAT2_ID': '200',
            'DEFAULT_CAT3_ID': '300'
        }):
            cat_ids = self.transformer._get_category_ids(category_info)
            assert cat_ids['cat1Id'] == 100
            assert cat_ids['cat2Id'] == 200
            assert cat_ids['cat3Id'] == 300
    
    def test_build_product_property_reqs(self):
        """测试产品属性构建"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        property_template = {
            "properties": [
                {
                    "required": True,
                    "templatePid": 1,
                    "pid": 1,
                    "refPid": 1,
                    "name": "颜色",
                    "values": [{"vid": 1, "value": "黑色"}]
                },
                {
                    "required": True,
                    "templatePid": 2,
                    "pid": 2,
                    "refPid": 2,
                    "name": "材质",
                    "values": [{"vid": 2, "value": "棉质"}]
                }
            ]
        }
        
        # 测试属性构建
        properties = self.transformer._build_product_property_reqs(
            scraped_product, property_template
        )
        
        assert len(properties) == 2
        assert properties[0].propName == "颜色"
        assert properties[1].propName == "材质"
    
    def test_build_product_sku_reqs(self):
        """测试SKU构建"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        spec_id_map = {"M": 1001, "L": 1002}
        uploaded_image_urls = ["https://uploaded1.jpg", "https://uploaded2.jpg"]
        
        # 测试SKU构建
        skus = self.transformer._build_product_sku_reqs(
            scraped_product, "M", 1001, uploaded_image_urls
        )
        
        assert len(skus) == 1
        sku = skus[0]
        assert sku.currencyType == "JPY"
        assert sku.supplierPrice == 2600  # 100 * 1.3 * 20
        assert len(sku.productSkuSpecReqs) == 1
        assert sku.productSkuSpecReqs[0].specId == 1001
    
    def test_build_product_skc_reqs(self):
        """测试SKC构建"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        spec_id_map = {"M": 1001, "L": 1002}
        uploaded_image_urls = ["https://uploaded1.jpg", "https://uploaded2.jpg"]
        
        # 模拟size_mapper
        self.size_mapper.map_size.return_value = "M"
        
        # 测试SKC构建
        skcs = self.transformer._build_product_skc_reqs(
            scraped_product, spec_id_map, uploaded_image_urls
        )
        
        assert len(skcs) >= 1
        skc = skcs[0]
        assert len(skc.productSkuReqs) >= 1
        assert len(skc.mainProductSkuSpecReqs) >= 1
    
    def test_transform_product(self):
        """测试完整产品转换"""
        # 创建测试数据
        scraped_product = ScrapedProduct(
            title="测试商品",
            price=100.0,
            description="测试描述",
            images=["image1.jpg", "image2.jpg"],
            sizes=["M", "L"],
            url="https://test.com",
            currency="CNY",
            brand="TestBrand",
            category="服装",
            specifications={}
        )
        
        category_info = {"catIdList": [1, 2, 3]}
        property_template = {"properties": []}
        spec_id_map = {"M": 1001, "L": 1002}
        uploaded_image_urls = ["https://uploaded1.jpg", "https://uploaded2.jpg"]
        
        # 模拟size_mapper
        self.size_mapper.map_size.return_value = "M"
        
        # 测试完整转换
        with patch.dict(os.environ, {
            'TEMU_APP_KEY': 'test_key',
            'TEMU_ACCESS_TOKEN': 'test_token'
        }):
            request = self.transformer.transform_product(
                scraped_product=scraped_product,
                category_info=category_info,
                property_template=property_template,
                spec_id_map=spec_id_map,
                uploaded_image_urls=uploaded_image_urls
            )
        
        # 验证结果
        assert isinstance(request, BgGoodsAddRequest)
        assert request.productName == "测试商品"
        assert request.cat1Id == 1
        assert request.cat2Id == 2
        assert request.cat3Id == 3
        assert len(request.carouselImageUrls) == 2
        assert request.materialImgUrl == "https://uploaded1.jpg"
        assert len(request.productSkcReqs) >= 1


if __name__ == "__main__":
    pytest.main([__file__])
