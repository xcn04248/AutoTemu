"""
商品管理器 - 生产环境的核心商品添加逻辑
"""

import os
import sys
import time
import json
import hashlib
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 加载环境变量
load_dotenv()

# 导入项目模块
from src.scraper.product_scraper import ProductScraper
from src.image.image_processor import ImageProcessor
from src.image.ocr_client import OCRClient
from src.image.size_chart_processor import SizeChartProcessor
from src.transform.data_transformer import DataTransformer
from src.transform.size_mapper import SizeMapper
from temu_api import TemuClient
from src.models.data_models import ProductData
from src.api.api_adapter import ApiAdapter
from src.api.bg_client import BgGoodsClient
from src.transform.bg_transformer import BgDataTransformer
from PIL import Image
import io
import requests
from src.utils.logger import get_logger

logger = get_logger("product_manager")


class ProductManager:
    """商品管理器 - 生产环境的核心商品添加逻辑"""
    
    def __init__(self, use_new_api: bool = True):
        """初始化商品管理器"""
        # 初始化各个模块
        self.scraper = ProductScraper()
        self.ocr_client = OCRClient()
        self.image_processor = ImageProcessor(self.ocr_client)
        self.size_chart_processor = SizeChartProcessor()
        self.size_mapper = SizeMapper()
        self.data_transformer = DataTransformer(self.size_mapper)
        
        # 根据配置选择API客户端
        self.use_new_api = use_new_api
        if use_new_api:
            # 初始化新版API客户端
            from src.utils.config import get_config
            config = get_config()
            self.bg_client = BgGoodsClient(
                app_key=config.bg_app_key,
                app_secret=config.bg_app_secret,
                access_token=config.bg_access_token,
                base_url=config.bg_base_url,
                debug=False
            )
            self.bg_transformer = BgDataTransformer()
            self.api_adapter = ApiAdapter()
            logger.info("使用新版API客户端 (bg.goods.add)")
        else:
            # 初始化旧版API客户端
            self.temu_client = TemuClient(
                app_key=os.getenv("TEMU_APP_KEY"),
                app_secret=os.getenv("TEMU_APP_SECRET"),
                access_token=os.getenv("TEMU_ACCESS_TOKEN"),
                base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
                debug=False
            )
            logger.info("使用旧版API客户端 (bg.local.goods.add)")
        
        # 缓存数据
        self.scraped_product = None
        self.temu_product = None
        self.categories_cache = {}
        self.leaf_categories_cache = {}
        self.templates_cache = {}
        self.spec_ids_cache = {}
        self.uploaded_images_cache = []
        self.size_chart_cache = None
        
        # 运行结果
        self.created_goods_id: Optional[str] = None
        self.created_sku_ids: List[str] = []
    
    def add_product(self, url: str, force_scrape: bool = False) -> Dict[str, Any]:
        """
        添加商品到Temu平台
        
        Args:
            url: 商品URL
            force_scrape: 是否强制重新抓取
            
        Returns:
            Dict: 添加结果
        """
        logger.info(f"开始添加商品: {url}")
        
        try:
            # 设置强制抓取标志
            if force_scrape:
                os.environ["FORCE_SCRAPE"] = "1"
            
            # 执行完整的商品添加流程
            success = self._execute_add_workflow(url)
            
            if success:
                result = {
                    "success": True,
                    "product_id": self.created_goods_id,
                    "sku_ids": self.created_sku_ids,
                    "message": "商品添加成功"
                }
                logger.info(f"商品添加成功: {self.created_goods_id}")
            else:
                result = {
                    "success": False,
                    "error": "商品添加失败",
                    "message": "请检查日志了解详细错误信息"
                }
                logger.error("商品添加失败")
            
            return result
            
        except Exception as e:
            logger.error(f"商品添加异常: {e}")
            return {
                "success": False,
                "error": f"异常: {e}",
                "message": "商品添加过程中发生异常"
            }
        finally:
            # 清理环境变量
            if "FORCE_SCRAPE" in os.environ:
                del os.environ["FORCE_SCRAPE"]
    
    def _execute_add_workflow(self, url: str) -> bool:
        """执行完整的商品添加工作流"""
        if self.use_new_api:
            # 新版API工作流
            workflow_steps = [
                ("抓取商品信息", self._scrape_product),
                ("处理商品图片", self._process_images),
                ("处理尺码表", self._process_size_chart),
                ("转换数据格式", self._transform_data),
                ("获取商品分类", self._get_categories_new),
                ("获取分类推荐", self._get_category_recommendation_new),
                ("获取分类模板", self._get_category_template_new),
                ("生成规格ID", self._generate_spec_ids_new),
                ("上传商品图片", self._upload_images_new),
                ("添加商品", self._create_product_new)
            ]
        else:
            # 旧版API工作流
            workflow_steps = [
                ("抓取商品信息", self._scrape_product),
                ("处理商品图片", self._process_images),
                ("处理尺码表", self._process_size_chart),
                ("转换数据格式", self._transform_data),
                ("获取商品分类", self._get_categories),
                ("获取分类推荐", self._get_category_recommendation),
                # ("查找叶子分类", self._find_leaf_category),  # 暂时禁用叶子分类查找
                ("获取分类模板", self._get_category_template),
                ("生成规格ID", self._generate_spec_ids),
                ("上传商品图片", self._upload_images),
                ("添加商品", self._create_product)
            ]
        
        for step_name, step_func in workflow_steps:
            logger.info(f"执行步骤: {step_name}")
            try:
                if step_name == "抓取商品信息":
                    success = step_func(url)
                else:
                    success = step_func()
                
                if not success:
                    logger.error(f"步骤失败: {step_name}")
                    return False
                    
            except Exception as e:
                logger.error(f"步骤异常: {step_name}, 错误: {e}")
                return False
        
        return True
    
    def _scrape_product(self, url: str) -> bool:
        """抓取商品信息"""
        try:
            # 优先使用缓存，避免重复抓取
            cache_path = "scraped_product.json"
            if os.path.exists(cache_path) and os.getenv("FORCE_SCRAPE") != "1":
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                try:
                    self.scraped_product = ProductData.from_dict(data)
                    logger.info(f"成功加载缓存数据: {self.scraped_product.name}, 详情图片: {len(self.scraped_product.detail_images)} 张")
                except Exception as e:
                    logger.warning(f"ProductData.from_dict失败: {e}, 使用兼容模式")
                    # 兼容旧结构
                    self.scraped_product = ProductData(
                        url=data.get("url", url),
                        name=data.get("name", ""),
                        price=float(data.get("price", 0) or 0),
                        description=data.get("description", ""),
                        main_image_url=data.get("main_image_url") or "",
                        detail_images=data.get("detail_images") or [],
                        sizes=[
                            (lambda s: s)(
                                __import__("src.models.data_models", fromlist=["SizeInfo"]).SizeInfo(**sd)
                            ) if isinstance(sd, dict) else sd
                            for sd in (data.get("sizes") or [])
                        ],
                    )
                    logger.info(f"兼容模式加载成功: {self.scraped_product.name}, 详情图片: {len(self.scraped_product.detail_images)} 张")
                logger.info("使用缓存的抓取结果")
                return True

            # 抓取商品信息
            self.scraped_product = self.scraper.scrape_product(url)
            
            if self.scraped_product:
                logger.info(f"商品抓取成功: {self.scraped_product.name}")
                # 保存抓取的商品信息到文件
                self._save_scraped_product()
                return True
            else:
                logger.error("商品抓取失败")
                return False
                
        except Exception as e:
            logger.error(f"商品抓取异常: {e}")
            return False
    
    def _process_images(self) -> bool:
        """处理商品图片"""
        if not self.scraped_product:
            return True
        
        # 收集所有图片URL
        all_images = []
        if self.scraped_product.main_image_url:
            all_images.append(self.scraped_product.main_image_url)
        all_images.extend(self.scraped_product.detail_images)
        
        if not all_images:
            logger.info("没有图片需要处理")
            return True
        
        try:
            # 检查是否强制抓取
            force_scrape = os.getenv("FORCE_SCRAPE") == "1"
            
            # 处理图片
            result = self.image_processor.process_images(all_images, force_scrape=force_scrape)
            logger.info(f"图片处理完成: 主图 {len(result['main'])}, 详情图 {len(result['detail'])}")
            
            # 保存处理后的图片信息 - 保存原始URL而不是文件路径
            # 我们需要从原始URL列表中找出成功处理的图片对应的URL
            processed_count = len(result['main']) + len(result['detail']) + len(result['other'])
            if processed_count > 0:
                # 取前processed_count个原始URL作为处理后的图片
                self.scraped_product.detail_images = all_images[:processed_count]
                logger.info(f"保存处理后的图片URL: 主图 {len(result['main'])}, 详情图 {len(result['detail'])}, 其他 {len(result['other'])}, 总计 {processed_count}")
            else:
                self.scraped_product.detail_images = []
                logger.info("没有成功处理的图片")
            return True
            
        except Exception as e:
            logger.error(f"图片处理异常: {e}")
            return False
    
    def _process_size_chart(self) -> bool:
        """处理尺码表"""
        if not self.scraped_product:
            return True
        
        # 收集详情图片URL
        detail_images = []
        if self.scraped_product.detail_images:
            detail_images.extend([img for img in self.scraped_product.detail_images if isinstance(img, str)])
        
        if not detail_images:
            logger.info("没有详情图片，跳过尺码表处理")
            return True
        
        try:
            # 获取商品分类类型
            cat_type = self._get_cat_type(int(self.temu_product.category_id)) if self.temu_product else 0
            
            # 尝试从详情图片中提取尺码表
            for i, image_url in enumerate(detail_images[:3]):  # 只检查前3张详情图
                logger.info(f"检查图片 {i+1}/{min(3, len(detail_images))}: {image_url[:50]}...")
                
                # 下载图片到临时文件
                temp_image_path = self._download_image_temp(image_url)
                if not temp_image_path:
                    continue
                
                # 处理尺码表
                size_chart = self.size_chart_processor.process_size_chart_from_image(temp_image_path, cat_type)
                
                # 清理临时文件
                try:
                    os.remove(temp_image_path)
                except:
                    pass
                
                if size_chart:
                    self.size_chart_cache = size_chart
                    logger.info(f"从图片中提取到尺码表，尺码数量: {len(size_chart[0].get('records', []))}")
                    return True
            
            logger.info("未在详情图片中发现尺码表")
            return True
            
        except Exception as e:
            logger.error(f"尺码表处理异常: {e}")
            return True  # 尺码表处理失败不影响整体流程
    
    def _transform_data(self) -> bool:
        """转换数据格式"""
        try:
            # 将ProductData转换为ScrapedProduct
            scraped_product = self._convert_to_scraped_product()
            
            # 转换数据
            result = self.data_transformer.transform_product(scraped_product)
            
            if result.success:
                self.temu_product = result.temu_product
                logger.info(f"数据转换成功: {self.temu_product.title}")
                return True
            else:
                logger.error(f"数据转换失败: {', '.join(result.errors)}")
                return False
                
        except Exception as e:
            logger.error(f"数据转换异常: {e}")
            return False
    
    def _get_categories(self) -> bool:
        """获取商品分类"""
        try:
            result = self.temu_client.product.cats_get(parent_cat_id=0)
            if result.get("success"):
                categories = result.get("result", {}).get("goodsCatsList", [])
                self.categories_cache = {cat.get("catId"): cat for cat in categories}
                logger.info(f"获取到 {len(categories)} 个分类")
                return True
            else:
                logger.error(f"获取分类失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            logger.error(f"获取分类异常: {e}")
            return False
    
    def _get_category_recommendation(self) -> bool:
        """获取分类推荐"""
        if not self.temu_product:
            return False
        
        try:
            # 多策略尝试
            attempts = [
                dict(goods_name=self.temu_product.title, description=None, image_url=None, expand_cat_type=None),
                dict(goods_name=self.temu_product.title, description=self.temu_product.description, image_url=None, expand_cat_type=None),
                dict(goods_name=self.temu_product.title, description=self.temu_product.description, image_url=self.scraped_product.main_image_url, expand_cat_type=0)
            ]

            for args in attempts:
                try:
                    res = self.temu_client.product.category_recommend(**args)
                except Exception as e:
                    continue
                if res.get("success"):
                    recommended_cat = res.get("result", {}) or {}
                    cat_id = recommended_cat.get("catId")
                    if cat_id:
                        cat_name = recommended_cat.get('catName', 'Unknown')
                        logger.info(f"分类推荐成功: {cat_name} (ID: {cat_id})")
                        logger.info(f"推荐分类列表: {recommended_cat.get('catIdList', [])}")
                        self.temu_product.category_id = str(cat_id)
                        return True
                else:
                    logger.warning(f"推荐失败: {res.get('errorMsg')}")

            # 回退到默认类目
            self.temu_product.category_id = "30847"
            logger.info("使用回退类目: 30847 (服饰)")
            return True

        except Exception as e:
            logger.error(f"分类推荐异常: {e}")
            return False
    
    def _find_leaf_category(self) -> bool:
        """查找叶子分类"""
        if not self.temu_product.category_id:
            return False
        
        try:
            # 递归查找叶子分类
            leaf_categories = self._find_leaf_categories(int(self.temu_product.category_id))
            
            if leaf_categories:
                # 使用第一个叶子分类
                leaf_cat = leaf_categories[0]
                self.temu_product.category_id = str(leaf_cat.get("catId"))
                logger.info(f"找到叶子分类: {leaf_cat.get('catName')} (ID: {self.temu_product.category_id})")
                return True
            else:
                logger.error("未找到叶子分类")
                return False
                
        except Exception as e:
            logger.error(f"查找叶子分类异常: {e}")
            return False
    
    def _get_category_template(self) -> bool:
        """获取分类模板"""
        if not self.temu_product.category_id:
            return False
        
        try:
            result = self.temu_client.product.template_get(cat_id=self.temu_product.category_id)
            if result.get("success"):
                template = result.get("result", {})
                self.templates_cache[self.temu_product.category_id] = template
                
                properties = template.get("propertyList", [])
                required_properties = [p for p in properties if p.get("required", False)]
                
                logger.info(f"获取分类模板成功: 属性数量 {len(properties)}, 必填属性 {len(required_properties)}")
                return True
            else:
                logger.error(f"获取分类模板失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            logger.error(f"获取分类模板异常: {e}")
            return False
    
    def _generate_spec_ids(self) -> bool:
        """生成规格ID"""
        if not self.temu_product.category_id:
            return False
        
        try:
            # 检查模板能力
            tmpl = self.templates_cache.get(self.temu_product.category_id) or {}
            if isinstance(tmpl, dict) and tmpl.get("inputMaxSpecNum") == 0:
                # 不允许自定义规格
                self.spec_ids_cache[self.temu_product.category_id] = {}
                logger.info("当前类目不支持自定义规格，跳过生成specId")
                return True
            
            # 查找Size父规格ID
            parent_spec_id = None
            for p in (tmpl.get("userInputParentSpecList") or []):
                if (p.get("parentSpecName") or "").lower() == "size":
                    parent_spec_id = p.get("parentSpecId")
                    break
            
            if not parent_spec_id:
                parent_spec_id = 3001

            spec_ids = {}
            # 为唯一尺码生成ID
            sizes = []
            for sku in self.temu_product.skus:
                s = (sku.size or "").strip()
                if s and s not in sizes:
                    sizes.append(s)

            for spec_value in sizes or ["Default"]:
                result = self.temu_client.product.spec_id_get(
                    cat_id=int(self.temu_product.category_id),
                    parent_spec_id=int(parent_spec_id),
                    child_spec_name=spec_value
                )
                if result.get("success"):
                    spec_id = result.get("result", {}).get("specId")
                    spec_ids[spec_value] = spec_id
                    logger.info(f"生成尺码规格ID: {spec_value} -> {spec_id}")
                else:
                    logger.warning(f"生成尺码规格ID失败: {spec_value} - {result.get('errorMsg')}")

            self.spec_ids_cache[self.temu_product.category_id] = spec_ids
            logger.info("规格ID生成完成")
            return True
        
        except Exception as e:
            logger.error(f"生成规格ID异常: {e}")
            return False
    
    def _upload_images(self) -> bool:
        """上传图片"""
        # 收集候选图片URL - 优先使用scraped_product的图片，因为它通常更完整
        all_images = []
        
        # 调试信息：检查scraped_product对象状态
        logger.info(f"调试: scraped_product类型: {type(self.scraped_product)}")
        logger.info(f"调试: hasattr detail_images: {hasattr(self.scraped_product, 'detail_images')}")
        if hasattr(self.scraped_product, 'detail_images'):
            logger.info(f"调试: detail_images值: {self.scraped_product.detail_images}")
            logger.info(f"调试: detail_images长度: {len(self.scraped_product.detail_images) if self.scraped_product.detail_images else 0}")
        
        # 首先添加主图
        if hasattr(self.scraped_product, 'main_image_url') and self.scraped_product.main_image_url:
            all_images.append(self.scraped_product.main_image_url)
            logger.info(f"添加主图: {self.scraped_product.main_image_url[:60]}...")
        
        # 然后添加详情图片 - 需要区分URL和本地文件路径
        if hasattr(self.scraped_product, 'detail_images') and self.scraped_product.detail_images:
            detail_images = [u for u in self.scraped_product.detail_images if isinstance(u, str)]
            # 过滤出URL（以http开头）而不是本地文件路径
            url_images = [u for u in detail_images if u.startswith('http')]
            all_images.extend(url_images)
            logger.info(f"添加详情图片: {len(url_images)} 张URL图片（过滤掉 {len(detail_images) - len(url_images)} 张本地路径）")
        else:
            logger.warning(f"调试: 详情图片条件失败 - hasattr: {hasattr(self.scraped_product, 'detail_images')}, 值: {getattr(self.scraped_product, 'detail_images', 'NO_ATTR')}")
        
        # 如果scraped_product有images属性，也添加进去
        if hasattr(self.scraped_product, 'images') and self.scraped_product.images:
            images = [u for u in self.scraped_product.images if isinstance(u, str)]
            all_images.extend(images)
            logger.info(f"添加images: {len(images)} 张")
        
        # 如果scraped_product没有图片，再尝试temu_product
        if not all_images:
            try:
                if self.temu_product and getattr(self.temu_product, "images", None):
                    all_images.extend(self.temu_product.images)
                    logger.info(f"添加temu_product图片: {len(self.temu_product.images)} 张")
            except Exception:
                pass
        
        logger.info(f"总共收集到 {len(all_images)} 张候选图片")
        
        if not all_images:
            logger.info("没有图片需要上传")
            return True
        
        try:
            # 获取类目类型
            cat_type = self._get_cat_type(int(self.temu_product.category_id))
            logger.info(f"商品分类类型: {'服装类' if cat_type == 0 else '非服装类'}")
            
            # 选择缩放规格 - 根据商品分类类型选择
            if cat_type == 0:  # 服装类
                scaling_type = 2  # 1350x1800
                logger.info(f"图片缩放规格: {scaling_type} (1350x1800 - 服装类)")
            else:  # 非服装类
                scaling_type = 1  # 800x800
                logger.info(f"图片缩放规格: {scaling_type} (800x800 - 非服装类)")
            
            # 过滤和选择最佳图片
            valid_images = self._filter_and_select_images(all_images, cat_type)
            if not valid_images:
                logger.error("没有符合要求的图片")
                return False
            
            logger.info(f"准备上传 {len(valid_images)} 张图片")
            
            uploaded_images = []
            for i, image_url in enumerate(valid_images):
                if len(uploaded_images) >= 5:
                    break
                    
                logger.info(f"处理图片 {len(uploaded_images)+1}/{min(5, len(valid_images))}: {image_url[:80]}...")
                
                # 使用重试机制上传图片
                success = self._upload_single_image_with_retry(
                    image_url, scaling_type, uploaded_images, max_retries=3
                )
                
                if not success:
                    logger.warning(f"图片上传失败，跳过: {image_url[:50]}...")

            self.uploaded_images_cache = uploaded_images
            logger.info(f"图片上传完成，成功上传 {len(uploaded_images)} 张")
            logger.info(f"上传的图片URLs: {uploaded_images}")
            
            # 等待图片处理完成
            if uploaded_images:
                logger.info("等待图片处理完成...")
                time.sleep(10)  # 增加等待时间
            
            return len(uploaded_images) > 0

        except Exception as e:
            logger.error(f"上传图片异常: {e}")
            return False
    
    def _create_product(self) -> bool:
        """添加商品"""
        try:
            # 构建商品数据
            product_data = self._build_product_data()
            
            # 构建完整的goods.add参数
            goods_add_params = {
                "goods_basic": product_data["goods_basic"],
                "goods_service_promise": product_data["goods_service_promise"],
                "goods_property": product_data["goods_property"],
                "sku_list": product_data["sku_list"],
                "goods_desc": product_data.get("goods_desc")
            }
            
            # 添加图片轮播图（如果存在）
            if product_data.get("goodsGalleryList"):
                goods_add_params["goodsGalleryList"] = product_data["goodsGalleryList"]
            
            # 添加尺码表（如果存在）
            if product_data.get("goodsSizeChartList"):
                goods_add_params["goodsSizeChartList"] = product_data["goodsSizeChartList"]
            
            result = self.temu_client.product.goods_add(**goods_add_params)
            
            if result.get("success"):
                result_obj = result.get("result", {}) or {}
                product_id = result_obj.get("goodsId")
                self.created_goods_id = str(product_id) if product_id is not None else None
                # 尝试解析SKU列表
                try:
                    sku_list = result_obj.get("goodsSkuList") or []
                    self.created_sku_ids = [str(s.get("skuId")) for s in sku_list if s.get("skuId") is not None]
                except Exception:
                    self.created_sku_ids = []
                logger.info(f"商品添加成功: {self.created_goods_id}")
                return True
            else:
                logger.error(f"商品添加失败: {result.get('errorMsg')}")
                return False
                
        except Exception as e:
            logger.error(f"添加商品异常: {e}")
            return False
    
    # 辅助方法
    def _download_image_temp(self, image_url: str) -> Optional[str]:
        """下载图片到临时文件"""
        try:
            import tempfile
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                return temp_file.name
                
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None
    
    def _get_cat_type(self, target_cat_id: int) -> int:
        """获取catType（0=服饰，1=非服饰）- 默认返回服装类"""
        try:
            # 环境变量强制指定
            env_cat_type = os.getenv("TEMU_CAT_TYPE")
            if env_cat_type in ("0", "1"):
                logger.info(f"使用环境变量指定的catType: {env_cat_type}")
                return int(env_cat_type)

            # 默认返回服装类（catType=0）
            logger.info("默认使用服装类分类 (catType=0)")
            return 0

            # 以下代码已注释，如需启用可取消注释
            # # 已知类目快速规则
            # if str(target_cat_id) == "30847" or str(self.temu_product.category_id) == "30847":
            #     logger.info("使用已知服装类目: 30847")
            #     return 0

            # # 从模板缓存中尝试读取
            # tmpl = self.templates_cache.get(str(target_cat_id)) or self.templates_cache.get(self.temu_product.category_id) or {}
            # if isinstance(tmpl, dict) and "catType" in tmpl:
            #     cat_type = int(tmpl.get("catType", 1))
            #     logger.info(f"从模板缓存获取catType: {cat_type}")
            #     return cat_type

            # # 智能判断：基于商品标题和描述（优先执行）
            # if self.temu_product and self.temu_product.title:
            #     title_lower = self.temu_product.title.lower()
            #     # 英文关键词
            #     english_keywords = ['pants', 'trousers', 'shirt', 'dress', 'jacket', 'coat', 'sweater', 'hoodie', 'jeans', 'shorts', 'skirt', 'blouse', 'top', 'bottom', 'clothing', 'apparel', 'fashion', 'wear', 'outfit', 'garment']
            #     # 中文关键词（扩展更多服装相关词汇）
            #     chinese_keywords = ['裤', '衣', '裙', '外套', '衬衫', '卫衣', '毛衣', '夹克', '大衣', '短裤', '长裤', '牛仔裤', '运动裤', '休闲裤', '工装裤', '登山裤', '街舞', 'hiphop', '机能', '户外', '运动', '休闲', '服装', '服饰', '针织衫', '背心', '马甲', '坎肩', '毛织', '无袖', '情侣', '学院风']
            #     
            #     if any(keyword in title_lower for keyword in english_keywords) or any(keyword in self.temu_product.title for keyword in chinese_keywords):
            #         logger.info(f"基于商品标题判断为服装类: {self.temu_product.title}")
            #         return 0

            # # 受限BFS查找
            # queue = [0]
            # visited = set()
            # api_calls = 0
            # max_calls = 30  # 减少API调用次数
            # while queue and api_calls < max_calls:
            #     parent = queue.pop(0)
            #     if parent in visited:
            #         continue
            #     visited.add(parent)
            #     resp = self.temu_client.product.cats_get(parent_cat_id=parent)
            #     api_calls += 1
            #     if not resp.get("success"):
            #         continue
            #     lst = (resp.get("result") or {}).get("goodsCatsList") or []
            #     for c in lst:
            #         cid = c.get("catId")
            #         if cid == target_cat_id:
            #             ct = int(c.get("catType", 1))
            #             logger.info(f"通过BFS找到catType: {ct} (分类ID: {target_cat_id})")
            #             return ct
            #         queue.append(cid)
            # 
            # logger.warning(f"未在限制内解析catType，使用默认1 (API calls={api_calls})")
        except Exception as e:
            logger.warning(f"获取catType异常: {e}，使用默认服装类")
        return 0  # 默认返回服装类
    
    def _filter_and_select_images(self, image_urls: List[str], cat_type: int) -> List[str]:
        """过滤和选择最佳图片"""
        valid_urls = []
        force_scrape = os.getenv("FORCE_SCRAPE") == "1"
        
        for i, url in enumerate(image_urls):
            if not isinstance(url, str) or not url.startswith("http"):
                continue
                
            # 检查是否已缓存为含中文图片（仅在非强制抓取时使用缓存）
            if not force_scrape:
                try:
                    cached = self.image_processor._get_cached_ocr(url)
                    if cached is not None and bool(cached[0]):
                        logger.info(f"跳过包含中文的图片: {url[:60]}...")
                        continue
                except Exception:
                    pass
            
            # 简化验证：直接使用URL，不下载到本地
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' in content_type:
                        valid_urls.append(url)
                        logger.info(f"图片验证通过: {url[:60]}...")
                        
            except Exception:
                logger.warning(f"图片验证失败: {url[:60]}...")
                continue
        
        logger.info(f"图片过滤完成: 输入 {len(image_urls)} 张，输出 {len(valid_urls)} 张")
        return valid_urls
    
    def _upload_single_image_with_retry(self, image_url: str, scaling_type: int, 
                                      uploaded_images: List[str], max_retries: int = 3) -> bool:
        """使用重试机制上传单张图片"""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)  # 指数退避
                
                resp = self.temu_client.product.image_upload(
                    scaling_type=scaling_type,
                    file_url=image_url,
                    compression_type=1,
                    format_conversion_type=0
                )
                
                if resp.get("success"):
                    result_obj = resp.get("result", {}) or {}
                    processed_url = (
                        result_obj.get("url") or
                        result_obj.get("imageUrl") or
                        result_obj.get("hdThumbUrl") or
                        result_obj.get("fileUrl")
                    )
                    
                    if processed_url:
                        uploaded_images.append(processed_url)
                        logger.info(f"图片上传成功: {processed_url}")
                        logger.info(f"完整上传响应: {resp}")
                        return True
                    else:
                        logger.warning(f"图片上传响应中缺少URL: {resp}")
                        return False
                else:
                    error_msg = resp.get('errorMsg', '未知错误')
                    logger.warning(f"上传图片失败: {error_msg}")
                    
                    # 如果是特定错误，不重试
                    if any(err in error_msg.lower() for err in ['invalid', 'format', 'size', 'corrupt', 'unsupported']):
                        return False
                        
            except Exception as e:
                logger.warning(f"上传图片异常: {str(e)}")
                if attempt == max_retries - 1:
                    return False
        
        return False
    
    def _find_leaf_categories(self, parent_cat_id: int, max_depth: int = 3) -> List[Dict[str, Any]]:
        """递归查找叶子分类"""
        try:
            result = self.temu_client.product.cats_get(parent_cat_id=parent_cat_id)
            if not result.get("success"):
                return []
            
            categories = result.get("result", {}).get("goodsCatsList", [])
            if not categories:
                # 没有子分类，说明这是叶子分类
                return [{"catId": parent_cat_id, "catName": "Leaf Category"}]
            
            leaf_categories = []
            for cat in categories:
                cat_id = cat.get("catId")
                sub_leafs = self._find_leaf_categories(cat_id, max_depth - 1)
                if sub_leafs:
                    leaf_categories.extend(sub_leafs)
                else:
                    leaf_categories.append(cat)
            
            return leaf_categories
        except Exception as e:
            logger.error(f"查找分类异常: {e}")
            return []
    
    def _build_product_data(self) -> Dict[str, Any]:
        """构建商品数据"""
        # 获取分类模板
        template = self.templates_cache.get(self.temu_product.category_id, {})
        properties = template.get("propertyList", [])
        
        # 构建商品属性
        goods_properties = []
        for prop in properties:
            if prop.get("required", False):
                prop_data = {
                    "vid": prop.get("vid", 0),
                    "value": self._get_property_value(prop),
                    "valueUnit": prop.get("valueUnit", ""),
                    "valueUnitId": prop.get("valueUnitId", 0),
                    "templatePid": prop.get("templatePid", 0),
                    "parentSpecId": prop.get("parentSpecId", 0),
                    "specId": prop.get("specId", 0),
                    "note": "",
                    "imgUrl": "",
                    "groupId": prop.get("groupId", 0),
                    "refPid": prop.get("refPid", 0),
                    "numberInputValue": ""
                }
                goods_properties.append(prop_data)
        
        # 构建SKU列表
        sku_list = []
        spec_ids = self.spec_ids_cache.get(self.temu_product.category_id, {})
        
        # 仅保留与已生成specId匹配的唯一尺码
        def norm(s: str) -> str:
            return (s or "").strip().upper().replace(" ", "")

        import re
        def extract_token(s: str) -> str:
            s = norm(s)
            m = re.match(r"([0-9A-Z]+)", s)
            return m.group(1) if m else s

        # 将模板key与SKU size归一到简单Token
        normalized_spec_map = {extract_token(k): v for k, v in spec_ids.items()}

        used_sizes = []
        filtered_skus = []
        for sku in self.temu_product.skus:
            raw = sku.size or ""
            nk = extract_token(raw)
            if not nk or nk not in normalized_spec_map:
                continue
            if nk in used_sizes:
                continue
            used_sizes.append(nk)
            filtered_skus.append(sku)

        # 若类目不支持自定义规格，也需要至少生成1个SKU
        if not filtered_skus and self.temu_product.skus:
            filtered_skus = [self.temu_product.skus[0]]

        for i, sku in enumerate(filtered_skus):
            # 价格从CNY转换到JPY
            from decimal import Decimal, ROUND_HALF_UP
            rate_str = os.getenv("TEMU_CNY_TO_JPY_RATE") or os.getenv("CNY_TO_JPY_RATE") or "20"
            try:
                rate = Decimal(rate_str)
            except Exception:
                rate = Decimal("20")
            jpy_amount_dec = (Decimal(str(sku.price)) * rate).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            amount_jpy = str(int(jpy_amount_dec))
            
            # 仅为该SKU选择对应尺码的specId
            size_key = extract_token(sku.size or "")
            sku_spec_ids = []
            if normalized_spec_map:
                if size_key and size_key in normalized_spec_map:
                    sku_spec_ids = [normalized_spec_map[size_key]]

            # 为每个SKU分配图片（至少3张）
            sku_images = []
            if self.uploaded_images_cache:
                # 为每个SKU分配3张图片，循环使用
                start_index = i * 3 % len(self.uploaded_images_cache)
                for j in range(3):  # 每个SKU需要至少3张图片
                    image_index = (start_index + j) % len(self.uploaded_images_cache)
                    sku_images.append(self.uploaded_images_cache[image_index])
            
            sku_data = {
                "outSkuSn": f"sku_{int(time.time())}_{i+1:03d}",
                **({"specIdList": sku_spec_ids} if sku_spec_ids else {}),
                "price": {
                    "basePrice": {
                        "amount": amount_jpy,
                        "currency": "JPY"
                    }
                },
                "quantity": sku.stock_quantity,
                "images": sku_images,  # 使用正确的字段名
                "weight": "300",
                "weightUnit": "g",
                "length": "30",
                "width": "25",
                "height": "2",
                "volumeUnit": "cm"
            }
            sku_list.append(sku_data)
        
        # 计算所有参与规格的子规格ID合集
        id_set = set()
        for s in sku_list:
            for sid in (s.get("specIdList") or []):
                id_set.add(sid)
        all_spec_ids = list(id_set)

        # 依据子规格ID查询其父规格，构建 goodsSpecProperties
        goods_spec_properties = []
        try:
            tmpl = self.templates_cache.get(self.temu_product.category_id) or {}
            tinfo = (tmpl or {}).get("templateInfo") or {}
            gsp = (tinfo or {}).get("goodsSpecProperties") or []
            chosen_map = {}
            for prop in gsp[:2]:  # 限制前两个销售属性
                parent_id = prop.get("parentSpecId")
                values = prop.get("values") or []
                chosen_spec = None
                for v in values:
                    if (v.get("value") or "").lower() == "black":
                        chosen_spec = v
                        break
                if not chosen_spec and values:
                    chosen_spec = values[0]
                if parent_id and chosen_spec and chosen_spec.get("specId"):
                    goods_spec_properties.append({
                        "parentSpecId": parent_id,
                        "specIdList": [chosen_spec.get("specId")]
                    })
                    chosen_map[parent_id] = chosen_spec.get("specId")

            # 将选中的预置规格值灌入每个SKU的specIdList
            if goods_spec_properties and sku_list:
                merged = list({sid for g in goods_spec_properties for sid in g.get("specIdList") or []})
                for s in sku_list:
                    s["specIdList"] = merged
                all_spec_ids = merged
        except Exception:
            pass
        
        # 获取运费模板ID
        cost_template_id = (
            os.getenv("TEMU_FREIGHT_TEMPLATE_ID")
            or "LFT-14230731738276073558"  # 日本物流模版
        )

        # 构建尺码表（仅服装类商品需要）
        size_chart = None
        cat_type = self._get_cat_type(int(self.temu_product.category_id))
        if cat_type == 0:  # 仅服装类商品需要尺码表
            # 暂时禁用尺码表，专注于解决核心商品添加问题
            logger.info("服装类商品，但暂时禁用尺码表以专注于核心功能")
            size_chart = None

        # 构建图片列表
        goods_gallery_list = []
        if self.uploaded_images_cache:
            for i, image_url in enumerate(self.uploaded_images_cache[:10]):  # 最多10张轮播图
                goods_gallery_list.append({
                    "galleryType": 1,  # 轮播图
                    "galleryUrl": image_url,
                    "sortOrder": i + 1
                })

        return {
            "goods_basic": {
                "goodsName": self.temu_product.title,
                "catId": self.temu_product.category_id,
                "outGoodsSn": f"goods_{int(time.time())}",
                # 主图URL应该在goods_basic里面
                **({"hdThumbUrl": self.uploaded_images_cache[0]} if self.uploaded_images_cache else {}),
                **({"carouselImageList": self.uploaded_images_cache[:10]} if self.uploaded_images_cache else {})
            },
            "goods_service_promise": {
                "shipmentLimitDay": 2,
                "fulfillmentType": 1,
                "costTemplateId": cost_template_id
            },
            "goods_property": {
                "goodsProperties": goods_properties,
                **({"goodsSpecProperties": goods_spec_properties} if goods_spec_properties else {})
            },
            "goods_desc": self.temu_product.description,
            "sku_list": sku_list,
            **({"goodsGalleryList": goods_gallery_list} if goods_gallery_list else {}),
            **({"goodsSizeChartList": size_chart} if size_chart else {})
        }
    
    def _build_size_chart(self) -> Optional[List[Dict]]:
        """构建尺码表，优先使用从图片中提取的尺码表"""
        try:
            # 优先使用从图片中提取的尺码表
            if self.size_chart_cache:
                logger.info("使用从图片中提取的尺码表")
                return self.size_chart_cache
            
            # 如果没有提取到尺码表，则生成基础尺码表
            logger.info("使用生成的尺码表")
            
            # 收集已选尺码（去重，保序）
            sizes = []
            for sku in self.temu_product.skus:
                s = (sku.size or "").strip().upper()
                if s and s not in sizes:
                    sizes.append(s)
            if not sizes:
                return None

            # 尝试使用更符合API要求的结构
            size_chart = {
                "classId": 128,  # 尺码表类型ID
                "meta": {
                    "groups": [
                        {"id": 1, "name": "size"}
                    ],
                    "elements": [
                        {"id": 10002, "name": "Size", "unit": 2}
                    ]
                },
                "records": []
            }
            
            # 为每个尺码创建记录
            for size in sizes:
                record = {
                    "values": [
                        {"id": 1, "value": size, "unit_value": "cm"},
                        {"id": 10002, "value": size, "unit_value": "cm"}
                    ]
                }
                size_chart["records"].append(record)

            logger.info(f"构建尺码表: {size_chart}")
            return [size_chart]
        except Exception as e:
            logger.error(f"构建尺码表异常: {e}")
            return None
    
    def _convert_to_scraped_product(self):
        """将ProductData转换为ScrapedProduct"""
        from src.models.product import ScrapedProduct
        
        # 收集所有图片URL
        all_images = []
        if self.scraped_product.main_image_url:
            all_images.append(self.scraped_product.main_image_url)
        all_images.extend(self.scraped_product.detail_images)
        
        # 提取尺码信息
        sizes = [size.size_name for size in self.scraped_product.sizes]
        
        return ScrapedProduct(
            title=self.scraped_product.name,
            price=self.scraped_product.price,
            description=self.scraped_product.description,
            images=all_images,
            sizes=sizes,
            url=self.scraped_product.url,
            currency="CNY",
            brand=self.scraped_product.brand,
            category=self.scraped_product.category,
            specifications={}
        )
    
    def _get_property_value(self, prop: Dict[str, Any]) -> str:
        """根据属性类型获取属性值"""
        prop_name = prop.get("propertyName", "").lower()
        
        if "age" in prop_name or "applicable" in prop_name:
            return "Adult"
        elif "material" in prop_name:
            return "Cotton"
        elif "color" in prop_name:
            return "Multi"
        elif "size" in prop_name:
            return "M"
        else:
            return prop.get("defaultValue", "Default")
    
    def _save_scraped_product(self):
        """保存抓取的商品信息"""
        if not self.scraped_product:
            return
        
        data = {
            "name": self.scraped_product.name,
            "price": self.scraped_product.price,
            "description": self.scraped_product.description,
            "main_image_url": self.scraped_product.main_image_url,
            "detail_images": self.scraped_product.detail_images,
            "sizes": [size.to_dict() for size in self.scraped_product.sizes],
            "url": self.scraped_product.url
        }
        
        with open("scraped_product.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info("抓取的商品信息已保存到 scraped_product.json")
    
    # 新版API方法
    def _get_categories_new(self) -> bool:
        """获取商品分类 (新版API)"""
        try:
            categories = self.api_adapter.get_categories(parent_cat_id=0)
            if categories:
                self.categories_cache = {cat.catId: cat for cat in categories}
                logger.info(f"获取到 {len(categories)} 个分类")
                return True
            else:
                logger.error("获取分类失败")
                return False
        except Exception as e:
            logger.error(f"获取分类异常: {e}")
            return False
    
    def _get_category_recommendation_new(self) -> bool:
        """获取分类推荐 (新版API)"""
        if not self.temu_product:
            return False
        
        try:
            # 使用新版API获取分类推荐
            # 这里需要根据新版API的具体实现来调整
            # 暂时使用默认分类
            self.temu_product.category_id = "30847"
            logger.info("使用默认分类: 30847 (服饰)")
            return True
        except Exception as e:
            logger.error(f"分类推荐异常: {e}")
            return False
    
    def _get_category_template_new(self) -> bool:
        """获取分类模板 (新版API)"""
        if not self.temu_product.category_id:
            return False
        
        try:
            template_response = self.api_adapter.get_property_template(int(self.temu_product.category_id))
            if template_response and template_response.success:
                template = template_response.result
                self.templates_cache[self.temu_product.category_id] = template
                
                properties = template.properties if template else []
                required_properties = [p for p in properties if p.required]
                
                logger.info(f"获取分类模板成功: 属性数量 {len(properties)}, 必填属性 {len(required_properties)}")
                return True
            else:
                logger.error(f"获取分类模板失败: {template_response.errorMsg if template_response else 'Unknown error'}")
                return False
        except Exception as e:
            logger.error(f"获取分类模板异常: {e}")
            return False
    
    def _generate_spec_ids_new(self) -> bool:
        """生成规格ID (新版API)"""
        if not self.temu_product.category_id:
            return False
        
        try:
            # 检查模板能力
            tmpl = self.templates_cache.get(self.temu_product.category_id) or {}
            if isinstance(tmpl, dict) and tmpl.get("inputMaxSpecNum") == 0:
                # 不允许自定义规格
                self.spec_ids_cache[self.temu_product.category_id] = {}
                logger.info("当前类目不支持自定义规格，跳过生成specId")
                return True
            
            # 查找Size父规格ID
            parent_spec_id = None
            for p in (tmpl.get("userInputParentSpecList") or []):
                if (p.get("parentSpecName") or "").lower() == "size":
                    parent_spec_id = p.get("parentSpecId")
                    break
            
            if not parent_spec_id:
                parent_spec_id = 3001

            spec_ids = {}
            # 为唯一尺码生成ID
            sizes = []
            for sku in self.temu_product.skus:
                s = (sku.size or "").strip()
                if s and s not in sizes:
                    sizes.append(s)

            for spec_value in sizes or ["Default"]:
                spec_id = self.api_adapter.get_spec_id(
                    cat_id=int(self.temu_product.category_id),
                    parent_spec_id=int(parent_spec_id),
                    child_spec_name=spec_value
                )
                if spec_id:
                    spec_ids[spec_value] = spec_id
                    logger.info(f"生成尺码规格ID: {spec_value} -> {spec_id}")
                else:
                    logger.warning(f"生成尺码规格ID失败: {spec_value}")

            self.spec_ids_cache[self.temu_product.category_id] = spec_ids
            logger.info("规格ID生成完成")
            return True
        
        except Exception as e:
            logger.error(f"生成规格ID异常: {e}")
            return False
    
    def _upload_images_new(self) -> bool:
        """上传图片 (新版API)"""
        # 收集候选图片URL
        all_images = []
        
        if hasattr(self.scraped_product, 'main_image_url') and self.scraped_product.main_image_url:
            all_images.append(self.scraped_product.main_image_url)
        
        if hasattr(self.scraped_product, 'detail_images') and self.scraped_product.detail_images:
            detail_images = [u for u in self.scraped_product.detail_images if isinstance(u, str)]
            url_images = [u for u in detail_images if u.startswith('http')]
            all_images.extend(url_images)
        
        logger.info(f"总共收集到 {len(all_images)} 张候选图片")
        
        if not all_images:
            logger.info("没有图片需要上传")
            return True
        
        try:
            # 获取类目类型
            cat_type = self._get_cat_type(int(self.temu_product.category_id))
            logger.info(f"商品分类类型: {'服装类' if cat_type == 0 else '非服装类'}")
            
            # 选择缩放规格
            if cat_type == 0:  # 服装类
                scaling_type = 2  # 1350x1800
            else:  # 非服装类
                scaling_type = 1  # 800x800
            
            # 过滤和选择最佳图片
            valid_images = self._filter_and_select_images(all_images, cat_type)
            if not valid_images:
                logger.error("没有符合要求的图片")
                return False
            
            logger.info(f"准备上传 {len(valid_images)} 张图片")
            
            uploaded_images = []
            for i, image_url in enumerate(valid_images):
                if len(uploaded_images) >= 5:
                    break
                    
                logger.info(f"处理图片 {len(uploaded_images)+1}/{min(5, len(valid_images))}: {image_url[:80]}...")
                
                # 使用新版API上传图片
                uploaded_url = self.api_adapter.upload_image(image_url, scaling_type)
                if uploaded_url:
                    uploaded_images.append(uploaded_url)
                    logger.info(f"图片上传成功: {uploaded_url}")
                else:
                    logger.warning(f"图片上传失败，跳过: {image_url[:50]}...")

            self.uploaded_images_cache = uploaded_images
            logger.info(f"图片上传完成，成功上传 {len(uploaded_images)} 张")
            
            return len(uploaded_images) > 0

        except Exception as e:
            logger.error(f"上传图片异常: {e}")
            return False
    
    def _create_product_new(self) -> bool:
        """添加商品 (新版API)"""
        try:
            # 将ProductData转换为ScrapedProduct
            scraped_product = self._convert_to_scraped_product()
            
            # 获取分类信息
            category_info = {"catIdList": [int(self.temu_product.category_id)]}
            
            # 获取属性模板
            property_template = self.templates_cache.get(self.temu_product.category_id, {})
            
            # 获取规格ID映射
            spec_id_map = self.spec_ids_cache.get(self.temu_product.category_id, {})
            
            # 使用API适配器创建商品
            result = self.api_adapter.create_product(
                scraped_product=scraped_product,
                category_info=category_info,
                property_template=property_template,
                spec_id_map=spec_id_map,
                uploaded_image_urls=self.uploaded_images_cache
            )
            
            if result.success:
                self.created_goods_id = result.product_id
                self.created_sku_ids = result.sku_ids
                logger.info(f"商品添加成功: {self.created_goods_id}")
                return True
            else:
                logger.error(f"商品添加失败: {', '.join(result.errors)}")
                return False
                
        except Exception as e:
            logger.error(f"添加商品异常: {e}")
            return False
