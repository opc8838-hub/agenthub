"""Focused visual, responsive, and playback checks for the products modal."""
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "playwright"
OUTPUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    errors = []

    desktop = browser.new_page(viewport={"width": 1448, "height": 1086})
    desktop.on("pageerror", lambda error: errors.append(str(error)))
    desktop.goto("http://127.0.0.1:4173/?products=desktop", wait_until="networkidle")
    desktop.locator('.page-shell [data-modal="products"]').first.click()

    dialog = desktop.locator("#products")
    modal = dialog.locator(".products-showcase-modal")
    videos = dialog.locator(".product-video")
    assert dialog.is_visible()
    assert videos.count() == 6
    assert dialog.locator(".product-poster").count() == 6
    assert dialog.locator(".product-showcase-card").count() == 7
    assert modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert dialog.locator(".products-service-panel").is_visible()

    desktop.wait_for_function(
        """() => [...document.querySelectorAll('#products .product-video')]
        .every(video => video.readyState >= 2 && !video.paused && video.loop && video.muted)""",
        timeout=15000,
    )
    video_states = videos.evaluate_all(
        "videos => videos.map(video => ({src: video.currentSrc, width: video.videoWidth, height: video.videoHeight, ready: video.readyState, paused: video.paused}))"
    )
    assert all(state["width"] > 0 and state["height"] > 0 for state in video_states), video_states
    assert videos.evaluate_all(
        "videos => videos.every(video => getComputedStyle(video).objectFit === 'cover')"
    )
    desktop.screenshot(
        path=str(OUTPUT / "products-modal-desktop.png"), animations="disabled"
    )

    dialog.locator(".products-close").click()
    assert dialog.is_hidden()
    assert videos.evaluate_all(
        "videos => videos.every(video => video.paused && video.currentTime === 0)"
    )

    mobile = browser.new_page(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
    )
    mobile.on("pageerror", lambda error: errors.append(str(error)))
    mobile.goto("http://127.0.0.1:4173/?products=mobile", wait_until="networkidle")
    mobile.locator('.page-shell [data-modal="products"]').first.click()
    mobile_dialog = mobile.locator("#products")
    mobile_modal = mobile_dialog.locator(".products-showcase-modal")
    assert mobile_dialog.is_visible()
    mobile.wait_for_function(
        """() => [...document.querySelectorAll('#products .product-media:has(.product-video)')]
        .every(media => media.classList.contains('is-playing'))""",
        timeout=15000,
    )
    assert mobile_dialog.locator(".products-gallery").evaluate(
        "el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1"
    )
    assert mobile_modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth")
    mobile.screenshot(
        path=str(OUTPUT / "products-modal-mobile.png"), animations="disabled",
        full_page=False,
    )

    browser.close()
    assert not errors, errors
    print("PASS: products modal layout, six looping videos, close reset, and responsive overflow")
    print("Previews: " + str(OUTPUT))
