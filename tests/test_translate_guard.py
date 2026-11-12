# -*- coding: utf-8 -*-
"""防翻译守门：所有被服务的 HTML 页面必须声明 notranslate。

背景（圆桌 v2 用户实测 + M席/Gr席 复验）：主页 lang=zh-CN 且无翻译保护，
Chrome 自动翻译把 "Remi Lin" 音译成「雷米」；splitHero(:1191) 拆字后
被翻译引擎改写还会把 h1 拆出残片——翻译对视觉与结构都是破坏项。
潮汛嵌入页早已带 notranslate，本测试把同一保护覆盖到站点全部页面。

跑法（站点根目录）：python -m pytest tests/test_translate_guard.py -q
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Google 站点验证文件是裸 token，必须字节原样（Google 按原文抓取），豁免且不得加 head。
VERIFICATION_FILES = {"google043d99ac8e7f5a5b.html"}


def _served_html() -> list[Path]:
    """整仓会被静态服务的 HTML（Vercel 全目录直出），含首页/案例/OS/归档页。"""
    files = sorted(ROOT.rglob("*.html"))
    # 排除测试脚手架等非页面产物（tests/ 目录下无 html，防御性过滤）与验证 token 文件
    return [
        p
        for p in files
        if "node_modules" not in p.parts and "tests" not in p.parts and p.name not in VERIFICATION_FILES
    ]


def test_verification_token_files_stay_byte_exact():
    """Google 验证 token 文件必须保持裸 token 原样（不得被模板化）。"""
    for name in VERIFICATION_FILES:
        text = (ROOT / name).read_text(encoding="utf-8").strip()
        assert text == "google-site-verification: google043d99ac8e7f5a5b.html", (
            f"{name} 内容被改动，Google 验证会失效"
        )


def test_every_served_html_declares_notranslate():
    missing: list[str] = []
    for p in _served_html():
        text = p.read_text(encoding="utf-8")
        if 'name="google" content="notranslate"' not in text:
            missing.append(p.relative_to(ROOT).as_posix())
    assert not missing, f"以下页面缺 notranslate 保护（Chrome 会把 Remi 音译成「雷米」）：{missing}"


def test_notranslate_meta_in_head():
    """meta 声明必须位于 <head> 内（放 body 里不生效）。"""
    for p in _served_html():
        text = p.read_text(encoding="utf-8")
        if 'name="google" content="notranslate"' not in text:
            continue  # 上一条断言已兜底
        head = text.split("</head>", 1)[0]
        assert 'name="google" content="notranslate"' in head, (
            f"{p.relative_to(ROOT)} 的 notranslate meta 不在 head 内"
        )
