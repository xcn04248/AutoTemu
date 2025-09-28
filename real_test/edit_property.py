#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Edit existing SPU properties using partner API: temu.goods.edit.property
Reads goods_min.json -> maps to edit payload -> submits for SPU ID arg

Usage:
  python real_test/edit_property.py --product-id 3979420093
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def load_full_goods(workspace: str) -> dict:
    p = os.path.join(workspace, "real_test", "goods.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def map_to_edit_payload(src: dict) -> dict:
    data = {
        # properties
        "productPropertyReqs": src.get("productPropertyReqs", []),
        # spu spec properties
        "productSpecPropertyReqs": src.get("productSpecPropertyReqs", []),
    }
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", required=True)
    args = parser.parse_args()

    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_goods = load_full_goods(workspace)
    edit_body = map_to_edit_payload(full_goods)
    edit_body["productId"] = args.product_id

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
            "temu.goods.edit.property",
            edit_body,
            require_auth=True,
        )
        out = os.path.join(workspace, "real_test", f"edit_property_{args.product_id}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out)
        return 0
    except Exception as e:
        print("edit property error:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


