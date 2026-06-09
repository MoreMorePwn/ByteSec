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
        await page.screenshot(path='course_redesign.png')
        print("Screenshot saved")
        
        info = await page.evaluate("""
            () => {
                const headings = [...document.querySelectorAll("h3")];
                const seqHeading = headings.find(h => h.textContent.includes("Course Sequence"));
                if (!seqHeading) return {error: "no heading"};
                const seqBox = seqHeading.closest(".rounded-xl");
                if (!seqBox) return {error: "no parent"};
                const rect = seqBox.getBoundingClientRect();
                const flexWrap = seqBox.querySelector(".flex-wrap");
                const circles = flexWrap ? flexWrap.querySelectorAll(".rounded-full") : [];
                const labels = flexWrap ? flexWrap.querySelectorAll("span:nth-child(2)") : [];
                return {
                    sectionTop: rect.top.toFixed(0),
                    sectionWidth: rect.width.toFixed(0),
                    sectionHeight: rect.height.toFixed(0),
                    numCircles: circles.length,
                    numLabels: labels.length,
                    firstLabel: labels.length > 0 ? labels[2].textContent : "none",
                    parentWidth: rect.width.toFixed(0),
                    hasOverflow: flexWrap ? (flexWrap.scrollWidth > rect.width + 2) : false,
                };
            }
        """)
        print(f"Sequence: {info}")
        await browser.close()

asyncio.run(main())
