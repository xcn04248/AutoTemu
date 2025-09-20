"""
数据转换模块

负责将爬取的数据转换为Temu API格式
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

from ..utils.logger import get_logger
from ..utils.exceptions import DataValidationException, TransformException
from ..models.product import ScrapedProduct, TemuProduct, TemuSKU
from .size_mapper import SizeMapper, SizeType

logger = get_logger(__name__)


@dataclass
class TransformResult:
    """转换结果数据类"""
    success: bool
    temu_product: Optional[TemuProduct] = None
    skus: List[TemuSKU] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.skus is None:
            self.skus = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class DataTransformer:
    """数据转换器"""

    def __init__(self, size_mapper: Optional[SizeMapper] = None):
        """
        初始化数据转换器
        
        Args:
            size_mapper: 尺码映射器实例，如果为None则创建新实例
        """
        self.size_mapper = size_mapper or SizeMapper()
        
        # 价格转换配置
        self.price_markup = 1.3  # 30%加价
        
        # 商品标题清理规则
        self.title_cleanup_patterns = [
            (r'\s+', ' '),  # 多个空格替换为单个空格
            (r'[^\w\s\-\.\(\)\[\]\/]', ''),  # 移除特殊字符，保留基本标点
            (r'\s+$', ''),  # 移除末尾空格
            (r'^\s+', ''),  # 移除开头空格
        ]
        
        # 描述清理规则
        self.description_cleanup_patterns = [
            (r'<[^>]+>', ''),  # 移除HTML标签
            (r'\s+', ' '),  # 多个空格替换为单个空格
            (r'[^\w\s\-\.\(\)\[\]\/\n]', ''),  # 移除特殊字符
        ]

    def transform_product(self, scraped_product: ScrapedProduct) -> TransformResult:
        """
        转换商品数据
        
        Args:
            scraped_product: 爬取的商品数据
            
        Returns:
            转换结果
        """
        result = TransformResult(success=False)
        
        try:
            # 验证输入数据
            self._validate_scraped_product(scraped_product, result)
            if not result.success:
                return result
            
            # 转换基本信息
            temu_product = self._transform_basic_info(scraped_product, result)
            if not result.success:
                return result
            
            # 转换SKU数据
            skus = self._transform_skus(scraped_product, result)
            if not result.success:
                return result
            
            # 设置转换结果
            result.success = True
            result.temu_product = temu_product
            result.skus = skus
            
            # 将SKU设置到TemuProduct对象中
            temu_product.skus = skus
            
            logger.info(f"商品转换成功: {temu_product.title}")
            
        except Exception as e:
            error_msg = f"商品转换失败: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
        
        return result

    def _validate_scraped_product(self, product: ScrapedProduct, result: TransformResult):
        """验证爬取的商品数据"""
        if not product.title or not product.title.strip():
            result.errors.append("商品标题不能为空")
        
        if not product.price or product.price <= 0:
            result.errors.append("商品价格必须大于0")
        
        if not product.description or not product.description.strip():
            result.warnings.append("商品描述为空")
        
        if not product.images or len(product.images) == 0:
            result.warnings.append("商品图片为空")
        
        if not product.sizes or len(product.sizes) == 0:
            result.warnings.append("商品尺码为空")
        
        # 检查是否有严重错误
        if result.errors:
            result.success = False
        else:
            result.success = True

    def _transform_basic_info(self, scraped_product: ScrapedProduct, result: TransformResult) -> TemuProduct:
        """转换基本信息"""
        # 清理标题
        title = self._clean_title(scraped_product.title)
        
        # 清理描述
        description = self._clean_description(scraped_product.description)
        
        # 计算价格
        original_price = scraped_product.price
        markup_price = original_price * self.price_markup
        
        # 检测尺码类型
        size_type = self.size_mapper.detect_size_type(title, description)
        
        # 创建Temu商品对象
        temu_product = TemuProduct(
            title=title,
            description=description,
            original_price=original_price,
            markup_price=markup_price,
            currency=scraped_product.currency or "JPY",
            category_id=None,  # 将在后续步骤中设置
            size_type=size_type.value,
            images=scraped_product.images,
            source_url=scraped_product.url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return temu_product

    def _transform_skus(self, scraped_product: ScrapedProduct, result: TransformResult) -> List[TemuSKU]:
        """转换SKU数据"""
        skus = []
        
        # 检测尺码类型
        size_type = self.size_mapper.detect_size_type(scraped_product.title, scraped_product.description)
        
        # 批量映射尺码
        size_infos = self.size_mapper.batch_map_sizes(
            scraped_product.sizes, 
            size_type, 
            scraped_product.title, 
            scraped_product.description
        )
        
        # 创建SKU
        for i, size_info in enumerate(size_infos):
            if not size_info.mapped_size:
                result.warnings.append(f"尺码 {size_info.original_size} 无法映射")
                continue
            
            # 计算SKU价格
            sku_price = scraped_product.price * self.price_markup
            
            # 创建SKU对象
            sku = TemuSKU(
                sku_id=f"SKU_{i+1:03d}",
                size=size_info.mapped_size,
                original_size=size_info.original_size,
                price=sku_price,
                stock_quantity=scraped_product.stock_quantity or 100,  # 默认库存
                size_chart_element=size_info.size_chart_element,
                images=scraped_product.images,  # 所有SKU共享图片
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            skus.append(sku)
        
        if not skus:
            result.errors.append("没有有效的SKU数据")
            result.success = False
        else:
            result.success = True
        
        return skus

    def _clean_title(self, title: str) -> str:
        """清理商品标题"""
        if not title:
            return ""
        
        cleaned = title.strip()
        
        # 应用清理规则
        for pattern, replacement in self.title_cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # 限制长度
        if len(cleaned) > 200:
            cleaned = cleaned[:197] + "..."
        
        return cleaned

    def _clean_description(self, description: str) -> str:
        """清理商品描述"""
        if not description:
            return ""
        
        cleaned = description.strip()
        
        # 应用清理规则
        for pattern, replacement in self.description_cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # 限制长度
        if len(cleaned) > 2000:
            cleaned = cleaned[:1997] + "..."
        
        return cleaned

    def transform_images(self, images: List[str], image_processor_result: Dict[str, List[str]]) -> List[str]:
        """
        转换图片数据
        
        Args:
            images: 原始图片URL列表
            image_processor_result: 图片处理结果
            
        Returns:
            处理后的图片URL列表
        """
        processed_images = []
        
        # 按优先级添加图片：主图 -> 详情图 -> 其他图
        for image_type in ['main', 'detail', 'other']:
            if image_type in image_processor_result:
                for image_path in image_processor_result[image_type]:
                    # 这里应该将本地图片路径转换为可访问的URL
                    # 目前直接返回本地路径
                    processed_images.append(str(image_path))
        
        return processed_images

    def validate_temu_product(self, temu_product: TemuProduct) -> Tuple[bool, List[str]]:
        """
        验证Temu商品数据
        
        Args:
            temu_product: Temu商品对象
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 验证标题
        if not temu_product.title or len(temu_product.title.strip()) == 0:
            errors.append("商品标题不能为空")
        elif len(temu_product.title) > 200:
            errors.append("商品标题长度不能超过200字符")
        
        # 验证价格
        if temu_product.markup_price <= 0:
            errors.append("商品价格必须大于0")
        
        # 验证货币
        if not temu_product.currency or len(temu_product.currency) != 3:
            errors.append("货币代码必须是3位字符")
        
        # 验证尺码类型
        if not temu_product.size_type or temu_product.size_type not in ['clothing', 'shoes', 'accessories', 'unknown']:
            errors.append("尺码类型无效")
        
        # 验证图片
        if not temu_product.images or len(temu_product.images) == 0:
            errors.append("商品图片不能为空")
        elif len(temu_product.images) > 10:
            errors.append("商品图片数量不能超过10张")
        
        return len(errors) == 0, errors

    def validate_temu_sku(self, sku: TemuSKU) -> Tuple[bool, List[str]]:
        """
        验证Temu SKU数据
        
        Args:
            sku: Temu SKU对象
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 验证SKU ID
        if not sku.sku_id or len(sku.sku_id.strip()) == 0:
            errors.append("SKU ID不能为空")
        
        # 验证尺码
        if not sku.size or len(sku.size.strip()) == 0:
            errors.append("SKU尺码不能为空")
        
        # 验证价格
        if sku.price <= 0:
            errors.append("SKU价格必须大于0")
        
        # 验证库存
        if sku.stock_quantity < 0:
            errors.append("SKU库存不能为负数")
        
        return len(errors) == 0, errors

    def get_transform_statistics(self, results: List[TransformResult]) -> Dict[str, Any]:
        """
        获取转换统计信息
        
        Args:
            results: 转换结果列表
            
        Returns:
            统计信息字典
        """
        total = len(results)
        if total == 0:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'total_skus': 0,
                'average_skus_per_product': 0.0,
                'total_errors': 0,
                'total_warnings': 0
            }
        
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        success_rate = successful / total
        
        total_skus = sum(len(r.skus) for r in results if r.success)
        average_skus = total_skus / successful if successful > 0 else 0
        
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'total_skus': total_skus,
            'average_skus_per_product': average_skus,
            'total_errors': total_errors,
            'total_warnings': total_warnings
        }

    def batch_transform(self, scraped_products: List[ScrapedProduct]) -> List[TransformResult]:
        """
        批量转换商品数据
        
        Args:
            scraped_products: 爬取的商品数据列表
            
        Returns:
            转换结果列表
        """
        results = []
        
        logger.info(f"开始批量转换 {len(scraped_products)} 个商品")
        
        for i, product in enumerate(scraped_products):
            try:
                result = self.transform_product(product)
                results.append(result)
                
                if result.success:
                    logger.debug(f"商品 {i+1}/{len(scraped_products)} 转换成功: {product.title}")
                else:
                    logger.warning(f"商品 {i+1}/{len(scraped_products)} 转换失败: {product.title}")
                    
            except Exception as e:
                logger.error(f"商品 {i+1}/{len(scraped_products)} 转换异常: {str(e)}")
                results.append(TransformResult(
                    success=False,
                    errors=[f"转换异常: {str(e)}"]
                ))
        
        # 记录统计信息
        stats = self.get_transform_statistics(results)
        logger.info(f"批量转换完成: 总计 {stats['total']} 个, 成功 {stats['successful']} 个, "
                   f"失败 {stats['failed']} 个, 成功率 {stats['success_rate']:.2%}")
        
        return results
