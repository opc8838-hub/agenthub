"""Focused visual and interaction checks for the consulting service modal."""
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "playwright"
OUTPUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    desktop = browser.new_page(viewport={"width": 1448, "height": 1085})
    errors = []
    desktop.on("pageerror", lambda error: errors.append(str(error)))
    desktop.goto("http://127.0.0.1:4173/?consulting=1", wait_until="networkidle")
    trigger = desktop.locator('.page-shell [data-modal="consulting"]').first
    trigger.click()

    dialog = desktop.locator("#consulting")
    modal = dialog.locator(".consulting-service-modal")
    assert dialog.is_visible()
    modal_box = modal.bounding_box()
    assert 1280 <= modal_box["width"] <= 1310, modal_box
    assert modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert modal.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
    assert dialog.locator(".consulting-option-card").count() == 2
    assert dialog.locator(".consulting-option-card li").count() == 10
    assert dialog.locator(".consulting-service-footer").is_visible()

    artwork = dialog.locator(".consulting-service-art img")
    artwork.evaluate("img => img.decode()")
    assert artwork.evaluate("img => img.complete && img.naturalWidth > 0")
    assert artwork.get_attribute("src") == "assets/consulting-scene-v4.png"
    assert artwork.evaluate('el => getComputedStyle(el).filter === "none"')
    assert dialog.locator(".consulting-service-art").evaluate(
        'el => getComputedStyle(el, "::before").animationName === "consulting-art-glow"'
    )

    close_button = dialog.locator(".consulting-close")
    assert "close-animated.svg" in close_button.evaluate(
        "el => getComputedStyle(el).backgroundImage"
    )
    assert close_button.locator(".icon").evaluate(
        'el => getComputedStyle(el).opacity === "0"'
    )
    assert close_button.evaluate(
        'el => getComputedStyle(el).backgroundColor === "rgb(245, 247, 250)"'
    )
    desktop.wait_for_timeout(800)
    desktop.screenshot(
        path=str(OUTPUT / "consulting-modal-desktop.png"), animations="disabled"
    )

    dialog.locator(".consulting-booking").click()
    assert desktop.locator("#contact").is_visible()
    desktop.keyboard.press("Escape")
    assert desktop.locator("#contact").is_hidden()

    compact = browser.new_page(viewport={"width": 1308, "height": 931})
    compact.goto("http://127.0.0.1:4173/?consulting=compact", wait_until="networkidle")
    compact.locator('.page-shell [data-modal="consulting"]').first.click()
    compact_dialog = compact.locator("#consulting")
    compact_modal = compact_dialog.locator(".consulting-service-modal")
    assert compact_dialog.is_visible()
    assert compact_modal.evaluate("el => el.scrollHeight <= el.clientHeight")
    assert compact_modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    compact_art = compact_dialog.locator(".consulting-service-art img").bounding_box()
    compact_cards = compact_dialog.locator(".consulting-option-grid").bounding_box()
    compact.screenshot(
        path=str(OUTPUT / "consulting-modal-compact.png"), animations="disabled"
    )
    assert compact_art["y"] + compact_art["height"] <= compact_cards["y"] + 1
    assert compact_dialog.locator(".consulting-service-footer").is_visible()
    compact.close()

    mobile = browser.new_page(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
    )
    mobile.goto("http://127.0.0.1:4173/?consulting=mobile", wait_until="networkidle")
    mobile.locator('.page-shell [data-modal="consulting"]').first.click()
    mobile_dialog = mobile.locator("#consulting")
    mobile_modal = mobile_dialog.locator(".consulting-service-modal")
    assert mobile_dialog.is_visible()
    assert mobile_dialog.locator(".consulting-option-grid").evaluate(
        "el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1"
    )
    assert mobile_dialog.locator(".consulting-service-art img").is_visible()
    assert mobile_modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth")
    mobile.screenshot(
        path=str(OUTPUT / "consulting-modal-mobile.png"), animations="disabled"
    )
    mobile.keyboard.press("Escape")
    assert mobile_dialog.is_hidden()

    browser.close()
    assert not errors, errors
    print(
        "PASS: consulting modal layout, artwork motion, animated close control, "
        "responsive overflow, nested contact flow, and keyboard close"
    )
    print("Previews: " + str(OUTPUT))
