"""Regression check: the primary community CTA must open the redesigned showcase."""
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview"
PREVIEW.mkdir(exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("http://127.0.0.1:4173/?intro-regression=1", wait_until="networkidle")

    trigger = page.locator('.chapter-community [data-modal="intro"]')
    assert trigger.count() == 1
    trigger.click()

    dialog = page.locator("#intro")
    modal = dialog.locator(".community-showcase-modal")
    assert dialog.is_visible()
    assert modal.count() == 1
    assert dialog.locator("#intro-title").inner_text() == "碳基社区"
    assert dialog.locator(".community-agent").get_attribute("src") == "assets/community-agent.jpg"
    assert dialog.locator(".community-metric-card").count() == 3
    assert dialog.locator(".community-talent-roles").get_attribute("src") == "assets/community-talents.png"
    assert dialog.locator(".community-moment-grid img").count() == 2
    assert modal.evaluate("el => el.scrollHeight <= el.clientHeight")
    page.wait_for_timeout(850)
    page.screenshot(path=str(PREVIEW / "intro-community-showcase.png"), animations="disabled")

    page.keyboard.press("Escape")
    page.locator('.chapter-social [data-modal="community"]').click()
    social_dialog = page.locator("#community")
    assert social_dialog.is_visible()
    assert social_dialog.locator(".community-offer-modal").count() == 1
    assert social_dialog.locator("#community-modal-title").inner_text() == "AI 实战社群与工具库"
    assert not errors, errors
    browser.close()
    print("PASS: primary community CTA opens the redesigned, non-scrolling showcase")
