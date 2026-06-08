from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "http://127.0.0.1:5009"
DEFAULT_USERNAME = "demo"
DEFAULT_PASSWORD = "demo123"
DEFAULT_FLAG = "BYTESEC{196f5dee6f071643}"


def wait_for_server(base_url: str, timeout: float = 45.0) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(base_url, timeout=3)
            if response.ok:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"Server at {base_url} did not become ready: {last_error}")


def maybe_start_app(base_url: str, port: int, start_app: bool) -> Optional[subprocess.Popen[str]]:
    if not start_app:
        wait_for_server(base_url)
        return None

    env = os.environ.copy()
    env.setdefault("BYTESEC_PORT", str(port))
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    wait_for_server(base_url)
    return process


def pause(page: Page, seconds: float) -> None:
    page.wait_for_timeout(int(seconds * 1000))


def click_if_visible(page: Page, selector: str, timeout: int = 1500) -> bool:
    locator = page.locator(selector)
    try:
        locator.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError:
        return False
    locator.click()
    return True


def safe_click(page: Page, selector: str, pause_seconds: float = 1.0, index: int = 0) -> None:
    page.locator(selector).nth(index).click()
    pause(page, pause_seconds)


def login(page: Page, base_url: str, username: str, password: str) -> None:
    page.goto(base_url, wait_until="networkidle")
    pause(page, 1.5)
    safe_click(page, 'a[href="/login"]', index=1)
    page.locator('input[name="username"]').fill(username)
    pause(page, 0.5)
    page.locator('input[name="password"]').fill(password)
    pause(page, 0.5)
    safe_click(page, 'button[type="submit"]', 1.5)
    page.wait_for_url("**/dashboard")


def visit_main_pages(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")
    pause(page, 1.5)
    safe_click(page, '#theme-toggle-btn', 1.0)
    safe_click(page, '#theme-toggle-btn', 1.0)
    page.mouse.wheel(0, 1400)
    pause(page, 1.0)
    page.mouse.wheel(0, -1400)
    pause(page, 1.0)


def visit_authenticated_sections(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/dashboard", wait_until="networkidle")
    pause(page, 2.0)

    page.goto(f"{base_url}/leaderboard", wait_until="networkidle")
    pause(page, 2.0)

    page.goto(f"{base_url}/admin/docker", wait_until="networkidle")
    pause(page, 2.0)

    for category in ("web", "rev", "crypto"):
        page.goto(f"{base_url}/course?cat={category}", wait_until="networkidle")
        pause(page, 1.5)
        page.mouse.wheel(0, 900)
        pause(page, 0.8)
        page.mouse.wheel(0, -900)
        pause(page, 0.8)


def answer_current_step(page: Page, flag_value: str) -> None:
    kind = page.locator("#activity-container").get_attribute("data-kind")
    pause(page, 1.0)
    click_if_visible(page, '#hint-btn', 1200)
    pause(page, 1.0)

    if kind in {"mcq", "predict"}:
        correct_answer = page.evaluate("CORRECT_ANSWER")
        selector = f'.mcq-option[data-option-id="{correct_answer}"]'
        safe_click(page, selector, 0.8)
    elif kind == "fitb":
        correct_answer = page.evaluate("CORRECT_ANSWER")
        if isinstance(correct_answer, list):
            answer_text = correct_answer[0]
        else:
            answer_text = correct_answer
        page.locator("#fitb-input").fill(str(answer_text))
        pause(page, 0.8)
    elif kind == "spot":
        correct_answer = page.evaluate("CORRECT_ANSWER")
        selector = f'.code-line[data-line="{correct_answer}"]'
        safe_click(page, selector, 0.8)
    elif kind == "flag":
        page.locator("#fitb-input").fill(flag_value)
        pause(page, 0.8)
    else:
        raise RuntimeError(f"Unsupported step kind: {kind}")

    safe_click(page, '#check-btn', 1.6)
    page.locator('#feedback-area').wait_for(state='visible', timeout=5000)
    pause(page, 1.2)

    if click_if_visible(page, '#continue-btn', 2500):
        pause(page, 1.8)
        return

    if click_if_visible(page, 'a:has-text("Next Lesson")', 2500):
        pause(page, 1.8)
        return

    if click_if_visible(page, 'a:has-text("Course Complete!")', 2500):
        pause(page, 1.8)
        return

    raise RuntimeError("Could not find a continue button after answering the step.")


def run_lesson_sequence(page: Page, base_url: str, flag_value: str) -> None:
    lesson_paths = [
        "/lesson/2",   # predict
        "/lesson/3",   # fitb
        "/lesson/7",   # spot
        "/lesson/43",  # rev predict + mcq
        "/lesson/45",  # rev fitb + spot
        "/lesson/56",  # crypto mcq
        "/lesson/68",  # flag lab
    ]

    for path in lesson_paths:
        page.goto(f"{base_url}{path}", wait_until="networkidle")
        pause(page, 2.0)

        while page.locator("#activity-container").count() > 0:
            answer_current_step(page, flag_value)
            current_path = page.url.replace(base_url, "")
            if current_path != path:
                break

        pause(page, 1.0)


def logout(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/dashboard", wait_until="networkidle")
    pause(page, 1.0)
    safe_click(page, f'a[href="/logout"]', 1.5)
    page.wait_for_url("**/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recordable ByteSec demo flow")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="ByteSec base URL")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Login username")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Login password")
    parser.add_argument("--flag", default=DEFAULT_FLAG, help="Known demo flag for the EzSQLi lesson")
    parser.add_argument("--slow-mo", type=int, default=350, help="Playwright slow motion in ms")
    parser.add_argument("--pause", type=float, default=0.9, help="Extra pause multiplier placeholder")
    parser.add_argument("--headed", action="store_true", help="Run with a visible browser window")
    parser.add_argument("--start-app", action="store_true", help="Start the Flask app automatically")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    port = int(base_url.rsplit(":", 1)[1])
    app_process = maybe_start_app(base_url, port, args.start_app)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed, slow_mo=args.slow_mo)
            context = browser.new_context(viewport={"width": 1440, "height": 960})
            page = context.new_page()

            visit_main_pages(page, base_url)
            login(page, base_url, args.username, args.password)
            visit_authenticated_sections(page, base_url)
            run_lesson_sequence(page, base_url, args.flag)
            page.goto(f"{base_url}/course?cat=web", wait_until="networkidle")
            pause(page, 1.5)
            page.goto(f"{base_url}/dashboard", wait_until="networkidle")
            pause(page, 1.5)
            logout(page, base_url)

            context.close()
            browser.close()
    finally:
        if app_process is not None:
            app_process.terminate()
            try:
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()

    print("ByteSec demo flow completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
