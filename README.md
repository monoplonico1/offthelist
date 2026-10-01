# Off The List — web

Sitio estático (HTML, CSS y JavaScript sin dependencias) a partir del Figma
"Off the List": `index.html` (Home), `sample-journeys.html` y `about.html`.

## Verlo en local

```bash
./descargar-assets.sh        # baja las imágenes del Figma a assets/ (solo las que falten)
python3 -m http.server 8000  # luego abre http://localhost:8000
```

## Caché

Las páginas cargan los CSS y JS con `?v=N`. **Al cambiar cualquier `.css` o `.js`
hay que subir ese número en los tres HTML**; si no, el navegador puede seguir
usando la versión anterior y mezclar HTML nuevo con estilos viejos.
