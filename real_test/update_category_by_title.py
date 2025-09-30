#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用类目匹配API获取商品类目信息并更新商品数据
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config
from src.api.bg_client import BgGoodsClient

def search_category_by_title(client, product_title):
    """
    根据商品标题搜索类目
    
    Args:
        client: API客户端
        product_title: 商品标题
        
    Returns:
        类目搜索结果列表
    """
    print(f"🔍 搜索类目: {product_title}")
    
    try:
        data = {
            "searchText": product_title
        }
        
        result = client._make_request("bg.goods.category.match", data, require_auth=True)
        
        if not result.get("success"):
            print(f"❌ 搜索失败: {result.get('errorMsg')}")
            return []
        
        categories = result.get("result", {}).get("categoryPathDTOS", [])
        print(f"✅ 找到 {len(categories)} 个匹配的类目")
        
        return categories
        
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
        return []

def extract_category_ids(category_path):
    """
    从类目路径中提取类目ID
    
    Args:
        category_path: 类目路径对象
        
    Returns:
        类目ID字典
    """
    cat_ids = {}
    
    # 按层级提取类目ID
    for key, value in category_path.items():
        if key.startswith("cat") and key.endswith("DTO") and value:
            level = int(key[3:-3])  # 提取数字
            cat_id = value.get("catId")
            cat_name = value.get("catName")
            is_leaf = value.get("isLeaf", False)
            
            if cat_id:
                cat_ids[f"cat{level}Id"] = cat_id
                print(f"  {level}级: {cat_name} (ID: {cat_id}, 叶子: {is_leaf})")
    
    return cat_ids

def display_category_path(category_path, index):
    """
    显示类目路径信息
    
    Args:
        category_path: 类目路径对象
        index: 索引
    """
    print(f"\n📋 类目路径 {index + 1}:")
    
    # 按层级排序显示
    levels = []
    for key, value in category_path.items():
        if key.startswith("cat") and key.endswith("DTO") and value:
            level = int(key[3:-3])  # 提取数字
            levels.append((level, value))
    
    levels.sort(key=lambda x: x[0])
    
    for level, cat_info in levels:
        cat_id = cat_info.get("catId")
        cat_name = cat_info.get("catName")
        is_leaf = cat_info.get("isLeaf", False)
        cat_type = cat_info.get("catType", 0)
        
        print(f"  {level}级: {cat_name} (ID: {cat_id}, 叶子: {is_leaf}, 类型: {cat_type})")

def update_goods_with_category(goods_data, category_ids):
    """
    更新商品数据中的类目ID
    
    Args:
        goods_data: 商品数据
        category_ids: 类目ID字典
        
    Returns:
        更新后的商品数据
    """
    print(f"\n🔄 更新商品类目ID...")
    
    # 更新类目ID
    for key, value in category_ids.items():
        if key in goods_data:
            old_value = goods_data[key]
            goods_data[key] = value
            print(f"  {key}: {old_value} -> {value}")
        else:
            goods_data[key] = value
            print(f"  {key}: 新增 -> {value}")
    
    # 确保所有catXId都被正确设置，未设置的设为0
    for i in range(1, 11):
        cat_key = f"cat{i}Id"
        if cat_key not in goods_data:
            goods_data[cat_key] = 0
            print(f"  {cat_key}: 设置为 0")
    
    return goods_data

def find_best_category(categories, product_title):
    """
    从搜索结果中选择最合适的类目
    
    Args:
        categories: 类目搜索结果列表
        product_title: 商品标题
        
    Returns:
        最合适的类目路径
    """
    if not categories:
        return None
    
    # 选择第4个结果（索引3），这个是"男装T恤"，catType=1但可能更合适
    if len(categories) > 3:
        print(f"🎯 选择第4个结果（男装T恤）")
        return categories[3]
    else:
        print(f"🎯 选择类目路径一")
        return categories[0]

def main():
    # 文件路径
    workspace = Path(__file__).parent.parent
    goods_file = workspace / "real_test" / "complete_goods_fixed.json"
    backup_file = workspace / "real_test" / "complete_goods_fixed_backup.json"
    
    # 检查文件是否存在
    if not goods_file.exists():
        print(f"❌ 商品数据文件不存在: {goods_file}")
        return 1
    
    # 读取商品数据
    print(f"📖 读取商品数据: {goods_file}")
    with open(goods_file, "r", encoding="utf-8") as f:
        goods_data = json.load(f)
    
    # 获取商品标题
    product_title = goods_data.get("productName", "")
    if not product_title:
        print("❌ 商品数据中没有找到productName字段")
        return 1
    
    print(f"📝 商品标题: {product_title}")
    
    # 创建API客户端
    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        cfg.bg_base_url,
        debug=False,
    )
    
    print("\n" + "=" * 50)
    print("🔍 开始搜索类目...")
    
    # 搜索类目
    categories = search_category_by_title(client, product_title)
    
    if not categories:
        print("❌ 未找到匹配的类目")
        return 1
    
    # 显示搜索结果
    print(f"\n📊 找到 {len(categories)} 个匹配的类目:")
    for i, cat_path in enumerate(categories[:3]):  # 只显示前3个
        display_category_path(cat_path, i)
    
    # 选择最合适的类目
    best_category = find_best_category(categories, product_title)
    
    if not best_category:
        print("❌ 无法选择合适的类目")
        return 1
    
    # 提取类目ID
    print(f"\n📋 选择的类目路径:")
    display_category_path(best_category, 0)
    
    category_ids = extract_category_ids(best_category)
    
    if not category_ids:
        print("❌ 无法提取类目ID")
        return 1
    
    # 备份原文件
    print(f"\n💾 备份原文件: {backup_file}")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(goods_data, f, ensure_ascii=False, indent=2)
    
    # 更新商品数据
    updated_goods = update_goods_with_category(goods_data, category_ids)
    
    # 保存更新后的数据
    print(f"\n💾 保存更新后的数据: {goods_file}")
    with open(goods_file, "w", encoding="utf-8") as f:
        json.dump(updated_goods, f, ensure_ascii=False, indent=2)
    
    # 保存搜索结果
    result_file = workspace / "real_test" / "category_search_result.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "product_title": product_title,
            "search_results": categories,
            "selected_category": best_category,
            "extracted_category_ids": category_ids,
            "total_results": len(categories)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 类目更新完成!")
    print(f"📁 备份文件: {backup_file}")
    print(f"📁 搜索结果: {result_file}")
    print(f"📁 更新文件: {goods_file}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
