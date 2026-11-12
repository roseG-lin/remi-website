# -*- coding: utf-8 -*-
"""HR 15 秒路径守门：nav「简历」入口在手机宽下可见、点击命中 #resume（圆桌 v2 M席条文 + D席判定口）。

背景（圆桌 v2 实锤）：:544 `.nav-links a:not(.nav-os){display:none}` 把手机端导航全藏，
只加链接不改规则 = grep 假绿。本测试用真实浏览器判定，拒绝静态 grep。

跑法（站点根目录）：python -m pytest tests/test_nav_resume.py -q
（需要 playwright：chromium 已装；本测试起独立 http.server，不依赖外部服务）
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


def test_mobile_nav_resume_visible_and_navigates(base_url):
    """390×844：简历入口可见（未被 :544 隐藏），点击后 hash=#resume 且简历区进入视口。"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(base_url + "/", wait_until="load")
        link = page.locator("nav#nav .nav-links a.nav-resume")
        link.wait_for(state="attached", timeout=5000)
        assert link.is_visible(), "手机宽下「简历」入口不可见——:544 隐藏规则未放行 .nav-resume"
        link.click()
        page.wait_for_timeout(200)
        assert "#resume" in page.url, f"点击后 hash 未变为 #resume（当前 {page.url}）"
        # 平滑滚动是距离相关的动画：轮询等它到位（4s 窗口），不用固定等待猜时长
        try:
            page.wait_for_function(
                "() => { const el = document.querySelector('#resume');"
                " const r = el.getBoundingClientRect(); return r.top < 200 && r.height > 0; }",
                timeout=4000,
            )
        except Exception:
            box = page.evaluate(
                "() => { const el = document.querySelector('#resume');"
                " const r = el.getBoundingClientRect(); return { top: r.top, height: r.height }; }"
            )
            assert False, f"#resume 4s 内未进入视口（top={box['top']:.0f}px）"
        browser.close()


def test_desktop_nav_resume_visible_first(base_url):
    """桌面宽：简历入口可见且为 nav 首个链接（HR 15 秒路径的第一落点）。"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(base_url + "/", wait_until="load")
        links = page.locator("nav#nav .nav-links a")
        first_text = links.first.text_content().strip()
        resume = page.locator("nav#nav .nav-links a.nav-resume")
        resume.wait_for(state="attached", timeout=5000)
        assert resume.is_visible(), "桌面宽下「简历」入口不可见"
        assert first_text == "简历", f"nav 首个链接不是「简历」（当前是「{first_text}」）"
        browser.close()
