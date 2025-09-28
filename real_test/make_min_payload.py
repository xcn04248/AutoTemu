#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a minimized goods payload from current goods.json to try initial creation.
Saves to real_test/goods_min.json
"""

import os
import sys
import json


def pick_first(lst):
    if isinstance(lst, list) and lst:
        return lst[0]
    return None


def build_min_payload(full: dict) -> dict:
    keys_basic = [
        "productName",
        "materialImgUrl",
        "skuClassification",
        "pieceUnitCode",
    ]
    payload = {k: full.get(k) for k in keys_basic if k in full}

    # categories
    for i in range(1, 11):
        key = f"cat{i}Id"
        if key in full:
            payload[key] = full.get(key) or 0

    # semi-managed/site
    if full.get("productSemiManagedReq"):
        payload["productSemiManagedReq"] = {
            "bindSiteIds": list(full["productSemiManagedReq"].get("bindSiteIds", []))
        }

    # shipment
    if full.get("productShipmentReq"):
        ps = full["productShipmentReq"]
        payload["productShipmentReq"] = {
            "freightTemplateId": ps.get("freightTemplateId"),
            "shipmentLimitSecond": ps.get("shipmentLimitSecond", 172800),
        }

    # origin
    payload["productWhExtAttrReq"] = {
        "productOrigin": {"region1ShortName": "CN"},
        "outerGoodsUrl": "",
    }

    # size template ids if present
    if full.get("sizeTemplateIds"):
        payload["sizeTemplateIds"] = list(full.get("sizeTemplateIds", []))

    # specs at SPU level (keep color & size if present)
    keep_pids = {13, 14}
    if full.get("productSpecPropertyReqs"):
        filtered = []
        for it in full["productSpecPropertyReqs"]:
            if not isinstance(it, dict):
                continue
            if it.get("pid") in keep_pids:
                filtered.append({
                    "templatePid": it.get("templatePid"),
                    "pid": it.get("pid"),
                    "refPid": it.get("refPid"),
                    "valueUnit": it.get("valueUnit", ""),
                    "parentSpecId": it.get("parentSpecId"),
                    "parentSpecName": it.get("parentSpecName"),
                    "specId": it.get("specId"),
                    "specName": it.get("specName"),
                    "vid": it.get("vid"),
                    "propValue": it.get("propValue"),
                    "propName": it.get("propName"),
                    "valueGroupId": it.get("valueGroupId"),
                    "valueGroupName": it.get("valueGroupName"),
                })
        if filtered:
            payload["productSpecPropertyReqs"] = filtered

    # SKC/SKU: pick first SKC and first SKU only
    skc0 = pick_first(full.get("productSkcReqs") or [])
    if skc0:
        min_skc = {}
        min_skc["extCode"] = skc0.get("extCode") or "AUTO-1"
        if skc0.get("previewImgUrls"):
            min_skc["previewImgUrls"] = list(skc0.get("previewImgUrls")[:3])
        if skc0.get("mainProductSkuSpecReqs"):
            min_skc["mainProductSkuSpecReqs"] = list(skc0.get("mainProductSkuSpecReqs"))
        sku0 = None
        for s in skc0.get("productSkuReqs") or []:
            sku0 = s
            break
        if sku0:
            min_sku = {
                "extCode": sku0.get("extCode") or "AUTO-1-M",
                "thumbUrl": sku0.get("thumbUrl"),
                "currencyType": sku0.get("currencyType", "CNY"),
                "siteSupplierPrices": sku0.get("siteSupplierPrices", []),
                "productSkuSpecReqs": sku0.get("productSkuSpecReqs", []),
            }
            # Keep minimal wh ext attrs: volume & weight
            wh = sku0.get("productSkuWhExtAttrReq") or {}
            vol = wh.get("productSkuVolumeReq") or {}
            w = wh.get("productSkuWeightReq") or {}
            min_sku["productSkuWhExtAttrReq"] = {
                "productSkuVolumeReq": {
                    "len": vol.get("len", 300),
                    "width": vol.get("width", 250),
                    "height": vol.get("height", 20),
                },
                "productSkuWeightReq": {
                    "value": w.get("value", 300000)
                },
            }
            min_sku["productSkuThumbUrlI18nReqs"] = []
            min_skc["productSkuReqs"] = [min_sku]
        payload["productSkcReqs"] = [min_skc]

    # minimal productPropertyReqs: include first item from full if available
    if full.get("productPropertyReqs"):
        base = pick_first(full["productPropertyReqs"])
        if isinstance(base, dict):
            payload["productPropertyReqs"] = [{
                "templatePid": base.get("templatePid"),
                "pid": base.get("pid"),
                "refPid": base.get("refPid"),
                "valueUnit": base.get("valueUnit", ""),
                "vid": base.get("vid", 0),
                "propValue": base.get("propValue", ""),
                "propName": base.get("propName", ""),
                "numberInputValue": base.get("numberInputValue", ""),
            }]

    return payload


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    goods_path = os.path.join(workspace, "real_test", "goods.json")
    out_path = os.path.join(workspace, "real_test", "goods_min.json")
    with open(goods_path, "r", encoding="utf-8") as f:
        full = json.load(f)
    min_payload = build_min_payload(full)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(min_payload, f, ensure_ascii=False, indent=2)
    print("Saved:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


