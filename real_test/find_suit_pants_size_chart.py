#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找名为"套装裤子"的尺码表模板
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def main() -> int:
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # 初始化客户端
    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi.kuajingmaihuo.com/openapi/router",
        debug=False,
    )
    
    try:
        # 使用bg.goods.sizecharts.meta.get接口获取所有尺码表模板
        print("正在查找名为'套装裤子'的尺码表模板...")
        
        # 尝试获取尺码表设置信息
        settings_params = {
            "catId": 39022  # 女式牛仔长裤类目ID
        }
        settings_result = client._make_request("bg.goods.sizecharts.settings.get", settings_params, require_auth=True)
        
        # 保存结果
        settings_result_path = os.path.join(workspace, "real_test", "size_chart_settings.json")
        with open(settings_result_path, "w", encoding="utf-8") as f:
            json.dump(settings_result, f, ensure_ascii=False, indent=2)
        print("尺码表设置信息已保存到:", settings_result_path)
        
        # 查找名为"套装裤子"的尺码表
        if settings_result.get("success") and settings_result.get("result"):
            result_data = settings_result["result"]
            
            # 检查是否有sizecharts字段
            if "sizecharts" in result_data:
                size_charts = result_data["sizecharts"]
                suit_pants_charts = []
                
                for chart in size_charts:
                    chart_name = chart.get("name", "")
                    if "套装裤子" in chart_name:
                        suit_pants_charts.append(chart)
                        print(f"找到尺码表: ID={chart.get('businessId')}, 名称={chart_name}")
                
                if suit_pants_charts:
                    print(f"\n共找到 {len(suit_pants_charts)} 个包含'套装裤子'的尺码表:")
                    for chart in suit_pants_charts:
                        print(json.dumps(chart, ensure_ascii=False, indent=2))
                    
                    # 保存找到的尺码表
                    suit_charts_path = os.path.join(workspace, "real_test", "suit_pants_size_charts.json")
                    with open(suit_charts_path, "w", encoding="utf-8") as f:
                        json.dump(suit_pants_charts, f, ensure_ascii=False, indent=2)
                    print("套装裤子尺码表已保存到:", suit_charts_path)
                else:
                    print("未找到名为'套装裤子'的尺码表模板")
                    
                    # 显示所有可用的尺码表名称
                    print("\n所有可用的尺码表名称:")
                    if isinstance(size_charts, list):
                        for chart in size_charts:
                            print(f"- {chart.get('name')}")
                    else:
                        print("尺码表数据格式异常")
            else:
                print("API响应中没有找到sizecharts字段")
                print("完整的响应数据:")
                print(json.dumps(settings_result, ensure_ascii=False, indent=2))
        else:
            print("获取尺码表设置信息失败:")
            print(json.dumps(settings_result, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print("查找尺码表模板时出错:", e)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())