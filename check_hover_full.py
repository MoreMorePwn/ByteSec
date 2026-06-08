from playwright.sync_api import sync_playwright

def run_tests():
    from collections import Counter
    results = Counter()

    def hover_test(desc, loc):
        import time
        try:
            if loc.count() == 0:
                print(f"  [SKIP] {desc:35s} - element not found")
                return
            bg_before = loc.evaluate("el => window.getComputedStyle(el).backgroundColor")
            loc.hover()
            time.sleep(0.2)
            bg_after = loc.evaluate("el => window.getComputedStyle(el).backgroundColor")
            bright = "255," in bg_after or "243," in bg_after or "250," in bg_after
            status = "BRIGHT!" if bright else "OK"
            print(f"  {desc:35s} {bg_before:30s} -> {bg_after:30s} [{status}]")
            results["pass" if not bright else "fail"] += 1
        except Exception as e:
            print(f"  [ERR]  {desc:35s} - {e}")
            results["fail"] += 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # Login + dark mode
        page.goto("http://127.0.0.1:5008/login")
        page.fill("input[name=username]", "demo")
        page.fill("input[name=password]", "demo123")
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.setItem('bytesec-theme', 'dark')")
        page.reload()
        page.wait_for_load_state("networkidle")
        dm = page.evaluate('document.getElementById("html-root").classList.contains("dark")')
        print(f"Dark mode: {dm}")
        print()

        # Tests
        nav = page.locator('nav')

        hover_test("Nav Dashboard",      nav.locator('a').filter(has_text='Dashboard'))
        hover_test("Nav Course",         nav.locator('a').filter(has_text='Course'))
        hover_test("Nav Leaderboard",    nav.locator('a').filter(has_text='Leaderboard'))
        hover_test("Nav Community",      nav.locator('a').filter(has_text='Community'))
        hover_test("Nav Articles",       nav.locator('a').filter(has_text='Articles'))
        hover_test("Theme toggle btn",   page.locator('#theme-toggle-btn'))
        hover_test("Logout button",      nav.locator('a').filter(has_text='demo'))

        # Lesson page
        page.goto("http://127.0.0.1:5008/course")
        page.wait_for_load_state("networkidle")
        first = page.locator('a[href*="lesson/"]').first
        if first.count() > 0:
            first.click()
            page.wait_for_load_state("networkidle")
            hbtn = page.locator('button#hint-btn')
            hover_test("Hint button", hbtn)

        # Admin community
        page.goto("http://127.0.0.1:5008/admin/community")
        page.wait_for_load_state("networkidle")
        admin_tr = page.locator('tbody tr').first
        hover_test("Admin community row", admin_tr)

        # Admin articles
        page.goto("http://127.0.0.1:5008/admin/articles")
        page.wait_for_load_state("networkidle")
        art_tr = page.locator('tbody tr').first
        hover_test("Admin articles row", art_tr)

        pub_btn = page.locator('a[href*="toggle-publish"]').first
        hover_test("Admin publish btn", pub_btn)

        print()
        print("=" * 40)
        pf = results.get("pass", 0)
        ff = results.get("fail", 0)
        print(f"Results: PASS={pf}, FAIL={ff}")
        if ff == 0 and pf > 0:
            print("ALL hover states dark-mode OK!")
        elif ff > 0:
            print(f"WARNING: {ff} hover states still have bright colors!")

        page.screenshot(path="screenshots_dark/hover_final.png")
        browser.close()

run_tests()
