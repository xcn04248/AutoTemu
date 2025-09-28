# GEMINI.md: AutoTemu 项目上下文 (中文版)

本文档为 Gemini agent 提供了关于 AutoTemu 项目的全面概述。

## 1. 项目概述

**AutoTemu** 是一个基于 Python 的自动化系统，旨在从电子商务网站上抓取商品信息，并自动将其发布到 Temu 电商平台（特别是日本站）。该系统能够处理 Temu 上的不同运营模式，尤其是“半托管”（semi-managed）和“全托管”（fully-managed）流程。

该项目高度模块化，并包含一套完整的用于配置、日志记录和错误处理的工具。

### 核心技术

*   **后端:** Python 3.8+
*   **网络抓取:** [Firecrawl](https://firecrawl.dev/)
*   **API 交互:** 一个用于与 Temu API 交互的自定义客户端。该系统被设计用于处理多个 API 版本和网关。
*   **图像处理:** 使用 Pillow 进行图像处理，并使用百度智能云 OCR 来检测和过滤包含中文文本的图片。
*   **主要依赖:** `requests`, `python-dotenv`, `Pillow`, `temu-api`, `firecrawl`。
*   **测试:** `pytest`, `pytest-cov`, `pytest-mock`。

### 系统架构

项目遵循位于 `src` 目录下的模块化结构：

*   `src/api/`: 包含用于 Temu (`temu_client.py`, `bg_client.py`) 和其他服务的 API 客户端。该层抽象了处理不同 API 版本的复杂性。
*   `src/core/`: 核心业务逻辑，包括 `product_manager.py`，它负责协调整个商品发布流程。
*   `src/image/`: 处理图像下载、处理和 OCR (`image_processor.py`, `ocr_client.py`)。
*   `src/scraper/`: 使用 Firecrawl 的网络抓取模块 (`product_scraper.py`)。
*   `src/transform/`: 数据转换逻辑，包括将抓取的数据映射到 Temu API 格式以及处理尺码表 (`data_transformer.py`, `size_mapper.py`)。
*   `src/models/`: 用于已抓取商品和 Temu API 对象的 Pydantic 数据模型。
*   `src/utils/`: 用于配置 (`config.py`)、日志 (`logger.py`) 和异常处理的工具模块。
*   `src/main.py`: 应用程序的主要命令行界面（CLI）入口点。

### API 集成详情

该项目的一个关键方面是与 Temu API 的交互，该 API 正在经历重大变更。

*   **网关迁移:** API 正在从原有的 `openapi.kuajingmaihuo.com` 网关迁移到一个新的 **`openapi-b-partner.temu.com`** 网关。应用程序必须知道针对给定的 API 调用应使用哪个端点。
*   **API 版本:** 文档指出了不同 API `type` 命名方案之间的过渡：
    *   **旧版 API:** 标准的端点（例如 `temu.goods.add`）。
    *   **新的 "BG" API:** 一套较新的、为“半托管”卖家设计的 API，前缀为 `bg.`（例如 `bg.goods.add`, `bg.goods.attrs.get`）。
    *   **最新的 "temu." API:** 最新的文档显示，一些 `bg.` API 正在被新的合作伙伴网关上的 `temu.` 前缀所取代（例如 `bg.goods.add` 正在变为 `temu.goods.add`）。
*   **关键工作流程:** `docs_new` 目录包含了详细且最新的商品发布工作流程，包括类目匹配、属性检索、尺码表创建和图频处理，这些对于正确使用 API至关重要。

## 2. 构建与运行

### 环境设置

1.  **创建虚拟环境:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **配置环境变量:**
    *   将 `.env.example` 复制为 `.env`。
    *   填入 Temu、Firecrawl 和百度 OCR 所需的 API 密钥。请注意，不同的 API 网关可能需要不同的凭证或授权范围。

### 运行应用

主要入口点是 `src/main.py`。它可以作为一个模块运行。

*   **处理单个商品 URL:**
    ```bash
    python -m src.main --url "https://example.com/product"
    ```
*   **处理多个 URL:**
    ```bash
    python -m src.main --urls "url1" "url2"
    ```
*   **测试 API 连接:**
    ```bash
    python -m src.main --test
    ```
*   **查看系统状态:**
    ```bash
    python -m src.main --status
    ```

### 运行测试

项目使用 `pytest` 进行测试。

*   **运行所有测试:**
    ```bash
    pytest
    ```
    或
    ```bash
    python -m pytest tests/
    ```
*   **运行测试并生成覆盖率报告:**
    ```bash
    pytest --cov=src tests/
    ```
*   项目中还有一个 `run_tests.py` 脚本，可能包含特定的测试配置。

## 3. 开发约定

*   **模块化设计:** 代码高度模块化，并按功能组织。核心逻辑与工具和 API 客户端分离。
*   **API 抽象:** 多个 API 客户端和不断变化的端点的存在表明，应在 `src/api` 层内谨慎进行更改，以避免破坏核心业务逻辑。
*   **类型注解:** 代码库广泛使用 Python 的类型提示。
*   **测试:** 项目非常重视测试，拥有一个专门的 `tests` 目录和大量的测试用例（文档中报告有216个），覆盖了所有模块。
*   **配置管理:** 应用程序配置通过 `.env` 文件和 `src/utils/config.py` 模块的组合进行管理。
*   **错误处理:** 项目中有一个自定义的异常层次结构 (`src/utils/exceptions.py`) 和一个重试机制 (`src/utils/retry.py`)，以实现稳健的错误处理。
*   **文档:** 项目文档齐全，拥有一个广泛的 `docs` 和 `docs_new` 目录。**`docs_new` 包含最新的 API 规范，应优先查阅。**
