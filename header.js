// Menú fijo: al bajar de la parte superior se compacta y toma fondo
// (clase .is-scrolled); al volver arriba recupera su aspecto original.
(function () {
  var nav = document.querySelector('.page .nav');
  if (!nav) return;

  var UMBRAL = 24; // px de scroll a partir de los que se compacta
  var pendiente = false;

  function actualizar() {
    pendiente = false;
    nav.classList.toggle('is-scrolled', window.scrollY > UMBRAL);
  }

  window.addEventListener('scroll', function () {
    if (pendiente) return;
    pendiente = true;
    window.requestAnimationFrame(actualizar);
  }, { passive: true });

  // Botón de menú (solo visible en móvil)
  var boton = nav.querySelector('.nav-toggle');
  function abrir(abierto) {
    nav.classList.toggle('is-open', abierto);
    if (boton) boton.setAttribute('aria-expanded', String(abierto));
  }
  if (boton) {
    boton.addEventListener('click', function () {
      abrir(!nav.classList.contains('is-open'));
    });
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { abrir(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') abrir(false);
    });
    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target)) abrir(false);
    });
  }

  actualizar();
})();
