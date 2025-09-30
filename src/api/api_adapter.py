"""
API适配器

统一新旧API接口，提供平滑迁移能力
"""

import os
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from ..utils.logger import get_logger
from ..utils.exceptions import AutoTemuException
from ..models.product import TemuProduct, TemuSKU
from ..models.data_models import CreateProductResult
from ..models.bg_models import BgGoodsAddData
from .bg_client import BgGoodsClient, create_bg_client, BgApiException
from ..transform.bg_transformer import BgDataTransformer

logger = get_logger(__name__)


@dataclass
class ApiAdapterConfig:
    """API适配器配置"""
    use_new_api: bool = True
    fallback_enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    debug: bool = False


class ApiAdapterException(AutoTemuException):
    """API适配器异常"""
    pass


class ApiAdapter:
    """API适配器，统一新旧API接口"""
    
    def __init__(self, config: ApiAdapterConfig = None, 
                 bg_client: BgGoodsClient = None, temu_client = None):
        """
        初始化API适配器
        
        Args:
            config: 适配器配置
            bg_client: 新API客户端
            temu_client: 旧API客户端
        """
        self.config = config or ApiAdapterConfig()
        
        # 初始化新API客户端
        if self.config.use_new_api:
            if bg_client:
                self.bg_client = bg_client
            else:
                try:
                    self.bg_client = create_bg_client(debug=self.config.debug)
                    logger.info("新API客户端初始化成功")
                except Exception as e:
                    logger.error(f"新API客户端初始化失败: {e}")
                    if not self.config.fallback_enabled:
                        raise ApiAdapterException(f"新API客户端初始化失败: {e}")
                    self.bg_client = None
        else:
            self.bg_client = None
        
        # 初始化旧API客户端（用于降级）
        if self.config.fallback_enabled or not self.config.use_new_api:
            self.temu_client = temu_client
            if not self.temu_client:
                try:
                    from temu_api import TemuClient
                    self.temu_client = TemuClient(
                        app_key=os.getenv("TEMU_APP_KEY"),
                        app_secret=os.getenv("TEMU_APP_SECRET"),
                        access_token=os.getenv("TEMU_ACCESS_TOKEN"),
                        base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
                        debug=self.config.debug
                    )
                    logger.info("旧API客户端初始化成功")
                except Exception as e:
                    logger.warning(f"旧API客户端初始化失败: {e}")
                    self.temu_client = None
        else:
            self.temu_client = None
        
        # 初始化数据转换器
        self.bg_transformer = BgDataTransformer()
        
        logger.info(f"API适配器初始化完成: use_new_api={self.config.use_new_api}, "
                   f"fallback_enabled={self.config.fallback_enabled}")
    
    def create_product(self, product_data: Union[TemuProduct, dict], 
                      context: Dict[str, Any] = None) -> CreateProductResult:
        """
        统一的商品创建接口
        
        Args:
            product_data: 商品数据
            context: 上下文信息（如上传的图片、分类模板等）
            
        Returns:
            创建结果
        """
        context = context or {}
        
        logger.info(f"开始创建商品: use_new_api={self.config.use_new_api}")
        
        try:
            if self.config.use_new_api and self.bg_client:
                return self._create_with_new_api(product_data, context)
            elif self.temu_client:
                return self._create_with_old_api(product_data, context)
            else:
                raise ApiAdapterException("没有可用的API客户端")
                
        except BgApiException as e:
            logger.error(f"新API调用失败: {e}")
            
            # 尝试降级到旧API
            if self.config.fallback_enabled and self.temu_client:
                logger.info("降级到旧API重试")
                try:
                    return self._create_with_old_api(product_data, context)
                except Exception as fallback_e:
                    logger.error(f"降级API也失败: {fallback_e}")
                    raise ApiAdapterException(f"新API失败: {e}, 降级API也失败: {fallback_e}")
            else:
                raise ApiAdapterException(f"新API调用失败: {e}")
                
        except Exception as e:
            logger.error(f"商品创建异常: {e}")
            raise ApiAdapterException(f"商品创建失败: {e}")
    
    def _create_with_new_api(self, product_data: Union[TemuProduct, dict], 
                           context: Dict[str, Any]) -> CreateProductResult:
        """使用新API创建商品"""
        logger.info("使用新API创建商品")
        
        # 转换数据格式
        if isinstance(product_data, TemuProduct):
            bg_data = self.bg_transformer.transform_product(
                temu_product=product_data,
                uploaded_images=context.get('uploaded_images', []),
                category_template=context.get('category_template'),
                spec_ids=context.get('spec_ids', {})
            )
        elif isinstance(product_data, dict):
            bg_data = BgGoodsAddData(**product_data)
        else:
            raise ApiAdapterException(f"不支持的商品数据类型: {type(product_data)}")
        
        # 验证数据
        is_valid, errors = bg_data.validate()
        if not is_valid:
            raise ApiAdapterException(f"商品数据验证失败: {', '.join(errors)}")
        
        # 调用新API
        try:
            result = self.bg_client.goods_add(bg_data)
            
            # 解析结果
            result_data = result.get("result", {})
            product_id = result_data.get("productId")
            
            # 提取SKU ID列表
            sku_ids = []
            if "goodsSkuList" in result_data:
                sku_ids = [
                    sku.get("skuId") for sku in result_data["goodsSkuList"] 
                    if sku.get("skuId")
                ]
            
            return CreateProductResult(
                success=True,
                goods_id=product_id,
                sku_ids=sku_ids,
                api_response=result,
                created_at=time.time()
            )
            
        except Exception as e:
            logger.error(f"新API商品创建失败: {e}")
            return CreateProductResult(
                success=False,
                error_message=str(e),
                api_response={"error": str(e)}
            )
    
    def _create_with_old_api(self, product_data: Union[TemuProduct, dict], 
                           context: Dict[str, Any]) -> CreateProductResult:
        """使用旧API创建商品"""
        logger.info("使用旧API创建商品")
        
        try:
            # 构建旧API格式的数据
            if isinstance(product_data, dict) and "goods_basic" in product_data:
                # 已经是旧API格式
                old_api_data = product_data
            else:
                # 需要转换为旧API格式
                old_api_data = self._convert_to_old_api_format(product_data, context)
            
            # 调用旧API
            result = self.temu_client.product.goods_add(**old_api_data)
            
            if result.get("success"):
                result_obj = result.get("result", {})
                product_id = result_obj.get("goodsId")
                
                # 尝试解析SKU列表
                sku_ids = []
                try:
                    sku_list = result_obj.get("goodsSkuList", [])
                    sku_ids = [sku.get("skuId") for sku in sku_list if sku.get("skuId")]
                except Exception:
                    pass
                
                return CreateProductResult(
                    success=True,
                    goods_id=product_id,
                    sku_ids=sku_ids,
                    api_response=result
                )
            else:
                error_msg = result.get("errorMsg", "未知错误")
                return CreateProductResult(
                    success=False,
                    error_message=error_msg,
                    api_response=result
                )
                
        except Exception as e:
            logger.error(f"旧API商品创建失败: {e}")
            return CreateProductResult(
                success=False,
                error_message=str(e),
                api_response={"error": str(e)}
            )
    
    def _convert_to_old_api_format(self, product_data: Union[TemuProduct, dict], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """将数据转换为旧API格式"""
        # 这里应该实现到旧API格式的转换
        # 为了简化，我们返回一个基本的格式
        if isinstance(product_data, TemuProduct):
            return {
                "goods_basic": {
                    "goodsName": product_data.title,
                    "catId": product_data.category_id or "30847",
                    "hdThumbUrl": product_data.images[0] if product_data.images else "",
                    "carouselImageList": product_data.images[:10]
                },
                "goods_service_promise": {
                    "shipmentLimitDay": 2,
                    "fulfillmentType": 1,
                    "costTemplateId": "LFT-14230731738276073558"
                },
                "goods_property": {
                    "goodsProperties": [],
                    "goodsSpecProperties": []
                },
                "sku_list": [],
                "goods_desc": product_data.description
            }
        else:
            return product_data
    
    def upload_image(self, image_url: str, **kwargs) -> str:
        """
        统一的图片上传接口
        
        Args:
            image_url: 图片URL
            **kwargs: 其他参数
            
        Returns:
            上传后的图片URL
        """
        logger.info(f"上传图片: {image_url[:80]}...")
        
        try:
            if self.config.use_new_api and self.bg_client:
                return self.bg_client.image_upload(image_url, **kwargs)
            elif self.temu_client:
                # 使用旧API上传
                result = self.temu_client.product.image_upload(file_url=image_url, **kwargs)
                if result.get("success"):
                    result_data = result.get("result", {})
                    return (
                        result_data.get("url") or
                        result_data.get("imageUrl") or
                        result_data.get("hdThumbUrl") or
                        image_url
                    )
                else:
                    raise ApiAdapterException(f"图片上传失败: {result.get('errorMsg')}")
            else:
                raise ApiAdapterException("没有可用的API客户端")
                
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            raise ApiAdapterException(f"图片上传失败: {e}")
    
    def get_categories(self, parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        统一的分类查询接口
        
        Args:
            parent_id: 父分类ID
            
        Returns:
            分类列表
        """
        try:
            if self.config.use_new_api and self.bg_client:
                result = self.bg_client.cats_get(parent_cat_id=parent_id)
                if result.get("success"):
                    return result.get("result", {}).get("goodsCatsList", [])
            elif self.temu_client:
                result = self.temu_client.product.cats_get(parent_cat_id=parent_id)
                if result.get("success"):
                    return result.get("result", {}).get("goodsCatsList", [])
            
            return []
            
        except Exception as e:
            logger.error(f"分类查询失败: {e}")
            return []
    
    def recommend_category(self, product_name: str, description: str = None, 
                         image_url: str = None) -> Dict[str, Any]:
        """
        统一的分类推荐接口
        
        Args:
            product_name: 商品名称
            description: 商品描述
            image_url: 商品图片
            
        Returns:
            推荐的分类信息
        """
        try:
            if self.config.use_new_api and self.bg_client:
                return self.bg_client.category_recommend(
                    goods_name=product_name,
                    description=description,
                    image_url=image_url
                )
            elif self.temu_client:
                return self.temu_client.product.category_recommend(
                    goods_name=product_name,
                    description=description,
                    image_url=image_url
                )
            else:
                return {"success": False, "errorMsg": "没有可用的API客户端"}
                
        except Exception as e:
            logger.error(f"分类推荐失败: {e}")
            return {"success": False, "errorMsg": str(e)}
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            是否连接成功
        """
        try:
            if self.config.use_new_api and self.bg_client:
                return self.bg_client.test_connection()
            elif self.temu_client:
                result = self.temu_client.product.cats_get(parent_cat_id=0)
                return result.get("success", False)
            else:
                return False
                
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        获取API状态信息
        
        Returns:
            API状态字典
        """
        return {
            "use_new_api": self.config.use_new_api,
            "fallback_enabled": self.config.fallback_enabled,
            "new_api_available": self.bg_client is not None,
            "old_api_available": self.temu_client is not None,
            "new_api_connected": self.bg_client.test_connection() if self.bg_client else False,
            "old_api_connected": self._test_old_api_connection() if self.temu_client else False
        }
    
    def _test_old_api_connection(self) -> bool:
        """测试旧API连接"""
        try:
            result = self.temu_client.product.cats_get(parent_cat_id=0)
            return result.get("success", False)
        except Exception:
            return False
    
    def switch_to_new_api(self):
        """切换到新API"""
        self.config.use_new_api = True
        logger.info("已切换到新API")
    
    def switch_to_old_api(self):
        """切换到旧API"""
        self.config.use_new_api = False
        logger.info("已切换到旧API")
    
    def enable_fallback(self):
        """启用降级机制"""
        self.config.fallback_enabled = True
        logger.info("已启用API降级机制")
    
    def disable_fallback(self):
        """禁用降级机制"""
        self.config.fallback_enabled = False
        logger.info("已禁用API降级机制")


def create_api_adapter(use_new_api: bool = None, fallback_enabled: bool = None, 
                      debug: bool = None, **kwargs) -> ApiAdapter:
    """
    创建API适配器
    
    Args:
        use_new_api: 是否使用新API（从环境变量获取）
        fallback_enabled: 是否启用降级（从环境变量获取）
        debug: 调试模式（从环境变量获取）
        **kwargs: 其他配置参数
        
    Returns:
        API适配器实例
    """
    # 从环境变量获取配置
    if use_new_api is None:
        use_new_api = os.getenv("USE_NEW_API", "true").lower() == "true"
    
    if fallback_enabled is None:
        fallback_enabled = os.getenv("API_FALLBACK_ENABLED", "true").lower() == "true"
    
    if debug is None:
        debug = os.getenv("DEBUG", "false").lower() == "true"
    
    config = ApiAdapterConfig(
        use_new_api=use_new_api,
        fallback_enabled=fallback_enabled,
        debug=debug,
        **kwargs
    )
    
    return ApiAdapter(config)


# 测试代码
if __name__ == "__main__":
    # 测试适配器
    try:
        adapter = create_api_adapter(debug=False)
        
        # 测试连接
        status = adapter.get_api_status()
        print(f"API状态: {status}")
        
        # 测试分类查询
        categories = adapter.get_categories(parent_id=0)
        print(f"分类查询成功: {len(categories)} 个分类")
        
    except Exception as e:
        print(f"测试失败: {e}")
