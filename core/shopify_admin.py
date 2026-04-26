"""
Shopify Admin API クライアント (REST 2024-10)

.env の SHOPIFY_ACCESS_TOKEN と SHOPIFY_STORE_DOMAIN を読み、
最低限の CRUD（接続確認・商品・注文・在庫・顧客）を関数として提供する。

依存: requests / python-dotenv（既に requirements.txt 済）
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-10")


class ShopifyConfigError(RuntimeError):
    pass


class ShopifyAPIError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"Shopify API {status}: {body[:300]}")
        self.status = status
        self.body = body


def _config() -> tuple[str, str]:
    token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
    domain = os.environ.get("SHOPIFY_STORE_DOMAIN", "").strip()
    if not token or token.startswith("shpat_xxx"):
        raise ShopifyConfigError("SHOPIFY_ACCESS_TOKEN が .env に未設定です")
    if not domain:
        raise ShopifyConfigError("SHOPIFY_STORE_DOMAIN が .env に未設定です")
    return token, domain


def _request(method: str, path: str, params: dict | None = None, json: dict | None = None) -> Any:
    token, domain = _config()
    url = f"https://{domain}/admin/api/{API_VERSION}/{path.lstrip('/')}"
    r = requests.request(
        method,
        url,
        headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        params=params,
        json=json,
        timeout=30,
    )
    if r.status_code >= 400:
        raise ShopifyAPIError(r.status_code, r.text)
    return r.json() if r.text else {}


# ---------- 公開関数 ----------

def is_configured() -> dict:
    """.env が揃っているかだけを返す（実通信なし）"""
    try:
        _config()
        return {"configured": True}
    except ShopifyConfigError as e:
        return {"configured": False, "reason": str(e)}


def shop_info() -> dict:
    """接続確認: ストア情報を取得"""
    data = _request("GET", "shop.json")
    s = data.get("shop", {})
    return {
        "name": s.get("name"),
        "domain": s.get("domain"),
        "myshopify_domain": s.get("myshopify_domain"),
        "email": s.get("email"),
        "country": s.get("country_name"),
        "currency": s.get("currency"),
        "plan_name": s.get("plan_display_name"),
        "primary_locale": s.get("primary_locale"),
    }


def list_products(limit: int = 20, query: str = "") -> dict:
    """商品一覧（titleの部分一致でフィルタ可）"""
    params: dict[str, Any] = {"limit": min(max(limit, 1), 250), "fields": "id,title,handle,status,vendor,product_type,variants,image"}
    if query:
        params["title"] = query
    data = _request("GET", "products.json", params=params)
    items = []
    for p in data.get("products", []):
        variants = p.get("variants") or []
        first = variants[0] if variants else {}
        items.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "handle": p.get("handle"),
            "status": p.get("status"),
            "vendor": p.get("vendor"),
            "product_type": p.get("product_type"),
            "price": first.get("price"),
            "inventory_quantity": first.get("inventory_quantity"),
            "image": (p.get("image") or {}).get("src", ""),
            "variants_count": len(variants),
        })
    return {"products": items, "count": len(items)}


def list_orders(limit: int = 20, status: str = "any") -> dict:
    """注文一覧（直近）"""
    params = {
        "limit": min(max(limit, 1), 250),
        "status": status,
        "fields": "id,name,created_at,total_price,currency,financial_status,fulfillment_status,customer,line_items",
    }
    data = _request("GET", "orders.json", params=params)
    items = []
    for o in data.get("orders", []):
        cust = o.get("customer") or {}
        items.append({
            "id": o.get("id"),
            "name": o.get("name"),
            "created_at": o.get("created_at"),
            "total_price": o.get("total_price"),
            "currency": o.get("currency"),
            "financial_status": o.get("financial_status"),
            "fulfillment_status": o.get("fulfillment_status"),
            "customer": f"{cust.get('first_name','')} {cust.get('last_name','')}".strip() or cust.get("email", ""),
            "items_count": len(o.get("line_items") or []),
        })
    return {"orders": items, "count": len(items)}


def search_customers(query: str, limit: int = 20) -> dict:
    """顧客検索（メール・名前・電話で部分一致）"""
    if not query.strip():
        return {"customers": [], "count": 0}
    params = {
        "query": query,
        "limit": min(max(limit, 1), 250),
        "fields": "id,first_name,last_name,email,phone,orders_count,total_spent,currency,created_at",
    }
    data = _request("GET", "customers/search.json", params=params)
    items = []
    for c in data.get("customers", []):
        items.append({
            "id": c.get("id"),
            "name": f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
            "email": c.get("email"),
            "phone": c.get("phone"),
            "orders_count": c.get("orders_count"),
            "total_spent": c.get("total_spent"),
            "currency": c.get("currency"),
            "created_at": c.get("created_at"),
        })
    return {"customers": items, "count": len(items)}


def list_locations() -> dict:
    """在庫拠点（Location）一覧。在庫更新時に必要"""
    data = _request("GET", "locations.json")
    return {"locations": data.get("locations", [])}


def get_inventory_levels(inventory_item_ids: list[int], location_ids: list[int] | None = None) -> dict:
    """指定 inventory_item_id の在庫レベル取得"""
    if not inventory_item_ids:
        return {"inventory_levels": []}
    params: dict[str, Any] = {"inventory_item_ids": ",".join(str(i) for i in inventory_item_ids)}
    if location_ids:
        params["location_ids"] = ",".join(str(i) for i in location_ids)
    data = _request("GET", "inventory_levels.json", params=params)
    return data


def set_inventory(inventory_item_id: int, location_id: int, available: int) -> dict:
    """在庫数を絶対値で設定"""
    payload = {
        "location_id": int(location_id),
        "inventory_item_id": int(inventory_item_id),
        "available": int(available),
    }
    return _request("POST", "inventory_levels/set.json", json=payload)
