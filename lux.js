// Off The List — versión clásica: animaciones de texto y scroll.
// Sin JavaScript todo se ve completo y estático; con "reducir movimiento"
// el contenido aparece sin animar.
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- Fotos: el recorte va en una capa interna para que las esquinas del
  // marco activo queden por fuera de la imagen
  document.querySelectorAll('.tone').forEach(function (fig) {
    var clip = document.createElement('span');
    clip.className = 'tone-clip';
    Array.prototype.slice.call(fig.childNodes).forEach(function (n) {
      if (n.nodeType === 1 && n.tagName === 'IMG') clip.appendChild(n);
    });
    fig.insertBefore(clip, fig.firstChild);
  });

  // --- Titulares que suben palabra por palabra -----------------------------
  // Mantiene <em>, <br> y demás etiquetas: solo parte los nodos de texto.
  function partir(el) {
    var i = 0;
    (function recorrer(nodo) {
      Array.prototype.slice.call(nodo.childNodes).forEach(function (h) {
        if (h.nodeType === 3) {
          var frag = document.createDocumentFragment();
          h.textContent.split(/(\s+)/).forEach(function (trozo) {
            if (!trozo) return;
            if (/^\s+$/.test(trozo)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span');
            w.className = 'w';
            var s = document.createElement('span');
            s.textContent = trozo;
            s.style.setProperty('--i', i++);
            w.appendChild(s);
            frag.appendChild(w);
          });
          h.parentNode.replaceChild(frag, h);
        } else if (h.nodeType === 1 && h.tagName !== 'BR') {
          recorrer(h);
        }
      });
    })(el);
  }
  document.querySelectorAll('[data-split]').forEach(partir);

  // --- Texto que se tiñe palabra a palabra con el scroll -------------------
  var scrubs = [];
  document.querySelectorAll('[data-scrub]').forEach(function (el) {
    var palabras = el.textContent.trim().split(/\s+/);
    el.innerHTML = palabras.map(function (p) { return '<span class="sw">' + p + '</span>'; }).join(' ');
    scrubs.push({ el: el, sw: el.querySelectorAll('.sw') });
  });

  // --- Entradas al hacer scroll y paso a color ------------------------------
  if ('IntersectionObserver' in window) {
    var entrar = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); entrar.unobserve(e.target); }
      });
    }, { threshold: .18, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('[data-split], [data-reveal], [data-line]').forEach(function (el) { entrar.observe(el); });

  } else {
    document.querySelectorAll('[data-split], [data-reveal], [data-line]').forEach(function (el) { el.classList.add('is-in'); });
  }

  // --- Cabecera: transparente sobre el hero, sólida al bajar ---------------
  var header = document.querySelector('.header');
  var menuBtn = document.querySelector('.menu-toggle');
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var abierto = header.classList.toggle('menu-open');
      menuBtn.setAttribute('aria-expanded', String(abierto));
      menuBtn.textContent = abierto ? 'Close' : 'Menu';
    });
  }

  // --- Galería horizontal fijada --------------------------------------------
  var pin = document.querySelector('[data-hscroll]');
  var pista = pin && pin.querySelector('.hs-track');

  // --- Fotos que pasan de blanco y negro a color con el scroll --------------
  var tonos = Array.prototype.slice.call(document.querySelectorAll('.tone[data-color]'));

  // --- Método: línea que une 01, 02 y 03 y se dibuja con el scroll ----------
  var linea = document.querySelector('.method-line');
  var numeros = linea ? linea.parentNode.querySelectorAll('.method-num') : [];

  // Solo una tarjeta activa a la vez: la más cercana al centro de la pantalla
  function marcarCentrada() {
    var tarjetas = pista.children, mejor = null, menor = Infinity, centro = window.innerWidth / 2;
    for (var j = 0; j < tarjetas.length; j++) {
      var rc = tarjetas[j].getBoundingClientRect();
      var d = Math.abs(rc.left + rc.width / 2 - centro);
      if (d < menor) { menor = d; mejor = tarjetas[j]; }
    }
    for (var m = 0; m < tarjetas.length; m++) tarjetas[m].classList.toggle('is-color', tarjetas[m] === mejor);
  }

  // --- Parallax ---------------------------------------------------------------
  var paralajes = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));

  // --- Botón flotante al quiz (solo móvil, por CSS) --------------------------
  var flotante = document.querySelector('.float-cta');
  var cierre = document.querySelector('.closing');

  var pendiente = false;
  function cuadro() {
    pendiente = false;
    var vh = window.innerHeight;
    if (header) header.classList.toggle('is-solid', window.scrollY > vh * .08 && !header.classList.contains('is-light'));
    if (flotante) {
      var cierreVisible = cierre && cierre.getBoundingClientRect().top < vh;
      flotante.classList.toggle('is-on', window.scrollY > vh * .6 && !cierreVisible);
    }

    scrubs.forEach(function (s) {
      var r = s.el.getBoundingClientRect();
      // Empieza al asomar y termina cuando el final del texto está en el 70 % de la pantalla
      var p = (vh * .9 - r.top) / (r.height + vh * .2);
      p = Math.max(0, Math.min(1, p));
      var n = Math.round(p * s.sw.length);
      for (var i = 0; i < s.sw.length; i++) s.sw[i].classList.toggle('on', i < n);
    });

    if (linea && numeros.length > 1) {
      var caja = linea.parentNode.getBoundingClientRect();
      // offsetTop ignora el desplazamiento de la animación de entrada de los números
      var n0 = numeros[0], n1 = numeros[numeros.length - 1];
      var arriba = n0.offsetTop + n0.offsetHeight / 2, alto = n1.offsetTop + n1.offsetHeight / 2 - arriba;
      linea.style.top = arriba + 'px';
      linea.style.height = alto + 'px';
      // Se completa cuando el último número llega a la mitad de la pantalla
      var avanceLinea = (vh * .5 - (caja.top + arriba)) / alto;
      linea.style.setProperty('--p', Math.max(0, Math.min(1, avanceLinea)).toFixed(3));
    }

    // Color completo cuando la foto llega al 40 % superior de la pantalla
    tonos.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var g = 1 - Math.max(0, Math.min(1, (vh * .95 - r.top) / (vh * .55)));
      el.style.setProperty('--g', g.toFixed(3));
      el.classList.toggle('is-active', g < .12);
    });

    if (!quieto) {
      paralajes.forEach(function (el) {
        var r = el.parentElement.getBoundingClientRect();
        var v = parseFloat(el.getAttribute('data-parallax')) || .12;
        var centro = r.top + r.height / 2 - vh / 2;
        el.style.transform = 'translate3d(0,' + (-centro * v).toFixed(1) + 'px,0)';
      });
    }

    if (pin && pista && window.innerWidth > 760) {
      var rp = pin.getBoundingClientRect();
      var recorrido = pin.offsetHeight - vh;
      var avance = Math.max(0, Math.min(1, -rp.top / recorrido));
      var max = pista.scrollWidth - window.innerWidth;
      pista.style.transform = 'translate3d(' + (-avance * max).toFixed(1) + 'px,0,0)';
      marcarCentrada();
    }
  }
  function alScroll() { if (!pendiente) { pendiente = true; requestAnimationFrame(cuadro); } }
  window.addEventListener('scroll', alScroll, { passive: true });
  window.addEventListener('resize', function () {
    if (pin && pista) pin.style.height = window.innerWidth > 760 ? (pista.scrollWidth - window.innerWidth + window.innerHeight) + 'px' : '';
    alScroll();
  });
  // En móvil la galería se desliza con el dedo: la tarjeta centrada toma color
  if (pista) {
    pista.addEventListener('scroll', function () {
      if (window.innerWidth <= 760) marcarCentrada();
    }, { passive: true });
    pista.dispatchEvent(new Event('scroll'));
  }
  if (pin && pista && window.innerWidth > 760) pin.style.height = (pista.scrollWidth - window.innerWidth + window.innerHeight) + 'px';
  cuadro();

  // --- Hero: "I want to …" con video (o imagen) y frase rotando ----------
  // Con video, cada toma pasa a la siguiente un poco antes de terminar; con
  // imagen, cada 4,2 s. Con "reducir movimiento" se queda el primer cuadro.
  var hero = document.querySelector('[data-rotator]');
  if (hero) {
    var slides = hero.querySelectorAll('.slide');
    var frases = hero.querySelectorAll('.phrase');
    var k = 0, espera = null;
    function videoDe(n) { return slides[n] && slides[n].querySelector('video'); }
    function siguiente() { mostrar((k + 1) % slides.length); }
    function mostrar(n) {
      var previo = videoDe(k);
      k = n;
      slides.forEach(function (s, i) { s.classList.toggle('is-active', i === n); });
      frases.forEach(function (f, i) {
        f.classList.toggle('is-active', i === n);
        f.classList.toggle('is-out', i === (n - 1 + frases.length) % frases.length);
      });
      hero.querySelectorAll('.counter b').forEach(function (b) { b.textContent = '0' + (n + 1); });
      if (quieto) return;
      clearTimeout(espera);
      var v = videoDe(n);
      if (v) {
        try { v.currentTime = 0; } catch (e) {}
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
        // Si el video no avanza (sin red, sin códec), la rotación sigue igual
        espera = setTimeout(siguiente, 11000);
        var proximo = videoDe((n + 1) % slides.length);
        if (proximo) proximo.preload = 'auto';
      } else {
        espera = setTimeout(siguiente, 4200);
      }
      if (previo && previo !== v) setTimeout(function () { previo.pause(); }, 1900);
    }
    slides.forEach(function (s, i) {
      var v = s.querySelector('video');
      if (!v) return;
      v.addEventListener('timeupdate', function () {
        if (i === k && v.duration && v.duration - v.currentTime < 1.4) siguiente();
      });
    });
    mostrar(0);
  }
})();
