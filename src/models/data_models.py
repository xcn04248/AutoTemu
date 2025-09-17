"""
数据模型定义

定义系统中使用的所有数据结构。
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json


class ProductStatus(Enum):
    """商品状态枚举"""
    SCRAPED = "scraped"          # 已爬取
    PROCESSING = "processing"    # 处理中
    READY = "ready"             # 准备上架
    UPLOADING = "uploading"     # 上架中
    SUCCESS = "success"         # 上架成功
    FAILED = "failed"           # 上架失败


class ImageStatus(Enum):
    """图片状态枚举"""
    PENDING = "pending"         # 待处理
    DOWNLOADING = "downloading" # 下载中
    DOWNLOADED = "downloaded"   # 已下载
    CHECKING = "checking"       # OCR检查中
    PASSED = "passed"          # 通过检查
    REJECTED = "rejected"      # 被拒绝（包含中文）
    PROCESSED = "processed"    # 已处理（尺寸调整等）
    FAILED = "failed"          # 处理失败


@dataclass
class SizeInfo:
    """尺码信息"""
    size_name: str                              # 尺码名称（如 S, M, L）
    size_image_url: Optional[str] = None        # 尺码图片URL
    measurements: Optional[Dict[str, float]] = None  # 尺寸测量数据
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class ImageInfo:
    """图片信息"""
    url: str                                    # 图片URL
    local_path: Optional[str] = None            # 本地存储路径
    status: ImageStatus = ImageStatus.PENDING   # 图片状态
    width: Optional[int] = None                 # 图片宽度
    height: Optional[int] = None                # 图片高度
    size_bytes: Optional[int] = None            # 文件大小
    format: Optional[str] = None                # 图片格式
    has_chinese: Optional[bool] = None          # 是否包含中文
    ocr_text: Optional[List[str]] = None        # OCR识别的文本
    error_message: Optional[str] = None         # 错误信息
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ImageInfo':
        """从字典创建实例"""
        if 'status' in data:
            data['status'] = ImageStatus(data['status'])
        return cls(**data)


@dataclass
class ProductData:
    """爬取的商品数据"""
    url: str                                    # 商品URL
    name: str                                   # 商品名称
    price: float                                # 商品价格
    description: str                            # 商品描述
    main_image_url: str                         # 主图URL
    detail_images: List[str] = field(default_factory=list)  # 详情图URL列表
    sizes: List[SizeInfo] = field(default_factory=list)     # 尺码信息列表
    product_code: Optional[str] = None          # 商品编码/货号
    category: Optional[str] = None              # 商品分类
    brand: Optional[str] = None                 # 品牌
    material: Optional[str] = None              # 材质
    scraped_at: datetime = field(default_factory=datetime.now)  # 爬取时间
    raw_data: Optional[Dict[str, Any]] = None   # 原始爬取数据
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['scraped_at'] = self.scraped_at.isoformat()
        data['sizes'] = [size.to_dict() for size in self.sizes]
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductData':
        """从字典创建实例"""
        if 'scraped_at' in data:
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])
        if 'sizes' in data:
            data['sizes'] = [SizeInfo(**size) for size in data['sizes']]
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProductData':
        """从JSON字符串创建实例"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class ProcessedImages:
    """处理后的图片集合"""
    main_image: Optional[ImageInfo] = None      # 主图
    detail_images: List[ImageInfo] = field(default_factory=list)  # 详情图列表
    size_images: Dict[str, ImageInfo] = field(default_factory=dict)  # 尺码图字典
    total_count: int = 0                        # 总图片数
    passed_count: int = 0                       # 通过的图片数
    rejected_count: int = 0                     # 被拒绝的图片数
    failed_count: int = 0                       # 失败的图片数
    
    def add_detail_image(self, image: ImageInfo):
        """添加详情图"""
        self.detail_images.append(image)
        self._update_counts()
    
    def add_size_image(self, size_name: str, image: ImageInfo):
        """添加尺码图"""
        self.size_images[size_name] = image
        self._update_counts()
    
    def _update_counts(self):
        """更新计数"""
        all_images = []
        if self.main_image:
            all_images.append(self.main_image)
        all_images.extend(self.detail_images)
        all_images.extend(self.size_images.values())
        
        self.total_count = len(all_images)
        self.passed_count = sum(1 for img in all_images if img.status == ImageStatus.PASSED)
        self.rejected_count = sum(1 for img in all_images if img.status == ImageStatus.REJECTED)
        self.failed_count = sum(1 for img in all_images if img.status == ImageStatus.FAILED)
    
    def get_valid_images(self) -> List[ImageInfo]:
        """获取所有有效的图片（通过或已处理）"""
        valid_statuses = {ImageStatus.PASSED, ImageStatus.PROCESSED}
        all_images = []
        
        if self.main_image and self.main_image.status in valid_statuses:
            all_images.append(self.main_image)
        
        for img in self.detail_images:
            if img.status in valid_statuses:
                all_images.append(img)
        
        return all_images


