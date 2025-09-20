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
        # 初始化各个模块
        self.scraper = ProductScraper()
        self.ocr_client = OCRClient()
        self.image_processor = ImageProcessor(self.ocr_client)
        self.size_mapper = SizeMapper()
        self.data_transformer = DataTransformer(self.size_mapper)
        
        # 初始化Temu客户端
        self.temu_client = TemuClient(
            app_key=os.getenv("TEMU_APP_KEY"),
            app_secret=os.getenv("TEMU_APP_SECRET"),
            access_token=os.getenv("TEMU_ACCESS_TOKEN"),
            base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
            debug=True
        )
        
        # 缓存数据
        self.scraped_product = None
        self.temu_product = None
        self.categories_cache = {}
        self.leaf_categories_cache = {}
        self.templates_cache = {}
        self.spec_ids_cache = {}
        self.uploaded_images_cache = []
    
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
            uploaded_images = []
            # 获取类目类型：0=Apparel, 1=Non-Apparel
            cat_type = self._get_cat_type(int(self.temu_product.category_id))
            # 选择缩放规格：服饰类目 -> 1350x1800(2)，非服饰 -> 800x800(1)
            scaling_type = 2 if cat_type == 0 else 1
            for i, image_url in enumerate(all_images):
                if len(uploaded_images) >= 5:
                    break
                if not isinstance(image_url, str) or not image_url.startswith("http"):
                    continue
                print(f"  📷 处理图片 {len(uploaded_images)+1}/{min(5, len(all_images))}: {image_url[:80]}...")
                # 若已缓存为包含中文的图片，跳过
                try:
                    cached = self.image_processor._get_cached_ocr(image_url)
                    if cached is not None and bool(cached[0]):
                        print("    ⏭️ 跳过含中文图片(缓存)")
                        continue
                except Exception:
                    pass
                # 使用Temu图片上传接口对远程URL进行规格化处理
                try:
                    resp = self.temu_client.product.image_upload(
                        scaling_type=scaling_type,
                        file_url=image_url,
                        compression_type=1,
                        format_conversion_type=0
                    )
                    if resp.get("success"):
                        result_obj = resp.get("result", {}) or {}
                        processed_url = (
                            result_obj.get("url")
                            or result_obj.get("imageUrl")
                            or result_obj.get("hdThumbUrl")
                            or result_obj.get("fileUrl")
                        )
                        if processed_url:
                            uploaded_images.append(processed_url)
                            print(f"    ✅ 上传图片成功: {processed_url}")
                        else:
                            print(f"    ⚠️ 上传成功但未返回URL，原始: {resp}")
                    else:
                        print(f"    ❌ 上传图片失败: {resp.get('errorMsg')}")
                except Exception as e:
                    print(f"    ❌ 上传图片异常: {e}")

            self.uploaded_images_cache = uploaded_images
            print(f"✅ 图片上传完成，成功上传 {len(uploaded_images)} 张")
            return True

        except Exception as e:
            print(f"❌ 上传图片异常: {e}")
            return False

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
        """步骤10: 创建商品"""
        print("\n🔍 步骤10: 创建商品")
        print("-" * 40)
        
        try:
            # 构建商品数据
            product_data = self._build_product_data()
            
            # 创建商品
            # 调试：打印要发送的数据
            print(f"🔍 调试信息 - goods_basic: {product_data['goods_basic']}")
            print(f"🔍 调试信息 - sku_list 第一个: {product_data['sku_list'][0] if product_data['sku_list'] else 'Empty'}")
            
            result = self.temu_client.product.goods_add(
                goods_basic=product_data["goods_basic"],
                goods_service_promise=product_data["goods_service_promise"],
                goods_property=product_data["goods_property"],
                sku_list=product_data["sku_list"],
                goods_desc=product_data.get("goods_desc")
            )
            
            if result.get("success"):
                product_id = result.get("result", {}).get("goodsId")
                print(f"✅ 商品创建成功: {product_id}")
                return True
            else:
                print(f"❌ 商品创建失败: {result.get('errorMsg')}")
                print(f"📋 错误详情: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 创建商品异常: {e}")
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
            # JPY不允许小数，四舍五入为整数
            from decimal import Decimal, ROUND_HALF_UP
            amount_jpy = str(int(Decimal(str(sku.price)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
            # 仅为该SKU选择对应尺码的specId（如无可用spec则留空）
            size_key = extract_token(sku.size or "")
            sku_spec_ids = []
            if normalized_spec_map:
                if size_key and size_key in normalized_spec_map:
                    sku_spec_ids = [normalized_spec_map[size_key]]

            sku_data = {
                "outSkuSn": f"sku_{self.temu_product.title}_{i+1:03d}",
                **({"specIdList": sku_spec_ids} if sku_spec_ids else {}),
                "price": {
                    "basePrice": {
                        "amount": amount_jpy,
                        "currency": "JPY"
                    }
                },
                "quantity": sku.stock_quantity,
                "images": self.uploaded_images_cache[:5],
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

        return {
            "goods_basic": {
                "goodsName": self.temu_product.title,
                "catId": self.temu_product.category_id,
                "outGoodsSn": f"goods_{int(time.time())}"
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
            "sku_list": sku_list
        }

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
            currency="JPY",
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
        
        steps = [
            ("抓取商品信息", self.step1_scrape_product),
            ("处理商品图片", self.step2_process_images),
            ("转换数据格式", self.step3_transform_data),
            ("获取商品分类", self.step4_get_categories),
            ("获取分类推荐", self.step5_get_category_recommendation),
            ("查找叶子分类", self.step6_find_leaf_category),
            ("获取分类模板", self.step7_get_category_template),
            ("生成规格ID", self.step8_generate_spec_ids),
            ("上传商品图片", self.step9_upload_images),
            ("创建商品", self.step10_create_product)
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n📋 步骤 {i}/{total_steps}: {step_name}")
            print("-" * 40)
            
            try:
                if step_name == "抓取商品信息":
                    success = step_func(url)
                else:
                    success = step_func()
                
                if success:
                    print(f"✅ 步骤 {i} 完成")
                    success_count += 1
                else:
                    print(f"❌ 步骤 {i} 失败")
                    break
                    
            except Exception as e:
                print(f"❌ 步骤 {i} 异常: {e}")
                break
        
        print(f"\n📊 测试结果汇总")
        print("=" * 40)
        print(f"✅ 成功步骤: {success_count}/{total_steps}")
        print(f"📈 成功率: {success_count/total_steps*100:.1f}%")
        
        if success_count == total_steps:
            print("🎉 所有测试通过！")
            return True
        else:
            print("⚠️ 部分测试失败")
            return False


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
