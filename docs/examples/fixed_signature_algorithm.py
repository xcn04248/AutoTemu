#!/usr/bin/env python3
"""
修复的签名生成算法

基于 Java 代码逻辑修复 Python 签名生成
"""

import hashlib
import json
from typing import Dict, Any


def fixed_signature_algorithm(params: Dict[str, Any], app_secret: str) -> str:
    """
    修复的签名生成算法
    
    基于 Java 代码逻辑：
    1. 参数排序
    2. 构建签名字符串: appSecret + key1value1 + key2value2 + ... + appSecret
    3. 跳过 null 值和 'sign' 键
    4. MD5加密
    5. 转换为十六进制字符串并转大写
    """
    try:
        # 1. 参数排序
        sorted_params = dict(sorted(params.items()))
        
        # 2. 构建签名字符串
        sign_str = app_secret
        
        for key, value in sorted_params.items():
            # 跳过 None 值和 'sign' 键
            if value is not None and key != "sign":
                # 处理嵌套对象
                if isinstance(value, (dict, list)):
                    # 将嵌套对象转换为 JSON 字符串，使用紧凑格式
                    value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
                else:
                    value_str = str(value)
                
                sign_str += str(key) + value_str
        
        sign_str += app_secret
        
        # 3. MD5加密
        md5_hash = hashlib.md5(sign_str.encode('utf-8'))
        
        # 4. 转换为十六进制字符串并转大写
        return md5_hash.hexdigest().upper()
        
    except Exception as e:
        raise RuntimeError(f"签名生成失败: {e}")


def test_fixed_signature():
    """测试修复的签名算法"""
    print("🔍 测试修复的签名算法")
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
    
    app_secret = "test_app_secret"
    
    print("📋 测试参数:")
    print(json.dumps(test_params, indent=2, ensure_ascii=False))
    print()
    
    # 1. 测试修复的签名算法
    print("1️⃣ 修复的签名算法")
    print("-" * 40)
    try:
        fixed_sign = fixed_signature_algorithm(test_params, app_secret)
        print(f"  ✅ 修复的签名: {fixed_sign}")
        
        # 显示签名字符串
        sorted_params = dict(sorted(test_params.items()))
        sign_str = app_secret
        for key, value in sorted_params.items():
            if value is not None and key != "sign":
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
                else:
                    value_str = str(value)
                sign_str += str(key) + value_str
        sign_str += app_secret
        
        print(f"  📊 签名字符串: {sign_str}")
        
    except Exception as e:
        print(f"  ❌ 修复的签名失败: {e}")
    print()
    
    # 2. 对比修复前后的差异
    print("2️⃣ 修复前后对比")
    print("-" * 40)
    
    # 修复前的算法（当前 Python 代码）
    def old_algorithm(params, app_secret):
        sorted_params = dict(sorted(params.items()))
        result_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        result_str = result_str.replace(" ", "").replace("'", '"')
        concatenated_str = f'{app_secret}{result_str}{app_secret}'
        md5_hash = hashlib.md5(concatenated_str.encode('utf-8'))
        return md5_hash.hexdigest().upper()
    
    try:
        old_sign = old_algorithm(test_params, app_secret)
        new_sign = fixed_signature_algorithm(test_params, app_secret)
        
        print(f"修复前签名: {old_sign}")
        print(f"修复后签名: {new_sign}")
        print(f"签名是否相同: {'✅ 是' if old_sign == new_sign else '❌ 否'}")
        
        if old_sign != new_sign:
            print("\n🔍 主要差异:")
            print("  1. 空值处理: 修复后跳过 None 值")
            print("  2. 字符串处理: 修复后不移除空格")
            print("  3. 嵌套对象: 修复后使用 JSON 序列化")
        
    except Exception as e:
        print(f"  ❌ 对比失败: {e}")
    print()
    
    # 3. 生成修复后的 BaseClient 代码
    print("3️⃣ 修复后的 BaseClient 代码")
    print("-" * 40)
    
    print("```python")
    print("def _get_sign(self, params):")
    print("    sorted_params = dict(sorted(params.items()))")
    print("    sign_str = self.app_secret")
    print("    ")
    print("    for key, value in sorted_params.items():")
    print("        # 跳过 None 值和 'sign' 键")
    print("        if value is not None and key != 'sign':")
    print("            # 处理嵌套对象")
    print("            if isinstance(value, (dict, list)):")
    print("                # 将嵌套对象转换为 JSON 字符串")
    print("                value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)")
    print("            else:")
    print("                value_str = str(value)")
    print("            ")
    print("            sign_str += str(key) + value_str")
    print("    ")
    print("    sign_str += self.app_secret")
    print("    return self._md5(sign_str)")
    print("```")
    print()
    
    # 4. 建议的修复步骤
    print("4️⃣ 建议的修复步骤")
    print("-" * 40)
    
    print("🔧 修复步骤:")
    print("  1. 修改 BaseClient._get_sign 方法")
    print("  2. 添加空值过滤逻辑")
    print("  3. 改进嵌套对象处理")
    print("  4. 移除不必要的字符串替换")
    print("  5. 测试修复后的签名生成")
    print()


if __name__ == "__main__":
    test_fixed_signature()
