#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Submit goods.json to partner gateway via temu.goods.add (V1).

Usage:
  python real_test/test_add_goods.py
"""

import os
import sys
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient, BgApiException  # noqa: E402


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Prefer minimized payload if exists
    goods_min = os.path.join(workspace, "real_test", "goods_min.json")
    goods_path = goods_min if os.path.exists(goods_min) else os.path.join(workspace, "real_test", "goods.json")
    out_path = os.path.join(workspace, "real_test", "publish_result_partner_goods.json")

    if not os.path.exists(goods_path):
        print("goods.json not found:", goods_path)
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Ensure required partner flags
    payload = dict(payload)
    payload["version"] = "V1"

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    try:
        resp = client._make_request("temu.goods.add", payload, require_auth=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out_path)
        # Print full response for debugging
        try:
            print("Full response:\n" + json.dumps(resp, ensure_ascii=False, indent=2))
        except Exception:
            print("Full response (raw):", resp)
        # Print concise summary
        code = resp.get("code") if isinstance(resp, dict) else None
        msg = resp.get("msg") if isinstance(resp, dict) else None
        sub_msg = resp.get("sub_msg") if isinstance(resp, dict) else None
        print("code:", code, "msg:", msg or sub_msg)
        return 0
    except BgApiException as e:
        # Print full exception payload and stacktrace
        err_out = os.path.join(workspace, "real_test", "publish_result_partner_goods_error.json")
        info = {
            "error": str(e),
            "errorCode": getattr(e, "error_code", None),
            "response": getattr(e, "response", None),
            "trace": traceback.format_exc(),
        }
        with open(err_out, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print("Saved error:", err_out)
        print("Full exception JSON:\n" + json.dumps(info, ensure_ascii=False, indent=2))
        return 2
    except Exception as e:
        print("Unexpected error:")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
