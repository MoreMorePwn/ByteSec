"""Fresh screenshot of submit form with file upload."""
import sys, os
sys.path.insert(0, r'C:\Users\FRTX\ByteSec')
os.chdir(r'C:\Users\FRTX\ByteSec')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    page.goto('http://127.0.0.1:5008/login', wait_until='networkidle')
    page.fill('input[name="username"]', 'demo')
    page.fill('input[name="password"]', 'demo123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    page.goto('http://127.0.0.1:5008/community/submit', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=r'C:\Users\FRTX\ByteSec\screenshots_dark\community_submit_file.png', full_page=True)
    print('OK')
    browser.close()
