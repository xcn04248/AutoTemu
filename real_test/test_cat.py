#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Determine category for current product and write results to real_test/test_cat.json.

Strategy:
- Load goods.json for productName
- Use old gateway match: bg.goods.category.match (legacy gateway only)
- Request params per doc: searchText, siteId(optional)
- Parse result.categoryPathDTOS into concise summary with full paths
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
    out_path = os.path.join(workspace, "real_test", "test_cat.json")

    if not os.path.exists(goods_path):
        print("goods.json not found:", goods_path)
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        goods = json.load(f)

    name = goods.get("productName")

    cfg = get_config()
    # Legacy client for bg.* endpoints (old gateway)
    legacy_base = cfg.bg_base_url or "https://openapi.kuajingmaihuo.com/openapi/router"
    legacy_client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        legacy_base,
        debug=False,
    )

    result = {"input": {"productName": name}}

    # Old gateway: bg category match
    try:
        # Per docs: searchText, siteId (optional). We'll pass siteId=300 by default.
        req = {"searchText": name or ""}
        req["siteId"] = 300
        resp_bg = legacy_client._make_request(
            "bg.goods.category.match",
            req,
            require_auth=True,
        )
        result["bg.goods.category.match"] = resp_bg
    except Exception as e:
        result["bg.goods.category.match.error"] = str(e)

    # Build a concise summary if possible
    # Parse categoryPathDTOS into paths summary
    summary = []
    resp = result.get("bg.goods.category.match")
    if isinstance(resp, dict):
        data = resp.get("result") or {}
        paths = data.get("categoryPathDTOS") or []
        for p in paths:
            # Collect path cat1..cat10 if present
            path_ids = []
            path_names = []
            leaf_id = None
            leaf_name = None
            leaf_level = None
            for level in range(1, 11):
                dto = p.get(f"cat{level}DTO")
                if isinstance(dto, dict) and dto.get("catId"):
                    path_ids.append(dto.get("catId"))
                    path_names.append(dto.get("catName"))
                    leaf_id = dto.get("catId")
                    leaf_name = dto.get("catName")
                    leaf_level = level
            if path_ids:
                summary.append({
                    "leafId": leaf_id,
                    "leafName": leaf_name,
                    "leafLevel": leaf_level,
                    "pathIds": path_ids,
                    "pathNames": path_names,
                })
    result["summary"] = summary

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Saved:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
