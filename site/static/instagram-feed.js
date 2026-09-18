(() => {
  const section = document.getElementById('instagram');
  if (!section) return;
  const track = section.querySelector('#instagram-track');
  const cards = [...track.querySelectorAll('.instagram-card')];
  const controls = section.querySelector('.instagram-controls');
  const previous = section.querySelector('[data-instagram-prev]');
  const next = section.querySelector('[data-instagram-next]');
  const position = section.querySelector('[data-instagram-position]');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!cards.length) return;
  controls.hidden = false;
  const offsets = () => cards.map(card => card.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft);
  const nearest = () => {
    const points = offsets();
    return points.reduce((best, point, index) => Math.abs(point - track.scrollLeft) < Math.abs(points[best] - track.scrollLeft) ? index : best, 0);
  };
  const update = () => {
    previous.disabled = track.scrollLeft <= 3;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 3;
    const first = nearest();
    const right = track.getBoundingClientRect().right;
    const last = cards.reduce((value, card, index) => card.getBoundingClientRect().right <= right + 3 ? index : value, first);
    position.textContent = `${first + 1}${last > first ? `–${last + 1}` : ''} / ${cards.length}`;
  };
  const move = direction => {
    const points = offsets();
    const target = direction > 0
      ? points.find(point => point > track.scrollLeft + 4)
      : points.findLast(point => point < track.scrollLeft - 4);
    track.scrollTo({ left: target ?? (direction > 0 ? track.scrollWidth : 0), behavior: reduceMotion.matches ? 'instant' : 'smooth' });
  };
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('keydown', event => {
    if (event.target !== track) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });
  let pending = false;
  track.addEventListener('scroll', () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { pending = false; update(); });
  }, { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(update).observe(track);
  else window.addEventListener('resize', update);
  update();
})();
