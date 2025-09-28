#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
End-to-end edit task flow for an existing SPU:
1) apply to create/fetch task (temu.goods.edit.task.apply)
2) if needed, get detail (temu.goods.edit.task.detail.get)
3) submit edit (temu.goods.edit.task.submit) with properties/specs

Usage:
  python real_test/edit_task_flow.py --product-id 3979420093
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", required=True)
    args = parser.parse_args()

    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    req_props = load_json(os.path.join(workspace, "real_test", "required_props.json"))
    goods_min = load_json(os.path.join(workspace, "real_test", "goods_min.json"))

    body_submit = {
        "productId": args.product_id,
        "productPropertyReqs": req_props.get("productPropertyReqs", []),
        "productSpecPropertyReqs": goods_min.get("productSpecPropertyReqs", []),
    }

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    # Step 1: apply
    task_uid = None
    version = None
    try:
        resp = client._make_request(
            "temu.goods.edit.task.apply",
            {"productId": args.product_id},
            require_auth=True,
        )
        res = resp.get("result") or {}
        task_uid = res.get("taskUid") or res.get("taskId")
        version = res.get("version") or res.get("taskVersion")
        out = os.path.join(workspace, "real_test", f"edit_task_apply_{args.product_id}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out)
    except Exception as e:
        print("apply error:", e)

    # Step 2: detail if missing
    if not task_uid or not version:
        try:
            resp = client._make_request(
                "temu.goods.edit.task.detail.get",
                {"productId": args.product_id},
                require_auth=True,
            )
            res = resp.get("result") or {}
            task_uid = task_uid or res.get("taskUid") or res.get("taskId")
            version = version or res.get("version") or res.get("taskVersion")
            out = os.path.join(workspace, "real_test", f"edit_task_detail_{args.product_id}.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(resp, f, ensure_ascii=False, indent=2)
            print("Saved:", out)
        except Exception as e:
            print("detail error:", e)

    if task_uid:
        body_submit["taskUid"] = task_uid
    if version:
        body_submit["version"] = version

    # Step 3: submit
    try:
        resp = client._make_request(
            "temu.goods.edit.task.submit",
            body_submit,
            require_auth=True,
        )
        out = os.path.join(workspace, "real_test", f"edit_task_submit_{args.product_id}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print("Saved:", out)
        return 0
    except Exception as e:
        print("submit error:", e)
        print("payload preview:\n", json.dumps(body_submit, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


