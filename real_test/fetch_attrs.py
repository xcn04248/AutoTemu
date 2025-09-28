#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def get_leaf_cat(goods: dict) -> int:
    for level in range(10, 0, -1):
        v = goods.get(f"cat{level}Id")
        if isinstance(v, int) and v > 0:
            return v
    return 0


def main() -> int:
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "goods.json")
    if not os.path.exists(goods_path):
        print("goods.json not found")
        return 1

    with open(goods_path, "r", encoding="utf-8") as f:
        goods = json.load(f)

    leaf = get_leaf_cat(goods)
    if not leaf:
        print("no leaf cat")
        return 2

    cfg = get_config()
    legacy = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        cfg.bg_base_url or "https://openapi.kuajingmaihuo.com/openapi/router",
        debug=False,
    )

    # legacy attrs template per doc: catId
    payload = {"catId": leaf}
    print("bg.goods.attrs.get payload:", payload)
    resp = legacy._make_request("bg.goods.attrs.get", payload, require_auth=True)
    out_raw = os.path.join(workspace, "real_test", f"attrs_{leaf}.json")
    with open(out_raw, "w", encoding="utf-8") as f:
        json.dump(resp, f, ensure_ascii=False, indent=2)
    print("Saved:", out_raw)

    # compute missing required pids
    tpl = resp.get("result") if isinstance(resp, dict) else {}
    props = tpl.get("properties") or tpl.get("propertyList") or []
    required_pids = set()
    for p in props:
        if isinstance(p, dict) and p.get("required"):
            pid = p.get("pid") or p.get("templatePid")
            if pid is not None:
                required_pids.add(pid)
    current = goods.get("productPropertyReqs") or []
    current_pids = {p.get("pid") for p in current if isinstance(p, dict) and p.get("pid") is not None}
    missing = sorted(list(required_pids - current_pids))
    diff = {"leaf": leaf, "requiredCount": len(required_pids), "currentCount": len(current_pids), "missingPids": missing}
    out_diff = os.path.join(workspace, "real_test", "attrs_diff.json")
    with open(out_diff, "w", encoding="utf-8") as f:
        json.dump(diff, f, ensure_ascii=False, indent=2)
    print("Saved:", out_diff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


