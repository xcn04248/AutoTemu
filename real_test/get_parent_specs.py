#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取父规格列表
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.bg_client import create_bg_client
from src.utils.config import get_config

config = get_config()
client = create_bg_client()

parent_spec_data = {
    "catId": 39022
}

try:
    response = client._make_request("bg.goods.parentspec.get", parent_spec_data, require_auth=True)
    
    with open('real_test/parent_specs.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    
    print("父规格查询结果:")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
    if response.get('success'):
        parent_specs = response.get('result', {}).get('parentSpecDTOS', [])
        print(f"\n找到 {len(parent_specs)} 个父规格:")
        for spec in parent_specs:
            spec_id = spec.get('parentSpecId')
            spec_name = spec.get('parentSpecName')
            print(f"  - ID: {spec_id}, 名称: {spec_name}")
    else:
        print("查询父规格失败")
        
except Exception as e:
    print(f"查询父规格时出错: {e}")