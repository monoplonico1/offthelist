# Off The List — web

Sitio estático (HTML, CSS y JavaScript sin dependencias ni compilación), en dos versiones:

- **Clásica:** `index.html` (Home), `sample-journeys.html` y `about.html`, con `lux.css` y `lux.js`.
- **Inmersiva:** `experience.html`, autocontenida (estilos y script en el mismo archivo).

El selector *Classic / Immersive* de la cabecera cambia entre las dos.

## Verlo en local

```bash
python3 -m http.server 8000  # luego abre http://localhost:8000
```

## Recursos

- `assets/lux/`: imágenes del film concepto y el logo (claro y oscuro).
- `assets/immersive/`: videos de acercamiento de la versión inmersiva (`to-<imagen>`, uno por capítulo), en MP4 (H.264) y WebM
  para navegadores sin H.264. Si se cambia un video, hay que regenerar los dos.
- `assets/fonts/`: Inter, Cormorant Garamond y Antonio (woff2, solo latín).

## Caché

Las páginas cargan `lux.css` y `lux.js` con `?v=N`. **Al cambiar cualquiera de
los dos hay que subir ese número en los tres HTML de la versión clásica**; si no,
el navegador puede seguir usando la versión anterior.
