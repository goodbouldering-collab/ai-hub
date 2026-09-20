(() => {
  const track = document.getElementById('instagram-track');
  if (!track) return;
  track.addEventListener('keydown', event => {
    if (event.target !== track || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const card = track.querySelector('.instagram-card');
    const step = card ? card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap) : 128;
    track.scrollBy({left: event.key === 'ArrowRight' ? step : -step,
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
})();
