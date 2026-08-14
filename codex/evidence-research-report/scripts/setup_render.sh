#!/usr/bin/env bash
# 安裝本地渲染層（Camoufox anti-detect Firefox + Playwright），並自檢。
# 無管理員權限：全部裝進 user 空間（uv venv 或 pip --user）；Camoufox 下載到 ~/.cache。
#
# 本機 python 若缺 Camoufox，fetch_page.py 會自動改用 ~/.local/share/render-venv/bin/python
# 跑 scripts/render_page.py 做本地渲染。
set -euo pipefail

VENV_PY="$HOME/.local/share/render-venv/bin/python"

if command -v uv >/dev/null 2>&1; then
    echo "==> using uv-managed python venv (self-contained, avoids system python issues)"
    if [ ! -x "$VENV_PY" ]; then
        uv venv --python 3.14.5 "$HOME/.local/share/render-venv" 2>/dev/null || \
            uv venv --python 3.12 "$HOME/.local/share/render-venv"
    fi
    uv pip install --python "$VENV_PY" -U "camoufox[geoip]" playwright
else
    echo "==> uv not found; installing to user site-packages of current python3"
    pip3 install --user -U "camoufox[geoip]" playwright
    VENV_PY="$(command -v python3)"
fi

"$VENV_PY" -m camoufox fetch

# 自檢：渲染 https://example.com，斷言含 "Example Domain"
CHECK=$("$VENV_PY" - <<'PY'
from camoufox.sync_api import Camoufox

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto("https://example.com", wait_until="networkidle", timeout=30000)
    print(page.inner_text("body"))
PY
)
echo "$CHECK"
if echo "$CHECK" | grep -q "Example Domain"; then
    echo "RENDER SELF-CHECK OK"
else
    echo "RENDER SELF-CHECK FAILED" >&2
    exit 1
fi
