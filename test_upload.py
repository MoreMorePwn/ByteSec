"""Test file upload flow for community challenges."""
import sys, os, io
sys.path.insert(0, r'C:\Users\FRTX\ByteSec')
os.chdir(r'C:\Users\FRTX\ByteSec')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    base = 'http://127.0.0.1:5008'
    out = r'C:\Users\FRTX\ByteSec\screenshots_dark'

    # Login
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

    # Create a test file
    test_file = os.path.join(out, 'test_challenge.txt')
    with open(test_file, 'w') as f:
        f.write('This is a test challenge file for ByteSec.\nFlag: BYTECSEC{test_upload_flow}\n')

    # Go to submit page
    page.goto(f'{base}/community/submit', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)

    # Fill form
    page.fill('input[name="title"]', 'Test Upload Challenge')
    page.select_option('select[name="category"]', 'web')
    page.select_option('select[name="difficulty"]', 'medium')
    page.fill('input[name="points"]', '200')
    page.fill('input[name="flag"]', 'BYTECSEC{test_upload_flow}')
    page.fill('textarea[name="description"]', 'A challenge with file upload to test the feature.')
    
    # Upload file
    file_input = page.query_selector('input[name="challenge_file"]')
    if file_input:
        file_input.set_input_files(test_file)
        print('✓ File selected for upload')
    else:
        print('✗ File input not found!')
    
    # Submit
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    print('✓ Form submitted')

    # Screenshot
    page.screenshot(path=f'{out}/community_after_upload_submit.png', full_page=True)

    # Now go to admin and approve
    page.goto(f'{base}/admin/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    page.screenshot(path=f'{out}/admin_community_upload.png', full_page=True)

    # Click approve
    approve_btn = page.query_selector('button:has-text("Approve")')
    if approve_btn:
        approve_btn.click()
        page.wait_for_load_state('networkidle')
        print('✓ Challenge approved!')
        page.evaluate("""() => {
            localStorage.setItem('bytesec-theme', 'dark');
            var html = document.getElementById('html-root');
            if (html) html.classList.add('dark');
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path=f'{out}/admin_community_upload_approved.png', full_page=True)
    else:
        print('✗ No Approve button')
        page.screenshot(path=f'{out}/admin_community_upload_no_approve.png', full_page=True)

    # View challenge detail
    page.goto(f'{base}/community', wait_until='networkidle')
    page.evaluate("""() => {
        localStorage.setItem('bytesec-theme', 'dark');
        var html = document.getElementById('html-root');
        if (html) html.classList.add('dark');
    }""")
    page.wait_for_timeout(500)
    
    ch_link = page.query_selector('text=Test Upload Challenge')
    if ch_link:
        ch_link.click()
        page.wait_for_load_state('networkidle')
        page.evaluate("""() => {
            localStorage.setItem('bytesec-theme', 'dark');
            var html = document.getElementById('html-root');
            if (html) html.classList.add('dark');
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path=f'{out}/community_challenge_with_file.png', full_page=True)
        
        # Check if download link is visible
        download_link = page.query_selector('text=Download')
        if download_link:
            print('✓ Download link visible!')
        else:
            print('✗ Download link not found')
    else:
        print('✗ Challenge not in listing')

    # Clean up test file
    os.remove(test_file)
    
    browser.close()
    print('\nDone!')
