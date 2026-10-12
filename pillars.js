// Pilares (Culture, Adventure, Explore, Transform).
// La sección se queda fija mientras se recorre .pillars-track: el avance del
// scroll dentro del track decide qué categoría está activa. Al pulsar una
// categoría, la página se desplaza hasta su tramo.
// Una línea de tiempo junto a los títulos se llena con el scroll y llega a
// cada punto justo cuando se activa su categoría.
(function () {
  var track = document.querySelector('.pillars-track');
  if (!track) return;

  var items = Array.prototype.slice.call(document.querySelectorAll('.pillar'));
  // Foto y figura de cada categoría; se activan junto con su título.
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.pillar-img, .pillar-shape'));
  var n = items.length;
  var actual = 0;

  var linea = document.querySelector('.pillars-progress');
  var relleno = document.querySelector('.pillars-progress-fill');
  var lista = document.querySelector('.pillars-list');

  function activar(i) {
    if (i === actual) return;
    actual = i;
    items.forEach(function (li, k) {
      var activo = k === i;
      li.classList.toggle('is-active', activo);
      li.classList.toggle('is-done', k < i);
      var boton = li.querySelector('.pillar-title');
      if (activo) boton.setAttribute('aria-current', 'true');
      else boton.removeAttribute('aria-current');
    });
    imgs.forEach(function (el) {
      el.classList.toggle('is-active', Number(el.getAttribute('data-pillar')) === i);
    });
  }

  // Centro vertical de cada título, en coordenadas de .pillars. Se suma
  // offsetTop hasta llegar a .pillars: así no influyen las animaciones de
  // entrada (translate), que sí moverían getBoundingClientRect.
  var contenedor = document.querySelector('.pillars');
  function arriba(el) {
    var y = 0;
    while (el && el !== contenedor) { y += el.offsetTop; el = el.offsetParent; }
    return y;
  }
  function centros() {
    return items.map(function (li) {
      var b = li.querySelector('.pillar-title');
      return arriba(b) + b.offsetHeight / 2;
    });
  }

  // La línea va del primer punto al último; el relleno llega al punto i
  // cuando el avance es i/n (el momento en que se activa esa categoría).
  function dibujarLinea(avance) {
    if (!linea || !relleno) return;
    var c = centros();
    linea.style.top = c[0] + 'px';
    linea.style.height = (c[n - 1] - c[0]) + 'px';
    var tramo = Math.min(avance * n, n - 1);
    var k = Math.min(Math.floor(tramo), n - 2);
    var y = c[k] + (c[k + 1] - c[k]) * Math.min(tramo - k, 1);
    relleno.style.height = Math.max(y - c[0], 0) + 'px';
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
    dibujarLinea(avance);
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
  // Al desplegarse el texto de una categoría los títulos se mueven: recolocar la línea
  if (lista && 'ResizeObserver' in window) new ResizeObserver(alHacerScroll).observe(lista);
  actualizar();
})();
