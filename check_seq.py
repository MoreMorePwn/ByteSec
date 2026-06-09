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
        await page.wait_for_timeout(500)
        await page.goto('http://127.0.0.1:5008/course/web')
        await page.wait_for_timeout(2000)
        
        el_count = await page.evaluate('document.querySelectorAll(".flex-wrap").length')
        print(f'Found {el_count} flex-wrap containers')
        
        result = await page.evaluate("""
            () => {
                const headings = [...document.querySelectorAll("h3")];
                const seqHeading = headings.find(h => h.textContent.includes("Course Sequence"));
                if (!seqHeading) return {error: "no Course Sequence heading"};
                const container = seqHeading.closest(".bg-surface");
                if (!container) return {error: "no parent container"};
                const rect = container.getBoundingClientRect();
                const flexWrap = container.querySelector(".flex-wrap");
                if (!flexWrap) return {error: "no flex-wrap in sequence"};
                const flexRect = flexWrap.getBoundingClientRect();
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
                    containerWidth: rect.width.toFixed(0),
                    flexWidth: flexRect.width.toFixed(0),
                    flexHeight: flexRect.height.toFixed(0),
                    numCircles: circles.length,
                    circleWidth: circles.length > 0 ? circles[0].offsetWidth : 0,
                    itemsInFlex: flexWrap.children.length,
                    rows: rows,
                };
            }
        """)
        print(f'Sequence: {result}')
        
        await page.screenshot(path='screenshots_dark/course_final_fix.png')
        
        await browser.close()

asyncio.run(main())
