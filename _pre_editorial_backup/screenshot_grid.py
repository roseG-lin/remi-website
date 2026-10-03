"""确认 YiSheng 卡片在作品集网格中的位置"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
OUT = os.path.join(os.path.dirname(__file__), "_screenshots")
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Desktop - 滚动到第二行
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()
        await page.goto(BASE + "/#work", wait_until="networkidle")
        await asyncio.sleep(1.5)
        # 找到 YiSheng 卡片
        await page.evaluate("""
            const el = document.querySelector('a[href="project-yisheng.html"]');
            if (el) el.scrollIntoView({block: 'center', behavior: 'instant'});
        """)
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(OUT, "17_yisheng_in_grid.png"))
        print("  ✓ 17_yisheng_in_grid.png")

        await ctx.close()

        # Mobile - 滚动到 YiSheng
        ctx_m = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
        )
        page_m = await ctx_m.new_page()
        await page_m.goto(BASE + "/#work", wait_until="networkidle")
        await asyncio.sleep(1)
        await page_m.evaluate("""
            const el = document.querySelector('a[href="project-yisheng.html"]');
            if (el) el.scrollIntoView({block: 'center', behavior: 'instant'});
        """)
        await asyncio.sleep(1)
        await page_m.screenshot(path=os.path.join(OUT, "18_yisheng_in_grid_mobile.png"))
        print("  ✓ 18_yisheng_in_grid_mobile.png")

        await ctx_m.close()
        await browser.close()
    print("\n完成")


if __name__ == "__main__":
    asyncio.run(main())