# TODO - AutoTemu 商品自动化上架系统

## 待完成任务清单

### 🔴 高优先级（核心功能实现）

#### T6: 爬虫模块实现
- [ ] 重构example/scrape_firecrawl.py代码
- [ ] 创建src/scraper/product_scraper.py
- [ ] 实现ProductScraper类
- [ ] 集成配置管理和日志系统
- [ ] 添加重试装饰器
- [ ] 编写单元测试

#### T7: OCR客户端封装  
- [ ] 创建src/image/ocr_client.py
- [ ] 封装百度OCR API调用
- [ ] 实现access_token获取和缓存
- [ ] 添加请求频率控制
- [ ] 处理API异常
- [ ] 编写单元测试

#### T8: 图片处理模块
- [ ] 创建src/image/processor.py
- [ ] 实现图片下载功能（带重试）
- [ ] 集成OCR客户端进行中文检测
- [ ] 实现图片尺寸调整（保持3:4比例）
- [ ] 支持图片格式转换和压缩
- [ ] 编写单元测试

### 🟡 中优先级（数据处理）

#### T9: 尺码映射模块
- [ ] 创建src/transformer/size_mapper.py
- [ ] 实现灵活的尺码映射规则
- [ ] 处理日本尺码到Temu标准的转换
- [ ] 生成符合Temu要求的尺码表数据
- [ ] 编写单元测试

#### T10: 数据转换模块  
- [ ] 创建src/transformer/data_transformer.py
- [ ] 实现价格计算逻辑（原价×1.3）
- [ ] 数据格式转换（ProductData → TemuProductData）
- [ ] 数据完整性验证
- [ ] 编写单元测试

#### T11: Temu API封装
- [ ] 创建src/temu/adapter.py
- [ ] 集成temu_api库
- [ ] 实现商品分类推荐功能
- [ ] 实现图片上传功能  
- [ ] 实现商品创建功能
- [ ] 添加API错误处理
- [ ] 编写单元测试

### 🟢 低优先级（集成和优化）

#### T12: 主程序集成
- [ ] 创建src/main.py
- [ ] 实现命令行参数解析
- [ ] 集成所有模块的完整流程
- [ ] 添加进度显示
- [ ] 异常处理和用户提示

#### T13: 单元测试
- [ ] 完善各模块的测试用例
- [ ] 提高测试覆盖率到80%以上
- [ ] 创建测试数据和fixtures
- [ ] Mock外部API调用

#### T14: 集成测试
- [ ] 创建端到端测试脚本
- [ ] 准备测试商品URL
- [ ] 验证完整流程
- [ ] 性能测试和优化

#### T15: 文档完善
- [ ] 更新README.md
- [ ] 编写API使用文档
- [ ] 创建部署指南
- [ ] 编写故障排查文档

## 配置需求

### 必需的环境变量（.env文件）
```ini
# Firecrawl配置
FIRECRAWL_API_KEY=你的Firecrawl API密钥

# 百度OCR配置  
BAIDU_API_KEY=你的百度API Key
BAIDU_SECRET_KEY=你的百度Secret Key

# Temu API配置
TEMU_APP_KEY=你的Temu App Key
TEMU_APP_SECRET=你的Temu App Secret
TEMU_ACCESS_TOKEN=你的Temu Access Token
TEMU_BASE_URL=https://openapi-jp.temu.com

# 业务配置
PRICE_MARKUP=1.3
LOG_LEVEL=INFO
IMAGE_SAVE_PATH=./images
```

## 已知问题和限制

1. **API配额限制**
   - 百度OCR API有调用频率限制
   - Temu API可能有日调用量限制
   - 需要实现请求频率控制

2. **图片处理**
   - 部分图片可能无法满足Temu的3:4比例要求
   - OCR可能存在误判（将非中文识别为中文）

3. **数据映射**
   - 某些特殊尺码可能无法准确映射
   - 商品分类推荐可能不够精确

## 开发建议

1. **优先完成核心流程**
   - 先实现基本的爬取→处理→上架流程
   - 确保单个商品能够成功处理
   - 再考虑批量处理和优化

2. **充分测试**
   - 每个模块都要有对应的单元测试
   - 使用Mock避免测试时调用真实API
   - 准备多种类型的测试数据

3. **日志和监控**
   - 充分利用已实现的日志系统
   - 关键操作都要记录日志
   - 便于问题排查和性能分析

4. **错误处理**
   - 利用已实现的异常类和重试机制
   - 对外部API调用都要有超时和重试
   - 提供清晰的错误信息

## 部署准备

1. **环境准备**
   - Python 3.8+
   - 稳定的网络连接
   - 足够的磁盘空间（存储图片）

2. **依赖安装**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **配置文件**
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入实际的API密钥
   ```

## 联系支持

如需技术支持或有任何问题，请：
1. 查看日志文件（logs目录）
2. 检查环境变量配置
3. 确认API密钥有效性
4. 查看故障排查文档（待编写）
