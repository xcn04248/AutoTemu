#!/usr/bin/env python3
"""
项目清理脚本
用于整理项目结构，移动文件到合适的位置
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """清理项目结构"""
    print("🧹 开始清理项目结构...")
    
    # 项目根目录
    root_dir = Path(".")
    
    # 创建必要的目录
    directories = [
        "docs/temu_api",
        "docs/guides", 
        "docs/examples",
        "docs/tests",
        "temp",
        "backup"
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    # 移动文件到合适的位置
    file_moves = [
        # 文档文件
        ("temu_product_listing_flow.md", "docs/temu_api/"),
        ("temu_field_validation_rules.md", "docs/temu_api/"),
        ("temu_image_specifications.md", "docs/temu_api/"),
        ("PROJECT_COMPLETION_REPORT.md", "docs/"),
        ("PROJECT_STATUS_REPORT.md", "docs/"),
        
        # 测试文件
        ("test_*.py", "docs/tests/"),
        
        # 示例和调试文件
        ("debug_*.py", "docs/examples/"),
        ("compare_*.py", "docs/examples/"),
        ("get_*.py", "docs/examples/"),
        ("fixed_*.py", "docs/examples/"),
        ("example_usage.py", "docs/examples/"),
        ("complete_product_listing.py", "docs/examples/"),
    ]
    
    # 处理文件移动
    for pattern, target_dir in file_moves:
        if "*" in pattern:
            # 处理通配符模式
            import glob
            files = glob.glob(pattern)
            for file_path in files:
                if os.path.exists(file_path):
                    target_path = os.path.join(target_dir, os.path.basename(file_path))
                    shutil.move(file_path, target_path)
                    print(f"✅ 移动文件: {file_path} -> {target_path}")
        else:
            # 处理单个文件
            if os.path.exists(pattern):
                target_path = os.path.join(target_dir, os.path.basename(pattern))
                shutil.move(pattern, target_path)
                print(f"✅ 移动文件: {pattern} -> {target_path}")
    
    # 清理临时文件
    temp_files = [
        "*.pyc",
        "__pycache__",
        "*.log",
        "*.tmp",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    for pattern in temp_files:
        import glob
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"🗑️ 删除临时文件: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"🗑️ 删除临时目录: {file_path}")
    
    print("✅ 项目清理完成！")

def create_gitignore():
    """创建或更新 .gitignore 文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
log/

# Images
images/
*.jpg
*.jpeg
*.png
*.gif
*.bmp
*.tiff

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Temporary files
temp/
tmp/
*.tmp
*.temp

# Backup files
backup/
*.bak
*.backup

# Test coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("✅ 创建 .gitignore 文件")

def create_docs_readme():
    """创建文档目录的 README"""
    readme_content = """# AutoTemu 项目文档

## 📚 文档结构

### 🚀 快速开始
- [快速开始指南](guides/quick_start.md) - 5分钟快速上手
- [环境配置指南](guides/environment_setup.md) - 详细环境配置

### 📖 核心文档
- [项目概述](AutoTemu/PROJECT_SUMMARY.md) - 项目整体介绍
- [系统设计](AutoTemu/DESIGN_AutoTemu.md) - 系统架构设计
- [任务分解](AutoTemu/TASK_AutoTemu.md) - 开发任务分解

### 🔧 Temu API 文档
- [商品上架流程](temu_api/temu_product_listing_flow.md) - 完整的商品上架流程
- [字段验证规则](temu_api/temu_field_validation_rules.md) - 详细的字段验证规则
- [图片规格要求](temu_api/temu_image_specifications.md) - 图片和媒体规格要求

### 📋 项目状态
- [项目完成报告](PROJECT_COMPLETION_REPORT.md) - 项目完成情况总结
- [待办事项](AutoTemu/TODO_AutoTemu.md) - 待完成任务列表

### 🧪 测试和示例
- [测试文件](tests/) - 所有测试脚本
- [示例代码](examples/) - 使用示例和调试脚本

## 🔍 快速导航

- [文档索引](index.md) - 完整文档导航
- [项目根目录](../README.md) - 返回项目主页

---
**最后更新**: 2024-01-XX
"""
    
    with open("docs/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ 创建文档 README")

if __name__ == "__main__":
    cleanup_project()
    create_gitignore()
    create_docs_readme()
    print("\n🎉 项目整理完成！")
    print("\n📁 新的项目结构:")
    print("├── docs/")
    print("│   ├── AutoTemu/          # 6A工作流文档")
    print("│   ├── temu_api/          # Temu API文档")
    print("│   ├── guides/            # 使用指南")
    print("│   ├── examples/          # 示例代码")
    print("│   └── tests/             # 测试脚本")
    print("├── src/                   # 源代码")
    print("├── tests/                 # 单元测试")
    print("└── README.md              # 项目主页")
