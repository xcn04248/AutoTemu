#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract size specifications from attrs_30476.json
"""

import json

def main():
    # Read the attrs_30476.json file
    with open('/Users/chunanxia/AutoTemu/real_test/attrs_30476.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find the size property (parentSpecId: 3001)
    properties = data['result']['properties']
    size_property = None
    for prop in properties:
        if prop.get('parentSpecId') == 3001:
            size_property = prop
            break
    
    if size_property is None:
        print("Size property not found")
        return
    
    print("Size property found:")
    print(f"  Name: {size_property.get('name')}")
    print(f"  PID: {size_property.get('pid')}")
    print(f"  RefPID: {size_property.get('refPid')}")
    print(f"  Is Sale: {size_property.get('isSale')}")
    print(f"  Parent Spec ID: {size_property.get('parentSpecId')}")
    
    # Look for standard size values
    values = size_property.get('values', [])
    print(f"\nNumber of values: {len(values)}")
    
    # Look for common size values
    size_values = []
    for value in values:
        val = value.get('value', '')
        if any(size in val.upper() for size in ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'ONE']):
            size_values.append(value)
    
    print(f"\nFound {len(size_values)} potential size values:")
    for value in size_values:
        print(f"  Spec ID: {value.get('specId')}, Value: {value.get('value')}, VID: {value.get('vid')}")

if __name__ == "__main__":
    main()