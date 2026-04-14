"""
サポートSNS 管理画面 (FastAPI)

起動:
    .venv/Scripts/python.exe -m uvicorn admin.server:app --port 4001 --reload

ブラウザ:
    http://localhost:4001/
"""
from __future__ import annotations
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "config" / "support_sns.yaml"
STATIC_DIR = Path(__file__).resolve().parent / "static"
SITE_DIST = ROOT / "site" / "dist"

Platform = Literal[
    "youtube",
    "x",
    "instagram_feed",
    "instagram_reel",
    "instagram_story",
    "threads",
    "facebook",
]

PLATFORMS: list[Platform] = [
    "youtube",
    "x",
    "instagram_feed",
    "instagram_reel",
    "instagram_story",
    "threads",
    "facebook",
]


class Account(BaseModel):
    name: str
    handle: str = ""
    url: str = ""
    note: str = ""


class AccountInput(BaseModel):
    input: str


URL_PREFIX = {
    "youtube":          "https://www.youtube.com/",
    "x":                "https://x.com/",
    "instagram_feed":   "https://www.instagram.com/",
    "instagram_reel":   "https://www.instagram.com/",
    "instagram_story":  "https://www.instagram.com/",
    "threads":          "https://www.threads.net/",
    "facebook":         "https://www.facebook.com/",
}


def normalize_account(platform: Platform, raw: str) -> Account:
    s = raw.strip()
    if not s:
        raise HTTPException(400, "input is empty")

    if s.startswith("http://") or s.startswith("https://"):
        url = s.rstrip("/")
        tail = url.rsplit("/", 1)[-1]
        if platform in ("instagram_feed", "instagram_reel", "instagram_story", "facebook"):
            handle = "@" + tail.lstrip("@") if tail else ""
        elif platform == "threads":
            handle = tail if tail.startswith("@") else "@" + tail
        elif platform == "youtube":
            handle = tail if tail.startswith("@") else tail
        else:
            handle = "@" + tail.lstrip("@")
        name = handle.lstrip("@") or tail
        return Account(name=name, handle=handle, url=url)

    handle_raw = s.lstrip("@")
    if not handle_raw:
        raise HTTPException(400, "invalid input")

    prefix = URL_PREFIX[platform]
    if platform == "youtube":
        url = f"{prefix}@{handle_raw}"
        handle = "@" + handle_raw
    elif platform == "threads":
        url = f"{prefix}@{handle_raw}"
        handle = "@" + handle_raw
    elif platform in ("instagram_feed", "instagram_reel", "instagram_story", "facebook"):
        url = f"{prefix}{handle_raw}"
        handle = "@" + handle_raw
    else:
        url = f"{prefix}{handle_raw}"
        handle = "@" + handle_raw

    return Account(name=handle_raw, handle=handle, url=url)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"support_sns": {p: [] for p in PLATFORMS}}
    data = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    sns = data.get("support_sns") or {}
    for p in PLATFORMS:
        sns.setdefault(p, [])
    return {"support_sns": sns}


def save_config(data: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


app = FastAPI(title="cclimb-intel")


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/site/")


@app.get("/admin")
@app.get("/admin/")
def admin_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/support-sns")
def get_all() -> dict:
    return load_config()["support_sns"]


@app.post("/api/support-sns/{platform}")
def add_account(platform: Platform, payload: AccountInput) -> dict:
    if platform not in PLATFORMS:
        raise HTTPException(400, f"unknown platform: {platform}")
    account = normalize_account(platform, payload.input)
    data = load_config()
    data["support_sns"][platform].append(account.model_dump())
    save_config(data)
    return {"ok": True, "platform": platform, "account": account.model_dump()}


@app.delete("/api/support-sns/{platform}/{index}")
def delete_account(platform: Platform, index: int) -> dict:
    if platform not in PLATFORMS:
        raise HTTPException(400, f"unknown platform: {platform}")
    data = load_config()
    items = data["support_sns"][platform]
    if index < 0 or index >= len(items):
        raise HTTPException(404, "index out of range")
    removed = items.pop(index)
    save_config(data)
    return {"ok": True, "removed": removed}


_run_state = {
    "running": False,
    "last_started": None,
    "last_finished": None,
    "last_status": None,
    "last_log": "",
}
_run_lock = threading.Lock()


def _execute_pipeline() -> None:
    log_lines: list[str] = []
    try:
        log_lines.append("[1/2] run.py")
        r1 = subprocess.run(
            [sys.executable, "run.py"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900,
        )
        log_lines.append(r1.stdout[-4000:] if r1.stdout else "")
        if r1.stderr:
            log_lines.append("[stderr] " + r1.stderr[-1000:])

        log_lines.append("\n[2/2] support_sns_collector")
        r2 = subprocess.run(
            [sys.executable, "-m", "core.support_sns_collector"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        log_lines.append(r2.stdout[-2000:] if r2.stdout else "")
        if r2.stderr:
            log_lines.append("[stderr] " + r2.stderr[-500:])

        _run_state["last_status"] = "ok" if r1.returncode == 0 else "error"
    except Exception as e:
        log_lines.append(f"[exception] {e}")
        _run_state["last_status"] = "error"
    finally:
        _run_state["last_log"] = "\n".join(log_lines)
        _run_state["last_finished"] = datetime.now(timezone.utc).isoformat()
        with _run_lock:
            _run_state["running"] = False


@app.post("/api/run")
def trigger_run() -> dict:
    with _run_lock:
        if _run_state["running"]:
            return {"ok": False, "message": "すでに実行中です", "state": _run_state}
        _run_state["running"] = True
        _run_state["last_started"] = datetime.now(timezone.utc).isoformat()
        _run_state["last_status"] = "running"
    threading.Thread(target=_execute_pipeline, daemon=True).start()
    return {"ok": True, "message": "巡回を開始しました", "state": _run_state}


@app.get("/api/run/status")
def run_status() -> dict:
    return _run_state


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if SITE_DIST.exists():
    app.mount("/site", StaticFiles(directory=SITE_DIST, html=True), name="site")
