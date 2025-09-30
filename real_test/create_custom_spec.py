#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建自定义规格
"""

import json
import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.bg_client import create_bg_client
from src.utils.config import get_config

def generate_unique_name(prefix="CUSTOM_"):
    """生成独特的规格名称"""
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + random_suffix

config = get_config()
client = create_bg_client()

def create_custom_spec(parent_spec_id, parent_spec_name):
    """创建自定义规格"""
    unique_name = generate_unique_name(f"CUSTOM_{parent_spec_name}_")
    print(f"生成的独特{parent_spec_name}规格名称: {unique_name}")

    spec_data = {
        "catId": 39022,
        "parentSpecId": parent_spec_id,
        "specName": unique_name
    }

    response = client._make_request("bg.goods.spec.create", spec_data, require_auth=True)

    result_file = f'real_test/custom_{parent_spec_name.lower()}_spec.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)

    print(f"自定义{parent_spec_name}规格创建结果:")
    print(json.dumps(response, ensure_ascii=False, indent=2))

    if response.get('success'):
        spec_id = response['result']['specId']
        print(f"自定义{parent_spec_name}规格ID: {spec_id}")
        
        with open(f'real_test/custom_{parent_spec_name.lower()}_spec_id.txt', 'w', encoding='utf-8') as f:
            f.write(str(spec_id))
        with open(f'real_test/custom_{parent_spec_name.lower()}_spec_name.txt', 'w', encoding='utf-8') as f:
            f.write(unique_name)
        
        print(f"规格ID已保存到 real_test/custom_{parent_spec_name.lower()}_spec_id.txt")
        print(f"规格名称已保存到 real_test/custom_{parent_spec_name.lower()}_spec_name.txt")
        return spec_id, unique_name
    else:
        print(f"创建自定义{parent_spec_name}规格失败")
        return None, None

if __name__ == "__main__":
    # 创建自定义风格规格
    style_spec_id, style_spec_name = create_custom_spec(18012, "风格")
    
    # 创建自定义颜色规格
    color_spec_id, color_spec_name = create_custom_spec(1001, "颜色")