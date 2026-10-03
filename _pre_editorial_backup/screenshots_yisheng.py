"""YiSheng 新作品截图：主页卡片 + 详情页"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
OUT = os.path.join(os.path.dirname(__file__), "_screenshots")
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Desktop
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        # 主页：滚动到作品集区域
        await page.goto(BASE + "/#work", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await page.screenshot(path=os.path.join(OUT, "12_yisheng_card_desktop.png"))
        print("  ✓ 12_yisheng_card_desktop.png")

        # 详情页 - Hero
        await page.goto(BASE + "/project-yisheng.html", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await page.screenshot(path=os.path.join(OUT, "13_yisheng_detail_hero.png"))
        print("  ✓ 13_yisheng_detail_hero.png")

        # 详情页 - 架构图
        await page.evaluate("window.scrollBy(0, 1200)")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(OUT, "14_yisheng_detail_arch.png"))
        print("  ✓ 14_yisheng_detail_arch.png")

        # 详情页 - API
        await page.evaluate("window.scrollBy(0, 1200)")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(OUT, "15_yisheng_detail_api.png"))
        print("  ✓ 15_yisheng_detail_api.png")

        await ctx.close()

        # Mobile
        ctx_m = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
        )
        page_m = await ctx_m.new_page()
        await page_m.goto(BASE + "/#work", wait_until="networkidle")
        await asyncio.sleep(1)
        await page_m.evaluate("window.scrollBy(0, 1400)")
        await asyncio.sleep(0.8)
        await page_m.screenshot(path=os.path.join(OUT, "16_yisheng_card_mobile.png"))
        print("  ✓ 16_yisheng_card_mobile.png")

        await ctx_m.close()
        await browser.close()
    print("\n全部 YiSheng 截图完成")


if __name__ == "__main__":
    asyncio.run(main())