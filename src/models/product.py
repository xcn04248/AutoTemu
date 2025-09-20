"""
商品数据模型

定义系统中使用的商品相关数据类
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProductStatus(Enum):
    """商品状态枚举"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    APPROVED = "approved"     # 已审核
    REJECTED = "rejected"     # 已拒绝
    ACTIVE = "active"         # 已上架
    INACTIVE = "inactive"     # 已下架
    DELETED = "deleted"       # 已删除


class SizeType(Enum):
    """尺码类型枚举"""
    CLOTHING = "clothing"     # 服装
    SHOES = "shoes"          # 鞋子
    ACCESSORIES = "accessories"  # 配饰
    UNKNOWN = "unknown"      # 未知


@dataclass
class ScrapedProduct:
    """爬取的商品数据"""
    title: str
    price: float
    description: str
    images: List[str]
    sizes: List[str]
    url: str
    currency: Optional[str] = "JPY"
    stock_quantity: Optional[int] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.title or not self.title.strip():
            raise ValueError("商品标题不能为空")
        
        if self.price <= 0:
            raise ValueError("商品价格必须大于0")
        
        if not self.url or not self.url.strip():
            raise ValueError("商品URL不能为空")
        
        # 清理数据
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else ""
        self.url = self.url.strip()
        
        # 确保列表不为None
        if self.images is None:
            self.images = []
        if self.sizes is None:
            self.sizes = []
        if self.tags is None:
            self.tags = []
        if self.specifications is None:
            self.specifications = {}


@dataclass
class TemuProduct:
    """Temu商品数据"""
    title: str
    description: str
    original_price: float
    markup_price: float
    currency: str
    category_id: Optional[str] = None
    size_type: str = "unknown"
    images: List[str] = field(default_factory=list)
    skus: List["TemuSKU"] = field(default_factory=list)
    source_url: Optional[str] = None
    status: ProductStatus = ProductStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.title or not self.title.strip():
            raise ValueError("商品标题不能为空")
        
        if self.markup_price <= 0:
            raise ValueError("商品价格必须大于0")
        
        if not self.currency or len(self.currency) != 3:
            raise ValueError("货币代码必须是3位字符")
        
        # 清理数据
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else ""
        
        # 确保列表不为None
        if self.images is None:
            self.images = []
        
        # 设置更新时间
        self.updated_at = datetime.now()


@dataclass
class TemuSKU:
    """Temu SKU数据"""
    sku_id: str
    size: str
    original_size: str
    price: float
    stock_quantity: int
    size_chart_element: Optional[str] = None
    images: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.sku_id or not self.sku_id.strip():
            raise ValueError("SKU ID不能为空")
        
        if not self.size or not self.size.strip():
            raise ValueError("SKU尺码不能为空")
        
        if self.price <= 0:
            raise ValueError("SKU价格必须大于0")
        
        if self.stock_quantity < 0:
            raise ValueError("SKU库存不能为负数")
        
        # 清理数据
        self.sku_id = self.sku_id.strip()
        self.size = self.size.strip()
        self.original_size = self.original_size.strip() if self.original_size else self.size
        
        # 确保列表不为None
        if self.images is None:
            self.images = []
        
        # 设置更新时间
        self.updated_at = datetime.now()


@dataclass
class TemuCategory:
    """Temu分类数据"""
    category_id: str
    name: str
    parent_id: Optional[str] = None
    level: int = 1
    is_leaf: bool = True
    children: List['TemuCategory'] = field(default_factory=list)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.category_id or not self.category_id.strip():
            raise ValueError("分类ID不能为空")
        
        if not self.name or not self.name.strip():
            raise ValueError("分类名称不能为空")
        
        # 清理数据
        self.category_id = self.category_id.strip()
        self.name = self.name.strip()
        
        # 确保列表不为None
        if self.children is None:
            self.children = []


@dataclass
class TemuSizeChart:
    """Temu尺码表数据"""
    chart_id: str
    category_id: str
    size_type: str
    elements: List[str] = field(default_factory=list)
    measurements: Dict[str, Dict[str, float]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.chart_id or not self.chart_id.strip():
            raise ValueError("尺码表ID不能为空")
        
        if not self.category_id or not self.category_id.strip():
            raise ValueError("分类ID不能为空")
        
        if not self.size_type or not self.size_type.strip():
            raise ValueError("尺码类型不能为空")
        
        # 清理数据
        self.chart_id = self.chart_id.strip()
        self.category_id = self.category_id.strip()
        self.size_type = self.size_type.strip()
        
        # 确保列表和字典不为None
        if self.elements is None:
            self.elements = []
        if self.measurements is None:
            self.measurements = {}


@dataclass
class TemuImage:
    """Temu图片数据"""
    image_id: str
    url: str
    image_type: str  # main, detail, size, etc.
    width: int
    height: int
    file_size: int
    format: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        if not self.image_id or not self.image_id.strip():
            raise ValueError("图片ID不能为空")
        
        if not self.url or not self.url.strip():
            raise ValueError("图片URL不能为空")
        
        if self.width <= 0 or self.height <= 0:
            raise ValueError("图片尺寸必须大于0")
        
        if self.file_size <= 0:
            raise ValueError("图片文件大小必须大于0")
        
        # 清理数据
        self.image_id = self.image_id.strip()
        self.url = self.url.strip()
        self.image_type = self.image_type.strip() if self.image_type else "main"


@dataclass
class TemuListingResult:
    """Temu上架结果"""
    success: bool
    product_id: Optional[str] = None
    sku_ids: List[str] = field(default_factory=list)
    image_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """数据验证和清理"""
        # 确保列表不为None
        if self.sku_ids is None:
            self.sku_ids = []
        if self.image_ids is None:
            self.image_ids = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
