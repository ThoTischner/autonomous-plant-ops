"""Browser end-to-end test — guards against browser-console errors.

Runs against the live stack over the Docker network:
  - dashboard-frontend (nginx, serves SPA + proxies /api/)

Asserts the dashboard loads and the Control Panel works WITHOUT any
console errors, page errors or failed/4xx-5xx requests.
"""
import pytest
from playwright.sync_api import sync_playwright

FRONTEND = "http://dashboard-frontend:80/"


@pytest.fixture(scope="module")
def page_session():
    console: list[tuple[str, str]] = []
    page_errors: list[str] = []
    req_failed: list[str] = []
    http_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console.append((m.type, m.text)))
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("requestfailed",
                lambda r: req_failed.append(f"{r.method} {r.url} :: {r.failure}"))
        page.on(
            "response",
            lambda r: http_errors.append(f"{r.status} {r.url}")
            if r.status >= 400 else None,
        )

        page.goto(FRONTEND, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(4000)

        # Exercise the Control Panel.
        page.get_by_text("Thermal Runaway").click(timeout=8000)
        page.wait_for_timeout(2000)
        page.get_by_text("Normalzustand wiederherstellen").click(timeout=8000)
        page.wait_for_timeout(2000)
        textarea = page.locator("textarea")
        textarea.fill(textarea.input_value() + "\n# e2e marker")
        page.get_by_text("Speichern", exact=True).click(timeout=8000)
        page.wait_for_timeout(3000)

        browser.close()

    return {
        "console": console,
        "page_errors": page_errors,
        "req_failed": req_failed,
        "http_errors": http_errors,
    }


def test_no_page_errors(page_session):
    assert page_session["page_errors"] == [], \
        f"Browser page errors: {page_session['page_errors']}"


def test_no_console_errors(page_session):
    errors = [t for t in page_session["console"] if t[0] == "error"]
    assert errors == [], f"Console errors: {errors}"


def test_no_failed_requests(page_session):
    assert page_session["req_failed"] == [], \
        f"Failed requests: {page_session['req_failed']}"


def test_no_http_error_responses(page_session):
    assert page_session["http_errors"] == [], \
        f"HTTP >=400 responses: {page_session['http_errors']}"
