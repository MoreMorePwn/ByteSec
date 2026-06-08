"""Take dark mode screenshots of all ByteSec pages."""
import sys, os

sys.path.insert(0, r'C:\Users\FRTX\ByteSec')
os.chdir(r'C:\Users\FRTX\ByteSec')

from playwright.sync_api import sync_playwright

pages = {
    'index': '/',
    'login': '/login',
    'register': '/register',
    'dashboard': '/dashboard',
    'course': '/course',
    'leaderboard': '/leaderboard',
    'admin_docker': '/admin/docker',
    'lesson': '/lesson/1',
}
base_url = 'http://127.0.0.1:5008'
out_dir = r'C:\Users\FRTX\ByteSec\screenshots_dark'
os.makedirs(out_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()

    # First login to see authenticated pages
    page.goto(f'{base_url}/login', wait_until='networkidle')
    page.fill('input[name="username"]', 'demo')
    page.fill('input[name="password"]', 'demo123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

    # Enable dark mode
    page.evaluate("""
        localStorage.setItem('bytesec-theme', 'dark');
        document.getElementById('html-root').classList.add('dark');
    """)
    page.wait_for_timeout(500)

    results = {}
    for page_name, path in pages.items():
        try:
            url = f'{base_url}{path}'
            page.goto(url, wait_until='networkidle', timeout=15000)
            # Re-ensure dark mode after navigation
            page.evaluate("""
                localStorage.setItem('bytesec-theme', 'dark');
                var html = document.getElementById('html-root');
                if (html) html.classList.add('dark');
            """)
            page.wait_for_timeout(500)
            screenshot_path = os.path.join(out_dir, f'{page_name}.png')
            page.screenshot(path=screenshot_path, full_page=True)
            results[page_name] = screenshot_path
            print(f'OK {page_name}: {screenshot_path}')
        except Exception as e:
            print(f'FAIL {page_name}: {e}')

    browser.close()

print(f'\nDone. Screenshots in: {out_dir}')
print(f'Captured: {list(results.keys())}')
