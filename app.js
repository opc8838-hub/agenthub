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

  document.querySelectorAll('.product-video').forEach(video => {
    video.addEventListener('playing', () => {
      video.closest('.product-media')?.classList.add('is-playing');
    });
  });

  function startProductVideos(dialog) {
    if (dialog?.id !== 'products') return;
    dialog.querySelectorAll('.product-video').forEach(video => {
      const source = video.querySelector('source[data-src]');
      if (source && !source.src) {
        source.src = source.dataset.src;
        video.load();
      }
      video.muted = true;
      const playback = video.play();
      if (playback) playback.catch(() => {});
    });
  }

  function stopProductVideos(dialog, reset = false) {
    if (dialog?.id !== 'products') return;
    dialog.querySelectorAll('.product-video').forEach(video => {
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
    if (document.hidden) stopProductVideos(active);
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
      const titleCount = prepareTypewriter(section.querySelector('.chapter-title'), 100, 38);
      const leadDelay = Math.min(560, 160 + titleCount * 34);
      prepareTypewriter(section.querySelector('.chapter-lead'), leadDelay, 15);
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
  window.addEventListener('wheel', () => setMobileNav(false), { passive: true });
  matchMedia('(min-width: 601px)').addEventListener('change', event => {
    if (event.matches) setMobileNav(false);
  });
})();
