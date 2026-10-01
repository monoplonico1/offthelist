// Anima los bloques de contenido cuando entran en pantalla con el scroll.
// Sin JavaScript, o con "reducir movimiento" activado, todo se ve sin animar.
(function () {
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Cada grupo entra escalonado: sus elementos aparecen uno tras otro.
  var GRUPOS = [
    { sel: '.hero-photo', tipo: 'zoom' },
    { sel: '.hero-content > *' },
    { sel: '.trust-bar li:not(.trust-sep)' },
    { sel: '.how-copy > *' },
    { sel: '.blob-how-1, .blob-how-2', tipo: 'zoom' },
    { sel: '.approach > .eyebrow, .approach > .display' },
    { sel: '.step' },
    { sel: '.mystery-card', tipo: 'zoom' },
    { sel: '.mystery-traveller', tipo: 'left' },
    { sel: '.mystery-copy > *' },
    { sel: '.pillars-head > *', tipo: 'right' },
    { sel: '.pillars-media', tipo: 'zoom' },
    { sel: '.pillars-dot', tipo: 'zoom' },
    { sel: '.pillar' },
    { sel: '.shot', paso: 60 },
    { sel: '.testimonials > *' },
    { sel: '.footer-content > *' },
    // Sample journeys
    { sel: '.sj-hero-copy > *' },
    { sel: '.sj-hero-art', tipo: 'zoom' },
    { sel: '.sj-intro', tipo: 'zoom' },
    { sel: '.journeys-head > *' },
    { sel: '.journey', paso: 0 },
    // About
    { sel: '.about-hero-copy > *' },
    { sel: '.about-portrait', tipo: 'zoom' },
    { sel: '.manifesto', tipo: 'zoom' },
    { sel: '.origin-media', tipo: 'left' },
    { sel: '.origin-copy > *' },
    { sel: '.founder', tipo: 'zoom' }
  ];

  var observer = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      observer.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

  GRUPOS.forEach(function (g) {
    var paso = g.paso === undefined ? 110 : g.paso;
    document.querySelectorAll(g.sel).forEach(function (el, i) {
      el.classList.add('reveal');
      if (g.tipo) el.classList.add('reveal-' + g.tipo);
      el.style.setProperty('--reveal-delay', Math.min(i * paso, 600) + 'ms');
      observer.observe(el);
    });
  });
})();