@dataclass
class TemuSKU:
    """Temu SKU数据"""
    sku_id: Optional[int] = None                # SKU ID（创建后由Temu分配）
    spec_list: List[Dict[str, Any]] = field(default_factory=list)  # 规格列表
    sku_price: float = 0.0                      # SKU价格
    sku_quantity: int = 100                     # SKU库存数量
    out_sku_sn: Optional[str] = None            # 外部SKU编码
    sku_img_url: Optional[str] = None           # SKU图片URL
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class TemuProductData:
    """Temu商品数据格式"""
    # 商品基础信息
    goods_name: str                             # 商品名称
    cat_id: int                                 # 类目ID
    hd_thumb_url: str                           # 主图URL
    carousel_image_list: List[str] = field(default_factory=list)  # 轮播图列表
    out_goods_sn: Optional[str] = None          # 外部商品编码
    
    # 商品属性
    goods_property: Dict[str, Any] = field(default_factory=dict)
    
    # 商品描述和卖点
    goods_desc: Optional[str] = None            # 商品描述
    bullet_points: Optional[List[str]] = None   # 卖点列表
    
    # SKU列表
    sku_list: List[TemuSKU] = field(default_factory=list)
    
    # 尺码表
    goods_size_chart_list: Optional[Dict[str, Any]] = None
    goods_size_image: Optional[List[str]] = None
    
    # 商家服务承诺
    goods_service_promise: Dict[str, Any] = field(default_factory=lambda: {
        "promiseDeliveryTime": 7,  # 承诺发货时间（天）
        "servicePromiseList": []    # 服务承诺列表
    })
    
    def to_api_format(self) -> dict:
        """转换为Temu API格式"""
        return {
            "goodsBasic": {
                "goodsName": self.goods_name,
                "catId": self.cat_id,
                "hdThumbUrl": self.hd_thumb_url,
                "carouselImageList": self.carousel_image_list,
                "outGoodsSn": self.out_goods_sn
            },
            "goodsProperty": self.goods_property,
            "goodsServicePromise": self.goods_service_promise,
            "skuList": [sku.to_dict() for sku in self.sku_list],
            "bulletPoints": self.bullet_points,
            "goodsDesc": self.goods_desc,
            "goodsSizeChartList": self.goods_size_chart_list,
            "goodsSizeImage": self.goods_size_image
        }


@dataclass
class CreateProductResult:
    """商品创建结果"""
    success: bool                               # 是否成功
    goods_id: Optional[int] = None              # 商品ID（成功时返回）
    sku_ids: Optional[List[int]] = None         # SKU ID列表（成功时返回）
    error_code: Optional[str] = None            # 错误代码
    error_message: Optional[str] = None         # 错误消息
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    api_response: Optional[Dict[str, Any]] = None  # 原始API响应
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class ProcessingResult:
    """商品处理结果"""
    product_url: str                            # 商品URL
    status: ProductStatus                       # 处理状态
    product_data: Optional[ProductData] = None  # 商品数据
    processed_images: Optional[ProcessedImages] = None  # 处理后的图片
    temu_product_data: Optional[TemuProductData] = None  # Temu格式数据
    create_result: Optional[CreateProductResult] = None  # 创建结果
    start_time: datetime = field(default_factory=datetime.now)  # 开始时间
    end_time: Optional[datetime] = None         # 结束时间
    duration_seconds: Optional[float] = None    # 处理时长
    error_message: Optional[str] = None         # 错误信息
    
    def mark_completed(self):
        """标记为完成"""
        self.end_time = datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            'product_url': self.product_url,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message
        }
        
        if self.product_data:
            data['product_data'] = self.product_data.to_dict()
        
        if self.create_result:
            data['create_result'] = self.create_result.to_dict()
        
        return data


# 尺码映射配置
SIZE_MAPPING = {
    # 国际尺码到Temu标准尺码的映射
    'XS': {'temu_size': 'XS', 'sort_order': 1},
    'S': {'temu_size': 'S', 'sort_order': 2},
    'M': {'temu_size': 'M', 'sort_order': 3},
    'L': {'temu_size': 'L', 'sort_order': 4},
    'XL': {'temu_size': 'XL', 'sort_order': 5},
    'XXL': {'temu_size': '2XL', 'sort_order': 6},
    '2XL': {'temu_size': '2XL', 'sort_order': 6},
    'XXXL': {'temu_size': '3XL', 'sort_order': 7},
    '3XL': {'temu_size': '3XL', 'sort_order': 7},
    '4XL': {'temu_size': '4XL', 'sort_order': 8},
    '5XL': {'temu_size': '5XL', 'sort_order': 9},
    
    # 日本尺码
    'F': {'temu_size': 'FREE', 'sort_order': 0},  # Free size
    'FREE': {'temu_size': 'FREE', 'sort_order': 0},
    
    # 数字尺码（亚洲尺码）
    '36': {'temu_size': 'XS', 'sort_order': 1},
    '38': {'temu_size': 'S', 'sort_order': 2},
    '40': {'temu_size': 'M', 'sort_order': 3},
    '42': {'temu_size': 'L', 'sort_order': 4},
    '44': {'temu_size': 'XL', 'sort_order': 5},
    '46': {'temu_size': '2XL', 'sort_order': 6},
    '48': {'temu_size': '3XL', 'sort_order': 7},
}


def normalize_size(size_name: str) -> str:
    """
    标准化尺码名称
    
    Args:
        size_name: 原始尺码名称
        
    Returns:
        标准化后的尺码名称
    """
    # 转换为大写并去除空格
    normalized = size_name.upper().strip()
    
    # 处理特殊情况
    if normalized in SIZE_MAPPING:
        return SIZE_MAPPING[normalized]['temu_size']
    
    # 如果没有找到映射，返回原始值
    return normalized
