// Anima los bloques de contenido cuando entran en pantalla con el scroll.
// Sin JavaScript, o con "reducir movimiento" activado, todo se ve sin animar.
(function () {
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Cada grupo entra escalonado: sus elementos aparecen uno tras otro.
  var GRUPOS = [
    { sel: '.nav', tipo: 'fade' },
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
    { sel: '.blob-pillars', tipo: 'zoom' },
    { sel: '.pillars-dot', tipo: 'zoom' },
    { sel: '.pillar-active, .pillar-rest li' },
    { sel: '.shot', paso: 60 },
    { sel: '.testimonials > *' },
    { sel: '.footer-content > *' }
  ];

  var observer = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      observer.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

  GRUPOS.forEach(function (g) {
    var paso = g.paso || 110;
    document.querySelectorAll(g.sel).forEach(function (el, i) {
      el.classList.add('reveal');
      if (g.tipo) el.classList.add('reveal-' + g.tipo);
      el.style.setProperty('--reveal-delay', Math.min(i * paso, 600) + 'ms');
      observer.observe(el);
    });
  });
})();
