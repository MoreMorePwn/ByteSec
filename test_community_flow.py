"""Take screenshots of community challenge pages + test submit flow."""
import sys, os
sys.path.insert(0, r'C:\Users\FRTX\ByteSec')
os.chdir(r'C:\Users\FRTX\ByteSec')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    base = 'http://127.0.0.1:5008'
    out = r'C:\Users\FRTX\ByteSec\screenshots_dark'

    # Login as demo
    page.goto(f'{base}/login', wait_until='networkidle')
    page.fill('input[name="username"]', 'demo')
    page.fill('input[name="password"]', 'demo123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)

    # 1. Community listing page
    page.goto(f'{base}/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/community_list.png', full_page=True)
    print('OK community_list')

    # 2. Submit challenge page
    page.goto(f'{base}/community/submit', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/community_submit.png', full_page=True)
    print('OK community_submit')

    # 3. Actually submit a test challenge
    page.fill('input[name="title"]', 'Test SQLi Challenge')
    page.select_option('select[name="category"]', 'web')
    page.select_option('select[name="difficulty"]', 'easy')
    page.fill('input[name="points"]', '150')
    page.fill('input[name="flag"]', 'BYTECSEC{test_flag_123}')
    page.fill('textarea[name="description"]', 'A simple SQL injection challenge to test the community feature.')
    page.fill('textarea[name="hint"]', 'Try using a single quote to break the query.')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    print('Test challenge submitted!')

    # 4. Check it appears on community page (should be hidden since pending)
    page.goto(f'{base}/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/community_after_submit.png', full_page=True)
    print('OK community after_submit')

    # 5. Admin community page - approve it
    # Login as demo user which is admin
    page.goto(f'{base}/admin/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/admin_community.png', full_page=True)
    print('OK admin_community')

    # Check if there's a pending challenge to approve
    pending = page.query_selector('text=Test SQLi Challenge')
    if pending:
        print('✓ Found pending test challenge')
        # Click Approve button
        approve_btn = page.query_selector('button:has-text("Approve")')
        if approve_btn:
            approve_btn.click()
            page.wait_for_load_state('networkidle')
            print('✓ Challenge approved!')
            # Re-apply dark mode
            page.evaluate("""() => {
                localStorage.setItem('bytesec-theme', 'dark');
                var html = document.getElementById('html-root');
                if (html) html.classList.add('dark');
            }""")
            page.wait_for_timeout(500)
            page.screenshot(path=f'{out}/admin_community_approved.png', full_page=True)
        else:
            print('✗ No Approve button found')
    else:
        print('✗ No pending test challenge found')
        # Screenshot current state
        page.screenshot(path=f'{out}/admin_community_state.png', full_page=True)

    # 6. Check community page now shows approved challenge
    page.goto(f'{base}/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/community_with_challenge.png', full_page=True)
    print('OK community_with_challenge')

    # 7. Check challenge detail page
    # Find the link to the challenge
    page.goto(f'{base}/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)

    # Try clicking the challenge card
    challenge_link = page.query_selector('text=Test SQLi Challenge')
    if challenge_link:
        challenge_link.click()
        page.wait_for_load_state('networkidle')
        page.evaluate("""() => {
            localStorage.setItem('bytesec-theme', 'dark');
            var html = document.getElementById('html-root');
            if (html) html.classList.add('dark');
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path=f'{out}/community_challenge_detail.png', full_page=True)
        print('OK challenge_detail')
    else:
        print('✗ Challenge not found on community page')

    browser.close()
    print('\nDone!')
