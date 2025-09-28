#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple image uploader for partner gateway.

Features:
- Reads images from real_test/images_filtered or real_test/images
- Uploads via temu.goods.image.upload.global (V1)
- Fallback: bg.goods.image.upload.global (V1)
- Saves each raw JSON response to real_test/upload_results/*.json
- Prints a compact summary including returned URLs/domains

Usage:
  python real_test/test_upload.py [--limit 8] [--size-mode {0,1,2}]
"""

import os
import sys
import json
import glob
import base64
import argparse
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import get_config  # noqa: E402
from src.api.bg_client import BgGoodsClient  # noqa: E402


def iter_images(base_dir: str):
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        for p in glob.glob(os.path.join(base_dir, ext)):
            yield p


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path


def save_json(obj, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def upload_one(client: BgGoodsClient, image_path: str, options: dict | None = None):
    with open(image_path, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")

    # Primary: temu.goods.image.upload.global (V1)
    try:
        payload = {"image": b64, "version": "V1"}
        if options:
            payload["options"] = options
        resp = client._make_request(
            "temu.goods.image.upload.global",
            payload,
            require_auth=True,
        )
        return resp, "temu.goods.image.upload.global"
    except Exception:
        pass

    # Fallback: bg.goods.image.upload.global (V1)
    try:
        payload = {"image": b64, "version": "V1"}
        if options:
            payload["options"] = options
        resp = client._make_request(
            "bg.goods.image.upload.global",
            payload,
            require_auth=True,
        )
        return resp, "bg.goods.image.upload.global"
    except Exception:
        pass

    # If both above fail, raise for caller to handle
    raise RuntimeError("All upload API attempts failed: temu.goods.image.upload.global and bg.goods.image.upload.global")


def extract_url(resp: dict):
    if not isinstance(resp, dict):
        return None
    res = resp.get("result") or {}
    for key in ("url", "imageUrl"):
        val = res.get(key)
        if isinstance(val, str) and val.startswith(("http://", "https://")):
            return val
    urls = res.get("urls")
    if isinstance(urls, list) and urls and isinstance(urls[0], str):
        return urls[0]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--size-mode", type=int, choices=(0, 1, 2), default=2, help="0=orig, 1=1:1 (800x800), 2=3:4 (1350x1800)")
    args = parser.parse_args()

    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    base1 = os.path.join(workspace, "real_test", "images_filtered")
    base2 = os.path.join(workspace, "real_test", "images")

    img_dir = base1 if os.path.isdir(base1) else base2
    files = list(iter_images(img_dir))[: args.limit]
    if not files:
        print("No images found in:", img_dir)
        return 1

    out_dir = ensure_dir(os.path.join(workspace, "real_test", "upload_results"))

    cfg = get_config()
    client = BgGoodsClient(
        cfg.bg_app_key,
        cfg.bg_app_secret,
        cfg.bg_access_token,
        "https://openapi-b-partner.temu.com/openapi/router",
        debug=False,
    )

    # Build upload options per 图片处理 API组文档
    # Prefer 3:4 portrait cropping to satisfy apparel carousel requirement (>=1340x1785)
    def load_leaf_cate_id():
        try:
            test_cat_path = os.path.join(workspace, "real_test", "test_cat.json")
            with open(test_cat_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            summary = data.get("summary") or []
            if summary and isinstance(summary[0], dict):
                return summary[0].get("leafId")
        except Exception:
            return None
        return None

    cate_id = load_leaf_cate_id()
    options = {
        "boost": True,
        "doIntelligenceCrop": True,
        "sizeMode": args.size_mode,
    }
    if isinstance(cate_id, int):
        options["cateId"] = cate_id

    rows = []
    for idx, fp in enumerate(files, 1):
        try:
            resp, used_api = upload_one(client, fp, options)
            url = extract_url(resp)
            host = urlparse(url).hostname if isinstance(url, str) else None
            save_json(resp, os.path.join(out_dir, f"upload_{idx:02d}.json"))
            rows.append({
                "file": os.path.basename(fp),
                "api": used_api,
                "url": url,
                "host": host,
            })
            print(f"[{idx}/{len(files)}] {os.path.basename(fp)} -> {used_api} -> {url}")
        except Exception as e:
            rows.append({"file": os.path.basename(fp), "api": None, "error": str(e)})
            print(f"[{idx}/{len(files)}] {os.path.basename(fp)} -> ERROR: {e}")

    # summary
    summary_path = os.path.join(out_dir, "summary.json")
    save_json({"items": rows}, summary_path)
    print("Saved:", summary_path)

    # also print hosts summary
    hosts = sorted({r.get("host") for r in rows if r.get("host")})
    if hosts:
        print("Domains:", ", ".join(hosts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
