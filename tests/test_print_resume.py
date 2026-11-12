# -*- coding: utf-8 -*-
"""简历打印路径守门（圆桌 v2 D席 R5 实锤修复的回归防线）。

背景：#printArea 原先只在 [data-print] 的 click 回调里被填充，而
@media print 会隐藏除 #printArea 外的一切——HR 在浏览器菜单里直接
Ctrl+P 得到的是一页白纸。修复 = 挂 beforeprint 监听兜底填充。

跑法（站点根目录）：python -m pytest tests/test_print_resume.py -q
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _index_js() -> str:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    # 内联 JS 在 </body> 前的 <script> 块里；直接全文检查（契约测试同风格）
    return text


def test_beforeprint_fallback_exists():
    """必须存在 beforeprint 监听兜底填充 #printArea（菜单打印不再白纸）。"""
    js = _index_js()
    assert "beforeprint" in js, "index.html 缺 beforeprint 监听——菜单打印会得到白纸"
    # 监听体内引用 #printArea 与 RESUME_HTML（与 click 路径同一填充来源）
    idx = js.index("beforeprint")
    window_slice = js[idx : idx + 400]
    assert "printArea" in window_slice, "beforeprint 监听未填充 #printArea"
    assert "RESUME_HTML" in window_slice, "beforeprint 监听未使用 RESUME_HTML 作为填充源"


def test_click_print_path_retained():
    """原「打印简历」按钮路径不得被修复破坏（双路径并存）。"""
    js = _index_js()
    assert "$$('[data-print]')" in js, "data-print 点击绑定丢失"
    assert "window.print()" in js, "window.print() 调用丢失"


def test_print_area_and_media_print_present():
    """@media print 与 #printArea 结构保留（PDF 只出简历的机制不变）。"""
    js = _index_js()
    assert "#printArea" in js, "#printArea 容器丢失"
    assert "@media print" in js, "@media print 样式丢失"
