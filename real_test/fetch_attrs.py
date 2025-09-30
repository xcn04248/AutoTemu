#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch latest category attributes for the current goods leaf category.
Saves attributes to real_test/attrs_<leaf>.json.
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
    if not os.path.exists(goods_path):
        print("goods.json not found:", goods_path)
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        goods = json.load(f)

    # Prefer deepest non-zero cat id as leaf
    leaf = 0
    for level in range(10, 0, -1):
        val = goods.get(f"cat{level}Id")
        if isinstance(val, int) and val > 0:
            leaf = val
            break
    if not leaf:
        # fallback to cat4Id if set
        leaf = int(goods.get("cat4Id") or 0)
    if not leaf:
        print("No leaf category id found in goods.json")
        return 2

    print(f"Using leaf category ID: {leaf}")

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi.kuajingmaihuo.com/openapi/router",
        debug=False,
    )

    # Try different parameter names for fetching attributes
    try:
        print(f"Fetching attributes for category {leaf} with leafCatId")
        data = {"leafCatId": leaf}
        resp = client._make_request("bg.goods.attrs.get", data, require_auth=True)
        out_file = os.path.join(workspace, "real_test", f"attrs_{leaf}_camel.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out_file)
        return 0
    except Exception as e:
        print("Error with leafCatId:", e)
    
    try:
        print(f"Fetching attributes for category {leaf} with leaf_cat_id")
        data = {"leaf_cat_id": leaf}
        resp = client._make_request("bg.goods.attrs.get", data, require_auth=True)
        out_file = os.path.join(workspace, "real_test", f"attrs_{leaf}_snake.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out_file)
        return 0
    except Exception as e:
        print("Error with leaf_cat_id:", e)
    
    try:
        print(f"Fetching attributes for category {leaf} with cat_id")
        data = {"cat_id": leaf}
        resp = client._make_request("bg.goods.attrs.get", data, require_auth=True)
        out_file = os.path.join(workspace, "real_test", f"attrs_{leaf}_cat.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out_file)
        return 0
    except Exception as e:
        print("Error with cat_id:", e)
    
    return 3


if __name__ == "__main__":
    raise SystemExit(main())