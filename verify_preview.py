"""Render local previews and exercise same-page dialog behavior."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'preview'
OUTPUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:4173/?v=26', wait_until='networkidle')
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('document.fonts.ready')
    assert page.locator('.scene-image').first.evaluate('(img) => img.complete && img.naturalWidth > 0')
    assert page.locator('.mascot-caption').count() == 0
    assert page.locator('.scene-image').count() == 7
    assert page.locator('.title-spark').count() == 7
    assert page.locator('.chapter-title-wrap.spark-left').count() == 4
    assert page.locator('.chapter-title-wrap.spark-right').count() == 3
    assert page.locator('#i-doodle-spark').count() == 1
    assert page.locator('#i-chip').count() == 1
    assert page.locator('.brand-chip use[href="#i-chip"]').count() == 1
    assert page.locator('#doodle-boil').count() == 1
    assert page.locator('text=。').count() == 0
    scene_sources = page.locator('.scene-image').evaluate_all('(images) => images.map((img) => img.src)')
    assert sum('-scene-v4.png' in src for src in scene_sources) == 6
    assert sum('products-scene-v5.png' in src for src in scene_sources) == 1
    assert page.locator('.action-label').count() == 7
    assert page.locator('.product-title-underline').count() == 1
    assert page.locator('#courses-home-title br').count() == 1
    assert page.locator('#courses-home-title .course-accent').inner_text() == '成长'
    assert page.locator('.site-nav button').count() == 8
    assert abs(page.locator('.nav-inner').bounding_box()['width'] - 1320) < 1
    assert page.locator('.nav-inner').bounding_box()['width'] < page.locator('.chapter-inner').first.bounding_box()['width']
    assert page.locator('.site-nav [data-scroll="chapter-leader"]').inner_text() == '负责人'
    assert page.locator('.site-nav .nav-contact').inner_text().strip() == '联系'
    assert page.evaluate("document.fonts.check('500 16px CommunityCN')")
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUTPUT / 'desktop-full.png'), full_page=True)
    page.screenshot(path=str(OUTPUT / 'desktop-first-screen.png'))
    assert page.locator('main > .chapter').count() == 7
    expected_titles = {
        'chapter-programs': '长期计划',
        'chapter-leader': '负责人 / 主讲老师',
        'chapter-courses': '课程成长路线',
        'chapter-social': 'AI 实战社群',
        'chapter-products': '产品与定制开发',
        'chapter-consulting': '咨询与 1V1 陪跑',
    }
    for section_id, expected_title in expected_titles.items():
        section = page.locator('#' + section_id)
        heading = section.locator('h2')
        assert ''.join(heading.inner_text().split()) == ''.join(expected_title.split())
        assert heading.evaluate('(el) => parseFloat(getComputedStyle(el).fontSize) >= 46')
    for section in page.locator('main > .chapter').all():
        assert section.bounding_box()['height'] >= 912
        section.evaluate('(el) => el.scrollIntoView({behavior:"instant"})')
        page.wait_for_timeout(80)
        for image in section.locator('.scene-image').all():
            image.evaluate('(img) => img.decode()')
            assert image.evaluate('(img) => img.complete && img.naturalWidth > 0')
        section_id = section.get_attribute('id')
        page.screenshot(path=str(OUTPUT / (section_id + '.png')))
        assert section.locator('.chapter-lead').evaluate('(el) => parseFloat(getComputedStyle(el).fontSize) >= 20')
    for action in page.locator('.chapter-action').all():
        label = action.locator('.action-label')
        assert label.bounding_box()['width'] < action.bounding_box()['width']
    initial_url = page.url
    for topic in ['intro', 'plans', 'leader', 'courses', 'community', 'products', 'consulting', 'contact']:
        trigger = page.locator('.page-shell [data-modal="' + topic + '"]').first
        trigger.click()
        dialog = page.locator('#' + topic)
        assert dialog.is_visible(), topic
        if topic == 'leader':
            dialog.locator('.profile-portrait').evaluate('(img) => img.decode()')
            page.screenshot(path=str(OUTPUT / 'leader-modal.png'), animations='disabled')
        assert page.evaluate('document.querySelector(".page-shell").inert')
        page.keyboard.press('Shift+Tab')
        assert dialog.evaluate('(d) => d.contains(document.activeElement)')
        page.keyboard.press('Escape')
        assert not dialog.is_visible()
        assert trigger.evaluate('(b) => b === document.activeElement')
        assert page.url == initial_url
    page.locator('.page-shell [data-modal="plans"]').click()
    page.locator('#plans [data-modal="contact"]').click()
    assert page.locator('#contact').is_visible()
    page.keyboard.press('Escape')
    assert page.locator('.chapter-programs .chapter-action').evaluate('(b) => b === document.activeElement')
    page.locator('.site-nav [data-scroll="chapter-courses"]').click()
    assert page.url == initial_url
    assert abs(page.locator('#chapter-courses').bounding_box()['y'] - 88) < 3
    page.locator('.page-shell [data-modal="courses"]').click()
    page.screenshot(path=str(OUTPUT / 'courses-modal.png'), animations='disabled')
    page.mouse.click(5, 5)
    assert page.locator('#courses').is_hidden()
    for width in [390, 375, 320, 768, 1024]:
        page.set_viewport_size({'width': width, 'height': 844})
        page.evaluate('scrollTo(0,0)')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
        if width == 390:
            page.screenshot(path=str(OUTPUT / 'mobile-full.png'), full_page=True)
            page.screenshot(path=str(OUTPUT / 'mobile-first-screen.png'))
            page.locator('.page-shell [data-modal="products"]').click()
            assert page.locator('#products').is_visible()
            assert page.locator('#products .modal').evaluate('(el) => el.scrollHeight > el.clientHeight')
            page.screenshot(path=str(OUTPUT / 'mobile-products.png'), animations='disabled')
            page.keyboard.press('Escape')
    assert not errors, errors
    motion_page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    motion_page.goto('http://127.0.0.1:4173/?v=26', wait_until='networkidle')
    motion_page.locator('.site-nav [data-scroll="chapter-programs"]').hover()
    assert motion_page.locator('.site-nav [data-scroll="chapter-programs"]').evaluate(
        '(el) => getComputedStyle(el, "::after").animationName === "doodle-line-nudge"'
    )
    assert motion_page.locator('.brand-chip').evaluate(
        '(el) => getComputedStyle(el).animationName === "doodle-nudge" && getComputedStyle(el).filter !== "none"'
    )
    assert motion_page.locator('.product-title-underline').evaluate(
        '(el) => getComputedStyle(el).animationName === "none" && getComputedStyle(el).filter === "none"'
    )
    arrow = motion_page.locator('.chapter-community .chapter-action .icon')
    samples = []
    for _ in range(5):
        samples.append(arrow.evaluate('(el) => getComputedStyle(el).translate'))
        motion_page.wait_for_timeout(120)
    assert len(set(samples)) > 1, samples
    motion_page.close()
    mobile_motion_page = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    mobile_motion_page.goto('http://127.0.0.1:4173/?v=26', wait_until='networkidle')
    mobile_arrow = mobile_motion_page.locator('.chapter-community .chapter-action .icon')
    mobile_samples = []
    for _ in range(5):
        mobile_samples.append(mobile_arrow.evaluate('(el) => getComputedStyle(el).translate'))
        mobile_motion_page.wait_for_timeout(120)
    assert len(set(mobile_samples)) > 1, mobile_samples
    assert mobile_motion_page.locator('.chapter-community .title-spark').evaluate(
        '(el) => getComputedStyle(el).animationName === "spark-breathe"'
    )
    mobile_motion_page.locator('#chapter-social').evaluate('(el) => el.scrollIntoView({behavior:"instant"})')
    mobile_motion_page.wait_for_timeout(200)
    assert mobile_motion_page.locator('#chapter-social').evaluate('(el) => el.classList.contains("is-active")')
    assert mobile_motion_page.locator('#chapter-social .scene-image').evaluate(
        '(el) => getComputedStyle(el).animationName === "scene-breathe"'
    )
    mobile_motion_page.close()
    browser.close()
    print('PASS: 7 code-built topics, centered compact navigation, 7 generated scene layers, readable typography, 8 dialogs, navigation scrolling, keyboard controls, desktop and mobile motion, reduced-motion fallback, no external navigation, 5 responsive widths, no JS errors.')
    print('Previews: ' + str(OUTPUT))
