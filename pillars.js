// Pilares (Culture, Adventure, Explore, Transform).
// La sección se queda fija mientras se recorre .pillars-track: el avance del
// scroll dentro del track decide qué categoría está activa. Al pulsar una
// categoría, la página se desplaza hasta su tramo.
(function () {
  var track = document.querySelector('.pillars-track');
  if (!track) return;

  var items = Array.prototype.slice.call(document.querySelectorAll('.pillar'));
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.pillar-img'));
  var n = items.length;
  var actual = 0;

  function activar(i) {
    if (i === actual) return;
    actual = i;
    items.forEach(function (li, k) {
      var activo = k === i;
      li.classList.toggle('is-active', activo);
      var boton = li.querySelector('.pillar-title');
      if (activo) boton.setAttribute('aria-current', 'true');
      else boton.removeAttribute('aria-current');
    });
    imgs.forEach(function (img, k) {
      img.classList.toggle('is-active', k === i);
    });
  }

  // Tramo del scroll que recorre las categorías (el track menos una pantalla).
  function recorrido() {
    var r = track.getBoundingClientRect();
    return { inicio: r.top + window.scrollY, largo: Math.max(r.height - window.innerHeight, 1) };
  }

  var pendiente = false;
  function actualizar() {
    pendiente = false;
    var t = recorrido();
    var avance = (window.scrollY - t.inicio) / t.largo;
    avance = Math.min(Math.max(avance, 0), 0.9999);
    activar(Math.floor(avance * n));
  }
  function alHacerScroll() {
    if (pendiente) return;
    pendiente = true;
    window.requestAnimationFrame(actualizar);
  }

  items.forEach(function (li, i) {
    li.querySelector('.pillar-title').addEventListener('click', function () {
      var t = recorrido();
      window.scrollTo({ top: t.inicio + t.largo * (i + 0.5) / n, behavior: 'smooth' });
    });
  });

  window.addEventListener('scroll', alHacerScroll, { passive: true });
  window.addEventListener('resize', alHacerScroll);
  actualizar();
})();
