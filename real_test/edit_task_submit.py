#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Submit an edit task for an existing SPU using temu.goods.edit.task.submit
Uses required_props.json for productPropertyReqs and goods_min.json for specs if present.
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", required=True)
    args = parser.parse_args()

    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    req_props_path = os.path.join(workspace, "real_test", "required_props.json")
    goods_min_path = os.path.join(workspace, "real_test", "goods_min.json")

    props = []
    if os.path.exists(req_props_path):
        props = load_json(req_props_path).get("productPropertyReqs", [])
    specs = []
    if os.path.exists(goods_min_path):
        specs = load_json(goods_min_path).get("productSpecPropertyReqs", [])

    body = {
        "productId": args.product_id,
        "productPropertyReqs": props,
        "productSpecPropertyReqs": specs,
    }

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    try:
        resp = client._make_request("temu.goods.edit.task.submit", body, require_auth=True)
        out = os.path.join(workspace, "real_test", f"edit_task_submit_{args.product_id}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out)
        return 0
    except Exception as e:
        print("edit task submit error:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


