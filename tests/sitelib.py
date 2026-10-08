"""Shared helpers for the site tests: where things live and what the site is about."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ORIGIN = "https://hkutluay.com"

APPS = {
    "chronolyze": {"id": "6790505948", "name": "Chronolyze", "shots": 6},
    "reelo": {"id": "6783331223", "name": "Reelo", "shots": 7},
}
