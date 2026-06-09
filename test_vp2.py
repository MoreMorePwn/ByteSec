import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [
    ('360x800', 360, 800),
    ('414x896', 414, 896),
    ('768x1024', 768, 1024),
    ('1024x768', 1024, 768),
    ('1280x800', 1280, 800),
    ('1440x900', 1440, 900),
]

JS_INSPECT = """
() => {
    const headings = [...document.querySelectorAll("h3")];
    const seqHeading = headings.find(h => h.textContent.includes("Course Sequence"));
    if (!seqHeading) return {error: "no heading"};
    const container = seqHeading.closest(".bg-surface");
    if (!container) return {error: "no container"};
    const flexWrap = container.querySelector(".flex-wrap");
    if (!flexWrap) return {error: "no flex-wrap"};
    const rect = flexWrap.getBoundingClientRect();
    const circles = flexWrap.querySelectorAll(".rounded-full");
    const items = [...flexWrap.children];
    let rows = 1;
    if (items.length > 1) {
        let prevTop = items[0].getBoundingClientRect().top;
        for (let i = 1; i < items.length; i++) {
            const t = items[i].getBoundingClientRect().top;
            if (t > prevTop + 2) rows++;
            prevTop = t;
        }
    }
    return {
        containerWidth: container.getBoundingClientRect().width.toFixed(0),
        flexWidth: rect.width.toFixed(0),
        flexHeight: rect.height.toFixed(0),
        circleWidth: circles.length > 0 ? circles[0].offsetWidth : 0,
        items: flexWrap.children.length,
        rows: rows,
    };
}
"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for name, w, h in VIEWPORTS:
            page = await browser.new_page(viewport={'width': w, 'height': h})
            await page.goto('http://127.0.0.1:5008/login')
            await page.fill('input[name="username"]', 'demo')
            await page.fill('input[name="password"]', 'demo123')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(500)
            await page.goto('http://127.0.0.1:5008/course/web')
            await page.wait_for_timeout(1500)
            
            info = await page.evaluate(JS_INSPECT)
            print(f"[{name}] {info}")
            
            await page.screenshot(path=f'screenshots_dark/course_{w}.png')
            await page.close()
        await browser.close()

asyncio.run(main())
