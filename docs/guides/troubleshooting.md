# AutoTemu 故障排除指南

## 常见问题与解决方案

### 🔧 API相关问题

#### 1. API认证失败
**错误信息**: `Invalid access token` 或 `Authentication failed`

**解决方案**:
```bash
# 检查环境变量配置
echo $TEMU_ACCESS_TOKEN
echo $TEMU_APP_KEY
echo $TEMU_APP_SECRET

# 重新获取访问令牌
# 联系Temu平台获取新的access_token
```

#### 2. API版本切换问题
**错误信息**: `Module not found` 或 `AttributeError`

**解决方案**:
```python
# 检查API版本配置
from src.core.product_manager import ProductManager

# 明确指定API版本
manager = ProductManager(use_new_api=True)  # 新版API
# 或
manager = ProductManager(use_new_api=False) # 旧版API
```

#### 3. 签名验证失败
**错误信息**: `Invalid signature` 或 `Signature verification failed`

**解决方案**:
```python
# 检查签名算法
from src.utils.bg_signature import generate_signature

# 测试签名生成
params = {"test": "data"}
signature = generate_signature(params, "your_app_secret")
print(f"Generated signature: {signature}")
```

### 🖼️ 图片处理问题

#### 1. 图片上传失败
**错误信息**: `Image upload failed` 或 `Invalid image format`

**解决方案**:
```python
# 检查图片URL有效性
import requests

def check_image_url(url):
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

# 使用示例
image_url = "https://example.com/image.jpg"
if check_image_url(image_url):
    print("图片URL有效")
else:
    print("图片URL无效")
```

#### 2. OCR识别问题
**错误信息**: `OCR service unavailable` 或 `OCR recognition failed`

**解决方案**:
```bash
# 检查百度OCR配置
echo $BAIDU_API_KEY
echo $BAIDU_SECRET_KEY

# 测试OCR服务
python -c "
from src.image.ocr_client import OCRClient
client = OCRClient()
result = client.detect_text('test_image.jpg')
print(result)
"
```

### 📊 数据转换问题

#### 1. 数据格式错误
**错误信息**: `Invalid data format` 或 `Missing required field`

**解决方案**:
```python
# 检查数据模型
from src.models.bg_models import BgGoodsAddRequest

# 验证请求数据
request = BgGoodsAddRequest(
    productName="测试商品",
    cat1Id=1,
    cat2Id=2,
    cat3Id=3
)

# 检查必填字段
required_fields = ['productName', 'cat1Id', 'cat2Id', 'cat3Id']
for field in required_fields:
    if not hasattr(request, field) or getattr(request, field) is None:
        print(f"缺少必填字段: {field}")
```

#### 2. 价格转换问题
**错误信息**: `Invalid price format` 或 `Currency conversion failed`

**解决方案**:
```python
# 检查汇率配置
import os
from decimal import Decimal, ROUND_HALF_UP

rate_str = os.getenv("TEMU_CNY_TO_JPY_RATE", "20.0")
rate = Decimal(rate_str)

# 测试价格转换
cny_price = Decimal("100.00")
jpy_price = (cny_price * rate).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
print(f"CNY {cny_price} = JPY {jpy_price}")
```

### 🔄 工作流程问题

#### 1. 商品抓取失败
**错误信息**: `Scraping failed` 或 `Product not found`

**解决方案**:
```python
# 检查URL有效性
import requests

def check_url_accessibility(url):
    try:
        response = requests.head(url, timeout=30)
        return response.status_code == 200
    except:
        return False

# 使用示例
product_url = "https://example.com/product"
if check_url_accessibility(product_url):
    print("URL可访问")
else:
    print("URL不可访问")
```

#### 2. 分类推荐失败
**错误信息**: `Category recommendation failed` 或 `No suitable category found`

**解决方案**:
```python
# 手动指定分类
from src.core.product_manager import ProductManager

manager = ProductManager(use_new_api=True)
manager.temu_product.category_id = "30847"  # 使用默认分类
```

### 🧪 测试问题

#### 1. 测试运行失败
**错误信息**: `Test failed` 或 `Import error`

**解决方案**:
```bash
# 检查测试环境
python -c "import sys; print(sys.path)"

# 运行单个测试
python -m pytest tests/test_bg_client.py -v

# 运行特定测试方法
python -m pytest tests/test_bg_client.py::TestBgClient::test_init -v
```

#### 2. 依赖问题
**错误信息**: `ModuleNotFoundError` 或 `ImportError`

**解决方案**:
```bash
# 重新安装依赖
pip install -r requirements.txt

# 检查依赖版本
pip list | grep -E "(requests|pytest|pillow)"
```

### 📝 日志调试

#### 1. 启用详细日志
```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 或在环境变量中设置
export LOG_LEVEL=DEBUG
```

#### 2. 查看API调用日志
```python
# 启用API日志记录
import os
os.environ['ENABLE_API_LOGGING'] = 'true'

# 查看日志文件
tail -f logs/autotemu.log
```

### 🔍 性能问题

#### 1. 处理速度慢
**解决方案**:
```python
# 调整重试参数
import os
os.environ['MAX_RETRY_ATTEMPTS'] = '1'
os.environ['RETRY_INITIAL_DELAY'] = '0.5'

# 减少图片处理数量
# 在ProductManager中限制处理的图片数量
```

#### 2. 内存使用过高
**解决方案**:
```python
# 清理缓存
from src.core.product_manager import ProductManager

manager = ProductManager()
# 处理完成后清理缓存
manager.categories_cache.clear()
manager.templates_cache.clear()
manager.spec_ids_cache.clear()
```

### 📞 获取帮助

如果以上解决方案都无法解决您的问题，请：

1. **查看日志文件**: `logs/autotemu.log`
2. **检查环境配置**: 确认所有环境变量正确设置
3. **运行测试**: `python run_tests.py --type new_api --verbose`
4. **查看文档**: `docs/AutoTemu/` 目录下的相关文档
5. **提交Issue**: 在项目仓库中提交详细的问题描述

### 🚀 最佳实践

1. **始终使用最新版本**: 定期更新代码和依赖
2. **配置环境变量**: 使用`.env`文件管理配置
3. **启用日志记录**: 便于问题排查和调试
4. **运行测试**: 在部署前运行完整的测试套件
5. **备份数据**: 定期备份重要的配置和数据

---

**最后更新**: 2025-01-10  
**版本**: v1.0
