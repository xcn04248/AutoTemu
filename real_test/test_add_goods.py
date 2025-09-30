#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主商品发布测试脚本
"""

import os
import sys
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config
from src.api.bg_client import BgGoodsClient, BgApiException


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "complete_goods_fixed.json")
    out_path = os.path.join(workspace, "real_test", "publish_result.json")

    if not os.path.exists(goods_path):
        print("商品数据文件不存在:", goods_path)
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    cfg = get_config()
    # 使用统一的API端点
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        cfg.bg_base_url,
        debug=False,
    )

    final_request_path = os.path.join(workspace, "real_test", "final_request.json")
    with open(final_request_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("--- 请求数据 ---")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("----------------")

    try:
        resp = client._make_request("temu.goods.add", payload, require_auth=True)
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        
        print("发布结果:")
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        
        code = resp.get("code") if isinstance(resp, dict) else None
        msg = resp.get("msg") if isinstance(resp, dict) else None
        sub_msg = resp.get("sub_msg") if isinstance(resp, dict) else None
        print("code:", code, "msg:", msg or sub_msg)
        return 0
        
    except BgApiException as e:
        err_out = os.path.join(workspace, "real_test", "publish_error.json")
        info = {
            "error": str(e),
            "errorCode": getattr(e, "error_code", None),
            "response": getattr(e, "response", None),
            "trace": traceback.format_exc(),
        }
        with open(err_out, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print("API错误:", str(e))
        return 2
        
    except Exception as e:
        print("未知错误:")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())