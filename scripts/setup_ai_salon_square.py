"""Create or reuse the Square subscription plan for AIオンラインサロン.

Required environment variables:
  SQUARE_ACCESS_TOKEN
  SQUARE_LOCATION_ID

Optional:
  SQUARE_ENVIRONMENT (production or sandbox; default: production)
  SQUARE_VERSION (default: 2026-05-20)
  SQUARE_AI_SALON_PRICE_YEN (default: 2200)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any

import requests


PLAN_NAME = "AIオンラインサロン"
VARIATION_NAME = "AIオンラインサロン 月額2,200円"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured.")
    return value


def square_base_url() -> str:
    environment = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
    if environment == "sandbox":
        return "https://connect.squareupsandbox.com"
    if environment != "production":
        raise RuntimeError("SQUARE_ENVIRONMENT must be production or sandbox.")
    return "https://connect.squareup.com"


def square_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = requests.request(
        method,
        f"{square_base_url()}{path}",
        headers={
            "Authorization": f"Bearer {required_env('SQUARE_ACCESS_TOKEN')}",
            "Square-Version": os.getenv("SQUARE_VERSION", "2026-05-20"),
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    try:
        body = response.json()
    except ValueError as error:
        raise RuntimeError(
            f"Square returned non-JSON response ({response.status_code})."
        ) from error
    if not response.ok:
        detail = (body.get("errors") or [{}])[0]
        message = detail.get("detail") or detail.get("code") or response.status_code
        raise RuntimeError(f"Square API error: {message}")
    return body


def list_subscription_objects() -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    cursor = ""
    while True:
        query = "types=SUBSCRIPTION_PLAN%2CSUBSCRIPTION_PLAN_VARIATION"
        if cursor:
            query += f"&cursor={requests.utils.quote(cursor)}"
        body = square_request("GET", f"/v2/catalog/list?{query}")
        objects.extend(body.get("objects") or [])
        cursor = body.get("cursor") or ""
        if not cursor:
            return objects


def find_exact_plan(objects: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [
        obj
        for obj in objects
        if obj.get("type") == "SUBSCRIPTION_PLAN"
        and (obj.get("subscription_plan_data") or {}).get("name") == PLAN_NAME
        and not obj.get("is_deleted")
    ]
    if len(matches) > 1:
        raise RuntimeError(f"Multiple Square plans named {PLAN_NAME} exist.")
    return matches[0] if matches else None


def variation_price(variation: dict[str, Any]) -> tuple[str, int | None]:
    data = variation.get("subscription_plan_variation_data") or {}
    phases = data.get("phases") or []
    if len(phases) != 1:
        return "", None
    phase = phases[0]
    money = ((phase.get("pricing") or {}).get("price_money") or {})
    return phase.get("cadence") or "", money.get("amount")


def find_exact_variation(
    objects: list[dict[str, Any]],
    plan_id: str,
    price_yen: int,
) -> dict[str, Any] | None:
    named = [
        obj
        for obj in objects
        if obj.get("type") == "SUBSCRIPTION_PLAN_VARIATION"
        and (obj.get("subscription_plan_variation_data") or {}).get("name")
        == VARIATION_NAME
        and not obj.get("is_deleted")
    ]
    valid = [
        obj
        for obj in named
        if (obj.get("subscription_plan_variation_data") or {}).get(
            "subscription_plan_id"
        )
        == plan_id
        and variation_price(obj) == ("MONTHLY", price_yen)
    ]
    if len(valid) > 1:
        raise RuntimeError(f"Multiple valid Square variations named {VARIATION_NAME} exist.")
    if named and not valid:
        raise RuntimeError(
            f"A Square variation named {VARIATION_NAME} exists with different settings."
        )
    return valid[0] if valid else None


def create_plan() -> dict[str, Any]:
    body = square_request(
        "POST",
        "/v2/catalog/object",
        {
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "SUBSCRIPTION_PLAN",
                "id": "#ai-salon-plan",
                "present_at_all_locations": True,
                "subscription_plan_data": {"name": PLAN_NAME},
            },
        },
    )
    return body["catalog_object"]


def create_variation(plan_id: str, price_yen: int) -> dict[str, Any]:
    body = square_request(
        "POST",
        "/v2/catalog/object",
        {
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "SUBSCRIPTION_PLAN_VARIATION",
                "id": "#ai-salon-monthly-2200",
                "subscription_plan_variation_data": {
                    "name": VARIATION_NAME,
                    "phases": [
                        {
                            "cadence": "MONTHLY",
                            "pricing": {
                                "type": "STATIC",
                                "price_money": {
                                    "amount": price_yen,
                                    "currency": "JPY",
                                },
                            },
                        }
                    ],
                    "subscription_plan_id": plan_id,
                },
            },
        },
    )
    return body["catalog_object"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create missing Square catalog objects. Default is a read-only check.",
    )
    args = parser.parse_args()

    price_yen = int(os.getenv("SQUARE_AI_SALON_PRICE_YEN", "2200"))
    if price_yen != 2200:
        raise RuntimeError("This release is fixed to monthly 2,200 JPY.")
    required_env("SQUARE_LOCATION_ID")

    objects = list_subscription_objects()
    plan = find_exact_plan(objects)
    if not plan and args.apply:
        plan = create_plan()
    if not plan:
        print(json.dumps({"status": "missing", "plan": PLAN_NAME}, ensure_ascii=False))
        return 2

    variation = find_exact_variation(objects, plan["id"], price_yen)
    if not variation and args.apply:
        variation = create_variation(plan["id"], price_yen)
    if not variation:
        print(
            json.dumps(
                {"status": "missing", "plan_id": plan["id"], "variation": VARIATION_NAME},
                ensure_ascii=False,
            )
        )
        return 2

    cadence, amount = variation_price(variation)
    print(
        json.dumps(
            {
                "status": "ready",
                "environment": os.getenv("SQUARE_ENVIRONMENT", "production"),
                "plan_id": plan["id"],
                "variation_id": variation["id"],
                "cadence": cadence,
                "amount": amount,
                "currency": "JPY",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
