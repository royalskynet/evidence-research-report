#!/usr/bin/env python3
"""Fetch a URL's readable content (markdown) with a fallback chain.

Usage:
    python3 fetch_page.py <URL> [--render] [--no-mirror] [-o out.md]

Chain (first success wins):
    direct (HTTP/1.1, realistic headers) -> block/shell detection
    -> Firecrawl /v1/scrape (if key) -> r.jina.ai/<URL> -> Wayback snapshot
    -> archive.today -> local Camoufox render (never sends URL outside)

--render    force local render layer (known SPA domains / JS-only pages).
--no-mirror never hand the URL to Firecrawl / jina / archive services;
            only direct fetch + local render.

Output: article markdown to stdout (or -o file).
stderr:  final pipeline tag (direct|firecrawl|jina|wayback|archive|render|cached)
         plus snapshot date when a mirror was used.

Exit codes:
    0  success (real content)
    2  whole chain failed
    4  fetched but suspected shell (no usable content found)
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html as html_mod
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    BeautifulSoup = None

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) "
    "Gecko/20100101 Firefox/128.0"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip",
}

BLOCK_MARKERS = (
    "recaptcha",
    "cf-challenge",
    "cf_chl",
    "unusual traffic",
    "verify you are human",
    "are you human",
    "enable javascript and cookies",
    "please turn javascript on",
)
SHELL_TITLE = re.compile(r"just a moment", re.IGNORECASE)
MIN_TEXT = 500

KNOWN_SPA = (
    "www.okx.com/help",
    "www.bybit.com/en/help-center",
    "www.gate.io",
    "www.lbank.com",
)

ENV_FILE = Path.home() / ".hermes" / ".env"
TMP_DIR = Path(os.environ.get("TMPDIR", "/tmp"))
CACHE_DIR = TMP_DIR / "err-fetch-cache"
CACHE_TTL = 15 * 60
COOLDOWN_FILE = TMP_DIR / "err-fetch-cooldown.json"
COOLDOWN_SECONDS = 10 * 60
REQUEST_GAP_SECONDS = 3.0
REQUEST_TIMEOUT = 25
MIN_CONTENT_WORDS = 80


def load_firecrawl_key() -> str | None:
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("FIRECRAWL_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return None


class Cooldown:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}
        if COOLDOWN_FILE.exists():
            try:
                self._data = json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._data = {}
        if not isinstance(self._data, dict):
            self._data = {}

    def blocked(self, key: str) -> bool:
        rec = self._data.get(key)
        return bool(rec) and rec.get("until", 0) > time.time()

    def hit(self, key: str) -> None:
        now = time.time()
        rec = self._data.get(key, {})
        count = int(rec.get("count", 0)) + 1
        until = now + COOLDOWN_SECONDS * min(count, 6)
        self._data[key] = {"count": count, "until": until}
        try:
            COOLDOWN_FILE.write_text(json.dumps(self._data, ensure_ascii=False))
        except OSError:
            pass


_cooldown = Cooldown()
_last_request: dict[str, float] = {}


def _respect_rate_limit(domain: str) -> None:
    gap = time.time() - _last_request.get(domain, 0)
    if 0 < gap < REQUEST_GAP_SECONDS:
        time.sleep(REQUEST_GAP_SECONDS - gap)
    _last_request[domain] = time.time()


def _domain_of(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.split("@")[-1]


def _decode_body(raw: bytes) -> str:
    try:
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    except OSError:
        pass
    for enc in ("utf-8", "utf-8-sig", "big5", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _get(url: str, headers: dict | None = None, extra_headers: dict | None = None) -> tuple[int, str]:
    hdrs = dict(headers or HEADERS)
    if extra_headers:
        hdrs.update(extra_headers)
    _respect_rate_limit(_domain_of(url))
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.status, _decode_body(resp.read())


def _post(url: str, payload: dict, extra_headers: dict | None = None) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    hdrs = dict(HEADERS)
    hdrs.update({"Content-Type": "application/json"})
    if extra_headers:
        hdrs.update(extra_headers)
    _respect_rate_limit(_domain_of(url))
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.status, _decode_body(resp.read())


def _shell_signals(body: str) -> bool:
    low = body.lower()
    for marker in BLOCK_MARKERS:
        if marker in low:
            return True
    if SHELL_TITLE.search(low):
        return True
    text = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    script_density = len(re.findall(r"<script[^>]+src=", body))
    return len(text) < MIN_TEXT and script_density > 3


def _html_to_markdown(body: str) -> str:
    if BeautifulSoup:
        soup = BeautifulSoup(body, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer"]):
            tag.decompose()
        container = soup.find("main") or soup.find("article") or soup.find("body") or soup
        if container is None:
            container = soup
        return _blocks_to_md(container)
    body = re.sub(r"<(script|style|noscript|iframe|nav|footer)[^>]*>.*?</\1>", "", body, flags=re.S)
    return _blocks_to_md_rough(body)


def _blocks_to_md(node) -> str:
    out: list[str] = []
    for el in node.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre"]):
        text = " ".join(el.stripped_strings)
        if not text:
            continue
        if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(el.name[1])
            out.append(f"{'#' * level} {text}")
        elif el.name == "li":
            out.append(f"- {text}")
        elif el.name == "blockquote":
            out.append(f"> {text}")
        elif el.name == "pre":
            out.append(f"```\n{text}\n```")
        else:
            out.append(text)
    return "\n\n".join(out).strip()


def _blocks_to_md_rough(body: str) -> str:
    out: list[str] = []
    for m in re.finditer(r"<(h[1-6])[^>]*>(.*?)</\1>|<p[^>]*>(.*?)</p>|<li[^>]*>(.*?)</li>", body, re.S):
        tag = m.group(1)
        if tag:
            level = int(tag[1])
            text = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
            if text:
                out.append(f"{'#' * level} {text}")
        elif m.group(3) is not None:
            text = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()
            if text:
                out.append(text)
        else:
            text = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(4))).strip()
            if text:
                out.append(f"- {text}")
    return "\n\n".join(out).strip()


def _usable(content: str) -> bool:
    words = len(re.findall(r"\S+", content))
    return words >= MIN_CONTENT_WORDS


def fetch_direct(url: str) -> tuple[str | None, str]:
    """Return (content, tag) or (None, reason)."""
    dom = _domain_of(url)
    if _cooldown.blocked(dom):
        return None, "cooldown"
    try:
        status, body = _get(url)
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}"
    if status in (403, 429, 503):
        _cooldown.hit(dom)
        return None, f"http{status}"
    if _shell_signals(body):
        return None, "shell"
    md = _html_to_markdown(body)
    if not _usable(md):
        return None, "thin"
    return md, "direct"


def fetch_firecrawl(url: str, key: str) -> tuple[str | None, str]:
    try:
        status, body = _post(
            "https://api.firecrawl.dev/v1/scrape",
            {"url": url, "formats": ["markdown"]},
            {"Authorization": f"Bearer {key}"},
        )
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}"
    if status != 200:
        return None, f"http{status}"
    try:
        md = json.loads(body).get("data", {}).get("markdown", "")
    except json.JSONDecodeError:
        return None, "parse"
    if not _usable(md):
        return None, "thin"
    return md, "firecrawl"


def fetch_jina(url: str) -> tuple[str | None, str]:
    try:
        status, body = _get(f"https://r.jina.ai/{url}")
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}"
    if status != 200:
        return None, f"http{status}"
    if not _usable(body):
        return None, "thin"
    return body, "jina"


def fetch_wayback(url: str) -> tuple[str | None, str, str | None]:
    try:
        status, body = _get(
            f"https://archive.org/wayback/available?url={urllib.parse.quote(url)}"
        )
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}", None
    if status != 200:
        return None, f"http{status}", None
    try:
        closest = json.loads(body).get("archived_snapshots", {}).get("closest", {})
        snap_url = closest.get("url")
        timestamp = closest.get("timestamp")
    except json.JSONDecodeError:
        return None, "parse", None
    if not snap_url:
        return None, "no-snapshot", None
    try:
        snap_status, snap_body = _get(snap_url)
    except Exception as exc:
        return None, f"error:{exc.__class__.__name__}", timestamp
    if snap_status != 200:
        return None, f"http{snap_status}", timestamp
    if _shell_signals(snap_body):
        return None, "shell", timestamp
    md = _html_to_markdown(snap_body)
    if not _usable(md):
        return None, "thin", timestamp
    return md, "wayback", timestamp


def fetch_archive_today(url: str) -> tuple[str | None, str]:
    for host in ("https://archive.ph", "https://archive.today"):
        try:
            status, body = _get(f"{host}/newest/{url}")
        except Exception as exc:
            continue
        if status == 200 and not _shell_signals(body):
            md = _html_to_markdown(body)
            if _usable(md):
                return md, "archive"
    return None, "failed"


def render_page(url: str) -> tuple[str | None, str]:
    """Local anti-detect render. Never sends URL outside this machine.

    Tries Camoufox in-process first, then plain Playwright in-process, then a
    dedicated render venv (for machines whose default python cannot host
    Camoufox, e.g. Homebrew pythons with broken stdlib C modules).
    """
    script_dir = Path(__file__).resolve().parent
    venv_python = Path.home() / ".local" / "share" / "render-venv" / "bin" / "python"

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
            return text.strip(), "render"
        except Exception as exc:
            print(f"[fetch] camoufox in-process failed ({exc}); trying playwright", file=sys.stderr)

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        pass
    else:
        with sync_playwright() as p:
            try:
                browser = p.firefox.launch(headless=True)
            except Exception as exc:
                print(f"[fetch] playwright firefox launch failed ({exc})", file=sys.stderr)
            else:
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
                return text.strip(), "render"

    if venv_python.exists():
        try:
            proc = subprocess.run(
                [str(venv_python), str(script_dir / "render_page.py"), url],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return None, "render-timeout"
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip(), "render"
        print(f"[fetch] render venv failed: {proc.stderr.strip()[:300]}", file=sys.stderr)
        return None, "no-render-backend"

    return None, "no-render-backend"


def cache_path(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.md"


def cache_meta_path(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch URL content with fallback chain.")
    ap.add_argument("url", help="target URL")
    ap.add_argument("--render", action="store_true", help="force local render layer")
    ap.add_argument("--no-mirror", action="store_true", help="never send URL to mirror services")
    ap.add_argument("-o", dest="out", help="write output to file instead of stdout")
    args = ap.parse_args()

    url = args.url
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    meta = {}
    cp, mp = cache_path(url), cache_meta_path(url)
    if cp.exists():
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            meta = {}
        if time.time() - float(meta.get("fetched_at", 0)) < CACHE_TTL:
            content = cp.read_text(encoding="utf-8")
            print(f"[fetch] cached: {meta.get('pipeline', '?')}", file=sys.stderr)
            print(content)
            return 0

    key = load_firecrawl_key()
    snap_date: str | None = None
    content: str | None = None
    pipeline = ""
    last_shell: str | None = None

    known_spa = any(d in url for d in KNOWN_SPA)
    if args.render or args.no_mirror or known_spa:
        content, pipeline = fetch_direct(url)
        if content is None:
            content, pipeline = render_page(url)
    else:
        content, pipeline = fetch_direct(url)
        if content is None and key:
            content, pipeline = fetch_firecrawl(url, key)
        if content is None:
            content, pipeline = fetch_jina(url)
        if content is None:
            content, pipeline, snap_date = fetch_wayback(url)
        if content is None:
            content, pipeline = fetch_archive_today(url)
        if content is None:
            content, pipeline = render_page(url)

    if content is None:
        print(f"[fetch] {pipeline}: whole chain failed", file=sys.stderr)
        return 2

    if not _usable(content):
        last_shell = pipeline

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(content, encoding="utf-8")
    else:
        print(content)

    extra = f", snapshot={snap_date}" if snap_date else ""
    print(f"[fetch] pipeline={pipeline}{extra}", file=sys.stderr)
    if last_shell:
        return 4

    meta = {"url": url, "pipeline": pipeline, "fetched_at": time.time(), "snapshot": snap_date}
    try:
        cp.write_text(content, encoding="utf-8")
        mp.write_text(json.dumps(meta), encoding="utf-8")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
