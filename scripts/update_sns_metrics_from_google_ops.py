from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOOGLE_OPS = ROOT.parent / "consul" / "google_ops"
GOOGLE_OPS_DIR = Path(os.environ.get("GOOGLE_OPS_DIR", DEFAULT_GOOGLE_OPS))
GOOGLE_OPS_SCRIPTS = GOOGLE_OPS_DIR / "scripts"
OUTPUT_PATH = Path(
    os.environ.get(
        "GUBBLE_SNS_METRICS_OUTPUT",
        ROOT / "site" / "static" / "admin" / "sns-metrics.js",
    )
)

ACCOUNT_LABEL = os.environ.get("GUBBLE_GOOGLE_ACCOUNT", "goodbouldering")
GSC_SITE_URL = os.environ.get("GUBBLE_GSC_SITE_URL", "sc-domain:goodbouldering.com")
GA4_PROPERTY_ID = os.environ.get("GUBBLE_GA4_PROPERTY_ID", "properties/257088701")
SHOP_BASE_URL = os.environ.get("GUBBLE_SHOP_BASE_URL", "https://goodbouldering.com/")
GA4_FALLBACK_URL = os.environ.get(
    "GUBBLE_GA4_FALLBACK_URL",
    "https://analytics.google.com/analytics/web/#/p257088701/reports/intelligenthome",
)

SEARCH_PAGE = "\u691c\u7d22\u30da\u30fc\u30b8"
LANDING_PAGE = "\u30e9\u30f3\u30c7\u30a3\u30f3\u30b0"
GSC_NOTE = "GSC 28\u65e5 \u81ea\u52d5"
GA4_NOTE = "GA4 28\u65e5 \u81ea\u52d5"


def require_google_ops() -> None:
    if not GOOGLE_OPS_SCRIPTS.exists():
        raise SystemExit(f"Missing google_ops scripts: {GOOGLE_OPS_SCRIPTS}")
    if not (GOOGLE_OPS_DIR / "credentials.json").exists():
        raise SystemExit(f"Missing credentials.json: {GOOGLE_OPS_DIR}")
    if not (GOOGLE_OPS_DIR / f"token_{ACCOUNT_LABEL}.json").exists():
        raise SystemExit(f"Missing token_{ACCOUNT_LABEL}.json: {GOOGLE_OPS_DIR}")
    sys.path.insert(0, str(GOOGLE_OPS_SCRIPTS))


def as_int(value: object) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def as_float(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def rounded_percent(rate: object) -> float:
    return round(as_float(rate) * 100, 2)


def shop_url(path: str) -> str:
    if not path or path == "(not set)":
        return GA4_FALLBACK_URL
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urljoin(SHOP_BASE_URL, path.lstrip("/"))


def build_metrics() -> dict:
    require_google_ops()
    import gsc  # type: ignore
    import ga4  # type: ignore

    gsc_start, gsc_end = gsc._window(28)
    gsc_total_rows = gsc.query_analytics(
        ACCOUNT_LABEL, GSC_SITE_URL, gsc_start, gsc_end, [], 1
    )
    gsc_total = gsc_total_rows[0] if gsc_total_rows else {}
    gsc_pages = gsc.top_pages(
        ACCOUNT_LABEL, GSC_SITE_URL, gsc_start, gsc_end, limit=1000
    )
    gsc_items = []
    for page in gsc_pages[:12]:
        title = str(page.get("page") or "")
        gsc_items.append(
            {
                "platform": "gsc",
                "type": SEARCH_PAGE,
                "title": title,
                "reach": as_int(page.get("impressions")),
                "reactions": as_int(page.get("clicks")),
                "engagement": rounded_percent(page.get("ctr")),
                "url": title,
                "note": GSC_NOTE,
            }
        )

    ga4_summary_rows = ga4.run_report(
        ACCOUNT_LABEL,
        GA4_PROPERTY_ID,
        dimensions=[],
        metrics=["activeUsers", "sessions", "eventCount", "engagementRate"],
        days=28,
        limit=1,
    )
    ga4_summary = ga4_summary_rows[0] if ga4_summary_rows else {}
    ga4_pages = ga4.run_report(
        ACCOUNT_LABEL,
        GA4_PROPERTY_ID,
        dimensions=["landingPagePlusQueryString"],
        metrics=["sessions", "eventCount", "engagementRate"],
        days=28,
        limit=12,
    )
    ga4_items = []
    for page in ga4_pages:
        title = str(page.get("landingPagePlusQueryString") or "")
        ga4_items.append(
            {
                "platform": "ga4",
                "type": LANDING_PAGE,
                "title": title,
                "reach": as_int(page.get("sessions")),
                "reactions": as_int(page.get("eventCount")),
                "engagement": rounded_percent(page.get("engagementRate")),
                "url": shop_url(title),
                "note": GA4_NOTE,
            }
        )

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "gubble-sns-metrics-collector",
        "platforms": {
            "gsc": {
                "followers": as_int(gsc_total.get("clicks")),
                "reach": as_int(gsc_total.get("impressions")),
                "posts": len(gsc_pages),
                "engagement": rounded_percent(gsc_total.get("ctr")),
                "note": GSC_NOTE,
            },
            "ga4": {
                "followers": as_int(ga4_summary.get("activeUsers")),
                "reach": as_int(ga4_summary.get("sessions")),
                "posts": as_int(ga4_summary.get("eventCount")),
                "engagement": rounded_percent(ga4_summary.get("engagementRate")),
                "note": GA4_NOTE,
            },
        },
        "items": gsc_items + ga4_items,
        "errors": [],
    }


def main() -> None:
    metrics = build_metrics()
    body = (
        "window.GUBBLE_SNS_METRICS = "
        + json.dumps(metrics, ensure_ascii=True, indent=2)
        + ";\n"
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(body, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "generatedAt": metrics["generatedAt"],
                "platforms": list(metrics["platforms"].keys()),
                "items": len(metrics["items"]),
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
