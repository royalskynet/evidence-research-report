#!/usr/bin/env python3
"""Standalone local renderer; used as a subprocess fallback by fetch_page.py.

Renders a URL with Camoufox (anti-detect Firefox) locally — the URL never
leaves this machine. Falls back to plain Playwright Firefox if Camoufox is
unavailable.

Usage:
    python3 render_page.py <URL>

stdout: page text (main/article element preferred, else document.body.innerText)
exit:   0 ok, 2 render backend unavailable / failure
"""

from __future__ import annotations

import argparse
import sys


def render(url: str) -> str | None:
    try:
        from camoufox.sync_api import Camoufox  # type: ignore
    except ImportError:
        Camoufox = None  # type: ignore

    if Camoufox is not None:
        try:
            with Camoufox(headless=True) as browser:
                page = browser.new_page()
                page.set_viewport_size({"width": 1280, "height": 1024})
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    pass
                el = page.query_selector("main, article")
                text = el.inner_text() if el else page.evaluate("document.body.innerText")
            return text.strip()
        except Exception as exc:
            print(f"[render] camoufox failed ({exc}); trying playwright", file=sys.stderr)

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        return None
    with sync_playwright() as p:
        try:
            browser = p.firefox.launch(headless=True)
        except Exception as exc:
            print(f"[render] playwright firefox launch failed ({exc})", file=sys.stderr)
            return None
        with browser:
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1024})
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            el = page.query_selector("main, article")
            text = el.inner_text() if el else page.evaluate("document.body.innerText")
    return text.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Local render a URL.")
    ap.add_argument("url")
    args = ap.parse_args()
    text = render(args.url)
    if text is None:
        return 2
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
