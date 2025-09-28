#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build minimal required property set from attrs_<leaf>.json and goods.json specs.
Output: real_test/required_props.json
"""

import os
import sys
import json


def load_goods(workspace: str) -> dict:
    p = os.path.join(workspace, "real_test", "goods.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def find_leaf(goods: dict) -> int:
    for level in range(10, 0, -1):
        v = goods.get(f"cat{level}Id")
        if isinstance(v, int) and v > 0:
            return v
    return 0


def load_attrs(workspace: str, leaf: int) -> dict:
    p = os.path.join(workspace, "real_test", f"attrs_{leaf}.json")
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d.get("result") or d


def choose_first_value(prop: dict):
    values = prop.get("values") or []
    for v in values:
        if not isinstance(v, dict):
            continue
        vid = v.get("vid")
        pv = v.get("value")
        if vid is not None and pv is not None:
            return vid, pv
    return None, None


def build_required_props(tpl: dict) -> list:
    result = []
    for p in tpl.get("properties", []):
        if not isinstance(p, dict):
            continue
        if not p.get("required"):
            continue
        item = {
            "templatePid": p.get("templatePid"),
            "pid": p.get("pid"),
            "refPid": p.get("refPid"),
            "valueUnit": (p.get("valueUnit") or [""])[0] if isinstance(p.get("valueUnit"), list) else "",
            "propName": p.get("name", ""),
        }
        control = p.get("controlType")
        # choose类型
        if control in (1, 3, 9, 16):
            vid, val = choose_first_value(p)
            if vid is not None:
                item["vid"] = vid
            if val is not None:
                item["propValue"] = val
            if control == 16 and p.get("valueRule") == 1:
                # sum to 100 rule; ensure numberInputValue set
                item["numberInputValue"] = "100"
        elif control in (0, 11, 12, 13, 14):
            # input type - put a safe minimal number/text
            item["numberInputValue"] = item.get("numberInputValue", "1")
            item.setdefault("propValue", "")
            item.setdefault("vid", 0)
        else:
            # fallback choose first if exists
            vid, val = choose_first_value(p)
            if vid is not None:
                item["vid"] = vid
            if val is not None:
                item["propValue"] = val
        result.append(item)
    return result


def main() -> int:
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods = load_goods(workspace)
    leaf = find_leaf(goods)
    tpl = load_attrs(workspace, leaf)
    props = build_required_props(tpl)
    out_path = os.path.join(workspace, "real_test", "required_props.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"productPropertyReqs": props}, f, ensure_ascii=False, indent=2)
    print("Saved:", out_path, "count:", len(props))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


