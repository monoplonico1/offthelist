# Concept film

Film de ~80 s para inversores: imágenes fijas con zoom lento, voz en off
femenina, música y efectos. Guion, storyboard y prompts de audio en el
documento "Off the List — Concept Film".

- `montar.py` — monta el film desde una carpeta con `01.jpg`…`13.jpg`,
  `vo-01.mp3`…`vo-12.mp3`, `music.mp3` y los `sfx-XX.mp3` opcionales.
  Los tiempos se ajustan a la duración real de cada línea de voz.
- `endcard.png` — tarjeta final (toma 14), 3840×2160.

```bash
python3 video/montar.py ruta/a/piezas --salida film-1080p.mp4
python3 video/montar.py ruta/a/piezas --salida film-4k.mp4 --4k
```

Requiere ffmpeg. Audio normalizado a −14 LUFS.

## v2 — "I want"

`film_v2.py` monta la versión poema: 15 líneas de voz con mucho aire, una
imagen por línea, negro en "I want nothing", el sobre como pausa antes de
la aurora y un cierre con todas las imágenes pasando rápido bajo una capa
negra, con `cierre-logo.png` y `cierre-tagline.png` (logo nuevo:
`logo-nuevo.svg`). Cinemascope 2.39:1, grano y viñeta.

La música y los efectos están sintetizados con ffmpeg: son temporales hasta
tener pistas definitivas.

```bash
python3 video/film_v2.py PIEZAS TRABAJO --salida film-v2.mp4
python3 video/film_v2.py PIEZAS TRABAJO --salida film-v2.mp4 --solo-audio   # solo remezcla
```

## v4 — "I want", POV con clips de Flow

`film_v4.py` monta la versión en primera persona: 16 escenas generadas en
Google Flow (`clip1.mp4` … `clip9.mp4`, algunos con dos escenas por clip),
la voz de ElevenLabs en un solo archivo y el sonido de la fogata para el
negro de "I want nothing". Cada escena toma su fragmento del clip según el
ritmo por tramos; el ambiente de Flow se nivela por energía y baja cuando
habla la voz. Cierre con montaje rápido, logo y tagline.

```bash
python3 video/film_v4.py CARPETA_CLIPS voz.mp3 video/cierre-logo.png video/cierre-tagline.png fogata.mp3 film-v4.mp4
```

Los tiempos de cada línea de voz están en `LINEAS` (medidos sobre la toma
actual de ElevenLabs): si se regenera la voz, hay que volver a medirlos.
