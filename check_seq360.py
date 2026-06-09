import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 360px mobile full page
        page = await browser.new_page(viewport={'width': 360, 'height': 800})
        await page.goto('http://127.0.0.1:5008/login')
        await page.fill('input[name="username"]', 'demo')
        await page.fill('input[name="password"]', 'demo123')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(500)
        await page.goto('http://127.0.0.1:5008/course/web')
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path='screenshots_dark/course_360_full.png', full_page=True)
        print('Saved full-page 360 screenshot')
        
        info = await page.evaluate("""
            () => {
                const headings = [...document.querySelectorAll("h3")];
                const seqHeading = headings.find(h => h.textContent.includes("Course Sequence"));
                if (!seqHeading) return {error: "no heading"};
                const seqBox = seqHeading.closest(".bg-surface");
                if (!seqBox) return {error: "no seq box"};
                const rect = seqBox.getBoundingClientRect();
                return {
                    top: rect.top.toFixed(0),
                    bottom: rect.bottom.toFixed(0),
                    height: rect.height.toFixed(0),
                    width: rect.width.toFixed(0),
                    circles: seqBox.querySelectorAll(".rounded-full").length,
                    visible: rect.bottom <= 800 ? "visible" : "below-fold",
                };
            }
        """)
        print(f'Sequence at 360px: {info}')
        await browser.close()

asyncio.run(main())
