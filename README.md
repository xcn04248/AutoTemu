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

```bash
python src/main.py --url "https://www.jp0663.com/detail/your-product-url"
```

## 项目结构

```
AutoTemu/
├── src/                    # 源代码目录
│   ├── scraper/           # 爬虫模块
│   ├── image/             # 图片处理模块
│   ├── transformer/       # 数据转换模块
│   ├── temu/              # Temu API封装
│   ├── utils/             # 工具类
│   └── models/            # 数据模型
├── tests/                 # 测试目录
├── logs/                  # 日志目录
├── images/                # 图片存储目录
├── docs/                  # 文档目录
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
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
pytest tests/
```

### 代码风格

项目遵循PEP8编码规范，使用black进行代码格式化。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
