# AutoTemu

🤖 **自动化商品信息爬取和Temu平台商品上架系统**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

## ✨ 功能特性

- 🔍 **智能爬取**: 基于Firecrawl的网页爬取，支持多种电商平台
- 🖼️ **图片处理**: OCR识别中文内容，自动过滤含中文图片
- 🔄 **数据转换**: 智能数据转换和尺码映射到Temu格式
- 🛒 **API集成**: 完整的Temu API集成和商品上架流程
- 🛡️ **错误处理**: 完善的错误处理和自动重试机制
- 📊 **合规检查**: 自动合规性检查和属性验证

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd AutoTemu

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，填入你的API密钥
vim .env
```

### 3. 运行示例
```bash
# 运行完整流程示例
python docs/examples/complete_product_listing.py

# 或运行基本示例
python src/main.py
```

## 📚 文档

### 🎯 快速开始
- [快速开始指南](docs/guides/quick_start.md) - 5分钟快速上手
- [环境配置指南](docs/guides/environment_setup.md) - 详细环境配置

### 📖 核心文档
- [项目概述](docs/AutoTemu/PROJECT_SUMMARY.md) - 项目整体介绍
- [系统设计](docs/AutoTemu/DESIGN_AutoTemu.md) - 系统架构设计
- [任务分解](docs/AutoTemu/TASK_AutoTemu.md) - 开发任务分解

### 🔧 Temu API 文档
- [商品上架流程](docs/temu_api/temu_product_listing_flow.md) - 完整的商品上架流程
- [字段验证规则](docs/temu_api/temu_field_validation_rules.md) - 详细的字段验证规则
- [图片规格要求](docs/temu_api/temu_image_specifications.md) - 图片和媒体规格要求

### 📋 项目状态
- [项目完成报告](docs/PROJECT_COMPLETION_REPORT.md) - 项目完成情况总结
- [待办事项](docs/AutoTemu/TODO_AutoTemu.md) - 待完成任务列表

## 🏗️ 项目结构

```
AutoTemu/
├── docs/                    # 📚 项目文档
│   ├── AutoTemu/           # 6A工作流文档
│   ├── temu_api/           # Temu API相关文档
│   ├── guides/             # 使用指南
│   ├── examples/           # 示例代码
│   └── tests/              # 测试脚本
├── src/                    # 💻 源代码
│   ├── api/               # API相关模块
│   ├── image/             # 图片处理模块
│   ├── models/            # 数据模型
│   ├── scraper/           # 爬虫模块
│   ├── transform/         # 数据转换模块
│   └── utils/             # 工具模块
├── tests/                 # 🧪 单元测试
├── images/                # 🖼️ 图片资源
├── logs/                  # 📝 日志文件
└── requirements.txt       # 📦 依赖列表
```

## 🎯 核心功能

### 1. 商品信息爬取
- 基于 Firecrawl 的网页爬取
- 支持多种电商平台
- 自动提取商品信息（名称、价格、描述、图片等）

### 2. 图片处理
- 自动下载商品图片
- OCR 识别中文内容
- 自动过滤含中文图片
- 支持多种图片格式和规格

### 3. 数据转换
- 爬取数据到 Temu 格式转换
- 智能尺码信息映射
- 价格计算和货币转换
- 属性验证和合规检查

### 4. Temu API 集成
- 完整的商品上架流程
- 分类推荐和属性获取
- 合规性检查和验证
- 商品创建和发布

## 🔧 使用示例

### 基本使用
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

### 高级配置
```python
# 自定义配置
from src.utils.config import get_config

config = get_config()
config.price_markup = 1.5  # 价格加价50%
config.log_level = "DEBUG"  # 调试模式
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_main.py

# 运行测试并显示覆盖率
python -m pytest --cov=src tests/
```

### 集成测试
```bash
# 运行集成测试
python docs/tests/test_temu_api_comprehensive.py
```

## 📊 项目状态

### ✅ 已完成
- [x] 项目基础设施搭建
- [x] 商品信息爬取模块
- [x] 图片处理模块
- [x] 数据转换模块
- [x] Temu API 集成
- [x] 完整文档编写

### 🔄 进行中
- [ ] 合规信息处理优化
- [ ] 图片规格自动调整
- [ ] 外部产品ID验证

### 📋 待办
- [ ] 性能优化
- [ ] 错误处理增强
- [ ] 监控和日志完善

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

如有问题或建议，请：
1. 查看 [FAQ](docs/guides/faq.md)
2. 提交 [Issue](../../issues)
3. 联系维护者

## 🙏 致谢

感谢以下开源项目的支持：
- [Firecrawl](https://firecrawl.dev/) - 网页爬取服务
- [百度智能云](https://cloud.baidu.com/) - OCR 识别服务
- [Temu API](https://partner.temu.com/) - 商品上架服务

---

**最后更新**: 2024-01-XX  
**版本**: v1.0.0  
**维护者**: AutoTemu Team