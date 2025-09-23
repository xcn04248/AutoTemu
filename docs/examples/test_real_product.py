#!/usr/bin/env python3
"""
真实商品测试 - 以 https://www.jp0663.com/detail/V52ZD9Ex1OKaCj1biny2494lGc4TVj0a 为例
"""

import os
import sys
import time
import json
import hashlib
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

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
from PIL import Image
import io
import requests

class RealProductTester:
    """真实商品测试器"""
    
    def __init__(self):
        """初始化测试器"""
        # 使用生产环境的商品管理器
        from src.core.product_manager import ProductManager
        self.product_manager = ProductManager()
        
        # 运行结果
        self.created_goods_id: Optional[str] = None
        self.created_sku_ids: List[str] = []
    
    def step1_scrape_product(self, url: str) -> bool:
        """步骤1: 抓取商品信息"""
        print("🔍 步骤1: 抓取商品信息")
        print("-" * 40)
        print(f"📋 目标URL: {url}")
        
        try:
            # 优先使用缓存，避免重复抓取（设置环境变量 FORCE_SCRAPE=1 可强制重新抓取）
            cache_path = "scraped_product.json"
            if os.path.exists(cache_path) and os.getenv("FORCE_SCRAPE") != "1":
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                try:
                    self.scraped_product = ProductData.from_dict(data)
                except Exception:
                    # 兼容旧结构，最少字段回填
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
                print("⏭️ 使用缓存的抓取结果 scraped_product.json")
                # 打印摘要
                image_count = int(bool(self.scraped_product.main_image_url)) + len(self.scraped_product.detail_images)
                print(f"  📦 商品名称: {self.scraped_product.name}")
                print(f"  💰 商品价格: {self.scraped_product.price}")
                print(f"  📝 商品描述: {self.scraped_product.description[:100]}...")
                print(f"  🖼️ 图片数量: {image_count}")
                return True

            # 抓取商品信息
            self.scraped_product = self.scraper.scrape_product(url)
            
            if self.scraped_product:
                print(f"✅ 商品抓取成功")
                print(f"  📦 商品名称: {self.scraped_product.name}")
                print(f"  💰 商品价格: {self.scraped_product.price}")
                print(f"  📝 商品描述: {self.scraped_product.description[:100]}...")
                # 计算图片数量
                image_count = 0
                if self.scraped_product.main_image_url:
                    image_count += 1
                image_count += len(self.scraped_product.detail_images)
                print(f"  🖼️ 图片数量: {image_count}")
                
                # 保存抓取的商品信息到文件
                self._save_scraped_product()
                return True
            else:
                print("❌ 商品抓取失败")
                return False
                
        except Exception as e:
            print(f"❌ 商品抓取异常: {e}")
            return False
    
    def step2_process_images(self) -> bool:
        """步骤2: 处理商品图片"""
        print("\n🔍 步骤2: 处理商品图片")
        print("-" * 40)
        
        if not self.scraped_product:
            print("⚠️ 没有商品数据")
            return True
        
        # 收集所有图片URL
        all_images = []
        if self.scraped_product.main_image_url:
            all_images.append(self.scraped_product.main_image_url)
        all_images.extend(self.scraped_product.detail_images)
        
        if not all_images:
            print("⚠️ 没有图片需要处理")
            return True
        
        # 检查是否有已处理的图片
        processed_images = self._check_processed_images(all_images)
        if processed_images:
            print(f"  ⏭️ 发现 {len(processed_images)} 张已处理的图片，跳过处理")
            # 使用已处理的图片
            self.scraped_product.detail_images = processed_images
            return True
        
        try:
            # 处理图片
            result = self.image_processor.process_images(all_images)
            
            print(f"✅ 图片处理完成")
            print(f"  🖼️ 主图数量: {len(result['main'])}")
            print(f"  🖼️ 详情图数量: {len(result['detail'])}")
            print(f"  🗑️ 过滤图片数量: {len(result['filtered'])}")
            
            # 保存处理后的图片信息
            self.scraped_product.detail_images = result['main'] + result['detail']
            return True
            
        except Exception as e:
            print(f"❌ 图片处理异常: {e}")
            return False
    
    def step2_5_process_size_chart(self) -> bool:
        """步骤2.5: 处理尺码表"""
        print("\n🔍 步骤2.5: 处理尺码表")
        print("-" * 40)
        
        if not self.scraped_product:
            print("⚠️ 没有商品数据")
            return True
        
        # 收集详情图片URL
        detail_images = []
        if self.scraped_product.detail_images:
            detail_images.extend([img for img in self.scraped_product.detail_images if isinstance(img, str)])
        
        if not detail_images:
            print("⚠️ 没有详情图片，跳过尺码表处理")
            return True
        
        try:
            # 获取商品分类类型
            cat_type = self._get_cat_type(int(self.temu_product.category_id)) if self.temu_product else 0
            
            # 尝试从详情图片中提取尺码表
            for i, image_url in enumerate(detail_images[:3]):  # 只检查前3张详情图
                print(f"  🔍 检查图片 {i+1}/{min(3, len(detail_images))}: {image_url[:50]}...")
                
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
                    print(f"✅ 从图片中提取到尺码表，尺码数量: {len(size_chart[0].get('records', []))}")
                    return True
            
            print("ℹ️ 未在详情图片中发现尺码表")
            return True
            
        except Exception as e:
            print(f"❌ 尺码表处理异常: {e}")
            return True  # 尺码表处理失败不影响整体流程
    
    def step3_transform_data(self) -> bool:
        """步骤3: 转换数据格式"""
        print("\n🔍 步骤3: 转换数据格式")
        print("-" * 40)
        
        try:
            # 将ProductData转换为ScrapedProduct
            scraped_product = self._convert_to_scraped_product()
            
            # 转换数据
            result = self.data_transformer.transform_product(scraped_product)
            
            if result.success:
                self.temu_product = result.temu_product
                print(f"✅ 数据转换成功")
                print(f"  📦 转换后商品名称: {self.temu_product.title}")
                print(f"  💰 转换后价格: {self.temu_product.markup_price}")
                print(f"  📏 SKU数量: {len(self.temu_product.skus)}")
                
                # 保存转换后的数据
                self._save_transformed_product()
                return True
            else:
                print(f"❌ 数据转换失败: {', '.join(result.errors)}")
                return False
                
        except Exception as e:
            print(f"❌ 数据转换异常: {e}")
            return False
    
    def step4_get_categories(self) -> bool:
        """步骤4: 获取商品分类"""
        print("\n🔍 步骤4: 获取商品分类")
        print("-" * 40)
        
        try:
            result = self.temu_client.product.cats_get(parent_cat_id=0)
            if result.get("success"):
                categories = result.get("result", {}).get("goodsCatsList", [])
                self.categories_cache = {cat.get("catId"): cat for cat in categories}
                print(f"✅ 获取到 {len(categories)} 个分类")
                
                # 显示前几个分类
                for i, cat in enumerate(categories[:5]):
                    print(f"  {i+1}. {cat.get('catName')} (ID: {cat.get('catId')})")
                
                return True
            else:
                print(f"❌ 获取分类失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"❌ 获取分类异常: {e}")
            return False
    
    def step5_get_category_recommendation(self) -> bool:
        """步骤5: 获取分类推荐"""
        print("\n🔍 步骤5: 获取分类推荐")
        print("-" * 40)
        
        if not self.temu_product:
            print("❌ 没有转换后的商品数据")
            return False
        
        try:
            # 多策略尝试：按官方文档优先仅用商品名，其次补充分词/图片/服饰类型提示
            attempts = []
            attempts.append(dict(goods_name=self.temu_product.title, description=None, image_url=None, expand_cat_type=None))
            attempts.append(dict(goods_name=self.temu_product.title, description=self.temu_product.description, image_url=None, expand_cat_type=None))
            first_image = self.scraped_product.main_image_url if (self.scraped_product and self.scraped_product.main_image_url) else None
            attempts.append(dict(goods_name=self.temu_product.title, description=self.temu_product.description, image_url=first_image, expand_cat_type=0))

            for args in attempts:
                try:
                    res = self.temu_client.product.category_recommend(**args)
                except Exception as e:
                    print(f"  ⚠️ 调用失败: {e}")
                    continue
                if res.get("success"):
                    recommended_cat = res.get("result", {}) or {}
                    cat_id = recommended_cat.get("catId")
                    cat_name = recommended_cat.get("catName")
                    if cat_id:
                        print("✅ 分类推荐成功")
                        print(f"  🎯 推荐分类: {cat_name} (ID: {cat_id})")
                        self.temu_product.category_id = str(cat_id)
                        return True
                else:
                    print(f"  ⛔ 推荐失败: {res.get('errorMsg')}")

            # 所有尝试失败时，回退到与当前商品更匹配的服饰类测试类目（避免书籍类导致Publisher必填）
            self.temu_product.category_id = "30847"
            print("  🔄 使用回退类目: 30847 (服饰)" )
            return True

        except Exception as e:
            print(f"❌ 分类推荐异常: {e}")
            return False
    
    def step6_find_leaf_category(self) -> bool:
        """步骤6: 查找叶子分类"""
        print("\n🔍 步骤6: 查找叶子分类")
        print("-" * 40)
        
        if not self.temu_product.category_id:
            print("❌ 没有分类ID")
            return False
        
        try:
            # 递归查找叶子分类
            leaf_categories = self._find_leaf_categories(int(self.temu_product.category_id))
            
            if leaf_categories:
                # 使用第一个叶子分类
                leaf_cat = leaf_categories[0]
                self.temu_product.category_id = str(leaf_cat.get("catId"))
                print(f"✅ 找到叶子分类: {leaf_cat.get('catName')} (ID: {self.temu_product.category_id})")
                return True
            else:
                print("❌ 未找到叶子分类")
                return False
                
        except Exception as e:
            print(f"❌ 查找叶子分类异常: {e}")
            return False
    
    def step7_get_category_template(self) -> bool:
        """步骤7: 获取分类模板"""
        print("\n🔍 步骤7: 获取分类模板")
        print("-" * 40)
        
        if not self.temu_product.category_id:
            print("❌ 没有分类ID")
            return False
        
        try:
            result = self.temu_client.product.template_get(cat_id=self.temu_product.category_id)
            if result.get("success"):
                template = result.get("result", {})
                self.templates_cache[self.temu_product.category_id] = template
                
                properties = template.get("propertyList", [])
                required_properties = [p for p in properties if p.get("required", False)]
                
                print(f"✅ 获取分类模板成功")
                print(f"  📊 属性数量: {len(properties)}")
                print(f"  📝 必填属性: {len(required_properties)}")
                
                # 显示必填属性
                if required_properties:
                    print("  📋 必填属性列表:")
                    for prop in required_properties[:5]:
                        print(f"    - {prop.get('propertyName')} ({prop.get('propertyType')})")
                
                # 不再切换类目，严格使用推荐/指定类目的模板
                return True
            else:
                print(f"❌ 获取分类模板失败: {result.get('errorMsg')}")
                return False
        except Exception as e:
            print(f"❌ 获取分类模板异常: {e}")
            return False
    
    def step8_generate_spec_ids(self) -> bool:
        """步骤8: 生成规格ID"""
        print("\n🔍 步骤8: 生成规格ID")
        print("-" * 40)
        
        if not self.temu_product.category_id:
            print("❌ 没有分类ID")
            return False
        
        try:
            # 检出模板能力：若不允许自定义规格，则跳过生成
            parent_spec_id = None
            tmpl = self.templates_cache.get(self.temu_product.category_id) or {}
            if isinstance(tmpl, dict) and tmpl.get("inputMaxSpecNum") == 0:
                # 不允许自定义规格，直接置空，让SKU无规格
                self.spec_ids_cache[self.temu_product.category_id] = {}
                print("ℹ️ 当前类目不支持自定义规格（inputMaxSpecNum=0），跳过生成specId")
                return True
            for p in (tmpl.get("userInputParentSpecList") or []):
                if (p.get("parentSpecName") or "").lower() == "size":
                    parent_spec_id = p.get("parentSpecId")
                    break
            # 常见 Size 父规格ID
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
                    print(f"  ✅ 生成尺码规格ID: {spec_value} -> {spec_id}")
                else:
                    print(f"  ❌ 生成尺码规格ID失败: {spec_value} - {result.get('errorMsg')}")

            self.spec_ids_cache[self.temu_product.category_id] = spec_ids
            print("✅ 规格ID生成完成")
            return True
        
        except Exception as e:
            print(f"❌ 生成规格ID异常: {e}")
            return False
    
    def step9_upload_images(self) -> bool:
        """步骤9: 上传图片"""
        print("\n🔍 步骤9: 上传图片")
        print("-" * 40)
        
        # 收集候选图片URL（优先使用转换阶段保留的原始URL）
        all_images = []
        try:
            if self.temu_product and getattr(self.temu_product, "images", None):
                all_images.extend(self.temu_product.images)
        except Exception:
            pass
        # 兜底：从抓取数据补充URL
        if not all_images:
            if self.scraped_product.main_image_url:
                all_images.append(self.scraped_product.main_image_url)
            # 仅保留字符串URL，忽略此前步骤生成的本地Path
            all_images.extend([u for u in (self.scraped_product.detail_images or []) if isinstance(u, str)])
        
        if not all_images:
            print("⚠️ 没有图片需要上传")
            return True
        
        try:
            # 获取类目类型：0=Apparel, 1=Non-Apparel
            cat_type = self._get_cat_type(int(self.temu_product.category_id))
            print(f"📂 商品分类类型: {'服装类' if cat_type == 0 else '非服装类'}")
            
            # 尝试使用服装类缩放规格，因为商品名称包含"外套"等服装关键词
            # 选择缩放规格：服饰类目 -> 1350x1800(2)，非服饰 -> 800x800(1)
            scaling_type = 2  # 强制使用服装类缩放规格
            print(f"🖼️ 图片缩放规格: {scaling_type} (1350x1800 - 服装类)")
            
            # 过滤和选择最佳图片
            valid_images = self._filter_and_select_images(all_images, cat_type)
            if not valid_images:
                print("❌ 没有符合要求的图片")
                return False
            
            print(f"📷 准备上传 {len(valid_images)} 张图片")
            
            uploaded_images = []
            for i, image_url in enumerate(valid_images):
                if len(uploaded_images) >= 5:
                    break
                    
                print(f"  📷 处理图片 {len(uploaded_images)+1}/{min(5, len(valid_images))}: {image_url[:80]}...")
                
                # 使用重试机制上传图片
                success = self._upload_single_image_with_retry(
                    image_url, scaling_type, uploaded_images, max_retries=3
                )
                
                if not success:
                    print(f"    ❌ 图片上传失败，跳过: {image_url[:50]}...")

            self.uploaded_images_cache = uploaded_images
            print(f"✅ 图片上传完成，成功上传 {len(uploaded_images)} 张")
            return len(uploaded_images) > 0

        except Exception as e:
            print(f"❌ 上传图片异常: {e}")
            return False

    def _filter_and_select_images(self, image_urls: List[str], cat_type: int) -> List[str]:
        """过滤和选择最佳图片"""
        print("🔍 开始过滤和选择图片...")
        
        valid_urls = []
        for i, url in enumerate(image_urls):
            if not isinstance(url, str) or not url.startswith("http"):
                continue
                
            # 检查是否已缓存为含中文图片
            try:
                cached = self.image_processor._get_cached_ocr(url)
                if cached is not None and bool(cached[0]):
                    print(f"    ⏭️ 跳过含中文图片(缓存): {url[:50]}...")
                    continue
            except Exception:
                pass
            
            # 简化验证：直接使用URL，不下载到本地
            try:
                # 检查URL是否可访问
                import requests
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    # 检查Content-Type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' in content_type:
                        valid_urls.append(url)
                        print(f"    ✅ 图片URL有效: {url[:50]}...")
                    else:
                        print(f"    ❌ 不是图片文件: {url[:50]}...")
                else:
                    print(f"    ❌ 图片URL不可访问: {url[:50]}...")
                    
            except Exception as e:
                print(f"    ❌ 检查图片失败: {url[:50]}..., 错误: {str(e)}")
                continue
        
        print(f"📊 图片过滤完成: 从 {len(image_urls)} 张中筛选出 {len(valid_urls)} 张有效图片")
        return valid_urls

    def _upload_single_image_with_retry(self, image_url: str, scaling_type: int, 
                                      uploaded_images: List[str], max_retries: int = 3) -> bool:
        """使用重试机制上传单张图片"""
        import time
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"    🔄 重试上传 (第 {attempt + 1} 次): {image_url[:50]}...")
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
                        print(f"    ✅ 上传图片成功: {processed_url}")
                        return True
                    else:
                        print(f"    ⚠️ 上传成功但未返回URL: {resp}")
                        return False
                else:
                    error_msg = resp.get('errorMsg', '未知错误')
                    print(f"    ❌ 上传图片失败: {error_msg}")
                    
                    # 如果是特定错误，不重试
                    if any(err in error_msg.lower() for err in ['invalid', 'format', 'size', 'corrupt', 'unsupported']):
                        return False
                        
            except Exception as e:
                print(f"    ❌ 上传图片异常: {str(e)}")
                if attempt == max_retries - 1:
                    return False
        
        return False

    def _download_image_temp(self, image_url: str) -> Optional[str]:
        """下载图片到临时文件"""
        try:
            import tempfile
            import requests
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                return temp_file.name
                
        except Exception as e:
            print(f"    ❌ 下载图片失败: {e}")
            return None

    def _get_cat_type(self, target_cat_id: int) -> int:
        """获取catType（0=服饰，1=非服饰），带有安全回退与上限，避免长时间阻塞。"""
        try:
            # 1) 环境变量强制指定
            env_cat_type = os.getenv("TEMU_CAT_TYPE")
            if env_cat_type in ("0", "1"):
                print(f"    ℹ️ 使用环境变量 TEMU_CAT_TYPE={env_cat_type}")
                return int(env_cat_type)

            # 2) 已知类目快速规则（推荐类目 30847 属于服饰）
            if str(target_cat_id) == "30847" or str(self.temu_product.category_id) == "30847":
                print("    ℹ️ 使用已知类目规则: 30847 -> Apparel(catType=0)")
                return 0

            # 3) 从模板缓存中尝试读取
            tmpl = self.templates_cache.get(str(target_cat_id)) or self.templates_cache.get(self.temu_product.category_id) or {}
            if isinstance(tmpl, dict) and "catType" in tmpl:
                print(f"    ℹ️ 从模板缓存获取 catType={tmpl.get('catType')}")
                return int(tmpl.get("catType", 1))

            # 4) 受限BFS查找，设置最大API调用次数，避免阻塞
            queue = [0]
            visited = set()
            api_calls = 0
            max_calls = 50
            while queue and api_calls < max_calls:
                parent = queue.pop(0)
                if parent in visited:
                    continue
                visited.add(parent)
                resp = self.temu_client.product.cats_get(parent_cat_id=parent)
                api_calls += 1
                if not resp.get("success"):
                    continue
                lst = (resp.get("result") or {}).get("goodsCatsList") or []
                for c in lst:
                    cid = c.get("catId")
                    if cid == target_cat_id:
                        ct = int(c.get("catType", 1))
                        print(f"    ℹ️ 通过cats_get定位 catType={ct} (API calls={api_calls})")
                        return ct
                    queue.append(cid)
            print(f"    ⚠️ 未在限制内解析catType，使用默认1 (API calls={api_calls})")
        except Exception as e:
            print(f"    ⚠️ 获取catType异常: {e}，使用默认1")
        return 1

    def _prepare_image_for_category(self, image_url: str, cat_type: int) -> str:
        """按类目规格调整图片并保存本地，返回本地路径。"""
        # 下载
        resp = requests.get(image_url, timeout=20)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        w, h = img.size
        # 规格
        if cat_type == 0:
            # Apparel: 3:4, ≥1340x1785
            target_ratio = 3/4
            min_w, min_h = 1340, 1785
        else:
            # Non-Apparel: 1:1, ≥800x800
            target_ratio = 1.0
            min_w, min_h = 800, 800
        # 调整比例（中心裁剪到目标比例）
        cur_ratio = w / h if h else target_ratio
        if cur_ratio > target_ratio:
            # 太宽，按高度裁剪
            new_w = int(h * target_ratio)
            x0 = (w - new_w) // 2
            img = img.crop((x0, 0, x0 + new_w, h))
        elif cur_ratio < target_ratio:
            # 太高，按宽度裁剪
            new_h = int(w / target_ratio)
            y0 = (h - new_h) // 2
            img = img.crop((0, y0, w, y0 + new_h))
        # 尺寸放大到最小要求
        w2, h2 = img.size
        scale = max(min_w / w2, min_h / h2, 1.0)
        if scale > 1.0:
            img = img.resize((int(w2 * scale), int(h2 * scale)), Image.LANCZOS)
        # 保存到临时文件
        os.makedirs("temp_images", exist_ok=True)
        out_path = os.path.join("temp_images", f"prepared_{hash(image_url)}.jpg")
        img.save(out_path, format="JPEG", quality=90)
        return out_path
    
    def step10_create_product(self) -> bool:
        """步骤10: 添加商品"""
        print("\n🔍 步骤10: 添加商品")
        print("-" * 40)
        
        try:
            # 构建商品数据
            product_data = self._build_product_data()
            
            # 添加商品
            # 调试：打印要发送的数据
            print(f"🔍 调试信息 - goods_basic: {product_data['goods_basic']}")
            print(f"🔍 调试信息 - sku_list 第一个: {product_data['sku_list'][0] if product_data['sku_list'] else 'Empty'}")
            
            # 构建完整的goods.add参数
            goods_add_params = {
                "goods_basic": product_data["goods_basic"],
                "goods_service_promise": product_data["goods_service_promise"],
                "goods_property": product_data["goods_property"],
                "sku_list": product_data["sku_list"],
                "goods_desc": product_data.get("goods_desc")
            }
            
            # 添加图片轮播图（如果存在）- 通过kwargs传递
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
                print(f"✅ 商品添加成功: {self.created_goods_id}")
                return True
            else:
                print(f"❌ 商品添加失败: {result.get('errorMsg')}")
                print(f"📋 错误详情: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 添加商品异常: {e}")
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
            print(f"查找分类异常: {e}")
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
        
        # 构建SKU列表（images字段为必填：使用已上传处理后的URL列表）
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

        # 将模板key与SKU size归一到简单Token（如 M/L/XL/2XL）
        normalized_spec_map = {extract_token(k): v for k, v in spec_ids.items()}

        used_sizes = []  # 保留顺序
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

        # 若类目不支持自定义规格（step8已缓存为空），也需要至少生成1个SKU（无specIdList）
        fallback_used = False
        if not filtered_skus and self.temu_product.skus:
            filtered_skus = [self.temu_product.skus[0]]
            fallback_used = True

        for i, sku in enumerate(filtered_skus):
            # 价格从CNY转换到JPY；JPY不允许小数
            from decimal import Decimal, ROUND_HALF_UP
            rate_str = os.getenv("TEMU_CNY_TO_JPY_RATE") or os.getenv("CNY_TO_JPY_RATE") or "20"
            try:
                rate = Decimal(rate_str)
            except Exception:
                rate = Decimal("20")
            jpy_amount_dec = (Decimal(str(sku.price)) * rate).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            amount_jpy = str(int(jpy_amount_dec))
            # 仅为该SKU选择对应尺码的specId（如无可用spec则留空）
            size_key = extract_token(sku.size or "")
            sku_spec_ids = []
            if normalized_spec_map:
                if size_key and size_key in normalized_spec_map:
                    sku_spec_ids = [normalized_spec_map[size_key]]

            # 为每个SKU分配不同的图片（如果有的话）
            sku_images = []
            if self.uploaded_images_cache:
                # 为每个SKU分配一张图片，循环使用
                sku_image_index = i % len(self.uploaded_images_cache)
                sku_images = [self.uploaded_images_cache[sku_image_index]]
            
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
                "images": sku_images,
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

        # 依据子规格ID查询其父规格（如 Size 的 parentSpecId），构建 goodsSpecProperties
        goods_spec_properties = []
        try:
            # 从模板读取预置销售属性（如颜色、尺码）并选择一个可用值（优先 Black）
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
        
        # 获取运费模板ID（优先使用环境变量或指定模板ID）
        cost_template_id = (
            os.getenv("TEMU_FREIGHT_TEMPLATE_ID")
            or "LFT-14230731738276073558"  # 日本物流模版
        )

        # 构建尺码表（仅服装类商品需要）
        size_chart = None
        cat_type = self._get_cat_type(int(self.temu_product.category_id))
        if cat_type == 0:  # 仅服装类商品需要尺码表
            size_chart = self._build_size_chart()

        # 构建图片列表
        goods_gallery_list = []
        if self.uploaded_images_cache:
            for i, image_url in enumerate(self.uploaded_images_cache[:10]):  # 最多10张轮播图
                goods_gallery_list.append({
                    "galleryType": 1,  # 轮播图
                    "galleryUrl": image_url,
                    "sortOrder": i + 1
                })
        
        # 调试信息：打印图片配置
        print(f"🔍 调试信息 - goods_gallery_list: {goods_gallery_list}")
        print(f"🔍 调试信息 - uploaded_images_cache: {self.uploaded_images_cache}")

        return {
            "goods_basic": {
                "goodsName": self.temu_product.title,
                "catId": self.temu_product.category_id,
                "outGoodsSn": f"goods_{int(time.time())}",
                # 添加主图URL
                "hdThumbUrl": self.uploaded_images_cache[0] if self.uploaded_images_cache else "",
                "carouselImageList": self.uploaded_images_cache[:10] if self.uploaded_images_cache else []
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
                print("✅ 使用从图片中提取的尺码表")
                return self.size_chart_cache
            
            # 如果没有提取到尺码表，则生成基础尺码表
            print("ℹ️ 使用生成的尺码表")
            
            # 收集已选尺码（去重，保序）
            sizes = []
            for sku in self.temu_product.skus:
                s = (sku.size or "").strip().upper()
                if s and s not in sizes:
                    sizes.append(s)
            if not sizes:
                return None

            # 生成Temu格式的尺码表
            size_chart = {
                "classId": 128,  # 尺码表类型ID
                "meta": {
                    "groups": [
                        {"id": 1, "name": "size"},
                        {"id": 20, "name": "JP"}  # 日本站
                    ],
                    "elements": [
                        {"id": 10002, "name": "胸围", "unit": 2},  # 胸围
                        {"id": 10003, "name": "衣长", "unit": 2}   # 衣长
                    ]
                },
                "records": []
            }
            
            # 以常见卫衣尺码为模板，按顺序略微递增
            base = {
                "bust": 100,
                "length": 65
            }
            step = {
                "bust": 4,
                "length": 2
            }

            for idx, sz in enumerate(sizes):
                record = {
                    "values": [
                        {"id": 1, "value": sz, "unit_value": "cm"},  # 尺码
                        {"id": 20, "value": sz, "unit_value": "cm"},  # 日本尺码
                        {"id": 10002, "value": str(base["bust"] + step["bust"] * idx), "unit_value": "cm"},  # 胸围
                        {"id": 10003, "value": str(base["length"] + step["length"] * idx), "unit_value": "cm"}   # 衣长
                    ]
                }
                size_chart["records"].append(record)

            return [size_chart]
        except Exception as e:
            print(f"❌ 构建尺码表异常: {e}")
            return None

    def _get_default_freight_template_id(self) -> Optional[str]:
        """获取一个可用的运费模板ID"""
        try:
            resp = self.temu_client.product.freight_template_list_query()
            if not resp or not resp.get("success"):
                return None
            result = resp.get("result") or {}
            # 兼容不同返回结构
            candidates = (
                result.get("freightTemplateList")
                or result.get("list")
                or (result if isinstance(result, list) else [])
            )
            if not candidates:
                return None
            first = candidates[0]
            # 可能的字段名
            for key in ("costTemplateId", "templateId", "id", "freightTemplateId"):
                if key in first and first[key]:
                    return str(first[key])
            return None
        except Exception:
            return None
    
    def _get_image_path(self, image_url: str) -> str:
        """根据图片URL生成本地文件路径"""
        # 使用URL的MD5哈希作为文件名，避免特殊字符
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # 从URL中提取文件扩展名
        file_ext = ".jpg"  # 默认扩展名
        if "." in image_url.split("/")[-1]:
            file_ext = "." + image_url.split(".")[-1].split("?")[0]
        
        # 创建临时图片目录
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)
        
        return os.path.join(temp_dir, f"{url_hash}{file_ext}")
    
    def _check_processed_images(self, image_urls: List[str]) -> List[str]:
        """检查是否有已处理的图片"""
        processed_images = []
        
        for image_url in image_urls:
            # 检查images目录中是否有对应的已处理图片
            image_path = self._get_image_path(image_url)
            
            # 检查images目录中的文件
            images_dir = "images"
            if os.path.exists(images_dir):
                # 查找可能的已处理图片文件
                url_hash = hashlib.md5(image_url.encode()).hexdigest()
                for filename in os.listdir(images_dir):
                    if filename.startswith("image_") and url_hash in filename:
                        # 找到对应的已处理图片
                        processed_images.append(image_url)
                        break
        
        return processed_images
    
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
        
        print(f"💾 抓取的商品信息已保存到 scraped_product.json")
    
    def _save_transformed_product(self):
        """保存转换后的商品信息"""
        if not self.temu_product:
            return
        
        data = {
            "title": self.temu_product.title,
            "description": self.temu_product.description,
            "original_price": self.temu_product.original_price,
            "markup_price": self.temu_product.markup_price,
            "currency": self.temu_product.currency,
            "category_id": self.temu_product.category_id,
            "skus": [
                {
                    "sku_id": sku.sku_id,
                    "size": sku.size,
                    "price": sku.price,
                    "stock_quantity": sku.stock_quantity
                } for sku in self.temu_product.skus
            ]
        }
        
        with open("transformed_product.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 转换后的商品信息已保存到 transformed_product.json")
    
    def run_complete_test(self, url: str) -> bool:
        """运行完整测试"""
        print("🚀 开始真实商品测试")
        print("=" * 60)
        print(f"🎯 测试商品: {url}")
        print("=" * 60)
        
        try:
            # 使用商品管理器添加商品
            result = self.product_manager.add_product(url, force_scrape=False)  # 测试时允许缓存
            
            if result["success"]:
                self.created_goods_id = result["product_id"]
                self.created_sku_ids = result["sku_ids"]
                
                print("🎉 商品添加测试成功！")
                print(f"📦 创建的商品ID: {self.created_goods_id}")
                print(f"📦 创建的SKU IDs: {self.created_sku_ids}")
                
                # 检查商品状态
                self.check_product_status()
                return True
            else:
                print(f"❌ 商品添加测试失败: {result.get('error', '未知错误')}")
                return False
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_product_status(self):
        """检查商品状态"""
        if not self.created_goods_id:
            print("❌ 没有商品ID，无法检查状态")
            return
        
        print(f"\n🔍 检查商品状态: {self.created_goods_id}")
        print("-" * 40)
        
        try:
            # 使用商品管理器的客户端获取商品状态
            resp = self.product_manager.temu_client.product.publish_status_get(
                goods_id=self.created_goods_id
            )
            
            if resp.get("success"):
                result = resp["result"]
                status = result.get("status", "未知")
                sub_status = result.get("subStatus", "未知")
                
                print(f"📊 商品状态: {status}")
                print(f"📊 子状态: {sub_status}")
                
                # 状态说明
                status_map = {
                    0: "草稿",
                    1: "审核中", 
                    2: "已上架",
                    3: "已下架",
                    4: "审核失败"
                }
                
                sub_status_map = {
                    201: "完整",
                    301: "不完整",
                    302: "待补充信息"
                }
                
                print(f"📋 状态说明: {status_map.get(status, '未知')}")
                print(f"📋 子状态说明: {sub_status_map.get(sub_status, '未知')}")
                
            else:
                print(f"❌ 获取状态失败: {resp.get('errorMsg', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 检查状态异常: {e}")


def main():
    """主函数"""
    # 测试URL
    test_url = "https://www.jp0663.com/detail/V52ZD9Ex1OKaCj1biny2494lGc4TVj0a"
    
    # 创建测试器
    tester = RealProductTester()
    
    # 运行完整测试
    success = tester.run_complete_test(test_url)
    
    if success:
        print("\n🎉 真实商品测试成功完成！")
    else:
        print("\n❌ 真实商品测试失败")


if __name__ == "__main__":
    main()
