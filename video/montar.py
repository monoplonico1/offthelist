#!/usr/bin/env python3
"""Monta el film concepto de Off the List a partir de las piezas entregadas.

Uso:
    python3 video/montar.py CARPETA_PIEZAS [--salida film.mp4] [--4k]

CARPETA_PIEZAS contiene (ver el documento "Off the List — Concept Film"):
    01.jpg … 13.jpg      imágenes del storyboard (14 = video/endcard.png)
    vo-01.mp3 … vo-12.mp3  una línea de voz en off por archivo
    music.mp3            música
    sfx-XX.mp3           efectos, opcionales; el número es el de la toma

Los tiempos se adaptan a la voz: cada toma dura lo que marca el storyboard
o lo que necesite su línea de voz, lo que sea mayor. La línea 9 cubre tres
tomas (especia, palabra, llave): los cortes caen en sus dos últimas pausas.
Solo usa ffmpeg y ffprobe.
"""
import argparse
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

# (toma, segundos del storyboard, línea de voz que arranca en ella, efecto)
TOMAS = [
    (1, 7, 1, "sfx-01"), (2, 7, 2, "sfx-02"), (3, 8, 3, "sfx-03"),
    (4, 5, 4, "sfx-04"), (5, 6, 5, "sfx-05"), (6, 6, 6, "sfx-06"),
    (7, 7, 7, "sfx-07"), (8, 7, 8, "sfx-08"), (9, 4, 9, "sfx-09"),
    (10, 2, None, None), (11, 3, None, "sfx-11"), (12, 6, 10, "sfx-12"),
    (13, 7, 11, "sfx-13"), (14, 7, 12, None),
]
FUNDIDO = 1.0          # crossfade entre imágenes (s)
ENTRADA_VOZ = 0.7      # la voz entra este tiempo después del corte (s)
APERTURA = 2.5         # silencio con imagen antes de la primera línea (s)
RESPIRO = 1.0          # pausa tras cada línea antes del siguiente corte (s)
CIERRE = 3.5           # la tarjeta final se queda tras la última línea (s)
FPS = 30
EMPUJE = 0.07          # zoom lento de cada imagen: de 1.00 a 1.07


def duracion(ruta):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", ruta], capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def pausas(ruta):
    """Centros de las pausas (>= 0.25 s bajo -35 dB) dentro de una línea de voz."""
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", ruta, "-af",
         "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duracion(ruta)
    # descarta el silencio del principio y del final del archivo
    return [(a + b) / 2 for a, b in zip(ini, fin) if a > 0.2 and b < total - 0.2]


def pieza(carpeta, nombre, exts):
    for e in exts:
        p = os.path.join(carpeta, nombre + e)
        if os.path.exists(p):
            return p
    return None


def planificar(carpeta):
    """Inicio de cada toma, inicio de cada línea de voz y duración total."""
    voz = {}
    for t in TOMAS:
        if t[2]:
            p = pieza(carpeta, "vo-%02d" % t[2], [".mp3", ".wav", ".m4a"])
            if not p:
                sys.exit("Falta vo-%02d" % t[2])
            voz[t[2]] = (p, duracion(p))

    inicio, entrada_voz, t = {}, {}, 0.0
    i = 0
    while i < len(TOMAS):
        toma, base, linea, _ = TOMAS[i]
        inicio[toma] = t
        lead = APERTURA if toma == 1 else ENTRADA_VOZ
        if linea == 9:
            # Una sola línea para las tomas 9, 10 y 11: cortes en sus pausas
            ruta, dur = voz[9]
            entrada_voz[9] = t + lead
            ps = pausas(ruta)
            if len(ps) >= 2:
                c10, c11 = ps[-2], ps[-1]
            else:  # sin pausas claras: reparto proporcional
                c10, c11 = dur * 0.62, dur * 0.8
            inicio[10] = t + lead + c10
            inicio[11] = t + lead + c11
            t = max(t + lead + dur + RESPIRO, inicio[11] + 2.0)
            i += 3
            continue
        largo = base
        if linea:
            entrada_voz[linea] = t + lead
            largo = max(base, lead + voz[linea][1] + (CIERRE if toma == 14 else RESPIRO))
        t += largo
        i += 1
    return inicio, entrada_voz, voz, t


