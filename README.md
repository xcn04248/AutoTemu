# AutoTemu - 商品自动化上架系统

AutoTemu是一个自动化系统，用于从购物网站抓取商品信息并自动上架到Temu日本站。

## 功能特性

- 🕷️ **智能爬虫**：基于Firecrawl技术，稳定抓取商品信息
- 🔍 **OCR筛选**：自动识别并过滤包含中文的图片
- 💹 **价格策略**：自动加价30%适配市场需求
- 🏷️ **智能分类**：使用Temu API自动推荐商品分类
- 📏 **尺码映射**：自动转换尺码信息符合Temu标准
- 🔄 **错误重试**：网络异常自动重试，确保稳定性
- 📝 **日志记录**：完整的操作日志便于追踪问题

## 快速开始

### 1. 环境要求

- Python 3.8+
- 稳定的网络连接
- 必要的API密钥（Firecrawl、百度OCR、Temu）

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/AutoTemu.git
cd AutoTemu

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入您的API密钥：
```ini
FIRECRAWL_API_KEY=your_actual_key
BAIDU_API_KEY=your_actual_key
BAIDU_SECRET_KEY=your_actual_key
TEMU_APP_KEY=your_actual_key
TEMU_APP_SECRET=your_actual_key
TEMU_ACCESS_TOKEN=your_actual_token
```

### 4. 使用

#### 基本命令

```bash
# 显示帮助信息
python -m src.main --help

# 测试系统连接
python -m src.main --test

# 显示系统状态
python -m src.main --status

# 处理单个商品URL
python -m src.main --url "https://example.com/product"

# 批量处理多个商品URL
python -m src.main --urls "https://example.com/product1" "https://example.com/product2"

# 指定输出目录
python -m src.main --url "https://example.com/product" --output "./output"

# 详细输出模式
python -m src.main --url "https://example.com/product" --verbose
```

#### 工作流程

1. **商品信息爬取**: 从指定URL爬取商品信息
2. **图片处理**: 下载并处理商品图片，使用OCR识别中文字符
3. **数据转换**: 将爬取的数据转换为Temu API格式
4. **尺码映射**: 自动映射商品尺码到Temu SKU系统
5. **商品上架**: 通过Temu API完成商品上架

## 项目结构

```
AutoTemu/
├── src/                    # 源代码目录
│   ├── api/               # API客户端
│   │   └── temu_client.py # Temu API封装
│   ├── image/             # 图片处理模块
│   │   ├── ocr_client.py  # OCR客户端
│   │   └── image_processor.py # 图片处理器
│   ├── scraper/           # 爬虫模块
│   │   └── product_scraper.py # 商品爬虫
│   ├── transformer/       # 数据转换模块
│   │   ├── data_transformer.py # 数据转换器
│   │   └── size_mapper.py # 尺码映射器
│   ├── utils/             # 工具模块
│   │   ├── config.py      # 配置管理
│   │   ├── logger.py      # 日志系统
│   │   ├── exceptions.py  # 异常定义
│   │   └── retry.py       # 重试机制
│   ├── models/            # 数据模型
│   │   └── data_models.py # 数据模型定义
│   └── main.py            # 主程序入口
├── tests/                 # 测试目录
├── logs/                  # 日志目录
├── images/                # 图片存储目录
├── docs/                  # 文档目录
├── requirements.txt       # 依赖列表
├── env.example           # 环境变量示例
└── README.md             # 本文件
```

## API密钥获取

### Firecrawl API
访问 [Firecrawl官网](https://firecrawl.com) 注册获取API密钥。

### 百度OCR API
1. 访问 [百度AI开放平台](https://ai.baidu.com)
2. 创建文字识别应用
3. 获取API Key和Secret Key

### Temu开发者API
1. 访问 [Temu开发者平台](https://seller.temu.com)
2. 申请开发者账号
3. 创建应用获取凭证

## 注意事项

- 请确保图片符合Temu要求：3:4比例，宽度≥1340px，高度≥1785px
- 每个商品至少需要3个尺码（如S、M、L）
- 上架失败的商品会记录在日志中，需要人工检查

## 故障排查

### 常见问题

1. **OCR识别失败**
   - 检查百度OCR API配额
   - 确认网络连接正常

2. **商品上架失败**
   - 检查Temu API凭证是否有效
   - 查看日志文件了解详细错误

3. **图片处理异常**
   - 确保有足够的磁盘空间
   - 检查图片URL是否可访问

## 开发

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_main.py -v

# 生成测试覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

### 代码风格

项目遵循PEP8编码规范，使用black进行代码格式化。

### 测试覆盖率

项目包含216个测试用例，覆盖所有核心功能模块：
- 配置管理 (10个测试)
- 数据模型 (25个测试)
- 数据转换 (25个测试)
- 异常处理 (15个测试)
- 图片处理 (15个测试)
- 日志系统 (10个测试)
- 主程序 (12个测试)
- OCR客户端 (20个测试)
- 商品爬虫 (15个测试)
- 重试机制 (15个测试)
- 尺码映射 (15个测试)
- Temu API客户端 (20个测试)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
