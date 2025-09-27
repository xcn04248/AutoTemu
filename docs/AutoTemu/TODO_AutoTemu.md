# TODO - AutoTemu 货品发布API更新待办事项

## 当前状态总结

### ✅ 已完成 (阶段1-2)
- **T1**: 新API数据模型创建 - `src/models/bg_models.py`
- **T2**: 签名工具模块实现 - `src/utils/bg_signature.py`  
- **T3**: 新API客户端实现 - `src/api/bg_client.py`
- **T4**: 数据转换器实现 - `src/transform/bg_transformer.py`
- **T5**: API适配器实现 - `src/api/api_adapter.py`

### 🔄 待完成 (阶段3)

## T6: 业务逻辑集成 [高优先级]

### 任务描述
更新ProductManager使用新的ApiAdapter，保持现有接口不变的同时支持新API。

### 具体工作
1. **更新ProductManager初始化**
   ```python
   # 在 src/core/product_manager.py 中
   from src.api.api_adapter import create_api_adapter
   
   def __init__(self):
       # 现有初始化...
       self.api_adapter = create_api_adapter()
   ```

2. **更新商品创建方法**
   ```python
   def _create_product(self) -> bool:
       # 构建上下文信息
       context = {
           'uploaded_images': self.uploaded_images_cache,
           'category_template': self.templates_cache.get(self.temu_product.category_id),
           'spec_ids': self.spec_ids_cache.get(self.temu_product.category_id, {})
       }
       
       # 使用适配器创建商品
       result = self.api_adapter.create_product(self.temu_product, context)
       
       if result.success:
           self.created_goods_id = str(result.goods_id)
           self.created_sku_ids = [str(sid) for sid in result.sku_ids or []]
           return True
       else:
           logger.error(f"商品创建失败: {result.error_message}")
           return False
   ```

3. **更新其他API调用**
   - 分类查询: `self.api_adapter.get_categories()`
   - 分类推荐: `self.api_adapter.recommend_category()`
   - 图片上传: `self.api_adapter.upload_image()`

### 验收标准
- [ ] 现有功能正常工作
- [ ] 新API调用成功
- [ ] 业务流程完整
- [ ] 错误处理正确

---

## T7: 配置和测试更新 [中优先级]

### 任务描述
更新配置文件、环境变量文档，创建必要的测试用例。

### 具体工作

#### 7.1 配置更新
1. **更新.env.example文件**
   ```bash
   # 新API配置
   USE_NEW_API=true
   BG_APP_KEY=your_app_key
   BG_APP_SECRET=your_app_secret  
   BG_ACCESS_TOKEN=your_access_token
   BG_BASE_URL=https://openapi.kuajingmaihuo.com/openapi/router
   
   # API切换配置
   API_FALLBACK_ENABLED=true
   API_TIMEOUT=30
   API_MAX_RETRIES=3
   
   # 新API特定配置
   BG_SCALING_TYPE=1
   BG_COMPRESSION_TYPE=1
   BG_FORMAT_CONVERSION_TYPE=0
   ```

2. **更新config.py支持新配置项**
   ```python
   class Config:
       # 现有配置...
       
       # 新API配置
       use_new_api: bool = True
       bg_app_key: str = ""
       bg_app_secret: str = ""
       bg_access_token: str = ""
       bg_base_url: str = "https://openapi.kuajingmaihuo.com/openapi/router"
   ```

#### 7.2 测试用例创建
1. **单元测试**
   - `tests/test_bg_models.py` - 数据模型测试
   - `tests/test_bg_signature.py` - 签名算法测试
   - `tests/test_bg_client.py` - API客户端测试
   - `tests/test_bg_transformer.py` - 数据转换测试
   - `tests/test_api_adapter.py` - 适配器测试

2. **集成测试**
   - `tests/test_bg_integration.py` - 端到端集成测试

### 验收标准
- [ ] 配置项完整
- [ ] 测试覆盖率≥90%
- [ ] 所有测试通过
- [ ] 文档更新正确

---

## T8: 文档和最终验证 [中优先级]

### 任务描述
创建使用文档、故障排除指南，执行最终的端到端验证。

### 具体工作

#### 8.1 文档创建
1. **API迁移指南** - `docs/guides/api_migration_guide.md`
   - 新旧API对比
   - 迁移步骤说明
   - 配置参数说明
   - 常见问题解答

