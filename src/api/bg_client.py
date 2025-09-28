"""
新的bg.goods.add API客户端

实现基于新API规范的TEMU商品管理客户端
"""

import time
import json
import requests
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin
import os

from ..utils.logger import get_logger
from ..utils.bg_signature import SignatureHelper, get_current_timestamp
from ..utils.retry import api_retry
from ..models.bg_models import BgGoodsAddData

logger = get_logger(__name__)


class BgApiException(Exception):
    """新API相关异常"""
    def __init__(self, message: str, error_code: str = None, response: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response


class SignatureException(BgApiException):
    """签名相关异常"""
    pass


class RequestException(BgApiException):
    """请求相关异常"""
    pass


class BgGoodsClient:
    """新的bg.goods.add API客户端"""
    
    def __init__(self, app_key: str, app_secret: str, access_token: str, 
                 base_url: str = None, debug: bool = False, timeout: int = 30):
        """
        初始化客户端
        
        Args:
            app_key: 应用key
            app_secret: 应用密钥
            access_token: 访问令牌
            base_url: API基础URL
            debug: 调试模式
            timeout: 请求超时时间（秒）
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = base_url or "https://openapi.kuajingmaihuo.com/openapi/router"
        self.debug = debug
        self.timeout = timeout
        
        # 初始化签名助手
        self.signature_helper = SignatureHelper(app_key, app_secret, debug)
        
        # 初始化session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AutoTemu-BgClient/1.0'
        })
        
        logger.info(f"BgGoodsClient初始化成功: app_key={app_key[:10]}***, debug={debug}")
    
    def _log_api_call(self, method: str, params: Dict[str, Any], response: dict):
        """记录API调用日志"""
        if self.debug:
            logger.debug(f"API调用: {method}")
            logger.debug(f"请求参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
            logger.debug(f"响应结果: {json.dumps(response, ensure_ascii=False, indent=2)}")
        else:
            logger.info(f"API调用: {method}, 成功: {response.get('success', False)}")
    
    def _make_request(self, api_method: str, data: Dict[str, Any], 
                     require_auth: bool = True) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            api_method: API方法名
            data: 请求数据
            require_auth: 是否需要认证
            
        Returns:
            API响应结果
            
        Raises:
            BgApiException: API调用异常
        """
        try:
            # 构建并签名请求
            params = self.signature_helper.sign_request(
                api_method=api_method,
                data=data,
                access_token=self.access_token if require_auth else None
            )
            
            # 发送请求
            response = self.session.post(
                self.base_url,
                json=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 记录日志
            self._log_api_call(api_method, params, result)
            
            # 检查业务错误
            if not result.get("success", False):
                error_code = result.get("errorCode", "UNKNOWN")
                error_msg = result.get("errorMsg", "未知错误")
                raise BgApiException(f"API调用失败: {error_msg}", error_code, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求异常: {e}")
            raise RequestException(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析异常: {e}")
            raise RequestException(f"响应解析失败: {e}")
        except BgApiException as e:
            # 保留服务端原始错误码与响应
            raise e
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            # 透传可能的 error_code/response 字段，避免信息丢失
            error_code = getattr(e, "error_code", None)
            response = getattr(e, "response", None)
            raise BgApiException(f"API请求失败: {e}", error_code, response)
    
    @api_retry(max_attempts=3)
    def goods_add(self, product_data: Union[BgGoodsAddData, dict]) -> Dict[str, Any]:
        """
        调用bg.goods.add接口创建商品
        
        Args:
            product_data: 商品数据
            
        Returns:
            创建结果
        """
        logger.info("调用bg.goods.add接口创建商品")
        
        # 转换数据格式
        if isinstance(product_data, BgGoodsAddData):
            data = product_data.to_dict()
        else:
            data = product_data
        
        # 验证数据
        if isinstance(product_data, BgGoodsAddData):
            is_valid, errors = product_data.validate()
            if not is_valid:
                raise BgApiException(f"商品数据验证失败: {', '.join(errors)}")
        
        # 需要鉴权
        result = self._make_request("bg.goods.add", data, require_auth=True)
        
        logger.info(f"商品创建成功: productId={result.get('result', {}).get('productId')}")
        return result
    
    @api_retry(max_attempts=5)
    def image_upload(self, file_url: str, scaling_type: int = 1, 
                    compression_type: int = 1, format_conversion_type: int = 0) -> str:
        """
        上传图片
        
        Args:
            file_url: 图片URL或本地文件路径
            scaling_type: 缩放类型（1:800x800, 2:1350x1800）
            compression_type: 压缩类型
            format_conversion_type: 格式转换类型
            
        Returns:
            上传后的图片URL
        """
        logger.info(f"上传图片: {file_url[:80]}...")
        
        # 按文档使用驼峰命名参数
        data = {
            "fileUrl": file_url,
            "scalingType": scaling_type,
            "compressionType": compression_type,
            "formatConversionType": format_conversion_type,
            "imageBizType": 1
        }
        
        # 使用已授权的全局图片上传接口
        # 使用商品图片上传接口
        result = self._make_request("bg.goods.image.upload", data, require_auth=True)
        
        # 提取图片URL
        result_data = result.get("result", {})
        image_url = (
            result_data.get("url") or
            result_data.get("imageUrl") or
            result_data.get("hdThumbUrl") or
            result_data.get("fileUrl")
        )
        
        if not image_url:
            raise BgApiException("图片上传失败: 响应中没有图片URL")
        
        logger.info(f"图片上传成功: {image_url}")
        return image_url
    
    def cats_get(self, parent_cat_id: int = 0) -> Dict[str, Any]:
        """
        查询商品分类
        
        Args:
            parent_cat_id: 父分类ID（0为根分类）
            
        Returns:
            分类信息
        """
        logger.info(f"查询商品分类: parent_cat_id={parent_cat_id}")
        
        data = {
            "parent_cat_id": parent_cat_id
        }
        
        result = self._make_request("bg.goods.cats.get", data, require_auth=True)
        return result
    
    def category_recommend(self, goods_name: str, description: str = None, 
                          image_url: str = None, expand_cat_type: int = None) -> Dict[str, Any]:
        """
        获取分类推荐
        
        Args:
            goods_name: 商品名称
            description: 商品描述
            image_url: 商品图片URL
            expand_cat_type: 扩展分类类型
            
        Returns:
            推荐的分类信息
        """
        logger.info(f"获取分类推荐: {goods_name}")
        
        data = {
            "goods_name": goods_name
        }
        
        if description:
            data["description"] = description
        if image_url:
            data["image_url"] = image_url
        if expand_cat_type is not None:
            data["expand_cat_type"] = expand_cat_type
        
        result = self._make_request("bg.goods.category.recommend", data)
        return result

    def category_mapping(self, goods_name: str, description: str = None,
                         image_url: str = None, top_k: int = None) -> Dict[str, Any]:
        """
        根据商品标题映射推荐类目
        
        Args:
            goods_name: 商品标题
            description: 描述（可选）
            image_url: 图片URL（可选）
            top_k: 返回TopK候选（可选）
        
        Returns:
            映射类目结果
        """
        logger.info(f"类目映射: {goods_name}")
        # 按平台参数命名：goodsName/imageUrl/topK
        data = {"goodsName": goods_name}
        if description:
            data["description"] = description
        if image_url:
            data["imageUrl"] = image_url
        if top_k is not None:
            data["topK"] = top_k
        # 需要鉴权
        result = self._make_request("bg.goods.category.mapping", data, require_auth=True)
        return result
    
    def template_get(self, cat_id: str) -> Dict[str, Any]:
        """
        获取分类模板
        
        Args:
            cat_id: 分类ID
            
        Returns:
            分类模板信息
        """
        logger.info(f"获取分类模板: cat_id={cat_id}")
        
        data = {
            "cat_id": cat_id
        }
        
        result = self._make_request("bg.goods.template.get", data)
        return result
    
    def parentspec_get(self, cat_id: int) -> Dict[str, Any]:
        """
        获取父规格列表（如 颜色/尺码）
        """
        logger.info(f"获取父规格: cat_id={cat_id}")
        data = {"cat_id": cat_id}
        return self._make_request("bg.goods.parentspec.get", data, require_auth=True)

    def spec_id_get(self, cat_id: int, parent_spec_id: int, child_spec_name: str) -> Dict[str, Any]:
        """
        获取规格ID
        
        Args:
            cat_id: 分类ID
            parent_spec_id: 父规格ID
            child_spec_name: 子规格名称
            
        Returns:
            规格ID信息
        """
        logger.info(f"获取规格ID: cat_id={cat_id}, parent_spec_id={parent_spec_id}, child_spec_name={child_spec_name}")
        
        # 文档为 bg.goods.spec.create（创建规格并返回 specId），若存在 id.get 也可能参数为 camelCase
        data = {
            "catId": cat_id,
            "parentSpecId": parent_spec_id,
            "childSpecName": child_spec_name
        }
        try:
            # 优先尝试 create
            result = self._make_request("bg.goods.spec.create", data, require_auth=True)
        except Exception:
            # 回退尝试 id.get（部分网关存在），并使用 snake_case
            data_fallback = {
                "cat_id": cat_id,
                "parent_spec_id": parent_spec_id,
                "child_spec_name": child_spec_name
            }
            result = self._make_request("bg.goods.spec.id.get", data_fallback, require_auth=True)
        return result

    def attrs_get(self, cat_id: int) -> Dict[str, Any]:
        """
        获取类目属性列表（包含是否必填及候选值）
        """
        logger.info(f"获取类目属性: cat_id={cat_id}")
        # 接口要求叶子类目ID，按文档为 camelCase: leafCatId
        data = {"leafCatId": cat_id}
        return self._make_request("bg.goods.attrs.get", data, require_auth=True)

    def catsmandatory_get(self, leaf_cat_id: int) -> Dict[str, Any]:
        """
        获取类目必填属性模板（可用于组装 productPropertyReqs）
        """
        logger.info(f"获取类目必填属性模板: leaf_cat_id={leaf_cat_id}")
        data = {"leafCatId": leaf_cat_id}
        return self._make_request("bg.goods.catsmandatory.get", data, require_auth=True)

    def add_property_get(self, leaf_cat_id: int) -> Dict[str, Any]:
        """
        获取发品属性模板（网关可能为 bg.goods.add.property）
        """
        logger.info(f"获取发品属性模板: leaf_cat_id={leaf_cat_id}")
        data = {"leafCatId": leaf_cat_id}
        try:
            return self._make_request("bg.goods.add.property", data, require_auth=True)
        except Exception:
            # 一些网关可能使用 snake_case 参数
            data2 = {"leaf_cat_id": leaf_cat_id}
            return self._make_request("bg.goods.add.property", data2, require_auth=True)
    
    def sizecharts_get(self, page: int = 1, page_size: int = 20, offset: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        查询尺码表列表
        
        Args:
            page: 页码
            page_size: 页大小
            
        Returns:
            尺码表列表
        """
        logger.info(f"查询尺码表列表: page={page}, page_size={page_size}, offset={offset}, limit={limit}")
        
        # 一些网关要求使用 offset/limit；兼容 page/pageSize -> 计算 offset/limit
        if offset is None:
            offset = max(0, (page - 1) * page_size)
        if limit is None:
            limit = page_size

        # 仅传递 offset/limit，避免参数歧义报错
        data = {
            "offset": offset,
            "limit": limit
        }
        
        result = self._make_request("bg.goods.sizecharts.get", data)
        return result
    
    def sizecharts_template_create(self, cat_id: str = None, business_id: str = None) -> Dict[str, Any]:
        """
        创建尺码表模板
        
        Args:
            cat_id: 分类ID
            business_id: 业务ID
            
        Returns:
            创建结果
        """
        logger.info(f"创建尺码表模板: cat_id={cat_id}, business_id={business_id}")
        
        data = {}
        if cat_id:
            data["catId"] = cat_id
        if business_id:
            data["businessId"] = business_id
        
        result = self._make_request("bg.goods.sizecharts.template.create", data)
        return result
    
    def sizecharts_create(self, meta: Dict[str, Any], values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        创建尺码表
        
        Args:
            meta: 尺码表元数据
            values: 尺码表数据
            
        Returns:
            创建结果
        """
        logger.info(f"创建尺码表: meta={meta}, values_count={len(values)}")
        
        data = {
            "meta": meta,
            "values": values
        }
        
        result = self._make_request("bg.goods.sizecharts.create", data)
        return result
    
    def sizecharts_class_get(self, cat_id: str = None, class_type: int = None) -> Dict[str, Any]:
        """
        查询尺码表分类
        
        Args:
            cat_id: 分类ID
            class_type: 分类类型（1为套装）
            
        Returns:
            尺码表分类信息
        """
        logger.info(f"查询尺码表分类: cat_id={cat_id}, class_type={class_type}")
        
        data = {}
        if cat_id:
            data["catId"] = cat_id
        if class_type is not None:
            data["classType"] = class_type
        
        result = self._make_request("bg.goods.sizecharts.class.get", data)
        return result
    
    def sizecharts_settings_get(self, class_id: str) -> Dict[str, Any]:
        """
        查询尺码表设置
        
        Args:
            class_id: 分类ID
            
        Returns:
            尺码表设置信息
        """
        logger.info(f"查询尺码表设置: class_id={class_id}")
        
        data = {
            "classId": class_id
        }
        
        result = self._make_request("bg.goods.sizecharts.settings.get", data)
        return result
    
    def sizecharts_meta_get(self, class_id: str = None, cat_id: str = None) -> Dict[str, Any]:
        """
        查询尺码表元数据
        
        Args:
            class_id: 分类ID（套装时使用）
            cat_id: 分类ID（非套装时使用）
            
        Returns:
            尺码表元数据
        """
        logger.info(f"查询尺码表元数据: class_id={class_id}, cat_id={cat_id}")
        
        data = {}
        if class_id:
            data["classId"] = class_id
        if cat_id:
            data["catId"] = cat_id
        
        result = self._make_request("bg.goods.sizecharts.meta.get", data)
        return result
    
    def texttopicture_add(self, text: str, style: Dict[str, Any], 
                         width: int = 750, height: int = 1200) -> Dict[str, Any]:
        """
        文字转图片
        
        Args:
            text: 文字内容
            style: 样式配置
            width: 图片宽度
            height: 图片高度
            
        Returns:
            生成的图片URL
        """
        logger.info(f"文字转图片: text_length={len(text)}, width={width}, height={height}")
        
        data = {
            "text": text,
            "style": style,
            "width": width,
            "height": height
        }
        
        result = self._make_request("bg.goods.texttopicture.add", data)
        return result
    
    def colorimageurl_get(self, color_value: str) -> Dict[str, Any]:
        """
        色块图转换
        
        Args:
            color_value: 颜色值
            
        Returns:
            色块图URL
        """
        logger.info(f"色块图转换: color_value={color_value}")
        
        data = {
            "color_value": color_value
        }
        
        result = self._make_request("bg.colorimageurl.get", data)
        return result
    
    def goods_list_get(self, page: int = 1, page_size: int = 20, **kwargs) -> Dict[str, Any]:
        """
        查询货品列表
        
        Args:
            page: 页码
            page_size: 页大小
            **kwargs: 其他筛选条件
            
        Returns:
            货品列表
        """
        logger.info(f"查询货品列表: page={page}, page_size={page_size}")
        
        data = {
            "page": page,
            "pageSize": page_size
        }
        data.update(kwargs)
        
        result = self._make_request("bg.goods.list.get", data)
        return result
    
    def goods_detail_get(self, product_id: str) -> Dict[str, Any]:
        """
        查询货品详情
        
        Args:
            product_id: 货品ID
            
        Returns:
            货品详情
        """
        logger.info(f"查询货品详情: product_id={product_id}")
        
        data = {
            "productId": product_id
        }
        
        result = self._make_request("bg.goods.detail.get", data)
        return result
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            是否连接成功
        """
        try:
            result = self.cats_get(parent_cat_id=0)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭客户端"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def create_bg_client(app_key: str = None, app_secret: str = None, 
                    access_token: str = None, **kwargs) -> BgGoodsClient:
    """
    创建BG API客户端
    
    Args:
        app_key: 应用key（可从环境变量获取）
        app_secret: 应用密钥（可从环境变量获取）
        access_token: 访问令牌（可从环境变量获取）
        **kwargs: 其他参数
        
    Returns:
        BG API客户端实例
    """
    # 从环境变量获取配置
    if not app_key:
        app_key = os.getenv("BG_APP_KEY") or os.getenv("TEMU_APP_KEY")
    if not app_secret:
        app_secret = os.getenv("BG_APP_SECRET") or os.getenv("TEMU_APP_SECRET")
    if not access_token:
        access_token = (
            os.getenv("BG_APP_ACCESS_TOKEN")
            or os.getenv("BG_ACCESS_TOKEN")
            or os.getenv("TEMU_ACCESS_TOKEN")
        )
    
    if not all([app_key, app_secret, access_token]):
        raise ValueError("缺少必要的API配置: app_key, app_secret, access_token")
    
    return BgGoodsClient(
        app_key=app_key,
        app_secret=app_secret,
        access_token=access_token,
        **kwargs
    )


# 测试代码
if __name__ == "__main__":
    # 测试客户端创建
    try:
        client = create_bg_client(debug=True)
        print("客户端创建成功")
        
        # 测试连接
        is_connected = client.test_connection()
        print(f"连接测试: {'成功' if is_connected else '失败'}")
        
        # 测试分类查询
        categories = client.cats_get(parent_cat_id=0)
        print(f"分类查询成功: {len(categories.get('result', {}).get('goodsCatsList', []))} 个分类")
        
    except Exception as e:
        print(f"测试失败: {e}")
