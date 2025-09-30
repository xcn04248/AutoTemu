#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze category attributes to understand specification limitations
"""

import json

def main():
    # Read the attrs_30476.json file
    with open('/Users/chunanxia/AutoTemu/real_test/attrs_30476.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = data['result']
    
    print("Category Attribute Analysis")
    print("=" * 50)
    print(f"inputMaxSpecNum: {result.get('inputMaxSpecNum')}")
    print(f"chooseAllQualifySpec: {result.get('chooseAllQualifySpec')}")
    print(f"singleSpecValueNum: {result.get('singleSpecValueNum')}")
    
    # Find size property (parentSpecId: 3001)
    properties = result['properties']
    size_property = None
    color_property = None
    
    for prop in properties:
        if prop.get('parentSpecId') == 3001 and prop.get('isSale'):
            size_property = prop
        elif prop.get('parentSpecId') == 1001 and prop.get('isSale'):
            color_property = prop
    
    if size_property:
        print("\nSize Property Details:")
        print(f"  Name: {size_property.get('name')}")
        print(f"  PID: {size_property.get('pid')}")
        print(f"  RefPID: {size_property.get('refPid')}")
        print(f"  Is Sale: {size_property.get('isSale')}")
        print(f"  Parent Spec ID: {size_property.get('parentSpecId')}")
        print(f"  Required: {size_property.get('required')}")
        
        # Check if there are any valid size values
        values = size_property.get('values', [])
        print(f"  Number of values: {len(values)}")
        
        # Look for values that might still be valid
        valid_values = []
        deleted_values = []
        for value in values:
            val = value.get('value', '')
            spec_id = value.get('specId')
            # We'll assume any value with a specId might be valid
            if spec_id:
                valid_values.append(value)
            else:
                deleted_values.append(value)
        
        print(f"  Valid values (with specId): {len(valid_values)}")
        print(f"  Deleted values (no specId): {len(deleted_values)}")
        
        # Show first few valid values
        print("\nFirst 10 valid size values:")
        for i, value in enumerate(valid_values[:10]):
            print(f"  {i+1}. Spec ID: {value.get('specId')}, Value: {value.get('value')}, VID: {value.get('vid')}")
    
    if color_property:
        print("\nColor Property Details:")
        print(f"  Name: {color_property.get('name')}")
        print(f"  PID: {color_property.get('pid')}")
        print(f"  RefPID: {color_property.get('refPid')}")
        print(f"  Is Sale: {color_property.get('isSale')}")
        print(f"  Parent Spec ID: {color_property.get('parentSpecId')}")
        print(f"  Required: {color_property.get('required')}")
        
        values = color_property.get('values', [])
        print(f"  Number of values: {len(values)}")

if __name__ == "__main__":
    main()