#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def load_template(template_path: str) -> dict:
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)
    return tpl.get("result") or tpl


def build_pid_map(tpl_result: dict) -> dict[int, dict]:
    props = tpl_result.get("properties") or []
    pid_map: dict[int, dict] = {}
    for p in props:
        if not isinstance(p, dict):
            continue
        pid = p.get("pid")
        if pid is None:
            continue
        pid_map[int(pid)] = p
    return pid_map


def find_vid_by_value(prop: dict, value: str):
    for v in prop.get("values") or []:
        if isinstance(v, dict) and v.get("value") == value:
            return v.get("vid"), v.get("specId")
    return None, None


def normalize_goods(goods_path: str, tpl_path: str) -> int:
    with open(goods_path, "r", encoding="utf-8") as f:
        goods = json.load(f)

    tpl = load_template(tpl_path)
    pid_map = build_pid_map(tpl)

    # Normalize productPropertyReqs
    changed = 0
    new_props = []
    for item in goods.get("productPropertyReqs") or []:
        if not isinstance(item, dict):
            continue
        pid = item.get("pid")
        if not isinstance(pid, int):
            continue
        t = pid_map.get(pid)
        if not t:
            # drop properties not in template of this category
            changed += 1
            continue
        # update templatePid/refPid/propName
        target_template_pid = t.get("templatePid")
        target_ref_pid = t.get("refPid")
        target_name = t.get("name")
        if item.get("templatePid") != target_template_pid:
            item["templatePid"] = target_template_pid
            changed += 1
        if target_ref_pid is not None and item.get("refPid") != target_ref_pid:
            item["refPid"] = target_ref_pid
            changed += 1
        if target_name and item.get("propName") != target_name:
            item["propName"] = target_name
            changed += 1
        # ensure vid/propValue pair valid if present
        if "vid" in item or "propValue" in item:
            vid, spec_id = find_vid_by_value(t, item.get("propValue"))
            if vid is not None:
                if item.get("vid") != vid:
                    item["vid"] = vid
                    changed += 1
            # else keep numberInputValue or free-text
        new_props.append(item)
    goods["productPropertyReqs"] = new_props

    # Normalize productSpecPropertyReqs (isSale true)
    for s in goods.get("productSpecPropertyReqs") or []:
        if not isinstance(s, dict):
            continue
        pid = s.get("pid")
        if not isinstance(pid, int):
            continue
        t = pid_map.get(pid)
        if not t:
            continue
        if s.get("templatePid") != t.get("templatePid"):
            s["templatePid"] = t.get("templatePid")
            changed += 1
        # refresh vid/specId by value
        vid, spec_id = find_vid_by_value(t, s.get("propValue"))
        if vid is not None and s.get("vid") != vid:
            s["vid"] = vid
            changed += 1
        if spec_id is not None and s.get("specId") != spec_id:
            s["specId"] = spec_id
            changed += 1

    # Also update each SKU's productSkuSpecReqs
    for skc in goods.get("productSkcReqs") or []:
        for sku in skc.get("productSkuReqs") or []:
            for spec in sku.get("productSkuSpecReqs") or []:
                pid = None
                # infer pid by matching parentSpecId to known refs
                if spec.get("parentSpecId") == 3001:
                    pid = 14
                elif spec.get("parentSpecId") == 1001:
                    pid = 13
                if pid is None:
                    continue
                t = pid_map.get(pid)
                if not t:
                    continue
                vid, spec_id = find_vid_by_value(t, spec.get("specName"))
                if spec_id is not None and spec.get("specId") != spec_id:
                    spec["specId"] = spec_id
                    changed += 1

    if changed:
        with open(goods_path, "w", encoding="utf-8") as f:
            json.dump(goods, f, ensure_ascii=False, indent=2)
    print("Normalized changes:", changed)
    return 0


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "goods.json")
    # Pick latest attrs_<leaf>.json by reading goods.json
    goods_path = os.path.join(workspace, "real_test", "goods.json")
    with open(goods_path, "r", encoding="utf-8") as f:
        g = json.load(f)
    leaf = 0
    for level in range(10, 0, -1):
        v = g.get(f"cat{level}Id")
        if isinstance(v, int) and v > 0:
            leaf = v
            break
    tpl_path = os.path.join(workspace, "real_test", f"attrs_{leaf}.json")
    return normalize_goods(goods_path, tpl_path)


if __name__ == "__main__":
    raise SystemExit(main())


