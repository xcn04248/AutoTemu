"""
新API数据转换器

将现有的TemuProduct数据转换为BgGoodsAddData格式
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

from ..utils.logger import get_logger
from ..models.product import TemuProduct, TemuSKU
from ..models.bg_models import (
    BgGoodsAddData, BgProductSkcReq, BgProductSkuReq, 
    BgProductProperty, BgProductSpecProperty, BgProductSkuSpecReq,
    BgProductSkuWhExtAttrReq, BgProductSkuWeightReq, BgProductSkuVolumeReq,
    BgProductSkuSensitiveAttrReq, BgMainProductSkuSpecReq,
    BgProductI18nReq, BgCarouselImageI18nReq, BgGoodsLayerDecorationReq,
    BgProductOrigin, BgProductWhExtAttrReq, BgProductOuterPackageReq,
    BgProductSemiManagedReq, BgProductShipmentReq, BgSiteSupplierPrice,
    PackageShape, PackageType
)

logger = get_logger(__name__)


class BgDataTransformer:
    """新API数据转换器"""
    
    def __init__(self):
        """初始化转换器"""
        # 价格转换配置
        self.cny_to_jpy_rate = Decimal(os.getenv("TEMU_CNY_TO_JPY_RATE", "20"))
        
        # 默认图片处理配置
        self.default_image_scaling_type = int(os.getenv("BG_SCALING_TYPE", "1"))
        
        # 默认运费模板ID
        self.default_freight_template_id = os.getenv(
            "TEMU_FREIGHT_TEMPLATE_ID", 
            "LFT-14230731738276073558"  # 日本物流模版
        )
        
        logger.info("BgDataTransformer初始化成功")
    
    def transform_product(self, temu_product: TemuProduct, 
                         uploaded_images: List[str] = None,
                         category_template: Dict[str, Any] = None,
                         spec_ids: Dict[str, int] = None) -> BgGoodsAddData:
        """
        转换商品数据为新API格式
        
        Args:
            temu_product: 原有商品数据
            uploaded_images: 已上传的图片URL列表
            category_template: 分类模板数据
            spec_ids: 规格ID映射
            
        Returns:
            转换后的BG API数据
        """
        logger.info(f"开始转换商品数据: {temu_product.title}")
        
        # 使用默认图片如果没有提供
        if not uploaded_images:
            uploaded_images = temu_product.images[:10] if temu_product.images else []
        
        # 构建基础数据
        bg_data = BgGoodsAddData(
            # 类目信息（需要外部提供完整的分类层级）
            cat1Id=self._extract_cat_id(temu_product.category_id, 1),
            cat2Id=self._extract_cat_id(temu_product.category_id, 2),
            cat3Id=self._extract_cat_id(temu_product.category_id, 3),
            
            # 基础信息
            productName=temu_product.title,
            carouselImageUrls=uploaded_images[:10],  # 最多10张轮播图
            materialImgUrl=uploaded_images[0] if uploaded_images else "",
            
            # 构建属性
            productPropertyReqs=self._build_product_properties(category_template, temu_product),
            productSpecPropertyReqs=self._build_spec_properties(spec_ids, temu_product),
            
            # 构建SKC和SKU
            productSkcReqs=self._build_product_skc_reqs(temu_product, uploaded_images, spec_ids),
            
            # 尺码表（如果有）
            sizeTemplateIds=[],  # 需要外部提供
            
            # 外包装信息
            productOuterPackageReq=BgProductOuterPackageReq(
                packageShape=PackageShape.IRREGULAR.value,
                packageType=PackageType.SOFT_SOFT.value
            ),
            
            # 产地信息
            productWhExtAttrReq=BgProductWhExtAttrReq(
                productOrigin=BgProductOrigin(
                    region1ShortName="CN",
                    region2Id=None
                )
            ),
            
            # 商详装饰（使用描述）
            goodsLayerDecorationReqs=self._build_goods_layer_decoration(temu_product.description)
        )
        
        # 添加多语言标题（如果需要）
        if self._is_semi_managed():
            bg_data.productI18nReqs = [
                BgProductI18nReq(language="en", productName=temu_product.title)
            ]
        
        # 添加半托管配置（如果是半托管）
        if self._is_semi_managed():
            bg_data.productSemiManagedReq = BgProductSemiManagedReq(
                bindSiteIds=[300],  # 日本站
                semiLanguageStrategy=1  # 本地语种
            )
            
            bg_data.productShipmentReq = BgProductShipmentReq(
                freightTemplateId=self.default_freight_template_id,
                shipmentLimitSecond=172800  # 2天
            )
        
        # 确保每个SKU携带规格列表（默认以尺码为规格）
        for skc in bg_data.productSkcReqs:
            # 确保主规格列表不为空
            if not skc.mainProductSkuSpecReqs:
                skc.mainProductSkuSpecReqs.append(
                    BgMainProductSkuSpecReq(
                        parentSpecId=3001,
                        parentSpecName="Size",
                        specId=0,
                        specName="Size"
                    )
                )
            # 为每个SKU添加规格属性
            for sku in skc.productSkuReqs:
                if not sku.productSkuSpecReqs and sku.extCode:
                    # 从extCode推断对应的Temu SKU尺寸
                    infer_size = "M"  # 默认尺寸
                    try:
                        # 根据extCode推断尺寸
                        if "_001" in sku.extCode:
                            infer_size = "S"
                        elif "_002" in sku.extCode:
                            infer_size = "M"
                        elif "_003" in sku.extCode:
                            infer_size = "L"
                        elif "_004" in sku.extCode:
                            infer_size = "XL"
                        elif "_005" in sku.extCode:
                            infer_size = "2XL"
                        elif "_006" in sku.extCode:
                            infer_size = "3XL"
                    except Exception:
                        pass
                    sku.productSkuSpecReqs.append(
                        BgProductSkuSpecReq(
                            parentSpecId=3001,
                            parentSpecName="Size",
                            specId=0,
                            specName=infer_size
                        )
                    )

        # 确保商品属性列表不为空，避免 Base Property Value 为空
        if not bg_data.productPropertyReqs:
            bg_data.productPropertyReqs = []

        # 将外部商品链接映射为扩展编码，便于溯源（商品/SKC/SKU）
        try:
            if getattr(temu_product, 'source_url', None):
                # 商品级：写入首个SKC的extCode
                if bg_data.productSkcReqs:
                    bg_data.productSkcReqs[0].extCode = temu_product.source_url
                # SKU级：附加不同后缀确保唯一
                counter = 1
                for skc in bg_data.productSkcReqs:
                    for sku in skc.productSkuReqs:
                        suffix = f"#{counter:03d}"
                        sku.extCode = (temu_product.source_url + suffix)
                        counter += 1
        except Exception:
            pass

        logger.info(
            f"商品数据转换完成: {len(bg_data.productSkcReqs)} SKC, "
            f"{sum(len(skc.productSkuReqs) for skc in bg_data.productSkcReqs)} SKU"
        )
        return bg_data
    
    def _extract_cat_id(self, category_id: str, level: int) -> int:
        """
        提取分类ID的指定层级
        
        Args:
            category_id: 分类ID字符串
            level: 层级（1-10）
            
        Returns:
            对应层级的分类ID
        """
        try:
            if not category_id:
                return 0
            
            # 简单处理：如果是单个ID，则根据层级返回
            cat_id = int(category_id)
            if level <= 3:
                return cat_id
            else:
                return 0
        except (ValueError, TypeError):
            return 0
    
    def _build_product_properties(self, template: Dict[str, Any], 
                                 product: TemuProduct) -> List[BgProductProperty]:
        """
        构建商品属性
        
        Args:
            template: 分类模板
            product: 商品数据
            
        Returns:
            商品属性列表
        """
        properties = []
        
        if not template:
            return properties
        
        # 处理必填属性
        property_list = template.get("propertyList", [])
        for prop in property_list:
            if not prop.get("required", False):
                continue
            
            # 构建属性值
            prop_value = self._get_property_value(prop, product)
            
            bg_prop = BgProductProperty(
                templatePid=prop.get("templatePid", 0),
                pid=prop.get("pid", 0),
                refPid=prop.get("refPid", 0),
                propName=prop.get("name", ""),
                vid=self._get_property_vid(prop, prop_value),
                propValue=prop_value,
                valueUnit=prop.get("valueUnit", [""])[0] if prop.get("valueUnit") else "",
                numberInputValue="",
                valueExtendInfo=""
            )
            
            properties.append(bg_prop)
        
        logger.info(f"构建了 {len(properties)} 个商品属性")
        return properties
    
    def _build_spec_properties(self, spec_ids: Dict[str, int], 
                              product: TemuProduct) -> List[BgProductSpecProperty]:
        """
        构建规格属性
        
        Args:
            spec_ids: 规格ID映射
            product: 商品数据
            
        Returns:
            规格属性列表
        """
        spec_properties = []
        
        if not product.skus:
            return spec_properties
        
        # 提取唯一尺码
        sizes = []
        for sku in product.skus:
            size = (sku.size or "").strip()
            if size and size not in sizes:
                sizes.append(size)
        
        # 为每个尺码创建规格属性
        for size in sizes:
            spec_prop = BgProductSpecProperty(
                templatePid=0,
                pid=0,
                refPid=0,
                propName="Size",
                vid=0,
                propValue=size,
                valueUnit="",
                parentSpecId=3001,  # 默认Size父规格ID
                parentSpecName="Size",
                specId=spec_ids.get(size, 0) if spec_ids else 0,
                specName=size,
                valueGroupId=0,
                valueGroupName="",
                numberInputValue="",
                valueExtendInfo=""
            )
            spec_properties.append(spec_prop)
        
        logger.info(f"构建了 {len(spec_properties)} 个规格属性")
        return spec_properties
    
    def _build_product_skc_reqs(self, product: TemuProduct, uploaded_images: List[str],
                               spec_ids: Dict[str, int] = None) -> List[BgProductSkcReq]:
        """
        构建SKC请求列表
        
        Args:
            product: 商品数据
            uploaded_images: 已上传图片列表
            spec_ids: 规格ID映射
            
        Returns:
            SKC请求列表
        """
        if not product.skus:
            return []
        
        # 简化处理：创建一个SKC包含所有SKU
        skc_req = BgProductSkcReq(
            previewImgUrls=uploaded_images[:5] if uploaded_images else [],
            extCode=f"SKC_{int(time.time())}",
            mainProductSkuSpecReqs=[
                BgMainProductSkuSpecReq(
                    parentSpecId=3001,
                    parentSpecName="Size",
                    specId=0,
                    specName="Size"
                )
            ],
            productSkuReqs=self._build_product_sku_reqs(product.skus, uploaded_images, spec_ids)
        )
        
        return [skc_req]
    
    def _build_product_sku_reqs(self, skus: List[TemuSKU], uploaded_images: List[str],
                               spec_ids: Dict[str, int] = None) -> List[BgProductSkuReq]:
        """
        构建SKU请求列表
        
        Args:
            skus: SKU列表
            uploaded_images: 已上传图片列表
            spec_ids: 规格ID映射
            
        Returns:
            SKU请求列表
        """
        sku_reqs = []
        
        for i, sku in enumerate(skus):
            # 价格转换
            jpy_price = self._convert_price_to_jpy(sku.price)
            
            # 构建规格
            sku_spec_reqs = []
            if spec_ids and sku.size and sku.size in spec_ids:
                sku_spec_reqs.append(
                    BgProductSkuSpecReq(
                        parentSpecId=3001,
                        specId=spec_ids[sku.size],
                        parentSpecName="Size",
                        specName=sku.size
                    )
                )
            
            # 构建扩展属性
            ext_attr = BgProductSkuWhExtAttrReq(
                productSkuWeightReq=BgProductSkuWeightReq(value=300000),  # 300g in mg
                productSkuVolumeReq=BgProductSkuVolumeReq(
                    len=300, width=250, height=20  # mm
                ),
                productSkuSensitiveAttrReq=BgProductSkuSensitiveAttrReq(
                    isSensitive=0,
                    sensitiveList=[]
                )
            )
            
            # 选择SKU图片
            sku_image = uploaded_images[i % len(uploaded_images)] if uploaded_images else ""
            
            sku_req = BgProductSkuReq(
                thumbUrl=sku_image,
                extCode=f"SKU_{int(time.time())}_{i+1:03d}",
                currencyType="JPY",
                productSkuSpecReqs=sku_spec_reqs,
                productSkuWhExtAttrReq=ext_attr
            )
            
            # 添加价格（根据是否半托管）
            if self._is_semi_managed():
                sku_req.siteSupplierPrices = [
                    BgSiteSupplierPrice(siteId=300, supplierPrice=jpy_price)  # 日本站
                ]
            else:
                sku_req.supplierPrice = jpy_price
            
            sku_reqs.append(sku_req)
        
        logger.info(f"构建了 {len(sku_reqs)} 个SKU")
        return sku_reqs
    
    def _build_goods_layer_decoration(self, description: str) -> List[BgGoodsLayerDecorationReq]:
        """
        构建商详装饰
        
        Args:
            description: 商品描述
            
        Returns:
            商详装饰列表
        """
        if not description or not description.strip():
            return []
        
        # 简化处理：将描述作为文字楼层
        from ..models.bg_models import BgGoodsLayerContentText
        
        decoration = BgGoodsLayerDecorationReq(
            type="text",
            key="DecImage",
            priority=0,
            lang="zh",
            contentList=[
                BgGoodsLayerContentText(
                    height=200,
                    text=description[:500],  # 限制长度
                    textModuleDetails={
                        "align": "left",
                        "backgroundColor": "#fff",
                        "fontColor": "#333",
                        "fontSize": 12
                    },
                    width=750
                )
            ]
        )
        
        return [decoration]
    
    def _get_property_value(self, prop: Dict[str, Any], product: TemuProduct) -> str:
        """
        获取属性值
        
        Args:
            prop: 属性定义
            product: 商品数据
            
        Returns:
            属性值
        """
        prop_name = prop.get("name", "").lower()
        
        # 根据属性名称返回合适的值
        if "age" in prop_name or "applicable" in prop_name:
            return "Adult"
        elif "material" in prop_name:
            return "Cotton"
        elif "color" in prop_name:
            return "Multi"
        elif "size" in prop_name:
            return "M"
        elif "gender" in prop_name:
            return "Unisex"
        elif "style" in prop_name:
            return "Casual"
        else:
            # 尝试从属性值列表中选择第一个
            values = prop.get("values", [])
            if values and len(values) > 0:
                return values[0].get("value", "Default")
            return "Default"
    
    def _get_property_vid(self, prop: Dict[str, Any], prop_value: str) -> int:
        """
        获取属性值ID
        
        Args:
            prop: 属性定义
            prop_value: 属性值
            
        Returns:
            属性值ID
        """
        values = prop.get("values", [])
        for value in values:
            if value.get("value") == prop_value:
                return value.get("vid", 0)
        return 0
    
    def _convert_price_to_jpy(self, cny_price: float) -> int:
        """
        将人民币价格转换为日元价格（分）
        
        Args:
            cny_price: 人民币价格
            
        Returns:
            日元价格（分）
        """
        try:
            cny_decimal = Decimal(str(cny_price))
            jpy_decimal = (cny_decimal * self.cny_to_jpy_rate).quantize(
                Decimal('1'), rounding=ROUND_HALF_UP
            )
            return int(jpy_decimal)
        except (ValueError, TypeError):
            logger.warning(f"价格转换失败: {cny_price}")
            return 100  # 默认价格
    
    def _is_semi_managed(self) -> bool:
        """
        判断是否为半托管模式
        
        Returns:
            是否半托管
        """
        return os.getenv("TEMU_MODE", "semi").lower() == "semi"
    
    def validate_transformed_data(self, bg_data: BgGoodsAddData) -> Tuple[bool, List[str]]:
        """
        验证转换后的数据
        
        Args:
            bg_data: 转换后的数据
            
        Returns:
            (是否有效, 错误列表)
        """
        return bg_data.validate()
    
    def get_transform_summary(self, original_product: TemuProduct, 
                            bg_data: BgGoodsAddData) -> Dict[str, Any]:
        """
        获取转换摘要
        
        Args:
            original_product: 原始商品数据
            bg_data: 转换后的数据
            
        Returns:
            转换摘要
        """
        return {
            "original_title": original_product.title,
            "transformed_title": bg_data.productName,
            "original_sku_count": len(original_product.skus) if original_product.skus else 0,
            "transformed_skc_count": len(bg_data.productSkcReqs),
            "transformed_sku_count": sum(len(skc.productSkuReqs) for skc in bg_data.productSkcReqs),
            "image_count": len(bg_data.carouselImageUrls),
            "property_count": len(bg_data.productPropertyReqs),
            "spec_property_count": len(bg_data.productSpecPropertyReqs),
            "has_decoration": len(bg_data.goodsLayerDecorationReqs) > 0,
            "is_semi_managed": bg_data.productSemiManagedReq is not None
        }
