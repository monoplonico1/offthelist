#!/usr/bin/env python3
"""Film "I want" v4: clips POV de Flow + voz de ElevenLabs.

Cada escena toma su fragmento del clip de Flow, con duración según el ritmo por
tramos. El ambiente de cada clip se nivela por energía (silencio en los tramos
calmos, picos en Holi, fuego y esquí) y baja solo cuando habla la voz.
"""
import re
import subprocess
import sys

CLIPS, VOZ, LOGO, TAG, FOGATA, SALIDA = sys.argv[1:7]
W, H, FPS = 1920, 1080, 24
BARRA = 138
DIS = 0.6                      # disolvencia en los tramos lentos
CORTE = 0.04                   # corte seco

def clip(n):
    return "%s/clip%d.mp4" % (CLIPS, n)

# (clip, entrada, duración, transición de entrada, nivel de ambiente en dB medio)
# clip None = negro con el sonido de la fogata
ESCENAS = [
    (1, 0.00, 4.9, "negro", -40),   # 1  find myself · Kioto
    (1, 5.05, 4.3, "dis", -36),     # 2  get lost · paddle
    (2, 0.50, 4.0, "corte", -29),   # 3  connect · águila
    (2, 5.40, 3.5, "corte", -32),   # 4  see what few · tiburón ballena
    (3, 3.00, 3.0, "corte", -21),   # 5  colour · Holi (primer pico)
    (None, 4.30, 2.5, "corte", -34),  # 6  nothing · negro + fogata
    (4, 0.30, 3.0, "corte", -17),   # 7  everything · fuego (lo más fuerte)
    (4, 4.00, 3.4, "corte", -38),   # 8  guest · telar
    (5, 0.85, 3.4, "corte", -36),   # 9  belong · café (antes del salto de la taza en 4.3 s)
    (6, 0.20, 3.0, "corte", -22),   # 10 go first · esquí (segundo pico)
    (6, 4.30, 3.5, "corte", -30),   # 11 be in awe · volcán
    (7, 0.00, 3.6, "corte", -32),   # 12 rise · globos
    (7, 4.80, 4.5, "dis", -36),     # 13 shine · cueva
    (8, 0.00, 3.5, "dis", -38),     # 14 breathe · selva
    (8, 4.90, 4.4, "dis", -42),     # 15 time to stop · piscina
    (9, 6.30, 3.5, "corte", -36),   # 16 surprised · sobre
]
# Líneas de voz en vo.mp3 (inicio, fin), medidas por sus pausas
LINEAS = [(0.00, 2.43), (3.09, 5.13), (5.70, 6.92), (7.45, 9.57), (10.15, 11.12),
          (11.63, 12.59), (13.06, 14.19), (14.82, 17.38), (17.83, 18.96), (19.51, 20.75),
          (21.19, 22.78), (23.22, 24.52), (24.95, 26.67), (27.15, 28.45), (28.88, 30.87),
          (31.35, 32.84), (33.43, 34.25), (34.60, 38.03)]
ENTRADA_VOZ = 0.35
# Recortes por escena (índice desde 0): bordes negros que dejó Flow
RECORTES = {4: "1892:1064:14:8", 10: "1476:830:222:125"}


def media(archivo, ini, dur):
    err = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-ss", str(ini), "-t", str(dur),
                          "-i", archivo, "-vn", "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: ([-\d.]+) dB", err)
    return float(m.group(1)) if m else -60.0


