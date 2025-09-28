#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def deepest_leaf(goods: dict) -> int:
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

    leaf = deepest_leaf(goods)
    if not leaf:
        print("no leaf category")
        return 2

    cfg = get_config()
    legacy = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        cfg.bg_base_url or "https://openapi.kuajingmaihuo.com/openapi/router",
        debug=False,
    )

    # Resolve parent spec id for Size from legacy API
    parent_spec_id = 3001
    try:
        ps = legacy._make_request("bg.goods.parentspec.get", {"cat_id": leaf}, require_auth=True)
        for it in (ps.get("result") or {}).get("parentSpecList", []):
            # pick Size (refPid==65) if present; otherwise keep default
            if it.get("refPid") == 65 or it.get("name") in ("Size", "尺码"):
                parent_spec_id = it.get("parentSpecId") or parent_spec_id
                break
    except Exception:
        pass

    target_sizes = ["M", "L"]
    created: dict[str, int] = {}
    for size_name in target_sizes:
        try:
            # Try camelCase
            payloads = [
                {"catId": leaf, "parentSpecId": parent_spec_id, "childSpecName": size_name},
                # snake_case
                {"cat_id": leaf, "parent_spec_id": parent_spec_id, "child_spec_name": size_name},
                # alternate key
                {"catId": leaf, "parentSpecId": parent_spec_id, "specName": size_name},
            ]
            resp = None
            for pl in payloads:
                try:
                    resp = legacy._make_request("bg.goods.spec.create", pl, require_auth=True)
                    if resp.get("success"):
                        break
                except Exception as e2:
                    last_err = e2
                    continue
            if not resp or not resp.get("success"):
                raise last_err  # type: ignore[name-defined]
            spec_id = (resp.get("result") or {}).get("specId")
            if not spec_id:
                print("create spec missing specId for", size_name, resp)
                continue
            created[size_name] = spec_id
            print("created spec:", size_name, spec_id)
        except Exception as e:
            print("create spec error:", size_name, e)

    if not created:
        print("no spec created")
        return 3

    # Update goods.json: productSpecPropertyReqs and productSkuSpecReqs
    psp = goods.get("productSpecPropertyReqs") or []
    for item in psp:
        if not isinstance(item, dict):
            continue
        if item.get("parentSpecId") == parent_spec_id and item.get("specName") in created:
            item["specId"] = created[item["specName"]]

    # Update sku spec refs
    skcs = goods.get("productSkcReqs") or []
    for skc in skcs:
        for sku in skc.get("productSkuReqs") or []:
            for spec in sku.get("productSkuSpecReqs") or []:
                if spec.get("parentSpecId") == parent_spec_id and spec.get("specName") in created:
                    spec["specId"] = created[spec["specName"]]

    with open(goods_path, "w", encoding="utf-8") as f:
        json.dump(goods, f, ensure_ascii=False, indent=2)
    print("Updated:", goods_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


