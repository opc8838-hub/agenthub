"""Focused visual and interaction checks for the leader profile modal."""
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
    desktop.goto("http://127.0.0.1:4173/?leader=1", wait_until="networkidle")
    desktop.locator("#chapter-leader").scroll_into_view_if_needed()
    chapter_detail = desktop.locator("#chapter-leader .chapter-detail")
    award_leading = chapter_detail.locator(".leader-award-leading")
    award_line = chapter_detail.locator(".leader-award-line")
    assert award_line.evaluate(
        "el => el.getBoundingClientRect().top > el.parentElement.getBoundingClientRect().top + 1"
    )
    assert award_leading.inner_text().endswith("服务商经验 ·")
    assert award_line.inner_text() == "两次 黑客松 Agent 赛道第一名"
    assert award_line.evaluate('el => getComputedStyle(el).whiteSpace === "nowrap"')
    award_accents = award_line.locator(".leader-award-accent")
    assert award_accents.all_inner_texts() == ["两次", "第一名"]
    assert award_accents.first.evaluate("el => getComputedStyle(el).color") == desktop.locator(
        "#chapter-leader .blue-text"
    ).evaluate("el => getComputedStyle(el).color")
    desktop.screenshot(
        path=str(OUTPUT / "leader-section-copy.png"), animations="disabled"
    )
    desktop.locator('.page-shell [data-modal="leader"]').first.click()

    dialog = desktop.locator("#leader")
    modal = dialog.locator(".leader-profile-modal")
    assert dialog.is_visible()
    desktop_box = modal.bounding_box()
    print("desktop modal:", desktop_box)
    assert desktop_box["width"] >= 1320, desktop_box
    assert modal.evaluate("el => el.scrollWidth <= el.clientWidth")
    assert modal.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
    assert dialog.locator(".leader-profile-card").count() == 2
    assert dialog.locator(".leader-profile-card li").count() == 10
    assert not dialog.locator(".leader-profile-summary").inner_text().startswith("我是黎健堂，")
    expected_award = "两次 黑客松 Agent 赛道第一名"
    assert dialog.locator(".leader-profile-experience li").last.inner_text() == expected_award
    chapter_award_text = " ".join(
        desktop.locator("#chapter-leader .chapter-detail").inner_text().split()
    )
    assert chapter_award_text.endswith(expected_award)
    experience_accent = dialog.locator(".leader-profile-experience").evaluate(
        "el => getComputedStyle(el).getPropertyValue('--card-accent').trim()"
    )
    directions_accent = dialog.locator(".leader-profile-directions").evaluate(
        "el => getComputedStyle(el).getPropertyValue('--card-accent').trim()"
    )
    assert experience_accent != directions_accent
    assert dialog.locator(".leader-profile-directions .leader-agent-crop").count() == 1
    assert "｜" not in dialog.locator(".leader-profile-heading p").inner_text()
    title_width = dialog.locator(".leader-profile-name h2").bounding_box()["width"]
    mark_width = dialog.locator(".leader-title-mark").bounding_box()["width"]
    assert abs(title_width - mark_width) < 1, (title_width, mark_width)
    cutout = dialog.locator(".leader-agent-crop img")
    assert cutout.get_attribute("src") == "assets/leader-agent-cutout-v2.png"
    assert cutout.evaluate("img => img.complete && img.naturalWidth > 0")
    assert cutout.evaluate(
        """img => {
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            const context = canvas.getContext('2d');
            context.drawImage(img, 0, 0);
            return context.getImageData(0, 0, 1, 1).data[3] === 0;
        }"""
    )

    for image in dialog.locator("img").all():
        image.evaluate("img => img.decode()")
        assert image.evaluate("img => img.complete && img.naturalWidth > 0")

    close_button = dialog.locator(".close")
    assert "close-animated.svg" in close_button.evaluate(
        "el => getComputedStyle(el).backgroundImage"
    )
    assert close_button.locator(".icon").evaluate(
        'el => getComputedStyle(el).opacity === "0"'
    )
    desktop.wait_for_timeout(800)
    desktop.screenshot(
        path=str(OUTPUT / "leader-modal-desktop.png"), animations="disabled"
    )
    desktop.keyboard.press("Escape")
    assert dialog.is_hidden()

    for width, height in ((1407, 987), (1440, 900), (1024, 900)):
        compact = browser.new_page(viewport={"width": width, "height": height})
        compact.goto(
            f"http://127.0.0.1:4173/?leader=compact-{height}",
            wait_until="networkidle",
        )
        compact.locator('.page-shell [data-modal="leader"]').first.click()
        compact_dialog = compact.locator("#leader")
        compact_modal = compact.locator("#leader .leader-profile-modal")
        dialog_box = compact_dialog.bounding_box()
        assert dialog_box["y"] >= 0 and dialog_box["y"] + dialog_box["height"] <= height + 1, (
            width,
            height,
            dialog_box,
        )
        assert compact_modal.evaluate("el => el.scrollHeight <= el.clientHeight + 1"), (
            width,
            height,
            compact_modal.evaluate("el => [el.clientHeight, el.scrollHeight]"),
        )
        assert compact_modal.evaluate("el => el.scrollWidth <= el.clientWidth")
        compact.screenshot(
            path=str(OUTPUT / f"leader-modal-{width}x{height}.png"),
            animations="disabled",
        )
        compact.close()

    mobile = browser.new_page(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
    )
    mobile.goto("http://127.0.0.1:4173/?leader=mobile", wait_until="networkidle")
    mobile.locator('.page-shell [data-modal="leader"]').first.click()
    mobile_dialog = mobile.locator("#leader")
    assert mobile_dialog.is_visible()
    assert mobile_dialog.locator(".leader-profile-cards").evaluate(
        "el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1"
    )
    assert mobile_dialog.locator(".leader-agent-crop").is_hidden()
    assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth")
    mobile.screenshot(
        path=str(OUTPUT / "leader-modal-mobile.png"), animations="disabled"
    )

    browser.close()
    assert not errors, errors
    print("PASS: leader modal layout, imagery, close animation, interaction, and responsive overflow")
