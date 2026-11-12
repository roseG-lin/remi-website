# -*- coding: utf-8 -*-
"""llms 档案完整性：给 AI 抓取的自述里引用的案例链接必须真实存在。

背景（圆桌 v2 Gr席 R5 实锤）：llms.txt:33 与 llms-full.txt:36/:43 的
case/04-reyes-video.html、case/07-mirror-value.html 是对调后的死链，
真身为 case/04-mirror-value.html 与 case/07-reyes-video.html。
代笔模型按档案改案例会写坏真身文件而 pytest 照绿——本测试就是那扇门。

跑法（站点根目录）：python -m pytest tests/test_llms_links.py -q
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LLMS_FILES = ("llms.txt", "llms-full.txt")

# 匹配 https://www.remifei.cn/case/xxx.html 与相对 case/xxx.html 两种写法
CASE_LINK_RE = re.compile(r"(?:https://www\.remifei\.cn/)?(case/[A-Za-z0-9_-]+\.html)")


def _existing_case_files() -> set[str]:
    case_dir = ROOT / "case"
    return {p.name for p in case_dir.glob("*.html")}


def test_llms_case_links_all_exist():
    """llms 档案里每个 case/*.html 链接都必须指向真实存在的文件（死链=代笔模型写坏真身的入口）。"""
    existing = _existing_case_files()
    assert existing, "case/ 目录为空？站点结构异常"

    dead: list[str] = []
    for rel in LLMS_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for link in CASE_LINK_RE.findall(text):
            filename = link.split("/", 1)[1]
            if filename not in existing:
                dead.append(f"{rel}: {link}")
    assert not dead, f"llms 档案存在死链（对调/改名未同步）：{dead}"


def test_llms_case_links_no_duplicates():
    """同一案例文件在单份档案内不得出现两次（编号对调修复时容易顺手写重）。"""
    for rel in LLMS_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        seen: dict[str, int] = {}
        for link in CASE_LINK_RE.findall(text):
            seen[link] = seen.get(link, 0) + 1
        dupes = {k: v for k, v in seen.items() if v > 1}
        assert not dupes, f"{rel} 案例链接重复引用：{dupes}"
