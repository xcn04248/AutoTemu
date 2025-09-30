#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

def build_required_props():
    # Read the latest category attributes
    attrs_path = os.path.join(os.path.dirname(__file__), "latest_category_attributes_39022.json")
    with open(attrs_path, "r", encoding="utf-8") as f:
        attrs_data = json.load(f)
    
    # Read the existing goods data
    goods_path = os.path.join(os.path.dirname(__file__), "updated_goods_no_duplicates.json")
    with open(goods_path, "r", encoding="utf-8") as f:
        goods_data = json.load(f)
    
    # Get all required properties from the template
    required_props = []
    properties = attrs_data.get("result", {}).get("properties", [])
    
    for prop in properties:
        if prop.get("required", False):
            required_props.append({
                "templatePid": prop.get("templatePid"),
                "pid": prop.get("pid"),
                "refPid": prop.get("refPid"),
                "propName": prop.get("name"),
                "required": True
            })
    
    print("Required properties:")
    for prop in required_props:
        print(f"  {prop['propName']} (pid: {prop['pid']}, templatePid: {prop['templatePid']})")
    
    # Save the required properties for reference
    required_props_path = os.path.join(os.path.dirname(__file__), "required_props.json")
    with open(required_props_path, "w", encoding="utf-8") as f:
        json.dump(required_props, f, ensure_ascii=False, indent=2)
    print(f"Saved required properties to: {required_props_path}")
    
    # Now update the goods data with only required properties
    # First, remove all existing productPropertyReqs
    goods_data["productPropertyReqs"] = []
    
    # Add back only the required properties with appropriate values
    # For now, let's keep the same values as before but ensure all required properties are included
    # We'll use the values from the original goods data where available
    
    # Read the original goods data to get property values
    original_goods_path = os.path.join(os.path.dirname(__file__), "updated_goods_with_s_size_fixed2.json")
    with open(original_goods_path, "r", encoding="utf-8") as f:
        original_goods = json.load(f)
    
    # Create a mapping of propName to property value from original goods
    prop_value_map = {}
    for prop in original_goods.get("productPropertyReqs", []):
        prop_value_map[prop.get("propName")] = prop
    
    # Build new productPropertyReqs with only required properties
    new_property_reqs = []
    for req_prop in required_props:
        prop_name = req_prop["propName"]
        if prop_name in prop_value_map:
            # Use the value from original goods
            new_property_reqs.append(prop_value_map[prop_name])
        else:
            # Create a default value for required properties not in original
            print(f"Warning: Required property '{prop_name}' not found in original goods data")
            # Add a placeholder value (you may need to adjust this based on the property type)
            new_property_reqs.append({
                "templatePid": req_prop["templatePid"],
                "pid": req_prop["pid"],
                "refPid": req_prop["refPid"],
                "valueUnit": "",
                "propName": prop_name,
                "vid": 0,
                "propValue": ""
            })
    
    goods_data["productPropertyReqs"] = new_property_reqs
    
    # Save the updated goods data
    updated_path = os.path.join(os.path.dirname(__file__), "updated_goods_with_required_props.json")
    with open(updated_path, "w", encoding="utf-8") as f:
        json.dump(goods_data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated goods data saved to: {updated_path}")
    return updated_path

if __name__ == "__main__":
    build_required_props()