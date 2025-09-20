# AutoTemu 文档中心

欢迎来到 AutoTemu 文档中心！这里包含了项目的所有文档，帮助您快速了解和使用 AutoTemu 系统。

## 📚 文档导航

### 🚀 新手上路
- [快速开始指南](guides/quick_start.md) - 5分钟快速上手
- [环境配置指南](guides/environment_setup.md) - 详细环境配置
- [常见问题解答](guides/faq.md) - 常见问题解答

### 📖 项目文档
- [项目概述](AutoTemu/PROJECT_SUMMARY.md) - 项目整体介绍
- [项目对齐](AutoTemu/ALIGNMENT_AutoTemu.md) - 需求分析和对齐
- [技术共识](AutoTemu/CONSENSUS_AutoTemu.md) - 技术方案共识
- [系统设计](AutoTemu/DESIGN_AutoTemu.md) - 系统架构设计
- [任务分解](AutoTemu/TASK_AutoTemu.md) - 开发任务分解
- [验收标准](AutoTemu/ACCEPTANCE_AutoTemu.md) - 功能验收标准

### 🔧 Temu API 文档
- [商品上架流程](temu_api/temu_product_listing_flow.md) - 完整的商品上架流程
- [字段验证规则](temu_api/temu_field_validation_rules.md) - 详细的字段验证规则
- [图片规格要求](temu_api/temu_image_specifications.md) - 图片和媒体规格要求

### 📋 项目状态
- [项目完成报告](PROJECT_COMPLETION_REPORT.md) - 项目完成情况总结
- [项目状态报告](PROJECT_STATUS_REPORT.md) - 当前项目状态
- [待办事项](AutoTemu/TODO_AutoTemu.md) - 待完成任务列表

### 🧪 测试和示例
- [测试文件](tests/) - 所有测试脚本
- [示例代码](examples/) - 使用示例和调试脚本

## 🎯 按角色导航

### 👨‍💻 开发者
- [系统设计](AutoTemu/DESIGN_AutoTemu.md) - 了解系统架构
- [任务分解](AutoTemu/TASK_AutoTemu.md) - 了解开发任务
- [API文档](temu_api/) - 了解API接口
- [测试指南](tests/) - 了解测试方法

### 🚀 用户
- [快速开始指南](guides/quick_start.md) - 快速上手
- [环境配置指南](guides/environment_setup.md) - 配置环境
- [常见问题解答](guides/faq.md) - 解决问题

### 📊 项目经理
- [项目概述](AutoTemu/PROJECT_SUMMARY.md) - 了解项目概况
- [项目完成报告](PROJECT_COMPLETION_REPORT.md) - 了解完成情况
- [待办事项](AutoTemu/TODO_AutoTemu.md) - 了解待办任务

## 🔍 按功能导航

### 商品爬取
- [商品爬虫模块](AutoTemu/DESIGN_AutoTemu.md#商品爬取模块) - 了解爬虫设计
- [示例代码](examples/) - 查看爬取示例

### 图片处理
- [图片处理模块](AutoTemu/DESIGN_AutoTemu.md#图片处理模块) - 了解图片处理
- [图片规格要求](temu_api/temu_image_specifications.md) - 了解图片规格

### 数据转换
- [数据转换模块](AutoTemu/DESIGN_AutoTemu.md#数据转换模块) - 了解数据转换
- [字段验证规则](temu_api/temu_field_validation_rules.md) - 了解验证规则

### Temu API
- [商品上架流程](temu_api/temu_product_listing_flow.md) - 了解上架流程
- [API集成](AutoTemu/DESIGN_AutoTemu.md#api集成) - 了解API集成

## 📁 文档结构

```
docs/
├── AutoTemu/              # 6A工作流文档
│   ├── PROJECT_SUMMARY.md
│   ├── ALIGNMENT_AutoTemu.md
│   ├── CONSENSUS_AutoTemu.md
│   ├── DESIGN_AutoTemu.md
│   ├── TASK_AutoTemu.md
│   ├── ACCEPTANCE_AutoTemu.md
│   ├── TODO_AutoTemu.md
│   └── FINAL_AutoTemu.md
├── temu_api/              # Temu API文档
│   ├── temu_product_listing_flow.md
│   ├── temu_field_validation_rules.md
│   └── temu_image_specifications.md
├── guides/                # 使用指南
│   ├── quick_start.md
│   ├── environment_setup.md
│   └── faq.md
├── examples/              # 示例代码
│   ├── complete_product_listing.py
│   ├── example_usage.py
│   └── debug_*.py
├── tests/                 # 测试脚本
│   └── test_*.py
├── PROJECT_COMPLETION_REPORT.md
├── PROJECT_STATUS_REPORT.md
└── README.md
```

## 🔄 文档更新

### 最近更新
- **2024-01-XX**: 完成文档结构整理
- **2024-01-XX**: 添加Temu API详细文档
- **2024-01-XX**: 完善快速开始指南

### 更新计划
- [ ] 添加故障排除指南
- [ ] 完善API参考文档
- [ ] 添加性能优化指南

## 🤝 贡献文档

### 如何贡献
1. Fork 项目
2. 创建文档分支
3. 编辑文档
4. 提交 Pull Request

### 文档规范
- 使用 Markdown 格式
- 遵循项目文档结构
- 保持内容准确和最新
- 使用清晰的语言和格式

## 📞 获取帮助

### 文档问题
- 查看 [常见问题解答](guides/faq.md)
- 提交 [Issue](../../issues)
- 联系维护者

### 技术问题
- 查看 [API文档](temu_api/)
- 查看 [示例代码](examples/)
- 提交 [Issue](../../issues)

---

**文档版本**: v1.0.0  
**最后更新**: 2024-01-XX  
**维护者**: AutoTemu Team
