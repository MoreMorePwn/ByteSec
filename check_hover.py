from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 200})
    page = ctx.new_page()

    # Login
    page.goto("http://127.0.0.1:5008/login")
    page.fill("input[name=username]", "demo")
    page.fill("input[name=password]", "demo123")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Force dark mode
    page.evaluate("localStorage.setItem('bytesec-theme', 'dark')")
    page.reload()
    page.wait_for_load_state("networkidle")

    dark = page.evaluate("document.getElementById('html-root').classList.contains('dark')")
    body_bg = page.evaluate("window.getComputedStyle(document.body).backgroundColor")
    print(f"Dark mode: {dark}, Body: {body_bg}")

    # Hover on Articles using Playwright's real mouse hover
    articles_link = page.locator('nav a').filter(has_text='Articles')
    print(f"Articles link found: {articles_link.count() > 0}")

    bg_before = articles_link.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Articles bg BEFORE hover: {bg_before}")

    articles_link.hover()
    page.wait_for_timeout(200)

    bg_after = articles_link.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Articles bg AFTER hover: {bg_after}")

    # Also hover on Dashboard
    dash_link = page.locator('nav a').filter(has_text='Dashboard')
    dash_hover_bg = dash_link.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Dashboard bg BEFORE hover: {dash_hover_bg}")

    dash_link.hover()
    page.wait_for_timeout(200)
    dash_hover_after = dash_link.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Dashboard bg AFTER hover: {dash_hover_after}")

    # Screenshot with current hover state
    page.screenshot(path="screenshots_dark/nav_hover.png")

    # Also check the Course active state
    course_link = page.locator('nav a').filter(has_text='Course')
    course_bg = course_link.evaluate("el => window.getComputedStyle(el).backgroundColor")
    print(f"Course (active) bg: {course_bg}")

    browser.close()
