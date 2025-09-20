# 环境配置指南

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**: 3.8+
- **内存**: 4GB RAM
- **存储空间**: 2GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python版本**: 3.9+
- **内存**: 8GB+ RAM
- **存储空间**: 5GB+ 可用空间
- **网络**: 高速互联网连接

## 🐍 Python 环境配置

### 1. 安装 Python

#### Windows
```bash
# 下载 Python 3.9+ 从官网
# https://www.python.org/downloads/

# 或使用 Chocolatey
choco install python

# 或使用 Scoop
scoop install python
```

#### macOS
```bash
# 使用 Homebrew
brew install python@3.9

# 或从官网下载安装包
# https://www.python.org/downloads/macos/
```

#### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装 Python 3.9+
sudo apt install python3.9 python3.9-venv python3.9-pip

# 设置默认 Python 版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

### 2. 验证 Python 安装
```bash
python --version
python3 --version
pip --version
```

## 🔧 项目环境配置

### 1. 克隆项目
```bash
git clone <repository-url>
cd AutoTemu
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖
```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 验证安装
```bash
# 检查依赖安装
pip list

# 运行测试
python -m pytest tests/ -v
```

## 🔑 API 密钥配置

### 1. 获取 API 密钥

#### Firecrawl API
1. 访问 [Firecrawl 官网](https://firecrawl.dev/)
2. 注册账户并登录
3. 在控制台获取 API 密钥

#### 百度 OCR API
1. 访问 [百度智能云](https://cloud.baidu.com/)
2. 注册账户并登录
3. 创建 OCR 应用
4. 获取 API Key 和 Secret Key

#### Temu API
1. 访问 [Temu 合作伙伴平台](https://partner.temu.com/)
2. 注册商家账户
3. 申请 API 访问权限
4. 获取 App Key、App Secret 和 Access Token

### 2. 配置环境变量

#### 创建 .env 文件
```bash
# 复制环境变量模板
cp env.example .env
```

#### 编辑 .env 文件
```bash
# Firecrawl API 配置
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# 百度 OCR API 配置
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here

# Temu API 配置
TEMU_APP_KEY=your_temu_app_key_here
TEMU_APP_SECRET=your_temu_app_secret_here
TEMU_ACCESS_TOKEN=your_temu_access_token_here
TEMU_BASE_URL=https://openapi-b-global.temu.com

# 业务配置
PRICE_MARKUP=1.3
LOG_LEVEL=INFO
IMAGE_SAVE_PATH=./images
MAX_RETRY_ATTEMPTS=3
RETRY_INITIAL_DELAY=1.0
RETRY_MAX_DELAY=60.0
```

### 3. 验证 API 配置
```python
# 测试 API 连接
python -c "
from src.main import AutoTemuApp
app = AutoTemuApp()
print('✅ 配置加载成功')
if app.test_connection():
    print('✅ Temu API 连接成功')
else:
    print('❌ Temu API 连接失败')
"
```

## 🗂️ 目录结构配置

### 1. 创建必要目录
```bash
# 创建图片存储目录
mkdir -p images

# 创建日志目录
mkdir -p logs

# 创建临时文件目录
mkdir -p temp
```

### 2. 设置目录权限
```bash
# Linux/macOS
chmod 755 images logs temp

# 设置日志目录可写
chmod 777 logs
```

## 🔧 开发环境配置

### 1. 安装开发依赖
```bash
# 安装开发工具
pip install pytest pytest-cov black flake8 mypy

# 安装调试工具
pip install ipdb pdbpp
```

### 2. 配置代码格式化
```bash
# 创建 .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
EOF

# 安装 pre-commit
pip install pre-commit
pre-commit install
```

### 3. 配置 IDE

#### VS Code
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm
1. 打开项目设置
2. 配置 Python 解释器为虚拟环境
3. 启用代码检查和格式化
4. 配置测试运行器为 pytest

## 🐳 Docker 配置（可选）

### 1. 创建 Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p images logs temp

# 设置环境变量
ENV PYTHONPATH=/app

# 运行命令
CMD ["python", "src/main.py"]
```

### 2. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  autotemu:
    build: .
    volumes:
      - ./images:/app/images
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - PYTHONPATH=/app
    command: python src/main.py
```

### 3. 使用 Docker
```bash
# 构建镜像
docker build -t autotemu .

# 运行容器
docker run -d --name autotemu autotemu

# 使用 docker-compose
docker-compose up -d
```

## 🔍 故障排除

### 1. 常见问题

#### Python 版本问题
```bash
# 检查 Python 版本
python --version

# 如果版本过低，升级 Python
# 或使用 pyenv 管理多个 Python 版本
```

#### 依赖安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 清理缓存
pip cache purge
```

#### 权限问题
```bash
# Linux/macOS 权限问题
sudo chown -R $USER:$USER .
chmod -R 755 .

# Windows 权限问题
# 以管理员身份运行命令提示符
```

#### 网络连接问题
```bash
# 检查网络连接
ping google.com

# 配置代理（如果需要）
export http_proxy=http://proxy:port
export https_proxy=https://proxy:port
```

### 2. 调试工具

#### 检查环境变量
```python
import os
from dotenv import load_dotenv

load_dotenv()
print("Firecrawl API Key:", os.getenv("FIRECRAWL_API_KEY"))
print("Baidu API Key:", os.getenv("BAIDU_API_KEY"))
print("Temu App Key:", os.getenv("TEMU_APP_KEY"))
```

#### 检查依赖安装
```python
import sys
import pkg_resources

# 检查已安装的包
installed_packages = [d.project_name for d in pkg_resources.working_set]
required_packages = ["requests", "pillow", "python-dotenv", "temu-api"]

for package in required_packages:
    if package in installed_packages:
        print(f"✅ {package} 已安装")
    else:
        print(f"❌ {package} 未安装")
```

#### 检查 API 连接
```python
# 测试各个 API 连接
from src.main import AutoTemuApp

app = AutoTemuApp()

# 测试 Temu API
if app.test_connection():
    print("✅ Temu API 连接正常")
else:
    print("❌ Temu API 连接失败")

# 测试系统状态
status = app.get_system_status()
print(f"系统状态: {status}")
```

## 📚 更多资源

### 官方文档
- [Python 官方文档](https://docs.python.org/3/)
- [pip 用户指南](https://pip.pypa.io/en/stable/user_guide/)
- [虚拟环境指南](https://docs.python.org/3/tutorial/venv.html)

### 项目文档
- [快速开始指南](quick_start.md)
- [API 文档](../temu_api/)
- [故障排除指南](troubleshooting.md)

### 社区支持
- [GitHub Issues](../../issues)
- [GitHub Discussions](../../discussions)
- [技术交流群]

---

**需要帮助？** 查看 [快速开始指南](quick_start.md) 或提交 [Issue](../../issues)。
