#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由映射工具类
根据API接口名称自动选择正确的网关路由
"""

import json
import os
from typing import Dict, Optional, Tuple
from pathlib import Path

class ApiRouteMapper:
    """API路由映射器"""
    
    def __init__(self, mapping_file_path: Optional[str] = None):
        """
        初始化API路由映射器
        
        Args:
            mapping_file_path: 映射文件路径，如果为None则使用默认路径
        """
        if mapping_file_path is None:
            # 使用默认路径
            current_dir = Path(__file__).parent.parent
            mapping_file_path = current_dir / "config" / "api_route_mapping.json"
        
        self.mapping_file_path = mapping_file_path
        self.mapping_data = self._load_mapping_data()
    
    def _load_mapping_data(self) -> Dict:
        """加载映射数据"""
        try:
            with open(self.mapping_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"API路由映射文件不存在: {self.mapping_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"API路由映射文件格式错误: {e}")
    
    def get_route_info(self, api_name: str) -> Tuple[str, str, str]:
        """
        根据API名称获取路由信息
        
        Args:
            api_name: API接口名称，如 'temu.goods.add' 或 'bg.goods.cats.get'
            
        Returns:
            Tuple[base_url, api_name, status]: 
                - base_url: 应该使用的网关地址
                - api_name: 实际应该使用的API名称（可能和输入不同）
                - status: API状态 ('migrated', 'legacy', 'unknown')
        """
        mapping = self.mapping_data["api_route_mapping"]
        base_urls = mapping["base_urls"]
        
        # 检查是否在已迁移的API列表中
        migrated_apis = mapping["migrated_apis"]["apis"]
        if api_name in migrated_apis:
            api_info = migrated_apis[api_name]
            return (
                base_urls[api_info["route"]],
                api_name,  # 使用新的API名称
                "migrated"
            )
        
        # 检查是否在旧API列表中（需要映射到新API）
        for new_api, api_info in migrated_apis.items():
            if api_info.get("old_api") == api_name:
                return (
                    base_urls[api_info["route"]],
                    new_api,  # 使用新的API名称
                    "migrated"
                )
        
        # 检查是否在遗留API列表中
        legacy_apis = mapping["legacy_apis"]["apis"]
        if api_name in legacy_apis:
            api_info = legacy_apis[api_name]
            return (
                base_urls[api_info["route"]],
                api_name,  # 使用原API名称
                "legacy"
            )
        
        # 未知API，默认使用旧网关
        return (
            base_urls["old_cn_gateway"],
            api_name,
            "unknown"
        )
    
    def get_base_url(self, api_name: str) -> str:
        """
        获取API应该使用的网关地址
        
        Args:
            api_name: API接口名称
            
        Returns:
            网关地址
        """
        base_url, _, _ = self.get_route_info(api_name)
        return base_url
    
    def get_actual_api_name(self, api_name: str) -> str:
        """
        获取实际应该使用的API名称
        
        Args:
            api_name: 输入的API接口名称
            
        Returns:
            实际应该使用的API名称
        """
        _, actual_api_name, _ = self.get_route_info(api_name)
        return actual_api_name
    
    def is_migrated_api(self, api_name: str) -> bool:
        """
        检查API是否已迁移到新网关
        
        Args:
            api_name: API接口名称
            
        Returns:
            是否已迁移
        """
        _, _, status = self.get_route_info(api_name)
        return status == "migrated"
    
    def get_migration_info(self, api_name: str) -> Optional[Dict]:
        """
        获取API迁移信息
        
        Args:
            api_name: API接口名称
            
        Returns:
            迁移信息字典，如果API未迁移则返回None
        """
        mapping = self.mapping_data["api_route_mapping"]
        migrated_apis = mapping["migrated_apis"]["apis"]
        
        # 直接查找
        if api_name in migrated_apis:
            return migrated_apis[api_name]
        
        # 通过旧API名称查找
        for new_api, api_info in migrated_apis.items():
            if api_info.get("old_api") == api_name:
                return api_info
        
        return None
    
    def list_migrated_apis(self) -> Dict[str, Dict]:
        """
        获取所有已迁移的API列表
        
        Returns:
            已迁移API的字典
        """
        return self.mapping_data["api_route_mapping"]["migrated_apis"]["apis"]
    
    def list_legacy_apis(self) -> Dict[str, Dict]:
        """
        获取所有遗留API列表
        
        Returns:
            遗留API的字典
        """
        return self.mapping_data["api_route_mapping"]["legacy_apis"]["apis"]
    
    def get_usage_notes(self) -> Dict:
        """
        获取使用说明
        
        Returns:
            使用说明字典
        """
        return self.mapping_data["api_route_mapping"]["usage_notes"]


# 全局实例
_route_mapper = None

def get_route_mapper() -> ApiRouteMapper:
    """获取全局路由映射器实例"""
    global _route_mapper
    if _route_mapper is None:
        _route_mapper = ApiRouteMapper()
    return _route_mapper


def get_api_route_info(api_name: str) -> Tuple[str, str, str]:
    """
    便捷函数：获取API路由信息
    
    Args:
        api_name: API接口名称
        
    Returns:
        Tuple[base_url, actual_api_name, status]
    """
    return get_route_mapper().get_route_info(api_name)


def get_api_base_url(api_name: str) -> str:
    """
    便捷函数：获取API网关地址
    
    Args:
        api_name: API接口名称
        
    Returns:
        网关地址
    """
    return get_route_mapper().get_base_url(api_name)


def get_actual_api_name(api_name: str) -> str:
    """
    便捷函数：获取实际API名称
    
    Args:
        api_name: API接口名称
        
    Returns:
        实际API名称
    """
    return get_route_mapper().get_actual_api_name(api_name)


if __name__ == "__main__":
    # 测试代码
    mapper = ApiRouteMapper()
    
    # 测试已迁移的API
    print("=== 已迁移API测试 ===")
    test_apis = [
        "temu.goods.add",
        "bg.goods.add",  # 旧API名称
        "bg.goods.image.upload",
        "bg.goods.image.upload.global"
    ]
    
    for api in test_apis:
        base_url, actual_api, status = mapper.get_route_info(api)
        print(f"{api} -> {actual_api} ({status}) -> {base_url}")
    
    print("\n=== 遗留API测试 ===")
    legacy_apis = [
        "bg.goods.cats.get",
        "bg.goods.attrs.get",
        "bg.mall.info.get"
    ]
    
    for api in legacy_apis:
        base_url, actual_api, status = mapper.get_route_info(api)
        print(f"{api} -> {actual_api} ({status}) -> {base_url}")
    
    print("\n=== 迁移信息 ===")
    migration_info = mapper.get_migration_info("bg.goods.add")
    if migration_info:
        print(f"bg.goods.add 迁移信息: {migration_info}")
    
    print("\n=== 使用说明 ===")
    notes = mapper.get_usage_notes()
    for key, value in notes.items():
        print(f"{key}: {value}")
