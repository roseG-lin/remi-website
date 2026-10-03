"""
Remi Portfolio — Editorial 升级后截图
- 桌面 1440×900 + 移动 390×844
- 覆盖主页（首屏 / Hero / About / Work / Journey / Contact）+ 项目页
"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
OUT_DIR = os.path.join(os.path.dirname(__file__), "_screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

# (路径, 截图名称, 描述)
SHOTS = [
    # 主页：分段截图
    ("/", "01_home_hero_desktop", "主页 Hero"),
    ("/#about", "02_home_about_desktop", "主页 About"),
    ("/#story", "03_home_story_desktop", "主页 Story"),
    ("/#work", "04_home_work_desktop", "主页 Work"),
    ("/#journey", "05_home_journey_desktop", "主页 Journey"),
    ("/#contact", "06_home_contact_desktop", "主页 Contact"),
    # 项目页
    ("/project-remi-radar.html", "07_project_radar_desktop", "项目页 Radar"),
    ("/project-novel-workflow.html", "08_project_novel_desktop", "项目页 Novel"),
    ("/project-agent-teams-playbook.html", "09_project_playbook_desktop", "项目页 Playbook"),
    # 移动端
    ("/", "10_home_hero_mobile", "主页 Hero 移动"),
    ("/#work", "11_home_work_mobile", "主页 Work 移动"),
]


async def shoot(page, url, name):
    await page.goto(BASE + url, wait_until="networkidle", timeout=30000)
    # 触发 reveal 动画
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)
    await page.evaluate("""
        document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
    """)
    await asyncio.sleep(0.5)
    out = os.path.join(OUT_DIR, name + ".png")
    await page.screenshot(path=out, full_page=False)
    print(f"  ✓ {name}.png")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Desktop
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = await ctx.new_page()
        print("== 桌面截图 ==")
        for url, name, desc in SHOTS:
            if "mobile" not in name:
                await shoot(page, url, name)
        await ctx.close()

        # Mobile
        ctx_m = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
        )
        page_m = await ctx_m.new_page()
        print("== 移动截图 ==")
        for url, name, desc in SHOTS:
            if "mobile" in name:
                await shoot(page_m, url, name)
        await ctx_m.close()

        await browser.close()
    print(f"\n全部截图已保存到：{OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())