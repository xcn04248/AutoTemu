#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch latest category template for the current goods leaf cate and diff with goods.json properties.
Saves full template to real_test/template_<leaf>.json and a brief diff to real_test/template_diff.json.
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

    cfg = get_config()
    partner_base = "https://openapi-b-partner.temu.com/openapi/router"
    partner_client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        partner_base,
        debug=False,
    )

    # Prefer partner: temu.goods.catsmandatory.get
    resp_partner = None
    try:
        req_partner = {
            "leafCatId": leaf,
            # Per doc: pass current productPropertyReqs (even if partial)
            "productPropertyReqs": goods.get("productPropertyReqs") or [],
            # Bind to CN siteId=300 if applicable
            "bindSiteIds": [300],
            # configItems: pass ONLY the leaf category id to avoid cross-category query
            "configItems": [leaf],
        }
        print("temu.goods.catsmandatory.get payload:\n" + json.dumps(req_partner, ensure_ascii=False, indent=2))
        resp_partner = partner_client._make_request(
            "temu.goods.catsmandatory.get", req_partner, require_auth=True
        )
        out_partner = os.path.join(workspace, "real_test", f"template_partner_{leaf}.json")
        with open(out_partner, "w", encoding="utf-8") as f:
            json.dump(resp_partner, f, ensure_ascii=False, indent=2)
        print("Saved:", out_partner)
    except Exception as e:
        print("partner catsmandatory error:", e)

    # Only use partner response
    resp = resp_partner or {}

    # Build a brief diff against goods.json productPropertyReqs
    template = resp.get("result") if isinstance(resp, dict) else None
    prop_list = []
    if isinstance(template, dict):
        # partner may use propertyList; fallback to list
        prop_list = template.get("propertyList") or template.get("list") or []
    required = [p for p in prop_list if isinstance(p, dict) and p.get("required")]
    # pid field may be pid or templatePid
    required_pids = set()
    for p in required:
        pid = p.get("pid")
        if pid is None:
            pid = p.get("templatePid")
        if pid is not None:
            required_pids.add(pid)

    current = goods.get("productPropertyReqs") or []
    current_pids = {p.get("pid") for p in current if isinstance(p, dict)}

    missing = sorted(list(required_pids - current_pids))
    all_pids = set()
    for p in prop_list:
        pid = p.get("pid") if isinstance(p, dict) else None
        if pid is None and isinstance(p, dict):
            pid = p.get("templatePid")
        if pid is not None:
            all_pids.add(pid)
    extra = sorted(list(current_pids - all_pids))

    diff = {
        "leafCatId": leaf,
        "requiredCount": len(required_pids),
        "currentCount": len(current_pids),
        "missingRequiredPids": missing,
        "extraCurrentPids": extra,
    }
    out_diff = os.path.join(workspace, "real_test", "template_diff.json")
    with open(out_diff, "w", encoding="utf-8") as f:
        json.dump(diff, f, ensure_ascii=False, indent=2)
    print("Saved:", out_diff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


