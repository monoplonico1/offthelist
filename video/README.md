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
