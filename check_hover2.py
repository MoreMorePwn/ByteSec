from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1280, "height": 200})
    page = ctx.new_page()

    page.goto("http://127.0.0.1:5008/login")
    page.fill("input[name=username]", "demo")
    page.fill("input[name=password]", "demo123")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    page.evaluate("localStorage.setItem('bytesec-theme', 'dark')")
    page.reload()
    page.wait_for_load_state("networkidle")

    links = ["Dashboard", "Course", "Leaderboard", "Community", "Articles"]
    nav = page.locator("nav")
    nav_bg = nav.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Nav bar background: {nav_bg}")

    for name in links:
        link = nav.locator("a").filter(has_text=name)
        bg_before = link.evaluate("el => window.getComputedStyle(el).backgroundColor")
        link.hover()
        time.sleep(0.15)
        bg_hover = link.evaluate("el => window.getComputedStyle(el).backgroundColor")
        print(f"  {name:15s} {bg_before:30s} -> {bg_hover:30s}")

    page.screenshot(path="screenshots_dark/hover_v2.png")
    print("\nScreenshot: hover_v2.png")
    b.close()
