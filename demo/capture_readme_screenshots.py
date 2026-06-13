from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_BASE_URL = "http://127.0.0.1:5009"
DEFAULT_USERNAME = "demo"
DEFAULT_PASSWORD = "demo123"
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 960}


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


def resolve_targets() -> dict[str, object]:
    from bytesec import create_app
    from bytesec.models import Article, CommunityChallenge, LessonStep
    from bytesec.seed import ensure_database

    app = create_app({"TESTING": True})
    with app.app_context():
        ensure_database()
        article = Article.query.order_by(Article.id).first()
        challenge = CommunityChallenge.query.order_by(CommunityChallenge.id).first()
        if article is None or challenge is None:
            raise RuntimeError("Expected demo article and community challenge data to exist.")

        lessons = {}
        for kind in ("mcq", "predict", "fitb", "spot", "flag"):
            step = LessonStep.query.filter_by(kind=kind).order_by(LessonStep.id).first()
            if step is None:
                raise RuntimeError(f"Could not find a lesson step for kind={kind}.")
            lessons[kind] = step.lesson_id

        return {
            "article_slug": article.slug,
            "challenge_id": challenge.id,
            "lessons": lessons,
        }


def goto(page: Page, url: str, pause_ms: int = 1200) -> None:
    page.goto(url, wait_until="networkidle")
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(pause_ms)


def capture(page: Page, name: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(
        path=str(SCREENSHOT_DIR / f"{name}.jpg"),
        type="jpeg",
        quality=78,
        full_page=False,
    )


def login(page: Page, base_url: str, username: str, password: str) -> None:
    goto(page, f"{base_url}/login")
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.locator('button[type="submit"]').click()
    page.wait_for_url("**/dashboard")
    page.wait_for_timeout(1200)


def capture_public_pages(page: Page, base_url: str) -> None:
    for path, name in (
        ("/", "landing"),
        ("/login", "login"),
        ("/register", "register"),
    ):
        goto(page, f"{base_url}{path}")
        capture(page, name)


def capture_authenticated_pages(page: Page, base_url: str, targets: dict[str, object]) -> None:
    lessons = targets["lessons"]
    article_slug = targets["article_slug"]
    challenge_id = targets["challenge_id"]

    pages = [
        ("/dashboard", "dashboard"),
        ("/course", "course-catalog"),
        ("/course/web", "course-track-web"),
        (f"/lesson/{lessons['mcq']}", "lesson-mcq"),
        (f"/lesson/{lessons['predict']}", "lesson-predict"),
        (f"/lesson/{lessons['fitb']}", "lesson-fitb"),
        (f"/lesson/{lessons['spot']}", "lesson-spot"),
        (f"/lesson/{lessons['flag']}", "lesson-flag"),
        ("/leaderboard", "leaderboard"),
        ("/articles", "articles"),
        (f"/articles/{article_slug}", "article-detail"),
        ("/articles/new", "article-new"),
        ("/community", "community"),
        (f"/community/{challenge_id}", "community-detail"),
        ("/community/submit", "community-submit"),
        ("/submissions", "submissions"),
        ("/profile", "profile"),
        ("/admin/docker", "admin-docker"),
        ("/admin/community", "admin-community"),
        ("/admin/articles", "admin-articles"),
    ]

    for path, name in pages:
        goto(page, f"{base_url}{path}")
        capture(page, name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture README screenshots for ByteSec.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="ByteSec base URL")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Login username")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Login password")
    parser.add_argument("--start-app", action="store_true", help="Start the Flask app automatically")
    parser.add_argument("--headed", action="store_true", help="Run with a visible browser window")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    port = int(base_url.rsplit(":", 1)[1])
    targets = resolve_targets()
    app_process = maybe_start_app(base_url, port, args.start_app)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed)
            context = browser.new_context(viewport=VIEWPORT)
            page = context.new_page()

            capture_public_pages(page, base_url)
            login(page, base_url, args.username, args.password)
            capture_authenticated_pages(page, base_url, targets)

            context.close()
            browser.close()
    finally:
        if app_process is not None:
            app_process.terminate()
            try:
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()

    print(f"Saved screenshots to {SCREENSHOT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
