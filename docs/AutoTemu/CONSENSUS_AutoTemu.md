# CONSENSUS - AutoTemu 货品发布API更新技术方案共识

## 明确的需求描述和验收标准

### 核心需求
将AutoTemu系统从现有的 `temu_api` 库迁移到新的 `bg.goods.add` API规范，实现完整的商品上架功能。

### 功能需求
1. **商品创建功能** - 使用新的 `bg.goods.add` 接口创建商品
2. **图片处理功能** - 适配新的图片上传和引用机制
3. **尺码表功能** - 使用新的尺码表接口族
4. **分类管理功能** - 适配新的分类查询接口
5. **属性管理功能** - 使用新的属性模板接口
6. **规格管理功能** - 适配新的规格创建接口

### 非功能需求
1. **性能要求** - 保持现有性能水平
2. **可靠性要求** - 保持现有错误处理能力
3. **可维护性要求** - 保持模块化架构
4. **兼容性要求** - 保持现有配置和接口

### 验收标准
1. **功能完整性** - 所有现有功能正常工作
2. **API兼容性** - 新API调用成功
3. **数据一致性** - 商品数据正确传递
4. **错误处理** - 错误信息正确显示
5. **测试通过** - 所有测试用例通过

## 技术实现方案

### 架构设计原则
1. **适配器模式** - 使用适配器模式处理API差异
2. **分层架构** - 保持业务逻辑与API实现分离
3. **配置驱动** - 支持API端点的配置化切换
4. **向后兼容** - 保持现有接口的兼容性

### 核心组件设计

#### 1. 新API客户端 (`src/api/bg_client.py`)
```python
class BgGoodsClient:
    """新的bg.goods.add API客户端"""
    
    def __init__(self, app_key: str, app_secret: str, access_token: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = "https://openapi.kuajingmaihuo.com/openapi/router"
    
    def sign_request(self, params: dict) -> str:
        """实现新的签名算法"""
        pass
    
    def goods_add(self, product_data: dict) -> dict:
        """调用bg.goods.add接口"""
        pass
    
    def image_upload(self, image_url: str) -> str:
        """上传图片并返回URL"""
        pass
    
    def sizecharts_create(self, size_data: dict) -> str:
        """创建尺码表"""
        pass
```

#### 2. 数据模型扩展 (`src/models/bg_models.py`)
```python
@dataclass
class BgGoodsAddData:
    """新的bg.goods.add数据模型"""
    productName: str
    carouselImageUrls: List[str]
    materialImgUrl: str
    productSkcReqs: List[dict]
    productSkuReqs: List[dict]
    sizeTemplateIds: List[str]
    # ... 其他字段

@dataclass
class BgProductSkcReq:
    """SKC请求数据模型"""
    previewImgUrls: List[str]
    mainProductSkuSpecReqs: List[dict]
    productSkuReqs: List[dict]

@dataclass
class BgProductSkuReq:
    """SKU请求数据模型"""
    thumbUrl: str
    supplierPrice: int
    currencyType: str
    productSkuSpecReqs: List[dict]
    productSkuWhExtAttrReq: dict
```

#### 3. 数据转换器扩展 (`src/transform/bg_transformer.py`)
```python
class BgDataTransformer:
    """新的数据转换器"""
    
    def __init__(self, bg_client: BgGoodsClient):
        self.bg_client = bg_client
    
    def transform_to_bg_format(self, temu_product: TemuProduct) -> BgGoodsAddData:
        """将TemuProduct转换为BgGoodsAddData"""
        pass
    
    def build_product_skc_reqs(self, temu_product: TemuProduct) -> List[BgProductSkcReq]:
        """构建SKC请求数据"""
        pass
    
    def build_product_sku_reqs(self, skus: List[TemuSKU]) -> List[BgProductSkuReq]:
        """构建SKU请求数据"""
        pass
```

#### 4. 适配器层 (`src/api/api_adapter.py`)
```python
class ApiAdapter:
    """API适配器，统一新旧API接口"""
    
    def __init__(self, use_new_api: bool = True):
        self.use_new_api = use_new_api
        if use_new_api:
            self.client = BgGoodsClient(...)
        else:
            self.client = TemuClient(...)
    
    def create_product(self, product_data: dict) -> dict:
        """统一的商品创建接口"""
        if self.use_new_api:
            return self.client.goods_add(product_data)
        else:
            return self.client.product.goods_add(**product_data)
```

### 技术约束

#### 1. 签名算法实现
- 实现文档中描述的签名算法
- 支持参数排序和编码
- 处理时区和编码问题

#### 2. 图片处理流程
- 先上传图片获取URL
- 在商品创建时引用图片URL
- 支持图片格式验证和尺寸调整

