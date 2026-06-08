import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # Login first
        await page.goto('http://127.0.0.1:5008/login')
        await page.fill('input[name="username"]', 'demo')
        await page.fill('input[name="password"]', 'demo123')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(1000)
        
        # Go to a course page
        await page.goto('http://127.0.0.1:5008/course/web')
        await page.wait_for_timeout(2000)
        
        # Take screenshot
        await page.screenshot(path='screenshots_dark/course_pov.png', full_page=True)
        print('Screenshot saved')
        
        # Get the actual rendered size of the sequence container
        dims = await page.evaluate("""() => {
            const parent = document.querySelector('.overflow-x-auto');
            if (!parent) return {error: 'no overflow-x-auto found'};
            const rect = parent.getBoundingClientRect();
            const circles = parent.querySelectorAll('.w-9');
            return {
                parentWidth: rect.width,
                parentScrollWidth: parent.scrollWidth,
                hasScrollbar: parent.scrollWidth > rect.width + 2,
                numCircles: circles.length,
                circleSize: circles.length > 0 ? {
                    width: circles[0].offsetWidth,
                    height: circles[0].offsetHeight
                } : null,
                lastCircleRight: circles.length > 0 ? circles[circles.length-1].getBoundingClientRect().right - rect.left : null
            };
        }""")
        print(f'Dims: {dims}')
        
        await browser.close()

asyncio.run(main())
