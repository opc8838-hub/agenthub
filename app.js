(() => {
  const dialogs = [...document.querySelectorAll('.modal-layer')];
  const page = document.querySelector('.page-shell');
  const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
  const mobileTopicMenu = document.querySelector('.mobile-topic-menu');
  const mobileCurrentTopic = document.querySelector('.mobile-current-topic');
  const mobileTopicNames = {
    'chapter-community': '社区介绍',
    'chapter-programs': '长期计划',
    'chapter-leader': '负责人',
    'chapter-courses': '成长课程',
    'chapter-social': '实战社群',
    'chapter-products': '开发定制',
    'chapter-consulting': '咨询服务'
  };
  let active = null;
  let opener = null;
  let mobileNavOpen = false;
  const focusable = 'button:not([disabled]), input, textarea, select, a[href], [tabindex="0"]';
  const coverHoldDuration = 1500;
  const productVideoTimers = new WeakMap();

  function clearProductVideoTimer(video) {
    const timer = productVideoTimers.get(video);
    if (timer) clearTimeout(timer);
    productVideoTimers.delete(video);
  }

  function holdCoverThenPlay(video) {
    clearProductVideoTimer(video);
    video.pause();
    try { video.currentTime = 0; } catch {}
    video.closest('.product-media')?.classList.remove('is-playing');

    const timer = setTimeout(() => {
      productVideoTimers.delete(video);
      if (active?.id !== 'products' || document.hidden) return;
      video.muted = true;
      const playback = video.play();
      if (playback) playback.catch(() => {});
    }, coverHoldDuration);
    productVideoTimers.set(video, timer);
  }

  document.querySelectorAll('.product-video').forEach(video => {
    video.addEventListener('playing', () => {
      video.closest('.product-media')?.classList.add('is-playing');
    });
    video.addEventListener('ended', () => holdCoverThenPlay(video));
  });

  function startProductVideos(dialog) {
    if (dialog?.id !== 'products') return;
    dialog.querySelectorAll('.product-video').forEach(video => {
      const source = video.querySelector('source[data-src]');
      if (source && !source.src) {
        source.src = source.dataset.src;
        video.load();
      }
      holdCoverThenPlay(video);
    });
  }

  function stopProductVideos(dialog, reset = false) {
    if (dialog?.id !== 'products') return;
    dialog.querySelectorAll('.product-video').forEach(video => {
      clearProductVideoTimer(video);
      video.pause();
      if (reset) {
        video.currentTime = 0;
        video.closest('.product-media')?.classList.remove('is-playing');
      }
    });
  }

  function setMobileNav(open, restoreFocus = false) {
    if (!mobileNavToggle || !mobileTopicMenu || mobileNavOpen === open) return;
    mobileNavOpen = open;
    mobileNavToggle.setAttribute('aria-expanded', String(open));
    mobileTopicMenu.hidden = !open;
    if (!open && restoreFocus) mobileNavToggle.focus({ preventScroll: true });
  }

  function close() {
    if (!active) return;
    stopProductVideos(active, true);
    active.hidden = true;
    active = null;
    page.inert = false;
    document.body.classList.remove('modal-open');
    if (opener?.isConnected) opener.focus({ preventScroll: true });
  }

  function open(id, trigger) {
    const next = dialogs.find(dialog => dialog.id === id);
    if (!next) return;
    if (!active) opener = trigger;
    if (active) {
      stopProductVideos(active);
      active.hidden = true;
    }
    active = next;
    active.hidden = false;
    active.querySelector('.modal').scrollTop = 0;
    document.body.classList.add('modal-open');
    active.querySelector('.close').focus({ preventScroll: true });
    page.inert = true;
    requestAnimationFrame(() => startProductVideos(active));
  }

  document.addEventListener('visibilitychange', () => {
    if (active?.id !== 'products') return;
    if (document.hidden) stopProductVideos(active, true);
    else startProductVideos(active);
  });

  document.addEventListener('click', event => {
    const mobileToggle = event.target.closest('.mobile-nav-toggle');
    if (mobileToggle) {
      setMobileNav(!mobileNavOpen);
      return;
    }
    const scrollButton = event.target.closest('[data-scroll]');
    if (scrollButton) {
      setMobileNav(false);
      close();
      const target = document.getElementById(scrollButton.dataset.scroll);
      if (target) {
        const headerHeight = document.querySelector('.masthead')?.offsetHeight || 0;
        const top = target.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({
          top,
          behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
        });
      }
      return;
    }
    const trigger = event.target.closest('[data-modal]');
    if (trigger) {
      setMobileNav(false);
      open(trigger.dataset.modal, trigger);
      return;
    }
    if (mobileNavOpen && !event.target.closest('.mobile-topic-menu')) setMobileNav(false);
    if (event.target.closest('.close') || event.target === active) close();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobileNavOpen) {
      event.preventDefault();
      setMobileNav(false, true);
      return;
    }
    if (!active) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      close();
    }
    if (event.key === 'Tab') {
      const controls = [...active.querySelectorAll(focusable)];
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  document.querySelector('.copy-wechat').addEventListener('click', async () => {
    const status = document.querySelector('.copy-status');
    try {
      await navigator.clipboard.writeText('allen_8838');
      status.textContent = '已复制微信号：allen_8838';
    } catch {
      status.textContent = '请长按或选中微信号 allen_8838 复制。';
    }
  });

  const chapters = [...document.querySelectorAll('.chapter')];
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function pageScrollTo(top) {
    if (reducedMotion) {
      window.scrollTo({ top, behavior: 'instant' });
      return;
    }
    const start = window.scrollY;
    const distance = top - start;
    const startedAt = performance.now();
    const duration = 360;
    document.documentElement.classList.add('is-wheel-paging');
    function frame(now) {
      const progress = Math.min(1, (now - startedAt) / duration);
      const eased = 1 - Math.pow(1 - progress, 2.3);
      window.scrollTo({ top: start + distance * eased, behavior: 'instant' });
      if (progress < 1) requestAnimationFrame(frame);
      else {
        window.scrollTo({ top, behavior: 'instant' });
        requestAnimationFrame(() => document.documentElement.classList.remove('is-wheel-paging'));
      }
    }
    requestAnimationFrame(frame);
  }

  function prepareTypewriter(element, startDelay, step) {
    if (!element) return 0;
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    let index = 0;
    textNodes.forEach(node => {
      const fragment = document.createDocumentFragment();
      [...node.nodeValue].forEach(character => {
        const span = document.createElement('span');
        span.className = 'type-char';
        span.style.setProperty('--char-delay', `${startDelay + index * step}ms`);
        span.textContent = character;
        fragment.append(span);
        index += 1;
      });
      node.replaceWith(fragment);
    });
    return index;
  }

  if (!reducedMotion) {
    chapters.forEach(section => {
      const titleStart = 100;
      const titleStep = 44;
      const titleCount = prepareTypewriter(section.querySelector('.chapter-title'), titleStart, titleStep);
      const titleUnderline = section.querySelector('.product-title-underline path');
      if (titleUnderline) {
        const titleFinish = titleStart + (titleCount - 1) * titleStep + 150;
        titleUnderline.style.setProperty('--underline-delay', `${titleFinish}ms`);
      }
      const leadDelay = Math.min(600, 160 + titleCount * 38);
      const leadCount = prepareTypewriter(section.querySelector('.chapter-lead'), leadDelay, 17);
      const leadFinish = leadCount > 0 ? leadDelay + (leadCount - 1) * 17 + 150 : 0;
      const actionLineDelay = leadCount > 0 ? leadFinish + 35 : 180;
      section.style.setProperty('--action-line-delay', `${actionLineDelay}ms`);
    });
    page.classList.add('motion-ready');
  }

  function activateChapter(section) {
    if (!section) return;
    chapters.forEach(chapter => chapter.classList.toggle('is-active', chapter === section));
    document.querySelectorAll('.site-nav [data-scroll]').forEach(button => {
      button.setAttribute('aria-current', button.dataset.scroll === section.id ? 'true' : 'false');
    });
    document.querySelectorAll('.mobile-topic-menu [data-scroll]').forEach(button => {
      button.setAttribute('aria-current', button.dataset.scroll === section.id ? 'true' : 'false');
    });
    if (mobileCurrentTopic) mobileCurrentTopic.textContent = mobileTopicNames[section.id] || '社区介绍';
  }

  const observer = new IntersectionObserver(entries => {
    const entering = entries
      .filter(entry => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (entering) activateChapter(entering.target);
  }, { rootMargin: '-22% 0px -48% 0px', threshold: [0, .18, .36] });
  chapters.forEach(section => observer.observe(section));

  const viewportCenter = (document.querySelector('.masthead')?.offsetHeight || 0) + innerHeight * .48;
  const initialChapter = chapters.reduce((nearest, section) => {
    const rect = section.getBoundingClientRect();
    const distance = Math.abs(rect.top + rect.height / 2 - viewportCenter);
    return !nearest || distance < nearest.distance ? { section, distance } : nearest;
  }, null)?.section;
  requestAnimationFrame(() => activateChapter(initialChapter || chapters[0]));
  window.addEventListener('touchmove', () => setMobileNav(false), { passive: true });

  // On desktop, one wheel gesture advances exactly one chapter. Native wheel
  // momentum plus mandatory snap made the previous transition feel delayed.
  let wheelLocked = false;
  window.addEventListener('wheel', event => {
    setMobileNav(false);
    if (innerWidth < 901 || event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY) || Math.abs(event.deltaY) < 12) return;
    if (active || mobileNavOpen) return;

    const direction = event.deltaY > 0 ? 1 : -1;
    let element = event.target instanceof Element ? event.target : null;
    while (element && element !== document.body) {
      const overflowY = getComputedStyle(element).overflowY;
      if ((overflowY === 'auto' || overflowY === 'scroll') && element.scrollHeight > element.clientHeight + 1) {
        const canScroll = direction > 0
          ? element.scrollTop + element.clientHeight < element.scrollHeight - 1
          : element.scrollTop > 0;
        if (canScroll) return;
      }
      element = element.parentElement;
    }

    event.preventDefault();
    if (wheelLocked) return;

    const footer = document.querySelector('.footer');
    const pages = footer ? [...chapters, footer] : chapters;
    const headerHeight = document.querySelector('.masthead')?.offsetHeight || 0;
    const scrollTopFor = page => page === footer
      ? Math.max(0, page.offsetTop + page.offsetHeight - innerHeight)
      : Math.max(0, page.getBoundingClientRect().top + scrollY - headerHeight);
    const currentIndex = pages.reduce((nearestIndex, page, index) => {
      const distance = Math.abs(scrollTopFor(page) - scrollY);
      return index === 0 || distance < Math.abs(scrollTopFor(pages[nearestIndex]) - scrollY) ? index : nearestIndex;
    }, 0);
    const nextPage = pages[currentIndex + direction];
    if (!nextPage) return;

    wheelLocked = true;
    pageScrollTo(scrollTopFor(nextPage));
    window.setTimeout(() => { wheelLocked = false; }, 500);
  }, { passive: false });
  matchMedia('(min-width: 601px)').addEventListener('change', event => {
    if (event.matches) setMobileNav(false);
  });
})();
