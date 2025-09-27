#!/usr/bin/env python3
"""
测试运行脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", verbose=False, coverage=False):
    """运行测试"""
    
    # 设置项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 添加测试路径
    if test_type == "unit":
        cmd.extend(["tests/test_bg_client.py", "tests/test_bg_transformer.py", "tests/test_api_adapter.py"])
    elif test_type == "integration":
        cmd.extend(["tests/test_product_manager_integration.py"])
    elif test_type == "new_api":
        cmd.extend([
            "tests/test_bg_client.py",
            "tests/test_bg_transformer.py", 
            "tests/test_api_adapter.py",
            "tests/test_product_manager_integration.py"
        ])
    else:  # all
        cmd.extend(["tests/"])
    
    # 添加选项
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # 添加其他选项
    cmd.extend([
        "--tb=short",  # 简短的traceback
        "--strict-markers",  # 严格标记检查
        "-x",  # 遇到第一个失败就停止
    ])
    
    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 50)
    
    # 运行测试
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 50)
        print("✅ 所有测试通过!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 50)
        print(f"❌ 测试失败，退出码: {e.returncode}")
        return False
    except Exception as e:
        print("=" * 50)
        print(f"❌ 运行测试时发生错误: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AutoTemu测试运行器")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "new_api"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true", 
        help="生成覆盖率报告"
    )
    
    args = parser.parse_args()
    
    print("🚀 AutoTemu测试运行器")
    print(f"测试类型: {args.type}")
    print(f"详细输出: {args.verbose}")
    print(f"覆盖率报告: {args.coverage}")
    print()
    
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    if success:
        print("\n🎉 测试完成!")
        sys.exit(0)
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
