/* Presentation only: never reads form values or sends network requests. */
(() => {
  if (!document.body.classList.contains('studio-theme')) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const schedule = callback => {
    let pending = false;
    return () => {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; callback(); });
    };
  };

  // Pointer-driven light and collage depth. No animation loop when idle.
  document.querySelectorAll('.studio-art-stack, .compact-course-card, .pf-card, .blog-card, .speaker-achievement-card, .lecture-card').forEach(element => {
    element.setAttribute('data-studio-glass', '');
    let frame = 0, point = null;
    const reset = () => {
      cancelAnimationFrame(frame); frame = 0; point = null;
      ['--glass-x', '--glass-y', '--art-x', '--art-y'].forEach(name => element.style.removeProperty(name));
    };
    element.addEventListener('pointermove', event => {
      if (reducedMotion.matches || !finePointer.matches || document.hidden || event.pointerType !== 'mouse') return;
      point = { x: event.clientX, y: event.clientY };
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        if (!point) return;
        const box = element.getBoundingClientRect();
        const x = Math.min(1, Math.max(0, (point.x - box.left) / box.width));
        const y = Math.min(1, Math.max(0, (point.y - box.top) / box.height));
        element.style.setProperty('--glass-x', `${x * 100}%`);
        element.style.setProperty('--glass-y', `${y * 100}%`);
        if (element.classList.contains('studio-art-stack')) {
          element.style.setProperty('--art-x', `${(x - .5) * 12}px`);
          element.style.setProperty('--art-y', `${(y - .5) * 12}px`);
        }
      });
    }, { passive: true });
    element.addEventListener('pointerleave', reset);
    reducedMotion.addEventListener('change', reset);
    finePointer.addEventListener('change', reset);
    document.addEventListener('visibilitychange', reset);
  });

  // A quiet reading cue lives inside the existing header, not another menu.
  const header = document.querySelector('.site-header');
  if (header) {
    const progress = document.createElement('span');
    progress.className = 'studio-reading-progress';
    progress.setAttribute('aria-hidden', 'true');
    header.append(progress);
    const sections = [...header.querySelectorAll('a[href*="#"]')].flatMap(link => {
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || url.pathname !== location.pathname || !url.hash) return [];
      const section = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      return section ? [{ link, section }] : [];
    });
    const updateReading = schedule(() => {
      const distance = document.documentElement.scrollHeight - innerHeight;
      progress.style.transform = `scaleX(${distance > 0 ? Math.min(1, Math.max(0, scrollY / distance)) : 0})`;
      const passed = sections.filter(({ section }) => section.getBoundingClientRect().top <= Math.max(header.offsetHeight + 24, innerHeight * 0.3));
      const current = passed.sort((a, b) => b.section.getBoundingClientRect().top - a.section.getBoundingClientRect().top)[0];
      sections.forEach(({ link, section }) => {
        const active = section === current?.section;
        link.toggleAttribute('data-studio-current', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
    addEventListener('scroll', updateReading, { passive: true });
    addEventListener('resize', updateReading, { passive: true });
    addEventListener('load', updateReading, { once: true });
    if ('ResizeObserver' in window) new ResizeObserver(updateReading).observe(document.body);
    updateReading();
  }

  // Keep the existing arrows and native touch scrolling; add mouse dragging.
  document.querySelectorAll('.pf-carousel').forEach(track => {
    const wrap = track.closest('.pf-carousel-wrap');
    const cards = [...track.children].filter(element => element.matches('a'));
    if (!wrap || cards.length < 2) return;
    track.classList.add('studio-grabbable');
    if (!track.hasAttribute('tabindex')) track.tabIndex = 0;
    if (!track.hasAttribute('role')) track.setAttribute('role', 'region');
    if (!track.hasAttribute('aria-label')) track.setAttribute('aria-label', track.id === 'works-carousel' ? '実績サイト' : 'ブログ記事');
    const meter = document.createElement('div');
    meter.className = 'studio-carousel-meter';
    meter.setAttribute('aria-hidden', 'true');
    const rail = document.createElement('span');
    rail.className = 'studio-carousel-rail';
    const fill = document.createElement('span');
    rail.append(fill);
    const position = document.createElement('span');
    position.className = 'studio-carousel-position';
    meter.append(rail, position);
    wrap.append(meter);
    const updatePosition = schedule(() => {
      const rect = track.getBoundingClientRect();
      let nearest = 0;
      cards.forEach((card, index) => {
        if (Math.abs(card.getBoundingClientRect().left - rect.left) < Math.abs(cards[nearest].getBoundingClientRect().left - rect.left)) nearest = index;
      });
      meter.hidden = track.scrollWidth <= track.clientWidth + 2;
      position.textContent = `${String(nearest + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
      fill.style.transform = `scaleX(${Math.min(1, (track.scrollLeft + track.clientWidth) / track.scrollWidth)})`;
      wrap.toggleAttribute('data-studio-at-start', track.scrollLeft < 2);
      wrap.toggleAttribute('data-studio-at-end', track.scrollLeft + track.clientWidth >= track.scrollWidth - 2);
    });
    track.addEventListener('scroll', updatePosition, { passive: true });
    addEventListener('resize', updatePosition, { passive: true });
    if ('ResizeObserver' in window) new ResizeObserver(updatePosition).observe(track);
    updatePosition();

    const move = (direction, edge) => {
      const left = edge === 'start' ? 0 : edge === 'end' ? track.scrollWidth : track.scrollLeft + direction * (cards[1].offsetLeft - cards[0].offsetLeft);
      track.scrollTo({ left, behavior: reducedMotion.matches ? 'instant' : 'smooth' });
    };
    track.addEventListener('keydown', event => {
      if (event.target !== track || event.altKey || event.ctrlKey || event.metaKey) return;
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      move(event.key === 'ArrowLeft' ? -1 : 1, event.key === 'Home' ? 'start' : event.key === 'End' ? 'end' : null);
    });
    // Older arrow handlers explicitly request smooth scrolling. Respect a
    // changed motion preference without rewriting those existing handlers.
    wrap.querySelectorAll('.pf-arrow').forEach(button => button.addEventListener('click', event => {
      if (!reducedMotion.matches) return;
      event.stopImmediatePropagation();
      move(button.classList.contains('pf-prev') ? -1 : 1);
    }, { capture: true }));

    let gesture = null;
    let suppressClick = false;
    const finish = event => {
      if (!gesture || (event.pointerId !== undefined && event.pointerId !== gesture.id)) return;
      const { id, dragging } = gesture;
      gesture = null;
      suppressClick = dragging && event.type === 'pointerup';
      track.classList.remove('studio-dragging');
      if (track.hasPointerCapture(id)) track.releasePointerCapture(id);
    };
    track.addEventListener('pointerdown', event => {
      suppressClick = false;
      if (!finePointer.matches || event.pointerType !== 'mouse' || event.button !== 0 || track.scrollWidth <= track.clientWidth + 2) return;
      if (event.target.closest('button, input, select, textarea')) return;
      gesture = { id: event.pointerId, x: event.clientX, y: event.clientY, left: track.scrollLeft, dragging: false };
    });
    track.addEventListener('pointermove', event => {
      if (!gesture || event.pointerId !== gesture.id) return;
      const dx = event.clientX - gesture.x;
      const dy = event.clientY - gesture.y;
      if (!gesture.dragging) {
        if (Math.abs(dy) > 8 && Math.abs(dy) > Math.abs(dx)) { gesture = null; return; }
        if (Math.abs(dx) < 8) return;
        gesture.dragging = true;
        track.classList.add('studio-dragging');
        track.setPointerCapture(event.pointerId);
      }
      event.preventDefault();
      track.scrollLeft = gesture.left - dx;
    });
    track.addEventListener('pointerup', finish);
    track.addEventListener('pointercancel', finish);
    track.addEventListener('lostpointercapture', finish);
    track.addEventListener('pointerleave', event => { if (!gesture?.dragging) finish(event); });
    addEventListener('blur', finish);
    track.addEventListener('dragstart', event => { if (gesture) event.preventDefault(); });
    track.addEventListener('click', event => {
      if (!suppressClick || event.detail === 0) return;
      suppressClick = false;
      event.preventDefault();
      event.stopImmediatePropagation();
    }, { capture: true });
  });

  if (!('IntersectionObserver' in window) || reducedMotion.matches) return;
  const reveal = document.querySelectorAll('.focus-section-head, .focus-split, .focus-step, .speaker-principle-grid article, .speaker-achievement-card');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.dataset.studioVisible = 'true';
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.04, rootMargin: '0px 0px 60px 0px' });
  reveal.forEach(element => {
    element.classList.add('studio-reveal');
    element.dataset.studioVisible = element.getBoundingClientRect().top < innerHeight ? 'true' : 'false';
    observer.observe(element);
  });
  reducedMotion.addEventListener('change', event => {
    if (!event.matches) return;
    observer.disconnect();
    reveal.forEach(element => { element.dataset.studioVisible = 'true'; });
  });
})();