def main():
    args = ["ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    f, n = [], 0
    etiquetas, inicios, t = [], [], 0.0
    for k, (c, ini, dur, trans, nivel) in enumerate(ESCENAS):
        solape = DIS if trans == "dis" else (CORTE if k else 0)
        largo = dur + solape
        inicios.append(t - (solape if k else 0) + (solape if trans == "dis" else 0) * 0)
        if c is None:
            args += ["-f", "lavfi", "-t", "%.3f" % largo, "-i", "color=black:s=%dx%d:r=%d" % (W, H, FPS)]
            f.append("[%d:v]format=yuv420p,setsar=1,settb=1/%d[v%d]" % (n, FPS, k))
        else:
            args += ["-ss", "%.3f" % ini, "-t", "%.3f" % largo, "-i", clip(c)]
            # tpad + trim: largo exacto aunque el clip se quede unos cuadros corto al final
            rc = ("crop=%s," % RECORTES[k]) if k in RECORTES else ""
            f.append("[%d:v]%sscale=%d:%d,fps=%d,format=yuv420p,setsar=1,setpts=PTS-STARTPTS,"
                     "tpad=stop_mode=clone:stop_duration=1,trim=0:%.3f,setpts=PTS-STARTPTS,settb=1/%d[v%d]"
                     % (n, rc, W, H, FPS, largo, FPS, k))
        etiquetas.append(("v%d" % k, largo, trans))
        n += 1
        t += dur
    cierre_ini = t

    # Cierre: montaje rápido de todas las escenas bajo una capa oscura, logo y tagline
    l17, l18 = LINEAS[16], LINEAS[17]
    t_logo = 0.8
    t_tag = t_logo + (l17[1] - l17[0]) + 0.7
    cierre = t_tag + (l18[1] - l18[0]) + 2.2
    CAMBIO = 0.32
    escenas_img = [e for e in ESCENAS if e[0]]
    piezas = []
    for j in range(int(cierre / CAMBIO) + 1):
        c, ini, dur, _, _ = escenas_img[j % len(escenas_img)]
        args += ["-ss", "%.3f" % (ini + dur * 0.4), "-t", "%.3f" % CAMBIO, "-i", clip(c)]
        f.append("[%d:v]scale=%d:%d,fps=%d,format=yuv420p,setsar=1,setpts=PTS-STARTPTS[m%d]" % (n, W, H, FPS, j))
        piezas.append("[m%d]" % j)
        n += 1
    f.append("%sconcat=n=%d:v=1:a=0,tpad=stop_mode=clone:stop_duration=2,trim=0:%.3f,setpts=PTS-STARTPTS,format=gbrp,"
             "colorlevels=romax=0.38:gomax=0.38:bomax=0.38,format=yuv420p[mont]"
             % ("".join(piezas), len(piezas), cierre))
    args += ["-loop", "1", "-t", "%.3f" % cierre, "-i", LOGO]; lg = n; n += 1
    args += ["-loop", "1", "-t", "%.3f" % cierre, "-i", TAG]; tg = n; n += 1
    f.append("[%d:v]format=rgba,fade=t=in:st=%.2f:d=0.6:alpha=1[lg]" % (lg, t_logo - 0.3))
    f.append("[%d:v]format=rgba,fade=t=in:st=%.2f:d=0.6:alpha=1[tg]" % (tg, t_tag - 0.3))
    f.append("[mont][lg]overlay=0:0[mo1];[mo1][tg]overlay=0:0,format=yuv420p,fps=%d,settb=1/%d[vc]" % (FPS, FPS))
    etiquetas.append(("vc", cierre + DIS, "dis"))
    total = cierre_ini + cierre

    # Encadenado de imagen
    previo, acumulado = etiquetas[0][0], etiquetas[0][1]
    for k in range(1, len(etiquetas)):
        nombre, largo, trans = etiquetas[k]
        d = DIS if trans == "dis" else CORTE
        offset = acumulado - d
        f.append("[%s][%s]xfade=transition=fade:duration=%.3f:offset=%.3f[x%d]" % (previo, nombre, d, offset, k))
        acumulado = offset + largo
        previo = "x%d" % k
    f.append("[%s]tpad=stop_mode=clone:stop_duration=2,trim=0:%.3f,drawbox=x=0:y=0:w=iw:h=%d:c=black:t=fill,"
             "drawbox=x=0:y=ih-%d:w=iw:h=%d:c=black:t=fill,fade=t=in:st=0:d=1.2,"
             "fade=t=out:st=%.3f:d=1.2[video]" % (previo, total, BARRA, BARRA, BARRA, total - 1.2))

    # Inicio real de cada escena en la línea de tiempo
    pos, t = [], 0.0
    for k, (_, _, dur, trans, _) in enumerate(ESCENAS):
        pos.append(t)
        t += dur

    # --- Ambiente: cada escena con su nivel, fundidos cortos entre escenas ---
    amb = []
    for k, (c, ini, dur, trans, nivel) in enumerate(ESCENAS):
        fuente, a_ini = (FOGATA, 1.0) if c is None else (clip(c), ini)
        medido = media(fuente, a_ini, dur)
        ganancia = max(-30, min(30, nivel - medido))
        largo = dur + (DIS if trans == "dis" else 0.06)
        empieza = max(0.0, pos[k] - (DIS if trans == "dis" else 0.03))
        args += ["-ss", "%.3f" % a_ini, "-t", "%.3f" % largo, "-i", fuente]
        fi = DIS if trans == "dis" else 0.05
        f.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.1fdB,"
                 "afade=t=in:d=%.2f,afade=t=out:st=%.3f:d=0.08,adelay=%d|%d[a%d]"
                 % (n, ganancia, fi, max(0, largo - 0.08), int(empieza * 1000), int(empieza * 1000), k))
        amb.append("[a%d]" % k)
        print("escena %2d  t=%5.2f  ambiente %5.1f dB → %5.1f (%+.1f)" % (k + 1, pos[k], medido, nivel, ganancia))
        n += 1
    # El sobre se apaga suave bajo el cierre
    f.append("%samix=inputs=%d:normalize=0,apad=whole_dur=%.3f,atrim=0:%.3f[ambiente]"
             % ("".join(amb), len(amb), total, total))

    # --- Voz ---
    args += ["-i", VOZ]; vz = n; n += 1
    entradas = [p + ENTRADA_VOZ + (0.5 if k == 0 else 0) for k, p in enumerate(pos)]
    entradas += [cierre_ini + t_logo, cierre_ini + t_tag]
    voces = []
    for i, (a, b) in enumerate(LINEAS):
        ms = int(entradas[i] * 1000)
        f.append("[%d:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                 "afade=t=in:d=0.02,afade=t=out:st=%.3f:d=0.08,adelay=%d|%d[l%d]"
                 % (vz, a, b, max(0, b - a - 0.08), ms, ms, i))
        voces.append("[l%d]" % i)
    f.append("%samix=inputs=%d:normalize=0,apad=whole_dur=%.3f,atrim=0:%.3f,volume=2.2,asplit=2[voz][voz_sc]"
             % ("".join(voces), len(voces), total, total))
    # El ambiente baja cuando habla la voz y vuelve en los silencios
    f.append("[ambiente][voz_sc]sidechaincompress=threshold=0.02:ratio=4:attack=60:release=700:makeup=1[amb_d]")
    f.append("[voz][amb_d]amix=inputs=2:normalize=0,alimiter=limit=0.9,"
             "loudnorm=I=-14:TP=-1.5:LRA=14,aresample=48000,afade=t=out:st=%.3f:d=1.2[audio]" % (total - 1.2))

    args += ["-filter_complex", ";".join(f), "-map", "[video]", "-map", "[audio]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "256k", "-t", "%.3f" % total, "-movflags", "+faststart", SALIDA]
    print("Duración: %.1f s (cierre desde %.1f s)" % (total, cierre_ini))
    subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
