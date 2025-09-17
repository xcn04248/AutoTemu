"""
商品爬虫模块

基于Firecrawl技术实现商品信息抓取功能。
"""

import os
import re
import json
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from firecrawl import Firecrawl
from firecrawl.types import ScrapeResponse

from ..utils.config import get_config
from ..utils.logger import get_logger
from ..utils.retry import network_retry
from ..utils.exceptions import NetworkException, ParseException
from ..models.data_models import ProductData, SizeInfo


class ProductScraper:
    """商品爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.config = get_config()
        self.logger = get_logger("scraper")
        
        # 初始化Firecrawl客户端
        try:
            self.firecrawl = Firecrawl(api_key=self.config.firecrawl_api_key)
            self.logger.info("Firecrawl客户端初始化成功")
        except Exception as e:
            self.logger.error(f"Firecrawl客户端初始化失败: {e}")
            raise NetworkException(f"Firecrawl初始化失败: {e}")
    
    @network_retry()
    def scrape_product(self, url: str) -> ProductData:
        """
        爬取商品信息
        
        Args:
            url: 商品URL
            
        Returns:
            ProductData: 商品数据对象
            
        Raises:
            NetworkException: 网络请求失败
            ParseException: 数据解析失败
        """
        self.logger.log_operation("商品爬取", "started", url=url)
        
        try:
            # 使用Firecrawl抓取页面
            result = self._scrape_with_firecrawl(url)
            
            # 解析商品数据
            product_data = self._parse_product_data(result, url)
            
            self.logger.log_operation("商品爬取", "completed", 
                                    url=url, 
                                    name=product_data.name,
                                    price=product_data.price)
            
            return product_data
            
        except Exception as e:
            self.logger.log_operation("商品爬取", "failed", url=url, error=str(e))
            raise
    
    def _scrape_with_firecrawl(self, url: str) -> ScrapeResponse:
        """
        使用Firecrawl抓取页面
        
        Args:
            url: 商品URL
            
        Returns:
            ScrapeResponse: Firecrawl响应对象
        """
        self.logger.info(f"开始抓取页面: {url}")
        
        try:
            result = self.firecrawl.scrape(
                url,
                formats=[
                    {
                        "type": "json",
                        "prompt": self._get_scrape_prompt()
                    }
                ],
                only_main_content=True,
                wait_for=5000,
                timeout=300000
            )
            
            if not hasattr(result, "json") or not result.json:
                raise ParseException("Firecrawl未返回有效的JSON数据")
            
            self.logger.info("页面抓取成功")
            return result
            
        except Exception as e:
            self.logger.error(f"Firecrawl抓取失败: {e}")
            raise NetworkException(f"页面抓取失败: {e}")
    
    def _get_scrape_prompt(self) -> str:
        """
        获取爬取提示词
        
        Returns:
            str: 提示词
        """
        return (
            "请提取商品名称、价格、描述、图片链接、尺码及其对应的图片链接、商品详情及其中的图片链接。"
            "请忽略店内新品、空间相册以及代发说明，忽略 liuchengtu.png 这个图片。"
            "返回JSON格式，包含以下字段："
            "- productName: 商品名称"
            "- price: 价格（数字）"
            "- description: 商品描述"
            "- imageLink: 主图链接"
            "- sizes: 尺码数组，每个包含size和sizeImageLink"
            "- productDetails: 包含details和detailImageLinks"
            "- brand: 品牌（如果有）"
            "- material: 材质（如果有）"
        )
    
    def _parse_product_data(self, result: ScrapeResponse, url: str) -> ProductData:
        """
        解析商品数据
        
        Args:
            result: Firecrawl响应
            url: 商品URL
            
        Returns:
            ProductData: 解析后的商品数据
        """
        try:
            data = result.json
            self.logger.info("开始解析商品数据")
            
            # 提取基本信息
            name = self._extract_text(data, "productName", "商品名称")
            price = self._extract_price(data, "price")
            description = self._extract_text(data, "description", "商品描述")
            main_image_url = self._extract_text(data, "imageLink", "主图链接")
            
            # 验证必需字段
            if not name:
                raise ParseException("商品名称不能为空")
            if price <= 0:
                raise ParseException("商品价格必须大于0")
            if not main_image_url:
                raise ParseException("主图链接不能为空")
            
            # 提取尺码信息
            sizes = self._extract_sizes(data)
            
            # 提取详情图片
            detail_images = self._extract_detail_images(data)
            
            # 提取商品编码
            product_code = self._extract_product_code(data)
            
            # 提取品牌和材质
            brand = self._extract_text(data, "brand", "品牌")
            material = self._extract_text(data, "material", "材质")
            
            # 创建商品数据对象
            product_data = ProductData(
                url=url,
                name=name,
                price=price,
                description=description,
                main_image_url=main_image_url,
                detail_images=detail_images,
                sizes=sizes,
                product_code=product_code,
                brand=brand,
                material=material,
                raw_data=data
            )
            
            self.logger.info(f"商品数据解析成功: {name}, 价格: {price}, 尺码数: {len(sizes)}")
            return product_data
            
        except Exception as e:
            self.logger.error(f"商品数据解析失败: {e}")
            raise ParseException(f"数据解析失败: {e}")
    
    def _extract_text(self, data: Dict[str, Any], key: str, field_name: str) -> Optional[str]:
        """
        提取文本字段
        
        Args:
            data: 数据字典
            key: 字段键
            field_name: 字段名称（用于日志）
            
        Returns:
            Optional[str]: 提取的文本，如果不存在则返回None
        """
        value = data.get(key)
        if value and isinstance(value, str) and value.strip():
            return value.strip()
        return None
    
    def _extract_price(self, data: Dict[str, Any], key: str) -> float:
        """
        提取价格字段
        
        Args:
            data: 数据字典
            key: 字段键
            
        Returns:
            float: 价格
            
        Raises:
            ParseException: 价格解析失败
        """
        price_value = data.get(key)
        
        if price_value is None:
            raise ParseException("未找到价格信息")
        
        # 处理字符串价格
        if isinstance(price_value, str):
            # 移除货币符号和逗号
            price_str = re.sub(r'[^\d.]', '', price_value)
            try:
                return float(price_str)
            except ValueError:
                raise ParseException(f"价格格式无效: {price_value}")
        
        # 处理数字价格
        if isinstance(price_value, (int, float)):
            return float(price_value)
        
        raise ParseException(f"价格类型无效: {type(price_value)}")
    
    def _extract_sizes(self, data: Dict[str, Any]) -> List[SizeInfo]:
        """
        提取尺码信息
        
        Args:
            data: 数据字典
            
        Returns:
            List[SizeInfo]: 尺码信息列表
        """
        sizes = []
        sizes_data = data.get("sizes", [])
        
        if not isinstance(sizes_data, list):
            self.logger.warning("尺码数据格式无效，跳过尺码提取")
            return sizes
        
        for size_info in sizes_data:
            if not isinstance(size_info, dict):
                continue
                
            size_name = size_info.get("size")
            size_image_url = size_info.get("sizeImageLink")
            
            if size_name and size_image_url:
                size_obj = SizeInfo(
                    size_name=size_name.strip(),
                    size_image_url=size_image_url.strip()
                )
                sizes.append(size_obj)
                self.logger.debug(f"提取尺码: {size_name}")
        
        self.logger.info(f"提取到 {len(sizes)} 个尺码")
        return sizes
    
    def _extract_detail_images(self, data: Dict[str, Any]) -> List[str]:
        """
        提取详情图片链接
        
        Args:
            data: 数据字典
            
        Returns:
            List[str]: 详情图片链接列表
        """
        detail_images = []
        product_details = data.get("productDetails", {})
        
        if isinstance(product_details, dict):
            detail_image_links = product_details.get("detailImageLinks", [])
            
            if isinstance(detail_image_links, list):
                for url in detail_image_links:
                    if isinstance(url, str) and url.strip():
                        detail_images.append(url.strip())
        
        self.logger.info(f"提取到 {len(detail_images)} 张详情图")
        return detail_images
    
    def _extract_product_code(self, data: Dict[str, Any]) -> Optional[str]:
        """
        提取商品编码
        
        Args:
            data: 数据字典
            
        Returns:
            Optional[str]: 商品编码
        """
        # 从商品详情中提取货号
        product_details = data.get("productDetails", {})
        if isinstance(product_details, dict):
            details = product_details.get("details", "")
            if isinstance(details, str):
                match = re.search(r"货号[:：]\s*(\S+)", details)
                if match:
                    return match.group(1).strip()
        
        return None
    
    def validate_url(self, url: str) -> bool:
        """
        验证URL是否有效
        
        Args:
            url: 商品URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def get_supported_domains(self) -> List[str]:
        """
        获取支持的域名列表
        
        Returns:
            List[str]: 支持的域名
        """
        return [
            "www.jp0663.com",
            "jp0663.com",
            # 可以添加更多支持的域名
        ]
    
    def is_supported_url(self, url: str) -> bool:
        """
        检查URL是否受支持
        
        Args:
            url: 商品URL
            
        Returns:
            bool: 是否受支持
        """
        if not self.validate_url(url):
            return False
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        return domain in self.get_supported_domains()


# 便捷函数
def scrape_product(url: str) -> ProductData:
    """
    爬取商品信息的便捷函数
    
    Args:
        url: 商品URL
        
    Returns:
        ProductData: 商品数据
    """
    scraper = ProductScraper()
    return scraper.scrape_product(url)


if __name__ == "__main__":
    # 测试代码
    test_url = "https://www.jp0663.com/detail/V52ZD9Ex1OKaCj1biny2494lGc4TVj0a"
    
    try:
        scraper = ProductScraper()
        
        if scraper.is_supported_url(test_url):
            print(f"开始爬取商品: {test_url}")
            product = scraper.scrape_product(test_url)
            
            print(f"商品名称: {product.name}")
            print(f"商品价格: {product.price}")
            print(f"尺码数量: {len(product.sizes)}")
            print(f"详情图数量: {len(product.detail_images)}")
            
            # 保存为JSON
            json_file = f"product_{product.product_code or 'unknown'}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(product.to_json())
            print(f"商品数据已保存到: {json_file}")
        else:
            print(f"不支持的URL: {test_url}")
            
    except Exception as e:
        print(f"爬取失败: {e}")
