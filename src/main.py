"""
AutoTemu主程序

整合所有模块，实现完整的商品爬取和添加流程
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
from temu_api import TemuClient
from .models.product import ScrapedProduct, TemuProduct, TemuSKU, TemuListingResult
from .models.data_models import ProductData

logger = get_logger(__name__)


def convert_product_data_to_scraped_product(product_data: ProductData) -> ScrapedProduct:
    """
    将ProductData转换为ScrapedProduct
    
    Args:
        product_data: 爬虫返回的ProductData对象
        
    Returns:
        ScrapedProduct: 数据转换器期望的ScrapedProduct对象
    """
    # 合并主图和详情图
    all_images = [product_data.main_image_url] + product_data.detail_images
    
    # 提取尺码名称列表
    size_names = [size.size_name for size in product_data.sizes]
    
    return ScrapedProduct(
        title=product_data.name,
        price=product_data.price,
        description=product_data.description,
        images=all_images,
        sizes=size_names,
        url=product_data.url,
        currency="JPY",
        brand=product_data.brand,
        category=product_data.category,
        scraped_at=product_data.scraped_at
    )


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
            self.temu_client = TemuClient(
            app_key=self.config.temu_app_key,
            app_secret=self.config.temu_app_secret,
            access_token=self.config.temu_access_token,
            base_url=self.config.temu_base_url,
            debug=False
        )
            self.scraper = ProductScraper()
            
            logger.info("AutoTemu应用程序初始化成功")
            
        except ConfigError as e:
            logger.error(f"配置加载失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"应用程序初始化失败: {str(e)}")
            raise AutoTemuException(f"初始化失败: {str(e)}")

    def _is_leaf_category(self, category_id: str) -> bool:
        """
        检查分类是否为叶子分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            bool: 是否为叶子分类
        """
        try:
            result = self.temu_client.product.cats_get(parent_cat_id=int(category_id))
            if result.get("success"):
                sub_categories = result.get("result", {}).get("goodsCatsList", [])
                if sub_categories is None:
                    return True  # 如果没有子分类列表，认为是叶子分类
                return len(sub_categories) == 0
            return False
        except Exception as e:
            logger.error(f"检查叶子分类失败: {e}")
            return False

    def process_single_url(self, url: str, output_dir: Optional[str] = None) -> TemuListingResult:
        """处理单个商品URL（真实运行）：复用经验证的完整添加流程。"""
        logger.info(f"开始处理商品URL(真实运行): {url}")
        try:
            from importlib import import_module
            tester_mod = import_module("docs.examples.test_real_product")
            tester = tester_mod.RealProductTester()
            ok = tester.run_complete_test(url)
            if ok:
                return TemuListingResult(
                    success=True,
                    product_id=tester.created_goods_id,
                    sku_ids=tester.created_sku_ids,
                    image_ids=[]
                )
            return TemuListingResult(success=False, errors=["真实运行失败"])
        except Exception as e:
            logger.error(f"真实运行异常: {e}")
            return TemuListingResult(success=False, errors=[f"异常: {e}"])

    def process_batch_urls(self, urls: List[str], output_dir: Optional[str] = None) -> List[TemuListingResult]:
        """
        批量处理商品URL
        
        Args:
            urls: 商品URL列表
            output_dir: 输出目录，如果为None则使用默认目录
            
        Returns:
            添加结果列表
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
            result = self.temu_client.product.cats_get(parent_cat_id=0)
            if not result.get("success"):
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
            "api_connection": self.test_connection()
        }
        
        return status


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AutoTemu - 自动化商品爬取和添加工具")
    parser.add_argument("--url", type=str, help="单个商品URL")
    parser.add_argument("--urls", type=str, nargs="+", help="多个商品URL")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--output", type=str, help="输出目录")
    parser.add_argument("--test", action="store_true", help="测试系统连接")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--golden", action="store_true", help="运行金测试（docs/examples/test_real_product.py）")
    
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
        
        # 运行金测试
        if args.golden:
            # 直接复用金测试脚本的完整流程，确保与真实测试一致
            try:
                # 动态导入，避免循环依赖
                from importlib import import_module
                tester_mod = import_module("docs.examples.test_real_product")
                tester = tester_mod.RealProductTester()
                test_url = args.url or "https://www.jp0663.com/detail/V52ZD9Ex1OKaCj1biny2494lGc4TVj0a"
                ok = tester.run_complete_test(test_url)
                if ok:
                    print(f"✅ 金测试通过 goodsId={tester.created_goods_id} skus={len(tester.created_sku_ids)}")
                    sys.exit(0)
                else:
                    print("❌ 金测试未通过")
                    sys.exit(2)
            except Exception as e:
                print(f"❌ 金测试执行失败: {e}")
                sys.exit(2)

        # 处理商品URL（常规流程）
        if args.url:
            result = app.process_single_url(args.url, args.output)
            if result.success:
                print(f"✅ 商品添加成功: {result.product_id}")
                sys.exit(0)
            else:
                print(f"❌ 商品添加失败: {', '.join(result.errors)}")
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
