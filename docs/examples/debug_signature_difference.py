#!/usr/bin/env python3
"""
调试签名差异

分析为什么其他 API 成功，但商品创建 API 失败
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_config
from temu_api import TemuClient
import json
import inspect


def debug_signature_difference():
    """调试签名差异"""
    print("🔍 调试签名差异")
    print("=" * 60)
    
    try:
        # 获取配置
        config = get_config()
        
        # 创建Temu客户端
        temu_client = TemuClient(
            app_key=config.temu_app_key,
            app_secret=config.temu_app_secret,
            access_token=config.temu_access_token,
            base_url=config.temu_base_url,
            debug=True  # 开启调试模式
        )
        
        print(f"📋 配置信息:")
        print(f"  - API端点: {config.temu_base_url}")
        print(f"  - App Key: {config.temu_app_key[:8]}...")
        print()
        
        # 1. 测试成功的 API - 分类获取
        print("1️⃣ 测试成功的 API - 分类获取")
        print("-" * 40)
        try:
            result = temu_client.product.cats_get(parent_cat_id=0)
            print(f"  ✅ 成功: {result.get('success')}")
            print(f"  📊 结果: 获取到 {len(result.get('result', {}).get('goodsCatsList', []))} 个分类")
        except Exception as e:
            print(f"  ❌ 失败: {e}")
        print()
        
        # 2. 测试失败的 API - 商品创建
        print("2️⃣ 测试失败的 API - 商品创建")
        print("-" * 40)
        try:
            result = temu_client.product.goods_add(
                goods_basic={
                    "goodsName": "测试商品",
                    "goodsDesc": "测试描述",
                    "catId": "30847"
                },
                goods_service_promise={},
                goods_property={},
                sku_list=[]
            )
            print(f"  ❌ 失败: {result.get('success')}")
            print(f"  📊 错误: {result.get('errorMsg')}")
            print(f"  📊 错误码: {result.get('errorCode')}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        print()
        
        # 3. 分析差异
        print("3️⃣ 分析差异")
        print("-" * 40)
        print("  成功 API 的特点:")
        print("  - 参数简单，主要是基本类型")
        print("  - 不需要复杂的嵌套结构")
        print("  - 参数数量少")
        print()
        print("  失败 API 的特点:")
        print("  - 参数复杂，包含嵌套字典和列表")
        print("  - 参数数量多")
        print("  - 可能包含特殊字符或格式")
        print()
        
        # 4. 检查 API 类型
        print("4️⃣ 检查 API 类型")
        print("-" * 40)
        try:
            # 检查分类获取 API 的类型
            cats_get_result = temu_client.product.cats_get(parent_cat_id=0)
            print(f"  📊 分类获取 API 类型: bg.local.goods.cats.get")
            print(f"  📊 成功: {cats_get_result.get('success')}")
            
            # 检查商品创建 API 的类型
            print(f"  📊 商品创建 API 类型: bg.local.goods.add")
            print(f"  📊 这是商品管理 API，可能需要特殊权限")
            print()
            
        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
        print()
        
        # 5. 检查权限
        print("5️⃣ 检查权限")
        print("-" * 40)
        try:
            result = temu_client.auth.get_access_token_info()
            if result.get("success"):
                api_scope_list = result.get("result", {}).get("apiScopeList", [])
                print(f"  📊 总权限数: {len(api_scope_list)}")
                
                # 检查商品相关权限
                goods_permissions = [perm for perm in api_scope_list if "goods" in perm]
                print(f"  📊 商品相关权限数: {len(goods_permissions)}")
                
                # 检查特定权限
                specific_permissions = [
                    "bg.local.goods.add",
                    "bg.local.goods.cats.get",
                    "bg.local.goods.category.recommend",
                    "bg.local.goods.size.element.get"
                ]
                
                for perm in specific_permissions:
                    has_perm = perm in api_scope_list
                    print(f"  📊 {perm}: {'✅' if has_perm else '❌'}")
                
            else:
                print("  ❌ 无法获取权限信息")
        except Exception as e:
            print(f"  ❌ 权限检查失败: {e}")
        print()
        
        # 6. 分析可能的原因
        print("6️⃣ 分析可能的原因")
        print("-" * 40)
        print("  可能的原因:")
        print("  1. 商品创建 API 需要特殊的权限验证")
        print("  2. 商品创建 API 的参数格式要求更严格")
        print("  3. 商品创建 API 需要额外的认证信息")
        print("  4. 商品创建 API 的签名算法可能不同")
        print("  5. 商品创建 API 需要特定的参数组合")
        print("  6. 商品创建 API 可能需要先上传图片")
        print("  7. 商品创建 API 可能需要先设置运费模板等")
        print()
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_signature_difference()
