"""
新API数据模型定义

基于bg.goods.add接口的数据结构定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json


class PackageShape(Enum):
    """包装形状枚举"""
    IRREGULAR = 0    # 不规则形状
    CUBOID = 1       # 长方体
    CYLINDER = 2     # 圆柱体


class PackageType(Enum):
    """包装类型枚举"""
    HARD = 0         # 硬包装
    SOFT_HARD = 1    # 软包装+硬物
    SOFT_SOFT = 2    # 软包装+软物


class SensitiveType(Enum):
    """敏感属性类型枚举"""
    PURE_ELECTRIC = 110001      # 纯电
    INTERNAL_ELECTRIC = 120001  # 内电
    MAGNETISM = 130001          # 磁性
    LIQUID = 140001             # 液体
    POWDER = 150001             # 粉末
    PASTE = 160001              # 膏体
    CUTTER = 170001             # 刀具


@dataclass
class BgProductProperty:
    """商品属性"""
    valueUnit: str = ""
    propValue: str = ""
    propName: str = ""
    refPid: int = 0
    vid: int = 0
    pid: int = 0
    templatePid: int = 0
    numberInputValue: str = ""
    valueExtendInfo: str = ""


@dataclass
class BgProductSpecProperty:
    """商品规格属性"""
    templatePid: int = 0
    pid: int = 0
    refPid: int = 0
    propName: str = ""
    vid: int = 0
    propValue: str = ""
    valueUnit: str = ""
    parentSpecId: int = 0
    parentSpecName: str = ""
    specId: int = 0
    specName: str = ""
    valueGroupId: int = 0
    valueGroupName: str = ""
    numberInputValue: str = ""
    valueExtendInfo: str = ""


@dataclass
class BgProductSkuSpecReq:
    """SKU规格请求"""
    parentSpecId: int
    specId: int
    parentSpecName: str = ""
    specName: str = ""
    isBasePlate: Optional[int] = None


@dataclass
class BgProductSkuWeightReq:
    """SKU重量请求"""
    value: int  # 重量（mg）


@dataclass
class BgProductSkuVolumeReq:
    """SKU体积请求"""
    len: int    # 长度（mm）
    width: int  # 宽度（mm）
    height: int # 高度（mm）


@dataclass
class BgProductSkuBarCodeReq:
    """SKU条码请求"""
    code: str
    codeType: int  # 1:EAN 2:UPC 3:ISBN


@dataclass
class BgProductSkuSensitiveAttrReq:
    """SKU敏感属性请求"""
    isSensitive: int  # 0:非敏感 1:敏感
    sensitiveList: List[int] = field(default_factory=list)


@dataclass
class BgProductSkuSensitiveLimitReq:
    """SKU敏感限制请求"""
    maxBatteryCapacity: Optional[int] = None  # 电池容量
    Wh: Optional[int] = None                  # 电量（Wh）
    μL: Optional[int] = None                  # 液体容量（μL）
    mm: Optional[int] = None                  # 刀具长度（mm）
    μm: Optional[int] = None                  # 其他尺寸（μm）
    knifeTipAngle: Optional[Dict[str, int]] = None  # 刀尖角度


@dataclass
class BgProductSkuWhExtAttrReq:
    """SKU扩展属性请求"""
    productSkuWeightReq: BgProductSkuWeightReq
    productSkuVolumeReq: BgProductSkuVolumeReq
    productSkuBarCodeReqs: List[BgProductSkuBarCodeReq] = field(default_factory=list)
    productSkuSensitiveAttrReq: Optional[BgProductSkuSensitiveAttrReq] = None
    productSkuSensitiveLimitReq: Optional[BgProductSkuSensitiveLimitReq] = None


@dataclass
class BgProductSkuThumbUrlI18nReq:
    """SKU缩略图多语言请求"""
    language: str
    imgUrlList: List[str]


@dataclass
class BgSiteSupplierPrice:
    """站点供货价"""
    siteId: int
    supplierPrice: int  # 站点申报价格（分/美分）


@dataclass
class BgProductSkuReq:
    """商品SKU请求"""
    thumbUrl: str
    extCode: Optional[str] = None
    currencyType: str = "CNY"
    supplierPrice: Optional[int] = None  # 全托供货价
    siteSupplierPrices: List[BgSiteSupplierPrice] = field(default_factory=list)  # 半托站点供货价
    productSkuSpecReqs: List[BgProductSkuSpecReq] = field(default_factory=list)
    productSkuWhExtAttrReq: Optional[BgProductSkuWhExtAttrReq] = None
    productSkuThumbUrlI18nReqs: List[BgProductSkuThumbUrlI18nReq] = field(default_factory=list)


@dataclass
class BgMainProductSkuSpecReq:
    """主规格请求"""
    parentSpecId: int = 0
    parentSpecName: str = ""
    specId: int = 0
    specName: str = ""
    isBasePlate: Optional[int] = None


@dataclass
class BgProductSkcCarouselImageI18nReq:
    """SKC轮播图多语言请求"""
    language: str
    imgUrlList: List[str]


@dataclass
class BgProductSkcReq:
    """商品SKC请求"""
    previewImgUrls: List[str]
    extCode: Optional[str] = None
    colorImageUrl: Optional[str] = None
    mainProductSkuSpecReqs: List[BgMainProductSkuSpecReq] = field(default_factory=list)
    productSkcCarouselImageI18nReqs: List[BgProductSkcCarouselImageI18nReq] = field(default_factory=list)
    productSkuReqs: List[BgProductSkuReq] = field(default_factory=list)


@dataclass
class BgCarouselImageI18nReq:
    """轮播图多语言请求"""
    language: str
    imgUrlList: List[str]


@dataclass
class BgProductI18nReq:
    """商品多语言请求"""
    language: str
    productName: str


@dataclass
class BgGoodsLayerContentText:
    """商详楼层文字内容"""
    height: int
    text: str
    textModuleDetails: Dict[str, Any]
    width: int


@dataclass
class BgGoodsLayerContentImage:
    """商详楼层图片内容"""
    height: int
    imgUrl: str
    width: int


@dataclass
class BgGoodsLayerDecorationReq:
    """商详装饰请求"""
    type: str  # "image" 或 "text"
    key: str = "DecImage"
    priority: int = 0
    lang: str = "zh"
    floorId: Optional[int] = None
    contentList: List[Union[BgGoodsLayerContentImage, BgGoodsLayerContentText]] = field(default_factory=list)


@dataclass
class BgGoodsModelReq:
    """模特信息请求"""
    modelProfileUrl: Optional[str] = None
    sizeSpecName: str = ""
    sizeSpecId: int = 0
    modelId: int = 0
    modelName: str = ""
    modelFeature: int = 1  # 1:真实模特
    modelType: int = 1     # 1:成衣模特 2:鞋模
    modelHeight: Optional[str] = None
    modelWaist: Optional[str] = None
    modelBust: Optional[str] = None
    modelHip: Optional[str] = None
    modelFootWidth: Optional[str] = None  # 鞋模专用
    modelFootLength: Optional[str] = None # 鞋模专用
    tryOnResult: int = 1  # 1:舒适 2:紧身 3:宽松


@dataclass
class BgProductOrigin:
    """产地信息"""
    region1ShortName: str  # 一级区域简称（如 CN, US）
    region2Id: Optional[int] = None  # 二级区域id（CN必传）


@dataclass
class BgProductWhExtAttrReq:
    """商品扩展属性请求"""
    productOrigin: BgProductOrigin


@dataclass
class BgProductCarouseVideoReq:
    """主图视频请求"""
    vid: str
    coverUrl: str
    videoUrl: str
    width: int
    height: int


@dataclass
class BgProductSkuSuggestedPriceReq:
    """建议零售价请求"""
    specialSuggestedPrice: str = "NA"  # 特殊建议价规则


@dataclass
class BgProductSkuNetContentReq:
    """净含量请求"""
    netContentUnitCode: int  # 净含量单位
    netContentNumber: int    # 净含量数值


@dataclass
class BgProductSkuMultiPackReq:
    """多包规请求"""
    numberOfPieces: int
    productSkuNetContentReq: BgProductSkuNetContentReq


@dataclass
class BgProductSecondHandReq:
    """二手信息请求"""
    isSecondHand: bool
    secondHandLevel: int  # 1:接近全新 2:状况极佳 3:良好 4:尚可


@dataclass
class BgProductNoChargerReq:
    """无充电器版本请求"""
    noChargerProductIds: List[str]  # 至少1，至多3


@dataclass
class BgProductOuterPackageImageReq:
    """外包装图片请求"""
    imageUrl: str


@dataclass
class BgProductOuterPackageReq:
    """外包装信息请求"""
    packageShape: int  # PackageShape枚举值
    packageType: int   # PackageType枚举值


@dataclass
class BgProductSemiManagedReq:
    """半托管信息请求"""
    bindSiteIds: List[int]
    semiManagedSiteMode: Optional[int] = None  # 欧盟区发品必填：1:泛欧 2:非泛欧
    semiLanguageStrategy: Optional[int] = None # 1:本地语种 2:英语及其他


@dataclass
class BgProductShipmentReq:
    """配送信息请求"""
    freightTemplateId: str
    shipmentLimitSecond: int  # 承诺发货时间（秒）


@dataclass
class BgWarehouseStockQuantityReq:
    """仓库库存请求"""
    warehouseId: str
    targetStockAvailable: int


@dataclass
class BgProductSkuStockQuantityReq:
    """SKU库存请求"""
    warehouseStockQuantityReqs: List[BgWarehouseStockQuantityReq]


@dataclass
class BgProductWarehouseRouteReq:
    """仓库路由请求"""
    targetRouteList: List[Dict[str, Any]]  # 包含siteIdList和warehouseId


@dataclass
class BgProductGuideFileReq:
    """说明书文件请求"""
    fileName: str
    pdfMaterialId: int
    languages: List[str]


@dataclass
class BgGoodsAddData:
    """bg.goods.add接口完整数据模型"""
    
    # 必填字段
    cat1Id: int
    productName: str
    carouselImageUrls: List[str]
    materialImgUrl: str
    
    # 可选分类字段
    cat2Id: int = 0
    cat3Id: int = 0
    cat4Id: int = 0
    cat5Id: int = 0
    cat6Id: int = 0
    cat7Id: int = 0
    cat8Id: int = 0
    cat9Id: int = 0
    cat10Id: int = 0
    
    productPropertyReqs: List[BgProductProperty] = field(default_factory=list)
    productSpecPropertyReqs: List[BgProductSpecProperty] = field(default_factory=list)
    productSkcReqs: List[BgProductSkcReq] = field(default_factory=list)
    sizeTemplateIds: List[str] = field(default_factory=list)
    productOuterPackageReq: BgProductOuterPackageReq = field(
        default_factory=lambda: BgProductOuterPackageReq(
            packageShape=PackageShape.IRREGULAR.value,
            packageType=PackageType.SOFT_SOFT.value
        )
    )
    productWhExtAttrReq: BgProductWhExtAttrReq = field(
        default_factory=lambda: BgProductWhExtAttrReq(
            productOrigin=BgProductOrigin(region1ShortName="CN")
        )
    )
    
    # 可选字段
    productI18nReqs: List[BgProductI18nReq] = field(default_factory=list)
    carouselImageI18nReqs: List[BgCarouselImageI18nReq] = field(default_factory=list)
    productOuterPackageImageReqs: List[BgProductOuterPackageImageReq] = field(default_factory=list)
    goodsLayerDecorationReqs: List[BgGoodsLayerDecorationReq] = field(default_factory=list)
    goodsModelReqs: List[BgGoodsModelReq] = field(default_factory=list)
    productCarouseVideoReqList: List[BgProductCarouseVideoReq] = field(default_factory=list)
    productSkuSuggestedPriceReq: Optional[BgProductSkuSuggestedPriceReq] = None
    productSkuMultiPackReq: Optional[BgProductSkuMultiPackReq] = None
    skuClassification: int = 1  # 1:单品 2:同款多件装 3:混合套装
    pieceUnitCode: int = 1      # 1:件 2:双 3:包
    individuallyPacked: Optional[int] = None  # 当skuClassification为2或3时必填
    productSecondHandReq: Optional[BgProductSecondHandReq] = None
    productNoChargerReq: Optional[BgProductNoChargerReq] = None
    showSizeTemplateIds: List[str] = field(default_factory=list)  # ≤2个重点展示尺码表
    productSemiManagedReq: Optional[BgProductSemiManagedReq] = None
    productShipmentReq: Optional[BgProductShipmentReq] = None
    productSkuStockQuantityReq: Optional[BgProductSkuStockQuantityReq] = None
    productWarehouseRouteReq: Optional[BgProductWarehouseRouteReq] = None
    productGuideFileReqs: List[BgProductGuideFileReq] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {}
        
        # 处理基本字段
        for field_name, field_value in self.__dict__.items():
            if field_value is None:
                continue
            
            if isinstance(field_value, list) and len(field_value) == 0:
                continue
                
            if hasattr(field_value, 'to_dict'):
                result[field_name] = field_value.to_dict()
            elif isinstance(field_value, list):
                result[field_name] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in field_value
                ]
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            else:
                result[field_name] = field_value
        
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def validate(self) -> tuple[bool, List[str]]:
        """验证数据完整性"""
        errors = []
        
        # 验证必填字段
        if not self.productName or not self.productName.strip():
            errors.append("商品名称不能为空")
        
        if not self.carouselImageUrls:
            errors.append("轮播图不能为空")
        
        if not self.materialImgUrl or not self.materialImgUrl.strip():
            errors.append("素材图不能为空")
        
        if not self.productSkcReqs:
            errors.append("SKC列表不能为空")
        
        # 验证类目至少到cat3Id
        if self.cat1Id == 0 or self.cat2Id == 0 or self.cat3Id == 0:
            errors.append("类目至少需要填写到三级分类")
        
        # 验证SKC和SKU结构
        for i, skc in enumerate(self.productSkcReqs):
            if not skc.previewImgUrls:
                errors.append(f"SKC[{i}]预览图不能为空")
            
            if not skc.productSkuReqs:
                errors.append(f"SKC[{i}]的SKU列表不能为空")
            
            for j, sku in enumerate(skc.productSkuReqs):
                if not sku.thumbUrl or not sku.thumbUrl.strip():
                    errors.append(f"SKC[{i}]SKU[{j}]缩略图不能为空")
                
                if not sku.currencyType or not sku.currencyType.strip():
                    errors.append(f"SKC[{i}]SKU[{j}]货币类型不能为空")
        
        return len(errors) == 0, errors


# 添加便捷的数据结构方法
def to_dict(obj) -> dict:
    """递归转换dataclass对象为字典"""
    if hasattr(obj, '__dataclass_fields__'):
        return {
            field_name: to_dict(field_value)
            for field_name, field_value in obj.__dict__.items()
            if field_value is not None
        }
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj


# 为所有dataclass添加to_dict方法
for cls in [BgProductProperty, BgProductSpecProperty, BgProductSkuSpecReq, 
           BgProductSkuWeightReq, BgProductSkuVolumeReq, BgProductSkuBarCodeReq,
           BgProductSkuSensitiveAttrReq, BgProductSkuSensitiveLimitReq, 
           BgProductSkuWhExtAttrReq, BgProductSkuThumbUrlI18nReq,
           BgSiteSupplierPrice, BgProductSkuReq, BgMainProductSkuSpecReq,
           BgProductSkcCarouselImageI18nReq, BgProductSkcReq, 
           BgCarouselImageI18nReq, BgProductI18nReq, BgGoodsLayerContentText,
           BgGoodsLayerContentImage, BgGoodsLayerDecorationReq, BgGoodsModelReq,
           BgProductOrigin, BgProductWhExtAttrReq, BgProductCarouseVideoReq,
           BgProductSkuSuggestedPriceReq, BgProductSkuNetContentReq,
           BgProductSkuMultiPackReq, BgProductSecondHandReq, BgProductNoChargerReq,
           BgProductOuterPackageImageReq, BgProductOuterPackageReq,
           BgProductSemiManagedReq, BgProductShipmentReq,
           BgWarehouseStockQuantityReq, BgProductSkuStockQuantityReq,
           BgProductWarehouseRouteReq, BgProductGuideFileReq]:
    if not hasattr(cls, 'to_dict'):
        setattr(cls, 'to_dict', lambda self: to_dict(self))
