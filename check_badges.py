"""Check computed CSS colors of dashboard badges after dark mode."""
import sys, os
sys.path.insert(0, r'C:\Users\FRTX\ByteSec')
os.chdir(r'C:\Users\FRTX\ByteSec')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()

    # Login
    page.goto('http://127.0.0.1:5008/login', wait_until='networkidle')
    page.fill('input[name="username"]', 'demo')
    page.fill('input[name="password"]', 'demo123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

    # Navigate to dashboard
    page.goto('http://127.0.0.1:5008/dashboard', wait_until='networkidle')

    # Enable dark mode
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        const html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)

    # Check the badge elements
    result = page.evaluate("""() => {
        const out = [];
        // Find all absolute-positioned badge divs at top of card headers
        const badges = document.querySelectorAll('div[class*="absolute"][class*="top-3"]');
        badges.forEach((el, i) => {
            const cs = getComputedStyle(el);
            out.push({
                index: i,
                text: el.textContent.trim().substring(0, 30),
                bgColor: cs.backgroundColor,
                color: cs.color,
                classes: el.className.substring(0, 80)
            });
        });

        // Also check card elements using surface-container-lowest
        const allCards = document.querySelectorAll('[class*="bg-surface-container-lowest"]');
        allCards.forEach((el, i) => {
            const cs = getComputedStyle(el);
            out.push({
                index: 100 + i,
                element: el.tagName,
                classes: el.className.substring(0, 80),
                bgColor: cs.backgroundColor,
                textContent: el.textContent.trim().substring(0, 40)
            });
        });

        return JSON.stringify(out, null, 2);
    }""")
    
    print("=== BADGE COLORS ===")
    print(result)

    # Take fresh screenshot
    page.screenshot(path=r'C:\Users\FRTX\ByteSec\screenshots_dark\dashboard_fresh.png', full_page=True)
    print("\nFresh screenshot saved!")
    
    browser.close()
