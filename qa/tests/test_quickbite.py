import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page, expect, sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STARTUP_TIMEOUT_SECONDS = 30


@pytest.fixture(scope="session")
def app_url(tmp_path_factory):
    """Run a copy of the app against a fresh, temporary SQLite database."""
    app_dir = tmp_path_factory.mktemp("quickbite-app")
    for filename in ("app.py", "db.py"):
        shutil.copy2(PROJECT_ROOT / filename, app_dir / filename)
    for directory in ("templates", "static"):
        shutil.copytree(PROJECT_ROOT / directory, app_dir / directory)

    subprocess.run(
        [sys.executable, "db.py"],
        cwd=app_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "from app import app; "
                f"app.run(host='127.0.0.1', port={port}, "
                "debug=False, use_reloader=False)"
            ),
        ],
        cwd=app_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"

    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                raise RuntimeError(f"QuickBite test server exited early:\n{output}")
            try:
                with urlopen(base_url, timeout=1):
                    break
            except (OSError, URLError):
                time.sleep(0.25)
        else:
            process.terminate()
            output, _ = process.communicate(timeout=5)
            raise RuntimeError(
                f"QuickBite test server did not start in time:\n{output}"
            )

        yield base_url
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def test_menu_shows_food_and_loads_local_images(page: Page, app_url: str):
    page.goto(app_url, wait_until="domcontentloaded")

    expect(page.locator("header")).to_contain_text("QuickBite")
    expect(page.locator(".card")).to_have_count(10)
    expect(page.get_by_role("heading", name="Pizza")).to_be_visible()
    expect(page.get_by_text("₹199")).to_be_visible()

    images_loaded = page.locator(".card img").evaluate_all(
        "(images) => images.length === 10 && "
        "images.every((image) => image.complete && image.naturalWidth > 0)"
    )
    assert images_loaded, "Every menu item should display its local image."


def test_customer_can_place_order_and_see_it_on_dashboard(
    page: Page, app_url: str
):
    page.goto(app_url, wait_until="domcontentloaded")
    page.locator(".card").filter(has=page.get_by_role("heading", name="Pizza")) \
        .get_by_role("button", name="Order Now").click()

    expect(page.get_by_role("heading", name="🚚 Delivery Details")).to_be_visible()
    expect(page.locator('input[name="food_id"]')).to_have_value("1")
    expect(page.locator('select[name="payment"]')).to_contain_text(
        "Cash on Delivery"
    )
    expect(page.locator('select[name="payment"]')).to_contain_text("PhonePe")

    page.locator('input[name="name"]').fill("QuickBite QA Test Customer")
    page.locator('input[name="phone"]').fill("5550100199")
    page.locator('textarea[name="address"]').fill("42 Test Lane")
    page.locator('select[name="payment"]').select_option(label="Cash on Delivery")
    page.get_by_role("button", name="Place Order").click()

    expect(page.get_by_text("Order Placed Successfully")).to_be_visible()

    page.goto(f"{app_url}/view_orders", wait_until="domcontentloaded")
    expect(page.get_by_role("heading", name="📦 Orders Dashboard")).to_be_visible()
    expect(page.get_by_text("QuickBite QA Test Customer")).to_be_visible()
    expect(page.get_by_text("42 Test Lane")).to_be_visible()
    expect(page.get_by_role("cell", name="Pizza")).to_be_visible()


def test_postman_collection_targets_only_existing_http_routes():
    collection_path = Path(__file__).resolve().parents[1] / "postman" / (
        "QuickBite.postman_collection.json"
    )
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    requests = {
        (
            item["request"]["method"],
            item["request"]["url"]["raw"].replace("{{baseUrl}}", "").split("?")[0],
        )
        for item in collection["item"]
    }

    assert requests == {
        ("GET", "/"),
        ("GET", "/order/1"),
        ("POST", "/submit_order"),
        ("GET", "/view_orders"),
    }