2. **故障排除指南** - `docs/guides/troubleshooting.md`
   - 常见错误及解决方案
   - 调试方法说明
   - 日志分析指导

3. **新API使用示例** - `docs/examples/bg_api_examples.py`
   ```python
   # 基本使用示例
   from src.api.api_adapter import create_api_adapter
   
   # 创建适配器
   adapter = create_api_adapter(use_new_api=True)
   
   # 测试连接
   if adapter.test_connection():
       print("API连接成功")
   
   # 创建商品示例...
   ```

#### 8.2 端到端验证
1. **完整流程测试**
   - 从商品URL到成功上架的完整流程
   - 验证新API各个环节工作正常
   - 测试API切换和降级功能

2. **性能验证**
   - 验证新API性能与旧API相当
   - 测试并发处理能力
   - 验证错误处理效果

### 验收标准
- [ ] 文档完整准确
- [ ] 示例代码可运行
- [ ] 端到端测试通过
- [ ] 性能指标达标

---

## 配置需求

### 必需的环境变量
```bash
# 基础API配置 (必需)
TEMU_APP_KEY=your_app_key
TEMU_APP_SECRET=your_app_secret
TEMU_ACCESS_TOKEN=your_access_token

# 新API配置 (可选，会从TEMU_*复制)
BG_APP_KEY=${TEMU_APP_KEY}
BG_APP_SECRET=${TEMU_APP_SECRET}  
BG_ACCESS_TOKEN=${TEMU_ACCESS_TOKEN}

# API控制配置 (可选)
USE_NEW_API=true
API_FALLBACK_ENABLED=true
```

### 可选的配置项
```bash
# API端点配置
BG_BASE_URL=https://openapi.kuajingmaihuo.com/openapi/router
TEMU_BASE_URL=https://openapi-b-global.temu.com

# 图片处理配置
BG_SCALING_TYPE=1  # 1:800x800, 2:1350x1800
BG_COMPRESSION_TYPE=1
BG_FORMAT_CONVERSION_TYPE=0

# 价格转换配置
TEMU_CNY_TO_JPY_RATE=20

# 运费模板配置
TEMU_FREIGHT_TEMPLATE_ID=LFT-14230731738276073558

# 调试配置
DEBUG=false
```

---

## 风险提示

### 高风险项目
1. **T6业务逻辑集成** - 需要仔细测试，确保不破坏现有功能
2. **生产环境部署** - 建议先在测试环境充分验证

### 缓解措施
1. **分步骤部署** - 先启用新API但保持降级功能
2. **监控告警** - 密切监控API调用成功率和错误日志
3. **快速回滚** - 保持`USE_NEW_API=false`的快速回滚能力

---

## 验证清单

### 功能验证
- [ ] 新API商品创建成功
- [ ] 图片上传正常工作
- [ ] 分类推荐功能正常
- [ ] 数据转换正确无误
- [ ] 错误处理机制有效
- [ ] API切换功能正常
- [ ] 降级机制工作正常

### 质量验证  
- [ ] 代码质量符合标准
- [ ] 测试覆盖率达标
- [ ] 性能指标满足要求
- [ ] 日志记录完整
- [ ] 文档更新正确
- [ ] 配置管理灵活

### 部署验证
- [ ] 环境变量配置正确
- [ ] 依赖包安装成功
- [ ] 服务启动正常
- [ ] 端到端流程测试通过
- [ ] 监控告警配置完成

---

## 支持联系

### 技术支持
- 如遇新API相关问题，请查看 `docs/guides/troubleshooting.md`
- 如需配置帮助，请参考 `docs/guides/api_migration_guide.md`
- 如有其他问题，请检查日志文件并提供详细的错误信息

### 紧急处理
如果新API出现严重问题，可以通过以下方式快速回滚：
```bash
# 方法1: 环境变量
export USE_NEW_API=false

# 方法2: 配置文件
echo "USE_NEW_API=false" >> .env

# 方法3: 代码级别
# 在ProductManager初始化中设置use_new_api=False
```

---

**最后更新**: 2025年9月26日
**状态**: 阶段1-2已完成，阶段3待执行
**预计完成时间**: 剩余5-8小时工作量