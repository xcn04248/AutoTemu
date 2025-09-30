#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze category attributes in detail to find any clues about unchecking options
"""

import json

def main():
    # Read the attrs_30476.json file
    with open('/Users/chunanxia/AutoTemu/real_test/attrs_30476.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = data['result']
    
    print("Detailed Category Attribute Analysis")
    print("=" * 50)
    print(f"inputMaxSpecNum: {result.get('inputMaxSpecNum')}")
    print(f"chooseAllQualifySpec: {result.get('chooseAllQualifySpec')}")
    print(f"singleSpecValueNum: {result.get('singleSpecValueNum')}")
    
    # Find size property (parentSpecId: 3001)
    properties = result['properties']
    size_property = None
    
    for prop in properties:
        if prop.get('parentSpecId') == 3001 and prop.get('isSale'):
            size_property = prop
            break
    
    if size_property:
        print("\nSize Property Details:")
        print(f"  Name: {size_property.get('name')}")
        print(f"  PID: {size_property.get('pid')}")
        print(f"  RefPID: {size_property.get('refPid')}")
        print(f"  Is Sale: {size_property.get('isSale')}")
        print(f"  Parent Spec ID: {size_property.get('parentSpecId')}")
        print(f"  Required: {size_property.get('required')}")
        print(f"  Control Type: {size_property.get('controlType')}")
        print(f"  Show Type: {size_property.get('showType')}")
        print(f"  Feature: {size_property.get('feature')}")
        print(f"  Property Value Type: {size_property.get('propertyValueType')}")
        print(f"  Input Max Num: {size_property.get('inputMaxNum')}")
        print(f"  Choose Max Num: {size_property.get('chooseMaxNum')}")
        
        # Check if there are any show conditions
        show_conditions = size_property.get('showCondition')
        if show_conditions:
            print(f"  Show Conditions: {show_conditions}")
        else:
            print("  Show Conditions: None")
        
        # Check if there are any template property value parent lists
        template_parent_list = size_property.get('templatePropertyValueParentList')
        if template_parent_list:
            print(f"  Template Property Value Parent List: {template_parent_list}")
        else:
            print("  Template Property Value Parent List: None")

if __name__ == "__main__":
    main()