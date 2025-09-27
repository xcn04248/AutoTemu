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

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "goods.json")
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
        # Print concise summary
        code = resp.get("code") if isinstance(resp, dict) else None
        msg = resp.get("msg") if isinstance(resp, dict) else None
        sub_msg = resp.get("sub_msg") if isinstance(resp, dict) else None
        print("code:", code, "msg:", msg or sub_msg)
        return 0
    except Exception as e:
        print("partner publish error:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
