#!/usr/bin/env python3
"""
根据商品ID查询商品状态
用法:
  python -u docs/examples/get_goods_status.py <goods_id>
"""

import os
import sys
import json
from dotenv import load_dotenv


def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: get_goods_status.py <goods_id>")
        sys.exit(1)

    goods_id = sys.argv[1]

    from temu_api import TemuClient
    client = TemuClient(
        app_key=os.getenv("TEMU_APP_KEY"),
        app_secret=os.getenv("TEMU_APP_SECRET"),
        access_token=os.getenv("TEMU_ACCESS_TOKEN"),
        base_url=os.getenv("TEMU_BASE_URL", "https://openapi-b-global.temu.com"),
        debug=False,
    )

    try:
        # 某些站点接口命名不同，优先尝试 detail_query，不支持则用 list_retrieve 过滤
        if hasattr(client.product, "goods_detail_query"):
            resp = client.product.goods_detail_query(goods_id=goods_id)
        else:
            resp = client.product.goods_list_retrieve(goods_search_type="ALL", page_size=50)
            # 从列表中筛选目标ID
            if resp.get("success"):
                goods = next((g for g in (resp.get("result", {}).get("goodsList") or []) if str(g.get("goodsId")) == str(goods_id)), None)
                resp = {"success": True, "result": goods or {}}
    except Exception as e:
        print(f"❌ API异常: {e}")
        sys.exit(2)

    # 打印原始结果
    print(json.dumps(resp, ensure_ascii=False, indent=2))

    # 额外提炼常见状态字段
    try:
        result = resp.get("result", {}) or {}
        status_fields = {
            "goodsStatus": result.get("goodsStatus"),
            "publishStatus": result.get("publishStatus"),
            "auditStatus": result.get("auditStatus"),
            "goodsShelvesStatus": result.get("goodsShelvesStatus"),
        }
        print("\n简要状态:")
        for k, v in status_fields.items():
            if v is not None:
                print(f"- {k}: {v}")
    except Exception:
        pass


if __name__ == "__main__":
    main()


