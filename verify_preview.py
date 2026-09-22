"""Render local previews and exercise same-page dialog behavior."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'preview'
OUTPUT.mkdir(exist_ok=True)
CLOSE_ASSET = ROOT / 'assets' / 'close-animated.svg'
COMMUNITY_IMAGE_ASSETS = [
    ROOT / 'assets' / 'community-trae-friends.png',
    ROOT / 'assets' / 'community-agi-meetup.png',
]
COMMUNITY_QR_ASSET = ROOT / 'assets' / 'community-wechat-qr-green.jpg'
assert CLOSE_ASSET.exists()
assert all(asset.exists() for asset in COMMUNITY_IMAGE_ASSETS)
assert COMMUNITY_QR_ASSET.exists()
close_svg = CLOSE_ASSET.read_text(encoding='utf-8')
assert 'stroke: #2b2a33' in close_svg
assert 'baseFrequency="0.055"' in close_svg
assert 'scale="4"' in close_svg
assert 'dur="0.64s"' in close_svg
assert 'animation:draw 0.70s' in close_svg

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:4173/?v=30', wait_until='networkidle')
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('document.fonts.ready')
    assert page.locator('.scene-image').first.evaluate('(img) => img.complete && img.naturalWidth > 0')
    assert page.locator('.mascot-caption').count() == 0
    assert page.locator('.scene-image').count() == 7
    assert page.locator('.title-spark').count() == 7
    assert page.locator('.chapter-title-wrap.spark-left').count() == 4
    assert page.locator('.chapter-title-wrap.spark-right').count() == 3
    assert page.locator('#i-doodle-spark').count() == 1
    assert page.locator('#i-chevron-up').count() == 1
    assert page.locator('#i-chevron-down').count() == 1
    assert page.locator('#i-chip').count() == 1
    assert page.locator('.modal-layer').count() == 9
    assert page.locator('.close').count() == 9
    assert all(header.evaluate(
        '(el) => getComputedStyle(el).borderBottomWidth === "0px"'
    ) for header in page.locator('.modal-top').all())
    english_modal_kickers = page.locator(
        '#plans .modal-kicker, #courses .modal-kicker, '
        '#community .modal-kicker, #products .modal-kicker, '
        '#consulting .modal-kicker, #contact .modal-kicker'
    )
    assert page.locator('#intro .modal-kicker').count() == 0
    assert english_modal_kickers.count() == 5
    assert all(not kicker.is_visible() for kicker in english_modal_kickers.all())
    assert page.locator('.brand-chip use[href="#i-chip"]').count() == 1
    assert page.locator('#doodle-boil').count() == 1
    assert page.locator('#chevron-boil').count() == 1
    assert page.locator('text=。').count() == 0
    scene_sources = page.locator('.scene-image').evaluate_all('(images) => images.map((img) => img.src)')
    assert sum('-scene-v4.png' in src for src in scene_sources) == 6
    assert sum('products-scene-v5.png' in src for src in scene_sources) == 1
    assert page.locator('.action-label').count() == 7
    assert page.locator('.product-title-underline').count() == 1
    assert page.locator('#courses-home-title br').count() == 1
    assert page.locator('#courses-home-title .course-accent').inner_text() == '成长'
    assert page.locator('.site-nav button').count() == 8
    assert page.locator('.site-nav').is_visible()
    assert page.locator('.mobile-nav-toggle').count() == 1
    assert page.locator('.mobile-nav-toggle').is_hidden()
    assert page.locator('.mobile-topic-menu button').count() == 8
    assert page.locator('.mobile-topic-menu').is_hidden()
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
        modal = dialog.locator('.modal')
        assert float(modal.evaluate('(el) => parseFloat(getComputedStyle(el).borderRadius)')) >= 20
        assert modal.evaluate('(el) => getComputedStyle(el).backgroundImage === "none"')
        close_button = dialog.locator('.close')
        assert close_button.evaluate('(el) => getComputedStyle(el).backgroundImage === "none"')
        assert close_button.locator('.icon').evaluate('(el) => getComputedStyle(el).opacity === "1"')
        for button in dialog.locator('.inside-button').all():
            if topic == 'community':
                assert button.evaluate('(el) => getComputedStyle(el).backgroundColor === "rgb(23, 100, 245)"')
                assert button.evaluate('(el) => getComputedStyle(el).color === "rgb(255, 255, 255)"')
            else:
                assert button.evaluate('(el) => getComputedStyle(el).backgroundColor === "rgb(23, 100, 245)"')
            assert float(button.evaluate('(el) => parseFloat(getComputedStyle(el).borderRadius)')) >= 20
        if topic == 'intro':
            intro_title = dialog.locator('#intro-title')
            assert 'modal-top' in intro_title.evaluate('(el) => el.parentElement.className')
            assert intro_title.evaluate('(el) => getComputedStyle(el).translate === "8px 14px"')
            assert abs(modal.bounding_box()['width'] - 1100) < 1
            assert dialog.locator('.modal-intro').bounding_box()['y'] - modal.bounding_box()['y'] < 170
            assert dialog.locator('.modal-top').evaluate(
                '(el) => getComputedStyle(el).borderBottomWidth === "0px"'
            )
            gallery_images = dialog.locator('.community-gallery img')
            assert gallery_images.count() == 2
            for image in gallery_images.all():
                image.evaluate('(img) => img.decode()')
                assert image.evaluate('(img) => img.complete && img.naturalWidth > 0')
                assert image.get_attribute('alt')
                assert float(image.evaluate('(el) => parseFloat(getComputedStyle(el).borderRadius)')) >= 20
            image_boxes = [image.bounding_box() for image in gallery_images.all()]
            assert image_boxes[0]['x'] < image_boxes[1]['x']
            assert all(box['width'] / box['height'] >= 1.7 for box in image_boxes)
            gallery_box = dialog.locator('.community-gallery').bounding_box()
            body_box = dialog.locator('.community-modal-body').bounding_box()
            assert gallery_box['width'] >= body_box['width'] * .9
            assert abs((gallery_box['x'] - body_box['x']) - (
                body_box['x'] + body_box['width'] - gallery_box['x'] - gallery_box['width']
            )) < 2
            assert dialog.locator('.community-purpose').bounding_box()['y'] < image_boxes[0]['y']
            assert dialog.locator('.community-metric').all_inner_texts() == ['2000+', '40+']
            assert all(metric.evaluate(
                '(el) => getComputedStyle(el).color === "rgb(23, 100, 245)"'
            ) for metric in dialog.locator('.community-metric').all())
            page.screenshot(path=str(OUTPUT / 'intro-modal.png'), animations='disabled')
        if topic == 'leader':
            dialog.locator('.profile-portrait').evaluate('(img) => img.decode()')
            page.screenshot(path=str(OUTPUT / 'leader-modal.png'), animations='disabled')
        if topic == 'community':
            assert dialog.locator('.modal-kicker').count() == 0
            counts = dialog.locator('.community-category-list strong').all_inner_texts()
            assert len(counts) == 9
            assert sum(int(''.join(character for character in value if character.isdigit())) for value in counts) == 28
            assert counts == ['10 个', '4 个', '3 个', '3 个', '1 个', '1 个', '2 个', '3 个', '1 个']
            assert dialog.locator('.community-category-icon').count() == 9
            assert dialog.locator('.community-category-track').count() == 0
            assert dialog.locator('.community-summary-card strong').all_inner_texts() == ['28', '9']
            summary_numbers = [item.bounding_box() for item in dialog.locator('.community-summary-card strong').all()]
            summary_labels = [item.bounding_box() for item in dialog.locator('.community-summary-card span').all()]
            assert abs(summary_numbers[0]['y'] - summary_numbers[1]['y']) < 1
            assert abs(summary_labels[0]['y'] - summary_labels[1]['y']) < 1
            assert all(card.evaluate(
                '(el) => getComputedStyle(el.querySelector("div")).flexWrap === "nowrap"'
            ) for card in dialog.locator('.community-summary-card').all())
            assert dialog.locator('.community-price strong').inner_text() == '¥99'
            assert dialog.locator('.community-price del').inner_text() == '原价 ¥199'
            qr = dialog.locator('.community-qr img')
            qr.evaluate('(img) => img.decode()')
            assert qr.evaluate('(img) => img.complete && img.naturalWidth === 651 && img.naturalHeight === 642')
            assert qr.get_attribute('src') == 'assets/community-wechat-qr-green.jpg'
            agent = dialog.locator('.community-peek-agent')
            agent.evaluate('(img) => img.decode()')
            assert agent.evaluate('(img) => img.complete && img.naturalWidth === 1062 && img.naturalHeight === 1481')
            assert agent.get_attribute('src') == 'assets/community-peek-agent.png'
            assert agent.evaluate('(img) => getComputedStyle(img).top === "90px"')
            assert dialog.locator('img').count() == 2
            assert dialog.locator('.community-price').evaluate(
                '(el) => getComputedStyle(el).alignItems === "center" && getComputedStyle(el).textAlign === "center"'
            )
            join_copy_box = dialog.locator('.community-join-copy').bounding_box()
            join_qr_box = dialog.locator('.community-qr').bounding_box()
            assert abs(join_copy_box['width'] - join_qr_box['width']) < 2
            qr_box = qr.bounding_box()
            qr_caption_box = dialog.locator('.community-qr figcaption').bounding_box()
            assert dialog.locator('.community-qr figcaption span').all_inner_texts() == ['微信扫码添加 ·', '非支付码']
            qr_group_center = (qr_box['x'] + qr_caption_box['x'] + qr_caption_box['width']) / 2
            qr_half_center = join_qr_box['x'] + join_qr_box['width'] / 2
            assert qr_box['width'] >= 120
            assert qr_group_center >= qr_half_center + 8
            assert dialog.locator('.community-category-list li').nth(7).locator('use').get_attribute('href') == '#i-chat'
            assert page.locator('symbol#i-chat circle').count() == 4
            assert '非支付码' in qr.get_attribute('alt')
            assert '社群服务' in dialog.inner_text()
            assert '近 2000 个' in dialog.inner_text()
            assert '实用工具库' in dialog.inner_text()
            assert '已逐项扫描本地开源技能与工具目录' not in dialog.inner_text()
            assert '标记为“原创”' not in dialog.inner_text()
            assert '这是黎健堂的微信二维码' not in dialog.inner_text()
            assert close_button.evaluate('(el) => getComputedStyle(el).outlineStyle === "none"')
            assert modal.evaluate('(el) => el.scrollHeight <= el.clientHeight + 1')
            page.screenshot(path=str(OUTPUT / 'community-modal.png'), animations='disabled')
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
        page.wait_for_timeout(120)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
        if width == 390:
            page.screenshot(path=str(OUTPUT / 'mobile-full.png'), full_page=True)
            page.screenshot(path=str(OUTPUT / 'mobile-first-screen.png'))
            assert page.locator('.site-nav').is_hidden()
            assert page.locator('.mobile-nav-toggle').is_visible()
            assert page.locator('.mobile-nav-chevron-down').is_visible()
            assert page.locator('.mobile-nav-chevron-up').is_hidden()
            assert page.locator('.mobile-nav-chevron-down').evaluate(
                '(el) => getComputedStyle(el).animationName === "none" && getComputedStyle(el).filter === "none"'
            )
            assert page.locator('.mobile-current-topic').inner_text() == '社区介绍'
            title_y = page.locator('#chapter-community .chapter-title').bounding_box()['y']
            page.locator('.mobile-nav-toggle').click()
            mobile_menu = page.locator('.mobile-topic-menu')
            assert mobile_menu.is_visible()
            assert page.locator('.mobile-nav-toggle').get_attribute('aria-expanded') == 'true'
            assert page.locator('.mobile-nav-chevron-down').is_hidden()
            assert page.locator('.mobile-nav-chevron-up').is_visible()
            assert mobile_menu.bounding_box()['height'] <= 140
            assert all(button.is_visible() for button in mobile_menu.locator('button').all())
            assert abs(page.locator('#chapter-community .chapter-title').bounding_box()['y'] - title_y) < 1
            assert mobile_menu.locator('[data-scroll="chapter-community"]').get_attribute('aria-current') == 'true'
            page.screenshot(path=str(OUTPUT / 'mobile-nav-open.png'))
            page.keyboard.press('Escape')
            assert mobile_menu.is_hidden()
            assert page.locator('.mobile-nav-toggle').get_attribute('aria-expanded') == 'false'
            assert page.locator('.mobile-nav-chevron-down').is_visible()
            assert page.locator('.mobile-nav-chevron-up').is_hidden()
            assert page.locator('.mobile-nav-toggle').evaluate('(button) => button === document.activeElement')
            page.locator('.mobile-nav-toggle').click()
            mobile_menu.locator('[data-scroll="chapter-courses"]').click()
            page.wait_for_timeout(120)
            assert mobile_menu.is_hidden()
            assert page.locator('.mobile-current-topic').inner_text() == '成长课程'
            assert page.locator('.mobile-topic-menu [data-scroll="chapter-courses"]').get_attribute('aria-current') == 'true'
            page.locator('.mobile-nav-toggle').click()
            page.mouse.click(4, 300)
            assert mobile_menu.is_hidden()
            page.locator('.mobile-nav-toggle').click()
            page.dispatch_event('body', 'touchmove')
            page.wait_for_timeout(80)
            assert mobile_menu.is_hidden()
            page.locator('.mobile-nav-toggle').click()
            assert mobile_menu.is_visible()
            mobile_menu.locator('[data-modal="contact"]').click()
            assert mobile_menu.is_hidden()
            assert page.locator('#contact').is_visible()
            page.keyboard.press('Escape')
            page.locator('.page-shell [data-modal="intro"]').click()
            mobile_gallery_images = page.locator('#intro .community-gallery img')
            assert mobile_gallery_images.count() == 2
            mobile_image_boxes = [image.bounding_box() for image in mobile_gallery_images.all()]
            assert mobile_image_boxes[0]['y'] < mobile_image_boxes[1]['y']
            assert all(box['width'] < width for box in mobile_image_boxes)
            assert all(box['width'] / box['height'] >= 1.7 for box in mobile_image_boxes)
            page.screenshot(path=str(OUTPUT / 'mobile-intro.png'), animations='disabled')
            page.keyboard.press('Escape')
            page.locator('.page-shell [data-modal="community"]').click()
            mobile_community = page.locator('#community')
            assert mobile_community.is_visible()
            assert mobile_community.locator('.community-category-list').evaluate(
                '(el) => getComputedStyle(el).gridTemplateColumns.split(" ").length === 1'
            )
            assert mobile_community.locator('.community-qr img').bounding_box()['width'] <= 240
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(OUTPUT / 'mobile-community.png'), animations='disabled')
            page.keyboard.press('Escape')
            page.locator('.page-shell [data-modal="products"]').click()
            assert page.locator('#products').is_visible()
            assert page.locator('#products .modal').evaluate('(el) => el.scrollHeight > el.clientHeight')
            assert float(page.locator('#products .modal').evaluate('(el) => parseFloat(getComputedStyle(el).borderRadius)')) >= 18
            assert page.locator('#products .modal').bounding_box()['width'] < width
            page.screenshot(path=str(OUTPUT / 'mobile-products.png'), animations='disabled')
            page.keyboard.press('Escape')
            page.locator('#chapter-leader').scroll_into_view_if_needed()
            page.wait_for_timeout(120)
            leader_title_box = page.locator('#leader-home-title').bounding_box()
            leader_spark_box = page.locator('.chapter-leader .title-spark').bounding_box()
            assert leader_spark_box['x'] >= leader_title_box['x'] + leader_title_box['width'] - 6
            assert leader_spark_box['x'] + leader_spark_box['width'] <= width
            page.screenshot(path=str(OUTPUT / 'mobile-leader.png'))
    compact_desktop = browser.new_page(viewport={'width': 1200, 'height': 900}, device_scale_factor=1)
    compact_desktop.goto('http://127.0.0.1:4173/?v=32', wait_until='networkidle')
    compact_desktop.locator('.page-shell [data-modal="community"]').click()
    compact_community = compact_desktop.locator('#community .community-offer-modal')
    compact_desktop.locator('#community .community-qr img').evaluate('(img) => img.decode()')
    compact_desktop.screenshot(path=str(OUTPUT / 'community-modal-1200x900.png'), animations='disabled')
    assert compact_community.evaluate('(el) => el.scrollHeight <= el.clientHeight + 1')
    assert compact_community.bounding_box()['height'] <= 860
    compact_desktop.close()
    assert not errors, errors
    motion_page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    motion_page.goto('http://127.0.0.1:4173/?v=30', wait_until='networkidle')
    motion_page.locator('.page-shell [data-modal="intro"]').click()
    assert 'close-animated.svg' in motion_page.locator('#intro .close').evaluate(
        '(el) => getComputedStyle(el).backgroundImage'
    )
    assert motion_page.locator('#intro .close .icon').evaluate(
        '(el) => getComputedStyle(el).opacity === "0"'
    )
    motion_page.wait_for_timeout(800)
    motion_page.screenshot(path=str(OUTPUT / 'modal-motion.png'))
    motion_page.keyboard.press('Escape')
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
    mobile_motion_page.goto('http://127.0.0.1:4173/?v=30', wait_until='networkidle')
    assert mobile_motion_page.locator('.mobile-nav-chevron-down').is_visible()
    assert mobile_motion_page.locator('.mobile-nav-chevron-down').evaluate(
        '(el) => getComputedStyle(el).filter !== "none" && getComputedStyle(el).animationName === "chevron-nudge"'
    )
    assert mobile_motion_page.locator('#i-chevron-down .doodle-chevron-stroke').evaluate(
        '(el) => getComputedStyle(el).animationName === "chevron-draw"'
    )
    chevron_samples = []
    for _ in range(6):
        chevron_samples.append(mobile_motion_page.locator('.mobile-nav-chevron-down').evaluate(
            '(el) => getComputedStyle(el).translate'
        ))
        mobile_motion_page.wait_for_timeout(80)
    assert len(set(chevron_samples)) >= 3, chevron_samples
    mobile_motion_page.locator('.mobile-nav-toggle').click()
    assert mobile_motion_page.locator('.mobile-nav-chevron-down').is_hidden()
    assert mobile_motion_page.locator('.mobile-nav-chevron-up').is_visible()
    mobile_motion_page.locator('.mobile-nav-toggle').click()
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
    print('PASS: 7 code-built topics, compact two-row mobile navigation, 7 generated scene layers, readable typography, 9 dialogs, navigation scrolling, keyboard controls, desktop and mobile motion, reduced-motion fallback, no external navigation, 5 responsive widths, no JS errors.')
    print('Previews: ' + str(OUTPUT))
