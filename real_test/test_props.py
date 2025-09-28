#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch latest add-property template for current leaf category via partner API
and save raw response for inspection.

Usage:
  python real_test/test_props.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def find_leaf_cat(goods: dict) -> int:
    # deepest non-zero catNId
    for level in range(10, 0, -1):
        val = goods.get(f"cat{level}Id")
        if isinstance(val, int) and val > 0:
            return val
    return int(goods.get("cat4Id") or 0)


def main() -> int:
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "goods.json")
    if not os.path.exists(goods_path):
        print("goods.json not found:", goods_path)
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        goods = json.load(f)

    leaf = find_leaf_cat(goods)
    if not leaf:
        print("No leaf category in goods.json")
        return 2

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    req = {"leafCatId": leaf}
    try:
        # Partner:新增货品属性
        resp = client._make_request("temu.goods.add.property", req, require_auth=True)
    except Exception as e:
        print("add.property error:", e)
        return 3

    out_raw = os.path.join(workspace, "real_test", f"template_partner_props_{leaf}.json")
    with open(out_raw, "w", encoding="utf-8") as f:
        json.dump(resp, f, ensure_ascii=False, indent=2)
    print("Saved:", out_raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


