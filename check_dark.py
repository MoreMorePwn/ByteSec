from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()

    page.goto("http://127.0.0.1:5008/login")
    page.evaluate("localStorage.setItem('bytesec-theme', 'dark')")
    page.goto("http://127.0.0.1:5008/")
    page.wait_for_load_state("networkidle")

    dark = page.evaluate("document.getElementById('html-root').classList.contains('dark')")
    print(f"Dark mode: {dark}")

    body_bg = page.evaluate("window.getComputedStyle(document.body).backgroundColor")
    print(f"Body bg: {body_bg}")

    # Check gradient overlay
    grad = page.evaluate("""
        const el = document.querySelector('.bg-gradient-to-b');
        el ? window.getComputedStyle(el).background.substring(0, 120) : 'no gradient'
    """)
    print(f"Gradient overlay: {grad}")

    # Check grid pattern
    grid = page.evaluate("""
        const s = window.getComputedStyle(document.querySelector('section'));
        s ? s.backgroundImage.substring(0, 100) : 'none'
    """)
    print(f"Grid pattern: {grid}")

    # Check stats cards
    card_bg = page.evaluate("""
        const c = document.querySelectorAll('.grid-cols-4 .bg-surface-container-lowest');
        c.length > 0 ? window.getComputedStyle(c[0]).backgroundColor : 'no cards'
    """)
    print(f"Stats card bg: {card_bg}")

    # Check track cards
    track_bg = page.evaluate("""
        const c = document.querySelectorAll('.grid-cols-5 .bg-surface-container-lowest');
        c.length > 0 ? window.getComputedStyle(c[0]).backgroundColor : 'no tracks'
    """)
    print(f"Track card bg: {track_bg}")

    page.screenshot(path="screenshots_dark/homepage_dark_fixed.png", full_page=True)
    print("Screenshot saved: homepage_dark_fixed.png")
    browser.close()
