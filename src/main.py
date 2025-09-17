"""
AutoTemu主程序

整合所有模块，实现完整的商品爬取和上架流程
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List
import json

from .utils.logger import get_logger
from .utils.config import get_config, ConfigError
from .utils.exceptions import AutoTemuException
from .scraper.product_scraper import ProductScraper
from .image.image_processor import ImageProcessor
from .image.ocr_client import OCRClient
from .transform.size_mapper import SizeMapper
from .transform.data_transformer import DataTransformer
from .api.temu_client import TemuAPIClient
from .models.product import ScrapedProduct, TemuProduct, TemuSKU, TemuListingResult

logger = get_logger(__name__)


class AutoTemuApp:
    """AutoTemu主应用程序"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化应用程序
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        try:
            # 加载配置
            if config_path:
                from .utils.config import reload_config
                self.config = reload_config(config_path)
            else:
                self.config = get_config()
            
            # 初始化各个模块
            self.ocr_client = OCRClient()
            self.image_processor = ImageProcessor(self.ocr_client)
            self.size_mapper = SizeMapper()
            self.data_transformer = DataTransformer(self.size_mapper)
            self.temu_client = TemuAPIClient(self.config)
            self.scraper = ProductScraper()
            
            logger.info("AutoTemu应用程序初始化成功")
            
        except ConfigError as e:
            logger.error(f"配置加载失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"应用程序初始化失败: {str(e)}")
            raise AutoTemuException(f"初始化失败: {str(e)}")

    def process_single_url(self, url: str, output_dir: Optional[str] = None) -> TemuListingResult:
        """
        处理单个商品URL
        
        Args:
            url: 商品URL
            output_dir: 输出目录，如果为None则使用默认目录
            
        Returns:
            上架结果
        """
        logger.info(f"开始处理商品URL: {url}")
        
        try:
            # 1. 爬取商品信息
            logger.info("步骤1: 爬取商品信息")
            scraped_product = self.scraper.scrape_product(url)
            logger.info(f"商品爬取成功: {scraped_product.title}")
            
            # 2. 处理图片
            logger.info("步骤2: 处理图片")
            image_result = self.image_processor.process_images(scraped_product.images)
            logger.info(f"图片处理完成: 主图 {len(image_result['main'])} 张, "
                       f"详情图 {len(image_result['detail'])} 张, "
                       f"尺码图 {len(image_result['size'])} 张, "
                       f"过滤 {len(image_result['filtered'])} 张")
            
            # 3. 转换数据
            logger.info("步骤3: 转换数据")
            transform_result = self.data_transformer.transform_product(scraped_product)
            if not transform_result.success:
                raise AutoTemuException(f"数据转换失败: {', '.join(transform_result.errors)}")
            
            temu_product = transform_result.temu_product
            skus = transform_result.skus
            logger.info(f"数据转换成功: {temu_product.title}, {len(skus)} 个SKU")
            
            # 4. 获取分类推荐
            logger.info("步骤4: 获取分类推荐")
            categories = self.temu_client.get_category_recommend(temu_product.title, temu_product.description)
            if not categories:
                raise AutoTemuException("无法获取商品分类推荐")
            
            # 选择第一个推荐分类
            selected_category = categories[0]
            logger.info(f"选择分类: {selected_category.name} (ID: {selected_category.category_id})")
            
            # 5. 获取尺码表元素
            logger.info("步骤5: 获取尺码表元素")
            size_elements = self.temu_client.get_size_chart_elements(
                selected_category.category_id, 
                temu_product.size_type
            )
            logger.info(f"尺码表元素: {size_elements}")
            
            # 更新SKU的尺码表元素
            for sku in skus:
                if size_elements:
                    sku.size_chart_element = size_elements[0]  # 使用第一个元素
            
            # 6. 上架商品
            logger.info("步骤6: 上架商品到Temu")
            listing_result = self.temu_client.list_product(
                temu_product, 
                skus, 
                selected_category.category_id
            )
            
            if listing_result.success:
                logger.info(f"商品上架成功: {temu_product.title}")
                logger.info(f"商品ID: {listing_result.product_id}")
                logger.info(f"SKU数量: {len(listing_result.sku_ids)}")
                logger.info(f"图片数量: {len(listing_result.image_ids)}")
            else:
                logger.error(f"商品上架失败: {', '.join(listing_result.errors)}")
            
            return listing_result
            
        except Exception as e:
            logger.error(f"处理商品URL失败: {url}, 错误: {str(e)}")
            return TemuListingResult(
                success=False,
                errors=[f"处理失败: {str(e)}"]
            )

    def process_batch_urls(self, urls: List[str], output_dir: Optional[str] = None) -> List[TemuListingResult]:
        """
        批量处理商品URL
        
        Args:
            urls: 商品URL列表
            output_dir: 输出目录，如果为None则使用默认目录
            
        Returns:
            上架结果列表
        """
        logger.info(f"开始批量处理 {len(urls)} 个商品URL")
        
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"处理第 {i}/{len(urls)} 个商品: {url}")
            try:
                result = self.process_single_url(url, output_dir)
                results.append(result)
                
                if result.success:
                    logger.info(f"第 {i} 个商品处理成功")
                else:
                    logger.warning(f"第 {i} 个商品处理失败: {', '.join(result.errors)}")
                    
            except Exception as e:
                logger.error(f"第 {i} 个商品处理异常: {str(e)}")
                results.append(TemuListingResult(
                    success=False,
                    errors=[f"处理异常: {str(e)}"]
                ))
        
        # 统计结果
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.info(f"批量处理完成: 总计 {len(results)} 个, 成功 {successful} 个, 失败 {failed} 个")
        
        return results

    def test_connection(self) -> bool:
        """
        测试系统连接
        
        Returns:
            连接是否正常
        """
        logger.info("开始测试系统连接")
        
        try:
            # 测试Temu API连接
            if not self.temu_client.test_connection():
                logger.error("Temu API连接失败")
                return False
            
            # 测试OCR服务连接
            # 这里可以添加OCR连接测试
            
            logger.info("系统连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"系统连接测试失败: {str(e)}")
            return False

    def get_system_status(self) -> dict:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        status = {
            "config": {
                "price_markup": self.config.price_markup,
                "log_level": self.config.log_level,
                "image_save_path": self.config.image_save_path,
                "max_retry_attempts": self.config.max_retry_attempts
            },
            "modules": {
                "scraper": "已初始化",
                "image_processor": "已初始化",
                "ocr_client": "已初始化",
                "size_mapper": "已初始化",
                "data_transformer": "已初始化",
                "temu_client": "已初始化"
            },
            "api_connection": self.temu_client.test_connection()
        }
        
        return status


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AutoTemu - 自动化商品爬取和上架工具")
    parser.add_argument("--url", type=str, help="单个商品URL")
    parser.add_argument("--urls", type=str, nargs="+", help="多个商品URL")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--output", type=str, help="输出目录")
    parser.add_argument("--test", action="store_true", help="测试系统连接")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    try:
        # 创建应用程序实例
        app = AutoTemuApp(args.config)
        
        # 测试连接
        if args.test:
            if app.test_connection():
                print("✅ 系统连接正常")
                sys.exit(0)
            else:
                print("❌ 系统连接失败")
                sys.exit(1)
        
        # 显示系统状态
        if args.status:
            status = app.get_system_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            sys.exit(0)
        
        # 处理商品URL
        if args.url:
            result = app.process_single_url(args.url, args.output)
            if result.success:
                print(f"✅ 商品上架成功: {result.product_id}")
                sys.exit(0)
            else:
                print(f"❌ 商品上架失败: {', '.join(result.errors)}")
                sys.exit(1)
        
        elif args.urls:
            results = app.process_batch_urls(args.urls, args.output)
            successful = sum(1 for r in results if r.success)
            print(f"✅ 批量处理完成: {successful}/{len(results)} 成功")
            sys.exit(0)
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
