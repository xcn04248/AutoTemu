#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch product detail via partner API (temu.goods.detail.get) and save to JSON.

Usage:
  python real_test/test_get_goods_detail.py --product-id <ID>
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", required=True, help="Product ID to fetch")
    args = parser.parse_args()

    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_path = os.path.join(workspace, "real_test", f"goods_detail_{args.product_id}.json")

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    try:
        resp = client._make_request(
            "temu.goods.detail.get",
            {"productId": args.product_id, "version": "V1"},
            require_auth=True,
        )
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out_path)
        return 0
    except Exception as e:
        print("detail error:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


