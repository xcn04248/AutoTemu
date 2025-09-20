#!/usr/bin/env python3
"""
修复的 BaseClient 类

修复签名生成算法以匹配 Java 代码逻辑
"""

import hashlib
import json
import logging
import time
import requests
from typing import Dict, Any


class FixedBaseClient:
    """修复的 BaseClient 类"""
    
    method = 'GET'

    def __init__(self, app_key, app_secret, access_token, base_url: str, debug=False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = base_url
        self.debug = debug
        self.headers = {
            "content-type": "application/json;charset=UTF-8",
        }
        self.common_params = {
            "app_key": self.app_key,
            "access_token": self.access_token,
            "data_type": "JSON",
        }

    def _md5(self, text: str) -> str:
        """计算输入字符串的 MD5 哈希值"""
        md5_hash = hashlib.md5(text.encode('utf-8'))
        return md5_hash.hexdigest().upper()

    def _get_sign(self, params: Dict[str, Any]) -> str:
        """
        修复的签名生成方法
        
        基于 Java 代码逻辑：
        1. 参数排序
        2. 构建签名字符串: appSecret + key1value1 + key2value2 + ... + appSecret
        3. 跳过 None 值和 'sign' 键
        4. MD5加密
        5. 转换为十六进制字符串并转大写
        """
        try:
            # 1. 参数排序
            sorted_params = dict(sorted(params.items()))
            
            # 2. 构建签名字符串
            sign_str = self.app_secret
            
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
            
            sign_str += self.app_secret
            
            # 3. MD5加密
            return self._md5(sign_str)
            
        except Exception as e:
            raise RuntimeError(f"签名生成失败: {e}")

    def _api_url(self):
        return self.base_url + '/openapi/router'

    def _params(self, api_type, extra_params={}):
        params = {
            'type': api_type,
            'app_key': self.app_key,
            'access_token': self.access_token,
            'timestamp': round(time.time()),
            "data_type": "JSON",
        }
        if extra_params:
            # 过滤 None 值
            filtered_params = {k: v for k, v in extra_params.items() if v is not None}
            params.update(filtered_params)
        sign = self._get_sign(params)
        params['sign'] = sign
        return params

    def request(self, data: dict = None):
        api_type = data.pop('path')
        method = data.pop('method')
        data = self._params(api_type, data)
        if method.upper() == "GET":
            response = requests.get(url=self._api_url(), headers=self.headers, params=data)
        else:
            response = requests.post(url=self._api_url(), headers=self.headers, json=data)
        return response.json()


def test_fixed_base_client():
    """测试修复的 BaseClient"""
    print("🔍 测试修复的 BaseClient")
    print("=" * 60)
    
    # 创建修复的客户端
    client = FixedBaseClient(
        app_key="test_app_key",
        app_secret="test_app_secret",
        access_token="test_access_token",
        base_url="https://openapi-b-global.temu.com",
        debug=False
    )
    
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
    
    print("📋 测试参数:")
    print(json.dumps(test_params, indent=2, ensure_ascii=False))
    print()
    
    # 测试签名生成
    print("1️⃣ 测试签名生成")
    print("-" * 40)
    try:
        sign = client._get_sign(test_params)
        print(f"  ✅ 生成的签名: {sign}")
        
        # 显示签名字符串
        sorted_params = dict(sorted(test_params.items()))
        sign_str = client.app_secret
        for key, value in sorted_params.items():
            if value is not None and key != "sign":
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
                else:
                    value_str = str(value)
                sign_str += str(key) + value_str
        sign_str += client.app_secret
        
        print(f"  📊 签名字符串: {sign_str}")
        
    except Exception as e:
        print(f"  ❌ 签名生成失败: {e}")
    print()
    
    # 测试参数构建
    print("2️⃣ 测试参数构建")
    print("-" * 40)
    try:
        params = client._params("bg.local.goods.add", test_params)
        print(f"  ✅ 构建的参数包含签名: {'sign' in params}")
        print(f"  📊 签名值: {params.get('sign')}")
        
    except Exception as e:
        print(f"  ❌ 参数构建失败: {e}")
    print()
    
    print("3️⃣ 修复总结")
    print("-" * 40)
    print("🔧 主要修复:")
    print("  1. 添加了空值过滤: 跳过 None 值")
    print("  2. 改进了嵌套对象处理: 使用 JSON 序列化")
    print("  3. 移除了不必要的字符串替换")
    print("  4. 确保与 Java 代码逻辑一致")
    print()


if __name__ == "__main__":
    test_fixed_base_client()
