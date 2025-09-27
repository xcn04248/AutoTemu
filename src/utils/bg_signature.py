"""
新API签名工具模块

实现bg.goods.add接口的签名算法
"""

import hashlib
import time
import json
from typing import Dict, Any, Union
from urllib.parse import quote


def md5_hex(s: str) -> str:
    """计算字符串的MD5哈希值"""
    # TEMU/BG网关要求签名为大写HEX
    return hashlib.md5(s.encode('utf-8')).hexdigest().upper()


def normalize_value(value: Any) -> str:
    """
    标准化参数值
    
    Args:
        value: 参数值
        
    Returns:
        标准化后的字符串
    """
    if value is None:
        return ""
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (dict, list)):
        # 使用紧凑JSON（无空格），不改变键顺序
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=False)
    else:
        return str(value)


def sign_request(params: Dict[str, Any], app_secret: str, debug: bool = False) -> str:
    """
    生成API请求签名
    
    根据文档描述的签名算法：
    1) 移除sign字段
    2) key按字典序排序
    3) 拼接为keyvalue串（值保持原样）
    4) 前后加密钥
    5) 取MD5/HEX
    
    Args:
        params: 请求参数字典
        app_secret: 应用密钥
        debug: 是否启用调试模式
        
    Returns:
        生成的签名字符串
    """
    if debug:
        print(f"[签名调试] 原始参数: {params}")
    
    # 1) 移除sign字段
    clean_params = {k: v for k, v in params.items() if k != 'sign'}
    
    if debug:
        print(f"[签名调试] 清理后参数: {clean_params}")
    
    # 2) key按字典序排序
    sorted_items = sorted(clean_params.items(), key=lambda x: x[0])
    
    if debug:
        print(f"[签名调试] 排序后参数: {sorted_items}")
    
    # 3) 拼接为keyvalue串（值保持原样）
    key_value_pairs = []
    for key, value in sorted_items:
        normalized_value = normalize_value(value)
        key_value_pairs.append(f"{key}{normalized_value}")
        
        if debug:
            print(f"[签名调试] {key} = {value} -> {normalized_value}")
    
    base_string = ''.join(key_value_pairs)
    
    if debug:
        print(f"[签名调试] 拼接字符串: {base_string}")
    
    # 4) 前后加密钥
    raw_string = f"{app_secret}{base_string}{app_secret}"
    
    if debug:
        print(f"[签名调试] 加密钥字符串: {raw_string}")
    
    # 5) 取MD5/HEX
    signature = md5_hex(raw_string)
    
    if debug:
        print(f"[签名调试] 最终签名: {signature}")
    
    return signature


def build_request_params(
    api_method: str,
    data: Dict[str, Any],
    app_key: str,
    access_token: str = None,
    timestamp: int = None
) -> Dict[str, Any]:
    """
    构建完整的请求参数
    
    Args:
        api_method: API方法名（如 bg.goods.add）
        data: 业务数据
        app_key: 应用key
        access_token: 访问令牌
        timestamp: 时间戳（可选，默认当前时间）
        
    Returns:
        完整的请求参数字典
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    # 构建基础参数
    params = {
        "type": api_method,
        "timestamp": timestamp,
        "app_key": app_key,
        "data_type": "JSON"
    }
    
    # 添加访问令牌（如果提供）
    if access_token:
        params["access_token"] = access_token
    
    # 添加业务数据
    params.update(data)
    
    return params


def sign_and_build_request(
    api_method: str,
    data: Dict[str, Any],
    app_key: str,
    app_secret: str,
    access_token: str = None,
    timestamp: int = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    构建并签名完整的请求
    
    Args:
        api_method: API方法名
        data: 业务数据
        app_key: 应用key
        app_secret: 应用密钥
        access_token: 访问令牌
        timestamp: 时间戳
        debug: 调试模式
        
    Returns:
        包含签名的完整请求参数
    """
    # 构建请求参数
    params = build_request_params(
        api_method=api_method,
        data=data,
        app_key=app_key,
        access_token=access_token,
        timestamp=timestamp
    )
    
    # 生成签名
    signature = sign_request(params, app_secret, debug=debug)
    
    # 添加签名
    params["sign"] = signature
    
    return params


