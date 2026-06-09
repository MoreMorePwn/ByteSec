import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://127.0.0.1:5008/login')
        await page.fill('input[name="username"]', 'demo')
        await page.fill('input[name="password"]', 'demo123')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(800)
        await page.goto('http://127.0.0.1:5008/course/web')
        await page.wait_for_timeout(2000)
        
        # Scroll to course sequence
        await page.evaluate("window.scrollTo(0, 700)")
        await page.wait_for_timeout(500)
        await page.screenshot(path='course_redesign_seq.png')
        print("Sequence area screenshot saved")
        
        # Full page
        await page.screenshot(path='course_redesign_full.png', full_page=True)
        print("Full page screenshot saved")
        
        await browser.close()

asyncio.run(main())
