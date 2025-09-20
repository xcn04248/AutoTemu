#!/usr/bin/env python3
"""
测试嵌套对象的签名生成

重点测试嵌套对象（如 goodsBasic, skuList）的签名生成
"""

import hashlib
import json
from typing import Dict, Any


def java_style_signature_with_nested(params: Dict[str, Any], app_secret: str) -> str:
    """
    按照 Java 代码逻辑生成签名，处理嵌套对象
    """
    try:
        # 1. 参数排序
        sorted_params = dict(sorted(params.items()))
        
        # 2. 构建签名字符串
        sign_str = app_secret
        
        for key, value in sorted_params.items():
            if value is not None and key != "sign":
                # 处理嵌套对象
                if isinstance(value, (dict, list)):
                    # 将嵌套对象转换为 JSON 字符串
                    value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
                else:
                    value_str = str(value)
                
                sign_str += str(key) + value_str
        
        sign_str += app_secret
        
        print(f"  📊 签名字符串: {sign_str}")
        
        # 3. MD5加密
        md5_hash = hashlib.md5(sign_str.encode('utf-8'))
        
        # 4. 转换为十六进制字符串并转大写
        return md5_hash.hexdigest().upper()
        
    except Exception as e:
        raise RuntimeError(f"签名生成失败: {e}")


def current_python_signature_with_nested(params: Dict[str, Any], app_secret: str) -> str:
    """
    当前 Python 代码的签名生成逻辑，处理嵌套对象
    """
    try:
        # 1. 参数排序
        sorted_params = dict(sorted(params.items()))
        
        # 2. 构建签名字符串
        result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        result_str = result_str.replace(" ", "").replace("'", '"')
        concatenated_str = f'{app_secret}{result_str}{app_secret}'
        
        print(f"  📊 签名字符串: {concatenated_str}")
        
        # 3. MD5加密
        md5_hash = hashlib.md5(concatenated_str.encode('utf-8'))
        
        # 4. 转换为十六进制字符串并转大写
        return md5_hash.hexdigest().upper()
        
    except Exception as e:
        raise RuntimeError(f"签名生成失败: {e}")


def test_nested_object_signature():
    """测试嵌套对象的签名生成"""
    print("🔍 测试嵌套对象的签名生成")
    print("=" * 60)
    
    # 测试参数 - 包含嵌套对象
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
    
    # 1. 测试 Java 风格签名
    print("1️⃣ Java 风格签名生成")
    print("-" * 40)
    try:
        java_sign = java_style_signature_with_nested(test_params, app_secret)
        print(f"  ✅ Java 风格签名: {java_sign}")
    except Exception as e:
        print(f"  ❌ Java 风格签名失败: {e}")
    print()
    
    # 2. 测试当前 Python 风格签名
    print("2️⃣ 当前 Python 风格签名生成")
    print("-" * 40)
    try:
        python_sign = current_python_signature_with_nested(test_params, app_secret)
        print(f"  ✅ Python 风格签名: {python_sign}")
    except Exception as e:
        print(f"  ❌ Python 风格签名失败: {e}")
    print()
    
    # 3. 对比结果
    print("3️⃣ 对比结果")
    print("-" * 40)
    try:
        java_sign = java_style_signature_with_nested(test_params, app_secret)
        python_sign = current_python_signature_with_nested(test_params, app_secret)
        
        print(f"Java 风格签名: {java_sign}")
        print(f"Python 风格签名: {python_sign}")
        print(f"签名是否相同: {'✅ 是' if java_sign == python_sign else '❌ 否'}")
        
        if java_sign != python_sign:
            print("\n🔍 差异分析:")
            print("  - Java 风格: 将嵌套对象转换为 JSON 字符串")
            print("  - Python 风格: 直接拼接嵌套对象")
            print("  - 这可能导致签名不一致")
        
    except Exception as e:
        print(f"  ❌ 对比失败: {e}")
    print()
    
    # 4. 测试真实商品创建参数
    print("4️⃣ 测试真实商品创建参数")
    print("-" * 40)
    
    real_params = {
        "type": "bg.local.goods.add",
        "app_key": "test_app_key",
        "access_token": "test_access_token",
        "timestamp": 1640995200,
        "data_type": "JSON",
        "goodsBasic": {
            "goodsName": "测试商品",
            "goodsDesc": "测试描述",
            "catId": "26579",
            "specIdList": [116084851],
            "brandId": None,
            "trademarkId": None,
            "goodsType": 1,
            "goodsStatus": 1,
            "goodsWeight": 0.1,
            "goodsLength": 10,
            "goodsWidth": 10,
            "goodsHeight": 10,
            "packageLength": 15,
            "packageWidth": 15,
            "packageHeight": 15,
            "packageWeight": 0.2,
            "goodsImageList": [],
            "goodsVideoList": [],
            "goodsAttributeList": []
        },
        "goodsServicePromise": {
            "shippingTemplateId": None,
            "warrantyTemplateId": None,
            "returnTemplateId": None,
            "servicePromise": []
        },
        "goodsProperty": {
            "material": "Cotton",
            "style": "Casual",
            "season": "All Season",
            "gender": "Unisex",
            "ageGroup": "Adult",
            "color": "Multi",
            "pattern": "Solid",
            "sleeveLength": "Long Sleeve",
            "neckline": "Round Neck",
            "fit": "Regular",
            "occasion": "Daily",
            "careInstructions": "Machine Wash"
        },
        "skuList": [
            {
                "skuId": "test_sku_001",
                "skuName": "M",
                "specIdList": [116084851],
                "skuImageList": [],
                "skuAttributeList": [],
                "price": 10.0,
                "currency": "USD",
                "inventory": 100,
                "skuStatus": 1
            }
        ]
    }
    
    try:
        java_sign = java_style_signature_with_nested(real_params, app_secret)
        python_sign = current_python_signature_with_nested(real_params, app_secret)
        
        print(f"Java 风格签名: {java_sign}")
        print(f"Python 风格签名: {python_sign}")
        print(f"签名是否相同: {'✅ 是' if java_sign == python_sign else '❌ 否'}")
        
    except Exception as e:
        print(f"  ❌ 真实参数测试失败: {e}")
    print()
    
    # 5. 修复建议
    print("5️⃣ 修复建议")
    print("-" * 40)
    
    print("🔧 关键修复点:")
    print("  1. 嵌套对象处理:")
    print("     - 使用 JSON 序列化嵌套对象")
    print("     - 确保与 Java 代码一致")
    print()
    print("  2. 空值处理:")
    print("     - 跳过 None 值")
    print("     - 跳过 'sign' 键")
    print()
    print("  3. 字符串格式:")
    print("     - 移除不必要的字符串替换")
    print("     - 保持与 Java 代码一致")
    print()


if __name__ == "__main__":
    test_nested_object_signature()
