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
    assert videos.count() == 7
    assert dialog.locator(".product-poster").count() == 7
    assert dialog.locator(".product-showcase-card").count() == 7
    assert dialog.locator('.product-showcase-card[target="_blank"]').count() == 7
    assert modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert dialog.locator(".products-service-panel").is_visible()

    desktop.wait_for_function(
        """() => [...document.querySelectorAll('#products .product-video')]
        .every(video => video.readyState >= 2 && !video.paused && !video.loop && video.muted)""",
        timeout=15000,
    )
    video_states = videos.evaluate_all(
        "videos => videos.map(video => ({src: video.currentSrc, width: video.videoWidth, height: video.videoHeight, ready: video.readyState, paused: video.paused}))"
    )
    assert all(state["width"] > 0 and state["height"] > 0 for state in video_states), video_states
    assert videos.evaluate_all(
        "videos => videos.every(video => getComputedStyle(video).objectFit === 'cover')"
    )

    first_video = videos.first
    first_media = first_video.locator("xpath=..").first
    first_video.evaluate("video => video.dispatchEvent(new Event('ended'))")
    assert first_video.evaluate("video => video.paused")
    assert "is-playing" not in (first_media.get_attribute("class") or "")
    desktop.wait_for_timeout(1000)
    assert first_video.evaluate("video => video.paused")
    desktop.wait_for_timeout(700)
    assert not first_video.evaluate("video => video.paused")
    assert "is-playing" in (first_media.get_attribute("class") or "")
    desktop.screenshot(
        path=str(OUTPUT / "products-modal-desktop.png"), animations="disabled"
    )

    dialog.locator(".products-close").click()
    assert dialog.is_hidden()
    assert videos.evaluate_all(
        "videos => videos.every(video => video.paused && video.currentTime === 0)"
    )

    compact = browser.new_page(viewport={"width": 1440, "height": 900})
    compact.on("pageerror", lambda error: errors.append(str(error)))
    compact.goto("http://127.0.0.1:4173/?products=compact", wait_until="networkidle")
    compact.locator('.page-shell [data-modal="products"]').first.click()
    compact_dialog = compact.locator("#products")
    compact_modal = compact_dialog.locator(".products-showcase-modal")
    compact_service = compact_dialog.locator(".products-service-panel")
    assert compact_dialog.is_visible()
    assert compact_modal.evaluate("el => el.scrollHeight <= el.clientHeight")
    assert compact_modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    modal_box = compact_modal.bounding_box()
    service_box = compact_service.bounding_box()
    assert service_box["y"] + service_box["height"] <= modal_box["y"] + modal_box["height"]
    bottom_gap = modal_box["y"] + modal_box["height"] - (service_box["y"] + service_box["height"])
    assert bottom_gap <= 24, bottom_gap
    assert compact_dialog.locator(".product-card-copy").evaluate_all(
        "copies => copies.every(copy => copy.scrollHeight <= copy.clientHeight + 1)"
    )
    compact.wait_for_timeout(1700)
    compact.screenshot(
        path=str(OUTPUT / "products-modal-desktop-compact.png"),
        animations="disabled",
    )
    compact.close()

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
    mobile_service = mobile_dialog.locator(".products-service-panel")
    mobile_service.scroll_into_view_if_needed()
    assert mobile_service.evaluate(
        "el => getComputedStyle(el).backgroundColor === 'rgba(0, 0, 0, 0)'"
    )
    assert mobile_service.evaluate("el => getComputedStyle(el).boxShadow === 'none'")
    agent = mobile_service.locator(".products-contact-area img")
    assert agent.evaluate("img => img.complete && img.naturalWidth > 0")
    mobile.screenshot(
        path=str(OUTPUT / "products-modal-mobile-service.png"),
        animations="disabled",
        full_page=False,
    )

    browser.close()
    assert not errors, errors
    print("PASS: products modal layout, seven linked videos, 1.5s cover loop, close reset, and responsive overflow")
    print("Previews: " + str(OUTPUT))
