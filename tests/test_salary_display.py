# -*- coding: utf-8 -*-
"""薪资「12-15K」渲染守门。

背景（圆桌 v2 + 阶段5 实测修正）：
- 原假设「删除线观感=换行断裂」被现场探针证伪：390×844 下 12-15K 本就是单行渲染。
- 真实原因=JetBrains Mono 连字符字形在字距下偏长（字体审美决策归用户，见 roundtable v2 报告）。
- 本期落地的是**防换行保险**：.num-nowrap 保证薪资串永不跨行断裂（未来改版防回归），
  同时把「12-15K 单行渲染」固化为可判定契约。

跑法（站点根目录，需 8790 本地服务）：python -m pytest tests/test_salary_display.py -q
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def base_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(40):
        try:
            urllib.request.urlopen(url + "/", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    else:
        proc.terminate()
        pytest.fail("本地 http.server 起不来")
    yield url
    proc.terminate()
    proc.wait(timeout=5)


def test_salary_spans_never_wrap(base_url):
    """所有「12-15K」文本：white-space=nowrap 且渲染为单一矩形（不跨行断裂）。"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(base_url + "/", wait_until="load")
        page.wait_for_timeout(500)
        results = page.evaluate(
            """() => {
              const out = [];
              const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
              while (walker.nextNode()) {
                const node = walker.currentNode;
                if (!node.textContent.includes('12-15K')) continue;
                const el = node.parentElement;
                const range = document.createRange();
                const i = node.textContent.indexOf('12-15K');
                range.setStart(node, i);
                range.setEnd(node, i + 6);
                const rects = Array.from(range.getClientRects()).filter(r => r.width > 0);
                out.push({
                  cls: el.className,
                  whiteSpace: getComputedStyle(el).whiteSpace,
                  rectCount: rects.length,
                });
              }
              return out;
            }"""
        )
        assert len(results) >= 2, f"页面上应至少 2 处「12-15K」（实测 {len(results)}）"
        for r in results:
            assert r["whiteSpace"] == "nowrap", (
                f"「12-15K」（{r['cls']}）white-space={r['whiteSpace']}——未套 .num-nowrap 防换行保险"
            )
            assert r["rectCount"] == 1, f"「12-15K」（{r['cls']}）跨行渲染为 {r['rectCount']} 段"
        browser.close()


def test_salary_chars_untouched():
    """契约：页面里的 12-15K 字符串原样保留（双 assert 锁的口径不变，本阶段零字符改动）。"""
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert text.count("12-15K") == 2, f"index.html 应恰好 2 处 12-15K（实测 {text.count('12-15K')}）"
