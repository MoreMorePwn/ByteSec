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

JS_MEASURE = """() => {
    // Find the flex-wrap container
    const viz = document.querySelector('.flex-wrap');
    if (!viz) return {error: 'no flex-wrap container'};
    const rect = viz.getBoundingClientRect();
    
    // Check that all circles fit
    const circles = viz.querySelectorAll('.rounded-full');
    const isOverflowing = viz.scrollWidth > rect.width + 2;
    const firstCircle = circles[0];
    const circleRect = firstCircle ? firstCircle.getBoundingClientRect() : null;
    
    // Count rows
    const items = [...viz.children];
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
        parentWidth: rect.width.toFixed(0),
        parentHeight: rect.height.toFixed(0),
        hasOverflow: isOverflowing,
        circleSize: circleRect ? circleRect.width.toFixed(0) : 'N/A',
        totalCircles: circles.length,
        rows: rows,
    };
}"""

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
            
            info = await page.evaluate(JS_MEASURE)
            print(f"[{'OK' if not info.get('hasOverflow') else 'BUG'}] {name} ({w}px): {info}")
            
            await page.screenshot(path=f'screenshots_dark/course_{w}.png')
            await page.close()
        await browser.close()

asyncio.run(main())
