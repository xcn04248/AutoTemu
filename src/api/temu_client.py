"""
Temu API客户端

封装Temu API的各种功能，包括商品创建、SKU管理、图片上传等
"""

import requests
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.config import get_config
from ..utils.exceptions import TemuAPIException, AuthenticationException, RateLimitException, APIResponseException
from ..utils.retry import retry
from ..models.product import TemuProduct, TemuSKU, TemuListingResult, TemuCategory, TemuSizeChart

logger = get_logger(__name__)


class TemuAPIClient:
    """Temu API客户端"""

    def __init__(self, config=None):
        """
        初始化Temu API客户端
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or get_config()
        self.base_url = self.config.temu_base_url
        self.app_key = self.config.temu_app_key
        self.app_secret = self.config.temu_app_secret
        self.access_token = self.config.temu_access_token
        
        # API版本
        self.api_version = "1.0"
        
        # 请求超时时间
        self.timeout = 30

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成API签名
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 按参数名排序
        sorted_params = sorted(params.items())
        
        # 构建签名字符串
        sign_string = ""
        for key, value in sorted_params:
            if value is not None:
                sign_string += f"{key}={value}&"
        
        # 移除最后的&
        sign_string = sign_string.rstrip("&")
        
        # 添加app_secret
        sign_string += f"&app_secret={self.app_secret}"
        
        # 计算HMAC-SHA256签名
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature

    def _prepare_request_params(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备请求参数
        
        Args:
            method: API方法名
            params: 业务参数
            
        Returns:
            完整的请求参数
        """
        # 基础参数
        request_params = {
            "app_key": self.app_key,
            "access_token": self.access_token,
            "method": method,
            "timestamp": str(int(time.time() * 1000)),
            "version": self.api_version,
            "format": "json",
            "charset": "utf-8",
            "sign_method": "hmac-sha256",
        }
        
        # 添加业务参数
        request_params.update(params)
        
        # 生成签名
        signature = self._generate_signature(request_params)
        request_params["sign"] = signature
        
        return request_params

    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: API方法名
            params: 业务参数
            
        Returns:
            API响应数据
            
        Raises:
            TemuAPIException: API请求失败
        """
        try:
            # 准备请求参数
            request_params = self._prepare_request_params(method, params)
            
            # 发送POST请求
            response = requests.post(
                self.base_url,
                data=request_params,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "AutoTemu/1.0"
                }
            )
            
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 检查API响应状态
            if result.get("code") != 0:
                error_code = result.get("code", "UNKNOWN")
                error_message = result.get("message", "Unknown error")
                
                # 根据错误码抛出特定异常
                if error_code == "AUTH_ERROR":
                    raise AuthenticationException(f"认证失败: {error_message}")
                elif error_code == "RATE_LIMIT":
                    retry_after = result.get("retry_after", 60)
                    raise RateLimitException(f"请求频率限制: {error_message}", retry_after=retry_after)
                else:
                    raise APIResponseException(
                        f"API请求失败: {error_message}",
                        api_code=error_code,
                        api_message=error_message
                    )
            
            return result.get("data", {})
            
        except (AuthenticationException, RateLimitException, APIResponseException):
            # 重新抛出特定异常，不包装
            raise
        except requests.RequestException as e:
            raise TemuAPIException(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise TemuAPIException(f"响应解析失败: {str(e)}")
        except Exception as e:
            raise TemuAPIException(f"API请求异常: {str(e)}")

    def get_category_recommend(self, title: str, description: str = "") -> List[TemuCategory]:
        """
        获取商品分类推荐
        
        Args:
            title: 商品标题
            description: 商品描述
            
        Returns:
            推荐分类列表
        """
        params = {
            "title": title,
            "description": description
        }
        
        result = self._make_request("category_recommend", params)
        
        # 解析分类数据
        categories = []
        for item in result.get("categories", []):
            category = TemuCategory(
                category_id=item.get("category_id"),
                name=item.get("category_name"),
                parent_id=item.get("parent_id"),
                level=item.get("level", 1),
                is_leaf=item.get("is_leaf", True)
            )
            categories.append(category)
        
        logger.info(f"获取分类推荐成功: {len(categories)} 个分类")
        return categories

    def get_size_chart_elements(self, category_id: str, size_type: str) -> List[str]:
        """
        获取尺码表元素
        
        Args:
            category_id: 分类ID
            size_type: 尺码类型
            
        Returns:
            尺码表元素列表
        """
        params = {
            "category_id": category_id,
            "size_type": size_type
        }
        
        result = self._make_request("size_element_get", params)
        
        elements = result.get("elements", [])
        logger.info(f"获取尺码表元素成功: {len(elements)} 个元素")
        return elements

    def upload_image(self, image_path: str, image_type: str = "main") -> str:
        """
        上传图片
        
        Args:
            image_path: 图片文件路径
            image_type: 图片类型 (main, detail, size)
            
        Returns:
            图片ID
        """
        try:
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 准备上传参数
            params = {
                "image_type": image_type,
                "image_data": image_data.hex()  # 转换为十六进制字符串
            }
            
            result = self._make_request("image_upload", params)
            
            image_id = result.get("image_id")
            if not image_id:
                raise TemuAPIException("上传图片失败: 未返回图片ID")
            
            logger.info(f"图片上传成功: {image_path} -> {image_id}")
            return image_id
            
        except FileNotFoundError:
            raise TemuAPIException(f"图片文件不存在: {image_path}")
        except Exception as e:
            raise TemuAPIException(f"上传图片失败: {str(e)}")

    def batch_upload_images(self, image_paths: List[str], image_types: List[str] = None) -> List[str]:
        """
        批量上传图片
        
        Args:
            image_paths: 图片文件路径列表
            image_types: 图片类型列表，如果为None则默认为main
            
        Returns:
            图片ID列表
        """
        if image_types is None:
            image_types = ["main"] * len(image_paths)
        
        if len(image_paths) != len(image_types):
            raise TemuAPIException("图片路径和类型数量不匹配")
        
        image_ids = []
        for image_path, image_type in zip(image_paths, image_types):
            try:
                image_id = self.upload_image(image_path, image_type)
                image_ids.append(image_id)
            except Exception as e:
                logger.error(f"上传图片失败: {image_path}, 错误: {str(e)}")
                # 继续上传其他图片
                continue
        
        logger.info(f"批量上传图片完成: {len(image_ids)}/{len(image_paths)} 成功")
        return image_ids

    def create_product(self, product: TemuProduct, category_id: str) -> str:
        """
        创建商品
        
        Args:
            product: Temu商品对象
            category_id: 分类ID
            
        Returns:
            商品ID
        """
        params = {
            "title": product.title,
            "description": product.description,
            "category_id": category_id,
            "price": product.markup_price,
            "currency": product.currency,
            "size_type": product.size_type,
            "images": product.images
        }
        
        result = self._make_request("goods_add", params)
        
        product_id = result.get("product_id")
        if not product_id:
            raise TemuAPIException("创建商品失败: 未返回商品ID")
        
        logger.info(f"商品创建成功: {product.title} -> {product_id}")
        return product_id

    def create_sku(self, product_id: str, sku: TemuSKU) -> str:
        """
        创建SKU
        
        Args:
            product_id: 商品ID
            sku: Temu SKU对象
            
        Returns:
            SKU ID
        """
        params = {
            "product_id": product_id,
            "sku_id": sku.sku_id,
            "size": sku.size,
            "price": sku.price,
            "stock_quantity": sku.stock_quantity,
            "size_chart_element": sku.size_chart_element,
            "images": sku.images
        }
        
        result = self._make_request("sku_add", params)
        
        sku_id = result.get("sku_id")
        if not sku_id:
            raise TemuAPIException("创建SKU失败: 未返回SKU ID")
        
        logger.info(f"SKU创建成功: {sku.sku_id} -> {sku_id}")
        return sku_id

    def batch_create_skus(self, product_id: str, skus: List[TemuSKU]) -> List[str]:
        """
        批量创建SKU
        
        Args:
            product_id: 商品ID
            skus: Temu SKU对象列表
            
        Returns:
            SKU ID列表
        """
        sku_ids = []
        for sku in skus:
            try:
                sku_id = self.create_sku(product_id, sku)
                sku_ids.append(sku_id)
            except Exception as e:
                logger.error(f"创建SKU失败: {sku.sku_id}, 错误: {str(e)}")
                # 继续创建其他SKU
                continue
        
        logger.info(f"批量创建SKU完成: {len(sku_ids)}/{len(skus)} 成功")
        return sku_ids

    def list_product(self, product: TemuProduct, skus: List[TemuSKU], category_id: str) -> TemuListingResult:
        """
        上架商品（创建商品和SKU）
        
        Args:
            product: Temu商品对象
            skus: Temu SKU对象列表
            category_id: 分类ID
            
        Returns:
            上架结果
        """
        result = TemuListingResult(success=False)
        
        try:
            # 上传图片
            if product.images:
                image_ids = self.batch_upload_images(product.images)
                result.image_ids = image_ids
                logger.info(f"图片上传完成: {len(image_ids)} 张")
            
            # 创建商品
            product_id = self.create_product(product, category_id)
            result.product_id = product_id
            logger.info(f"商品创建完成: {product_id}")
            
            # 创建SKU
            if skus:
                sku_ids = self.batch_create_skus(product_id, skus)
                result.sku_ids = sku_ids
                logger.info(f"SKU创建完成: {len(sku_ids)} 个")
            
            result.success = True
            logger.info(f"商品上架成功: {product.title}")
            
        except Exception as e:
            error_msg = f"商品上架失败: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
        
        return result

    def get_product_status(self, product_id: str) -> Dict[str, Any]:
        """
        获取商品状态
        
        Args:
            product_id: 商品ID
            
        Returns:
            商品状态信息
        """
        params = {
            "product_id": product_id
        }
        
        result = self._make_request("goods_get", params)
        
        logger.info(f"获取商品状态成功: {product_id}")
        return result

    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新商品信息
        
        Args:
            product_id: 商品ID
            updates: 更新字段
            
        Returns:
            是否更新成功
        """
        params = {
            "product_id": product_id,
            **updates
        }
        
        self._make_request("goods_update", params)
        
        logger.info(f"商品更新成功: {product_id}")
        return True

    def delete_product(self, product_id: str) -> bool:
        """
        删除商品
        
        Args:
            product_id: 商品ID
            
        Returns:
            是否删除成功
        """
        params = {
            "product_id": product_id
        }
        
        self._make_request("goods_delete", params)
        
        logger.info(f"商品删除成功: {product_id}")
        return True

    def get_api_quota(self) -> Dict[str, Any]:
        """
        获取API配额信息
        
        Returns:
            API配额信息
        """
        result = self._make_request("quota_get", {})
        
        logger.info("获取API配额信息成功")
        return result

    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否正常
        """
        try:
            self.get_api_quota()
            logger.info("API连接测试成功")
            return True
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return False