def validate_signature(
    params: Dict[str, Any],
    app_secret: str,
    expected_signature: str = None
) -> bool:
    """
    验证签名是否正确
    
    Args:
        params: 请求参数
        app_secret: 应用密钥
        expected_signature: 期望的签名（如果不提供，从params中的sign字段获取）
        
    Returns:
        签名是否正确
    """
    if expected_signature is None:
        expected_signature = params.get("sign")
    
    if not expected_signature:
        return False
    
    # 重新计算签名
    calculated_signature = sign_request(params, app_secret)
    
    return calculated_signature == expected_signature


def get_current_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def format_timestamp(timestamp: int = None) -> str:
    """
    格式化时间戳为可读字符串
    
    Args:
        timestamp: 时间戳（可选，默认当前时间）
        
    Returns:
        格式化的时间字符串
    """
    if timestamp is None:
        timestamp = get_current_timestamp()
    
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class SignatureHelper:
    """签名助手类"""
    
    def __init__(self, app_key: str, app_secret: str, debug: bool = False):
        """
        初始化签名助手
        
        Args:
            app_key: 应用key
            app_secret: 应用密钥
            debug: 调试模式
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.debug = debug
    
    def sign_request(self, api_method: str, data: Dict[str, Any], 
                    access_token: str = None, timestamp: int = None) -> Dict[str, Any]:
        """
        签名请求
        
        Args:
            api_method: API方法名
            data: 业务数据
            access_token: 访问令牌
            timestamp: 时间戳
            
        Returns:
            包含签名的完整请求参数
        """
        return sign_and_build_request(
            api_method=api_method,
            data=data,
            app_key=self.app_key,
            app_secret=self.app_secret,
            access_token=access_token,
            timestamp=timestamp,
            debug=self.debug
        )
    
    def validate_signature(self, params: Dict[str, Any]) -> bool:
        """
        验证签名
        
        Args:
            params: 请求参数
            
        Returns:
            签名是否正确
        """
        return validate_signature(params, self.app_secret)
    
    def enable_debug(self):
        """启用调试模式"""
        self.debug = True
    
    def disable_debug(self):
        """禁用调试模式"""
        self.debug = False


# 便捷函数
def create_signature_helper(app_key: str, app_secret: str, debug: bool = False) -> SignatureHelper:
    """
    创建签名助手实例
    
    Args:
        app_key: 应用key
        app_secret: 应用密钥
        debug: 调试模式
        
    Returns:
        签名助手实例
    """
    return SignatureHelper(app_key, app_secret, debug)


# 测试用例
if __name__ == "__main__":
    # 测试签名功能
    test_params = {
        "type": "bg.goods.add",
        "timestamp": 1709015480,
        "app_key": "test_app_key",
        "data_type": "JSON",
        "access_token": "test_token",
        "productName": "Test Product",
        "price": 100
    }
    
    test_secret = "test_secret"
    
    print("测试签名功能:")
    signature = sign_request(test_params, test_secret, debug=True)
    print(f"生成的签名: {signature}")
    
    # 验证签名
    test_params["sign"] = signature
    is_valid = validate_signature(test_params, test_secret)
    print(f"签名验证结果: {is_valid}")
    
    # 测试签名助手
    print("\n测试签名助手:")
    helper = SignatureHelper("test_app_key", "test_secret", debug=True)
    signed_request = helper.sign_request(
        "bg.goods.add",
        {"productName": "Test Product", "price": 100},
        access_token="test_token"
    )
    print(f"签名助手生成的请求: {json.dumps(signed_request, indent=2, ensure_ascii=False)}")
