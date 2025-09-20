#!/usr/bin/env python3
"""
对比签名生成算法

对比 Java 代码和 Python 代码的签名生成逻辑
"""

import hashlib
import json
from typing import Dict, Any


def java_style_signature(params: Dict[str, Any], app_secret: str) -> str:
    """
    按照 Java 代码逻辑生成签名
    
    Java 代码逻辑：
    1. 参数排序 (TreeMap)
    2. 构建签名字符串: appSecret + key1value1 + key2value2 + ... + appSecret
    3. MD5加密
    4. 转换为十六进制字符串并转大写
    """
    try:
        # 1. 参数排序
        sorted_params = dict(sorted(params.items()))
        
        # 2. 构建签名字符串
        sign_str = app_secret
        
        for key, value in sorted_params.items():
            if value is not None and key != "sign":
                sign_str += str(key) + str(value)
        
        sign_str += app_secret
        
        # 3. MD5加密
        md5_hash = hashlib.md5(sign_str.encode('utf-8'))
        
        # 4. 转换为十六进制字符串并转大写
        return md5_hash.hexdigest().upper()
        
    except Exception as e:
        raise RuntimeError(f"签名生成失败: {e}")


def current_python_signature(params: Dict[str, Any], app_secret: str) -> str:
    """
    当前 Python 代码的签名生成逻辑
    """
    try:
        # 1. 参数排序
        sorted_params = dict(sorted(params.items()))
        
        # 2. 构建签名字符串
        result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        result_str = result_str.replace(" ", "").replace("'", '"')
        concatenated_str = f'{app_secret}{result_str}{app_secret}'
        
        # 3. MD5加密
        md5_hash = hashlib.md5(concatenated_str.encode('utf-8'))
        
        # 4. 转换为十六进制字符串并转大写
        return md5_hash.hexdigest().upper()
        
    except Exception as e:
        raise RuntimeError(f"签名生成失败: {e}")


def compare_signature_algorithms():
    """对比两种签名算法"""
    print("🔍 对比签名生成算法")
    print("=" * 60)
    
    # 测试参数
    test_params = {
        "type": "bg.local.goods.add",
        "app_key": "test_app_key",
        "access_token": "test_access_token",
        "timestamp": 1640995200,
        "data_type": "JSON",
        "goodsBasic": {
            "goodsName": "测试商品",
            "catId": "12345",
            "specIdList": [123456]
        },
        "skuList": [
            {
                "skuId": "test_sku_001",
                "specIdList": [123456]
            }
        ]
    }
    
    app_secret = "test_app_secret"
    
    print("📋 测试参数:")
    print(json.dumps(test_params, indent=2, ensure_ascii=False))
    print()
    
    # 1. 对比算法逻辑
    print("1️⃣ 算法逻辑对比")
    print("-" * 40)
    
    print("Java 代码逻辑:")
    print("  1. 参数排序 (TreeMap)")
    print("  2. 构建签名字符串: appSecret + key1value1 + key2value2 + ... + appSecret")
    print("  3. 跳过 null 值和 'sign' 键")
    print("  4. MD5加密")
    print("  5. 转换为十六进制字符串并转大写")
    print()
    
    print("当前 Python 代码逻辑:")
    print("  1. 参数排序 (dict sorted)")
    print("  2. 构建签名字符串: appSecret + key1value1 + key2value2 + ... + appSecret")
    print("  3. 替换空格和单引号")
    print("  4. MD5加密")
    print("  5. 转换为十六进制字符串并转大写")
    print()
    
    # 2. 关键差异分析
    print("2️⃣ 关键差异分析")
    print("-" * 40)
    
    print("🔍 主要差异:")
    print("  1. 空值处理:")
    print("     - Java: 跳过 null 值")
    print("     - Python: 没有明确跳过 None 值")
    print()
    print("  2. 字符串处理:")
    print("     - Java: 直接拼接 key + value")
    print("     - Python: 拼接后替换空格和单引号")
    print()
    print("  3. 嵌套对象处理:")
    print("     - Java: 直接转换为字符串")
    print("     - Python: 可能有问题，需要 JSON 序列化")
    print()
    
    # 3. 测试签名生成
    print("3️⃣ 测试签名生成")
    print("-" * 40)
    
    try:
        # 简化参数进行测试
        simple_params = {
            "type": "bg.local.goods.add",
            "app_key": "test_app_key",
            "access_token": "test_access_token",
            "timestamp": 1640995200,
            "data_type": "JSON"
        }
        
        java_sign = java_style_signature(simple_params, app_secret)
        python_sign = current_python_signature(simple_params, app_secret)
        
        print(f"Java 风格签名: {java_sign}")
        print(f"Python 风格签名: {python_sign}")
        print(f"签名是否相同: {'✅ 是' if java_sign == python_sign else '❌ 否'}")
        print()
        
    except Exception as e:
        print(f"❌ 签名生成测试失败: {e}")
        print()
    
    # 4. 问题分析
    print("4️⃣ 问题分析")
    print("-" * 40)
    
    print("🔍 可能的问题:")
    print("  1. 嵌套对象处理:")
    print("     - 当前代码直接拼接嵌套对象，可能格式不正确")
    print("     - 需要将嵌套对象转换为 JSON 字符串")
    print()
    print("  2. 空值处理:")
    print("     - 当前代码没有跳过 None 值")
    print("     - 可能包含 'None' 字符串")
    print()
    print("  3. 数据类型处理:")
    print("     - 列表和字典需要正确序列化")
    print("     - 数字类型需要正确转换")
    print()
    
    # 5. 修复建议
    print("5️⃣ 修复建议")
    print("-" * 40)
    
    print("🔧 建议的修复:")
    print("  1. 添加空值过滤:")
    print("     - 跳过 None 值")
    print("     - 跳过 'sign' 键")
    print()
    print("  2. 改进嵌套对象处理:")
    print("     - 使用 JSON 序列化嵌套对象")
    print("     - 确保一致的格式")
    print()
    print("  3. 统一字符串处理:")
    print("     - 移除不必要的字符串替换")
    print("     - 保持与 Java 代码一致")
    print()


if __name__ == "__main__":
    compare_signature_algorithms()
