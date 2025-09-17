"""
数据模型模块

定义系统中使用的各种数据类
"""

from .product import (
    ScrapedProduct,
    TemuProduct,
    TemuSKU,
    TemuCategory,
    TemuSizeChart,
    TemuImage,
    TemuListingResult,
    ProductStatus,
    SizeType
)

__all__ = [
    'ScrapedProduct',
    'TemuProduct',
    'TemuSKU',
    'TemuCategory',
    'TemuSizeChart',
    'TemuImage',
    'TemuListingResult',
    'ProductStatus',
    'SizeType'
]