def montar(carpeta, salida, ancho, alto):
    inicio, entrada_voz, voz, total = planificar(carpeta)
    tomas = [t[0] for t in TOMAS]
    args = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    filtros, n = [], 0

    # --- Imagen: una entrada por toma, zoom lento, crossfades encadenados ---
    factor = 3 if ancho <= 1920 else 2       # sobremuestreo: zoom sin temblor
    super_w, super_h = ancho * factor, alto * factor
    etiquetas = []
    for k, toma in enumerate(tomas):
        img = (os.path.join(AQUI, "endcard.png") if toma == 14
               else pieza(carpeta, "%02d" % toma, [".jpg", ".jpeg", ".png", ".webp"]))
        if not img or not os.path.exists(img):
            sys.exit("Falta la imagen %02d" % toma)
        fin = inicio[tomas[k + 1]] if k + 1 < len(tomas) else total
        dur = fin - inicio[toma] + (FUNDIDO if k > 0 else 0)
        frames = int(round(dur * FPS))
        args += ["-i", img]
        empuje = 0.02 if toma == 14 else EMPUJE
        filtros.append(
            "[%d:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
            "zoompan=z='1+%f*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            ":d=%d:s=%dx%d:fps=%d,setsar=1,format=yuv420p[v%d]"
            % (n, super_w, super_h, super_w, super_h, empuje, frames, frames,
               ancho, alto, FPS, k))
        etiquetas.append(("v%d" % k, dur))
        n += 1

    previo, acumulado = etiquetas[0][0], etiquetas[0][1]
    for k in range(1, len(etiquetas)):
        nombre = "x%d" % k
        offset = acumulado - FUNDIDO
        filtros.append("[%s][%s]xfade=transition=fade:duration=%.3f:offset=%.3f[%s]"
                       % (previo, etiquetas[k][0], FUNDIDO, offset, nombre))
        acumulado = offset + etiquetas[k][1]
        previo = nombre
    filtros.append("[%s]fade=t=in:st=0:d=1.5,fade=t=out:st=%.3f:d=1.2[video]"
                   % (previo, total - 1.2))

    # --- Voz: cada línea en su sitio ---
    voces = []
    for linea, (ruta, _) in sorted(voz.items()):
        args += ["-i", ruta]
        ms = int(entrada_voz[linea] * 1000)
        filtros.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,"
                       "adelay=%d|%d[vo%d]" % (n, ms, ms, linea))
        voces.append("[vo%d]" % linea)
        n += 1
    filtros.append("%samix=inputs=%d:normalize=0,apad=whole_dur=%.3f,"
                   "asplit=2[voz][voz_sc]" % ("".join(voces), len(voces), total))

    mezcla = ["[voz]"]
    # --- Música: entra suave y baja sola cuando habla la voz ---
    musica = pieza(carpeta, "music", [".mp3", ".wav", ".m4a"])
    if musica:
        args += ["-i", musica]
        filtros.append(
            "[%d:a]aresample=48000,aformat=channel_layouts=stereo,apad,"
            "atrim=0:%.3f,afade=t=in:st=0:d=3,afade=t=out:st=%.3f:d=4,volume=0.6[mus]"
            % (n, total, total - 4))
        filtros.append("[mus][voz_sc]sidechaincompress=threshold=0.03:ratio=5:"
                       "attack=120:release=900:makeup=1[musica]")
        mezcla.append("[musica]")
        n += 1
    else:
        filtros.append("[voz_sc]anullsink")

    # --- Efectos: cada uno con su toma, por debajo de todo ---
    for toma, _, _, sfx in TOMAS:
        ruta = sfx and pieza(carpeta, sfx, [".mp3", ".wav", ".m4a"])
        if not ruta:
            continue
        args += ["-i", ruta]
        desde = max(inicio[toma] - FUNDIDO / 2, 0)
        k = tomas.index(toma)
        hasta = (inicio[tomas[k + 1]] if k + 1 < len(tomas) else total) + FUNDIDO
        largo = max(hasta - desde, 1.0)
        ms = int(desde * 1000)
        filtros.append(
            "[%d:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:%.3f,"
            "afade=t=in:st=0:d=0.4,afade=t=out:st=%.3f:d=0.9,volume=0.4,"
            "adelay=%d|%d[sfx%d]" % (n, largo, max(largo - 0.9, 0), ms, ms, toma))
        mezcla.append("[sfx%d]" % toma)
        n += 1

    filtros.append(
        "%samix=inputs=%d:normalize=0,atrim=0:%.3f,alimiter=limit=0.89,"
        "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[audio]"
        % ("".join(mezcla), len(mezcla), total))

    args += ["-filter_complex", ";".join(filtros), "-map", "[video]", "-map", "[audio]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
             "-t", "%.3f" % total, "-movflags", "+faststart", salida]
    print("Duración total: %.1f s" % total)
    for toma in tomas:
        print("  toma %02d desde %5.2f s" % (toma, inicio[toma]))
    subprocess.run(args, check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--salida", default="off-the-list-film.mp4")
    ap.add_argument("--4k", dest="cuatro_k", action="store_true")
    a = ap.parse_args()
    w, h = (3840, 2160) if a.cuatro_k else (1920, 1080)
    montar(a.carpeta, a.salida, w, h)
