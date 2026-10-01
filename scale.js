// La maqueta de escritorio mide 1440 px. Se escala con zoom para que ocupe
// el 100 % del ancho: sin esto quedan franjas vacías a los lados en pantallas
// más anchas, y el contenido se recorta en las más estrechas.
(function () {
  var DISENO = 1440;
  var MIN_ESCRITORIO = 1024; // igual que la media query de styles.css
  var page = document.querySelector('.page');

  function ajustar() {
    var ancho = document.documentElement.clientWidth;
    page.style.zoom = ancho >= MIN_ESCRITORIO ? ancho / DISENO : '';
  }

  ajustar();
  window.addEventListener('resize', ajustar);
})();
