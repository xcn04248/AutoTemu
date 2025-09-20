# AutoTemu 快速开始指南

## 🚀 5分钟快速上手

### 1. 环境准备

#### 系统要求
- Python 3.8+
- 8GB+ 内存
- 网络连接

#### 安装步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd AutoTemu

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

#### 复制环境变量模板
```bash
cp env.example .env
```

#### 编辑 .env 文件
```bash
# Firecrawl API (用于网页爬取)
FIRECRAWL_API_KEY=your_firecrawl_api_key

# 百度OCR API (用于图片文字识别)
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key

# Temu API (用于商品上架)
TEMU_APP_KEY=your_temu_app_key
TEMU_APP_SECRET=your_temu_app_secret
TEMU_ACCESS_TOKEN=your_temu_access_token
TEMU_BASE_URL=https://openapi-b-global.temu.com

# 业务配置
PRICE_MARKUP=1.3
LOG_LEVEL=INFO
IMAGE_SAVE_PATH=./images
```

### 3. 运行第一个示例

#### 基本使用
```python
from src.main import AutoTemuApp

# 创建应用实例
app = AutoTemuApp()

# 处理单个商品URL
url = "https://example.com/product/123"
result = app.process_single_url(url)

if result.success:
    print(f"✅ 商品上架成功！商品ID: {result.product_id}")
else:
    print(f"❌ 商品上架失败: {', '.join(result.errors)}")
```

#### 完整流程示例
```python
# 运行完整示例
python docs/examples/complete_product_listing.py
```

### 4. 测试API连接

#### 测试Temu API连接
```python
from src.main import AutoTemuApp

app = AutoTemuApp()
if app.test_connection():
    print("✅ Temu API 连接成功")
else:
    print("❌ Temu API 连接失败")
```

#### 测试系统状态
```python
status = app.get_system_status()
print(f"系统状态: {status}")
```

## 📖 详细使用说明

### 1. 商品信息爬取

#### 基本爬取
```python
from src.scraper.product_scraper import ProductScraper

scraper = ProductScraper()
product_data = scraper.scrape_product("https://example.com/product/123")

print(f"商品名称: {product_data.name}")
print(f"商品价格: {product_data.price}")
print(f"商品描述: {product_data.description}")
```

#### 爬取配置
```python
# 自定义爬取配置
scraper = ProductScraper(
    max_retries=3,
    timeout=30,
    user_agent="Custom Agent"
)
```

### 2. 图片处理

#### 基本图片处理
```python
from src.image.image_processor import ImageProcessor
from src.image.ocr_client import OCRClient

# 创建OCR客户端
ocr_client = OCRClient()

# 创建图片处理器
processor = ImageProcessor(ocr_client)

# 处理图片列表
image_urls = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
result = processor.process_images(image_urls)

print(f"主图数量: {len(result['main'])}")
print(f"详情图数量: {len(result['detail'])}")
print(f"过滤图片数量: {len(result['filtered'])}")
```

#### 图片规格要求
- **详情图**: 最多49张，宽高≥480px，≤3MB
- **轮播图**: 服装类3:4比例，非服装类1:1比例
- **格式**: JPEG, JPG, PNG

### 3. 数据转换

#### 基本数据转换
```python
from src.transform.data_transformer import DataTransformer
from src.transform.size_mapper import SizeMapper

# 创建尺码映射器
size_mapper = SizeMapper()

# 创建数据转换器
transformer = DataTransformer(size_mapper)

# 转换商品数据
result = transformer.transform_product(scraped_product)

if result.success:
    temu_product = result.temu_product
    skus = result.skus
    print(f"转换成功: {temu_product.title}")
else:
    print(f"转换失败: {', '.join(result.errors)}")
```

### 4. Temu API集成

#### 商品上架
```python
from src.main import AutoTemuApp

app = AutoTemuApp()

# 处理商品URL
url = "https://example.com/product/123"
result = app.process_single_url(url)

if result.success:
    print(f"商品ID: {result.product_id}")
    print(f"SKU数量: {len(result.sku_ids)}")
    print(f"图片数量: {len(result.image_ids)}")
```

#### 分类推荐
```python
# 获取分类推荐
category_result = app.temu_client.product.category_recommend(
    goods_name="测试商品",
    goods_desc="商品描述"
)

if category_result.get("success"):
    cat_id = category_result.get("result", {}).get("catId")
    print(f"推荐分类ID: {cat_id}")
```

## 🔧 高级配置

### 1. 自定义配置

#### 配置文件
```python
from src.utils.config import get_config

# 获取配置
config = get_config()

# 自定义配置
config.price_markup = 1.5  # 价格加价50%
config.max_retry_attempts = 5  # 最大重试次数
config.log_level = "DEBUG"  # 日志级别
```

#### 环境变量
```bash
# 价格加价比例
PRICE_MARKUP=1.3

# 最大重试次数
MAX_RETRY_ATTEMPTS=3

# 日志级别
LOG_LEVEL=INFO

# 图片保存路径
IMAGE_SAVE_PATH=./images
```

### 2. 错误处理

#### 基本错误处理
```python
from src.utils.exceptions import AutoTemuException

try:
    result = app.process_single_url(url)
except AutoTemuException as e:
    print(f"业务错误: {e}")
except Exception as e:
    print(f"系统错误: {e}")
```

#### 重试机制
```python
from src.utils.retry import retry

@retry(max_attempts=3, delay=1.0)
def api_call():
    # API调用代码
    pass
```

### 3. 日志配置

#### 基本日志
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("开始处理商品")
logger.error("处理失败")
```

#### 日志级别
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 🧪 测试和调试

### 1. 运行测试

#### 单元测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_main.py

# 运行测试并显示覆盖率
python -m pytest --cov=src tests/
```

#### 集成测试
```bash
# 运行集成测试
python docs/tests/test_temu_api_comprehensive.py

# 运行商品上架测试
python docs/tests/test_new_flow.py
```

### 2. 调试工具

#### API调试
```bash
# 调试API请求
python docs/examples/debug_api_request.py

# 调试签名算法
python docs/examples/debug_signature.py
```

#### 商品上架调试
```bash
# 调试商品上架流程
python docs/examples/complete_product_listing.py
```

## 📚 更多资源

### 文档链接
- [完整API文档](temu_api/temu_product_listing_flow.md)
- [字段验证规则](temu_api/temu_field_validation_rules.md)
- [图片规格要求](temu_api/temu_image_specifications.md)
- [系统设计文档](AutoTemu/DESIGN_AutoTemu.md)

### 示例代码
- [完整示例](examples/complete_product_listing.py)
- [基本使用](examples/example_usage.py)
- [API调试](examples/debug_api_request.py)

### 常见问题
- [FAQ](faq.md)
- [故障排除](troubleshooting.md)

## 🆘 获取帮助

### 问题反馈
1. 查看 [FAQ](faq.md)
2. 搜索 [Issues](../../issues)
3. 提交新问题

### 社区支持
- GitHub Discussions
- 技术交流群
- 邮件支持

---

**需要更多帮助？** 查看 [完整文档](../README.md) 或联系维护者。