#### 3. 尺码表处理
- 使用 `bg.goods.sizecharts` 接口族
- 支持尺码表的创建和引用
- 处理服装类商品的尺码要求

#### 4. 错误处理
- 实现新的错误码映射
- 保持现有错误处理机制
- 提供详细的错误信息

### 集成方案

#### 1. 配置管理
```python
# 在配置中添加新API相关配置
class Config:
    # 现有配置...
    use_new_api: bool = True
    bg_app_key: str = ""
    bg_app_secret: str = ""
    bg_access_token: str = ""
    bg_base_url: str = "https://openapi.kuajingmaihuo.com/openapi/router"
```

#### 2. 依赖注入
```python
# 在ProductManager中使用适配器
class ProductManager:
    def __init__(self):
        # 现有初始化...
        self.api_adapter = ApiAdapter(use_new_api=True)
    
    def _create_product(self) -> bool:
        """使用适配器创建商品"""
        product_data = self._build_product_data()
        result = self.api_adapter.create_product(product_data)
        # 处理结果...
```

#### 3. 数据流转换
```
ScrapedProduct -> TemuProduct -> BgGoodsAddData -> API调用
```

## 任务边界限制

### 包含范围
1. **API客户端实现** - 新的BgGoodsClient类
2. **数据模型扩展** - 新的BgGoodsAddData等模型
3. **数据转换器** - 新的BgDataTransformer类
4. **适配器层** - ApiAdapter类
5. **配置更新** - 添加新API相关配置
6. **测试用例** - 新的API测试用例

### 不包含范围
1. **爬虫逻辑修改** - 保持现有实现
2. **OCR功能修改** - 保持现有实现
3. **基础工具修改** - 保持现有实现
4. **用户界面修改** - 保持现有实现

### 验收标准

#### 功能验收
1. **商品创建成功** - 使用新API成功创建商品
2. **图片上传成功** - 图片正确上传和引用
3. **尺码表创建成功** - 尺码表正确创建和关联
4. **分类推荐成功** - 分类推荐功能正常
5. **属性设置成功** - 商品属性正确设置

#### 质量验收
1. **代码质量** - 通过代码审查
2. **测试覆盖率** - 保持现有测试覆盖率
3. **性能指标** - 保持现有性能水平
4. **错误处理** - 错误处理正确有效
5. **日志记录** - 日志记录完整准确

#### 兼容性验收
1. **向后兼容** - 现有功能正常工作
2. **配置兼容** - 现有配置继续有效
3. **接口兼容** - 现有接口保持不变
4. **数据兼容** - 现有数据格式支持

## 确认所有不确定性已解决

### 技术不确定性
✅ **API迁移策略** - 采用适配器模式，支持新旧API切换
✅ **数据模型设计** - 创建新的数据模型，保持现有模型
✅ **错误处理策略** - 实现错误码映射，保持现有机制
✅ **测试策略** - 创建新测试用例，保持现有测试

### 业务不确定性
✅ **功能完整性** - 确保所有现有功能正常工作
✅ **性能要求** - 保持现有性能水平
✅ **兼容性要求** - 保持向后兼容
✅ **质量要求** - 保持代码质量标准

### 实施不确定性
✅ **实施顺序** - 按模块逐步实施
✅ **风险控制** - 使用适配器模式降低风险
✅ **回滚策略** - 支持新旧API切换
✅ **验证方法** - 使用金测试验证功能

## 项目特性规范已对齐

### 技术特性
- **模块化设计** - 保持现有模块结构
- **配置驱动** - 支持API端点配置
- **错误处理** - 统一的错误处理机制
- **日志记录** - 完整的日志记录系统

### 业务特性
- **商品上架** - 完整的商品上架流程
- **图片处理** - 图片上传和引用
- **尺码管理** - 尺码表创建和管理
- **分类管理** - 分类推荐和设置

### 质量特性
- **代码质量** - 符合代码规范
- **测试覆盖** - 完整的测试用例
- **文档完整** - 详细的API文档
- **性能优化** - 高效的API调用

## 最终确认

基于以上技术方案，本次更新将采用**适配器模式**实现新旧API的平滑迁移，在保持现有架构和功能的基础上，逐步适配新的API规范。更新将确保功能完整性、向后兼容性和代码质量，同时提供灵活的配置选项支持不同API的使用。

**核心优势：**
1. **风险可控** - 使用适配器模式降低迁移风险
2. **功能完整** - 确保所有功能正常工作
3. **向后兼容** - 保持现有接口和配置
4. **质量保证** - 保持代码质量和测试覆盖率

**实施保障：**
1. **渐进式迁移** - 按模块逐步实施
2. **充分测试** - 完整的测试用例覆盖
3. **详细文档** - 完整的API文档和示例
4. **持续监控** - 完整的日志和错误处理