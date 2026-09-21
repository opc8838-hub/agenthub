(() => {
  const dialogs = [...document.querySelectorAll('.modal-layer')];
  const page = document.querySelector('.page-shell');
  let active = null;
  let opener = null;
  const focusable = 'button:not([disabled]), input, textarea, select, a[href], [tabindex="0"]';

  function close() {
    if (!active) return;
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
    if (active) active.hidden = true;
    active = next;
    active.hidden = false;
    active.querySelector('.modal').scrollTop = 0;
    document.body.classList.add('modal-open');
    active.querySelector('.close').focus({ preventScroll: true });
    page.inert = true;
  }

  document.addEventListener('click', event => {
    const scrollButton = event.target.closest('[data-scroll]');
    if (scrollButton) {
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
      open(trigger.dataset.modal, trigger);
      return;
    }
    if (event.target.closest('.close') || event.target === active) close();
  });

  document.addEventListener('keydown', event => {
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
})();
