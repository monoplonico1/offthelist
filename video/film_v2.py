#!/usr/bin/env python3
"""Film concepto v2 de Off the List: "I want".

Uso:
    python3 video/film_v2.py PIEZAS TRABAJO --salida film.mp4

PIEZAS: 1.jpeg … 13.jpeg y una carpeta vo/ con 01.wav … 15.wav (una línea
de voz por archivo, ya separadas). TRABAJO: carpeta temporal para pistas.

Imagen: zoom lento por toma, cinemascope 2.39:1, grano y viñeta. Cierre:
todas las imágenes pasando rápido bajo una capa negra, con logo y tagline.
Audio: voz, música y efectos sintetizados con ffmpeg (versión temporal hasta
tener música y efectos definitivos), mezcla a -14 LUFS.
"""
import argparse
import math
import os
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1920, 1080, 30, 48000
BARRA = 138                     # franjas negras del 2.39:1 en 1080p

# (imagen, segundos, línea de voz, fundido de entrada, movimiento, efecto)
# fundido 0.034 = corte seco (un frame)
TOMAS = [
    (None, 1.4, None, 0.0, None, None),            # negro inicial
    ("1", 4.2, 1, 1.2, "in", "lago"),
    ("2", 3.9, 2, 0.8, "izq", "viento"),
    (None, 3.4, 3, 0.034, None, "grillos"),        # I want nothing
    ("3", 3.5, 4, 0.034, "in", "fuegos"),          # I want everything
    ("4", 3.7, 5, 0.7, "der", "ciudad"),
    ("5", 3.5, 6, 0.5, "in", "ola"),
    ("6", 3.7, 7, 0.7, "out", "mesa"),
    ("7", 4.1, 8, 0.9, "in", "quieto"),
    ("8", 3.1, 9, 0.4, "der", "galope"),
    ("9", 3.6, 10, 0.7, "out", "tren"),
    ("10", 3.9, 11, 0.8, "in", "olas"),
    ("12", 3.9, 12, 0.6, "izq", "aeropuerto"),
    ("11", 2.3, None, 0.6, "in", "espera"),        # el sobre: pausa
    ("13", 4.8, 13, 0.034, "out", "aurora"),       # I want to be surprised
]
MONTAJE = 9.5                   # cierre con todas las imágenes
FUNDIDO_CIERRE = 0.6
CAMBIO = 0.32                   # segundos por imagen en el cierre
ENTRADA_VOZ = 0.55


def run(cmd):
    subprocess.run(cmd, check=True)


def ff(*args):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", p], capture_output=True, text=True, check=True).stdout
    return float(out)


# ---------------------------------------------------------------- tiempos
def tiempos():
    """Inicio (imagen ya completa) de cada toma, del cierre y el total."""
    inicio, t = [], 0.0
    for toma in TOMAS:
        inicio.append(t)
        t += toma[1]
    return inicio, t, t + MONTAJE


# ----------------------------------------------------------------- imagen
def clip_toma(piezas, trabajo, k, largo):
    img, _, _, _, mov, _ = TOMAS[k]
    out = os.path.join(trabajo, "v%02d.mp4" % k)
    frames = int(round(largo * FPS))
    if img is None:
        ff("-f", "lavfi", "-i", "color=c=black:s=%dx%d:r=%d" % (W, H, FPS),
           "-t", "%.3f" % largo, "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", out)
        return out
    sw, sh = W * 3, H * 3
    z = {"in": "1+0.075*on/%d" % frames, "out": "1.075-0.075*on/%d" % frames,
         "izq": "1.06", "der": "1.06"}[mov]
    x = {"izq": "(iw-iw/zoom)*(1-on/%d)" % frames, "der": "(iw-iw/zoom)*on/%d" % frames}.get(
        mov, "iw/2-(iw/zoom/2)")
    ff("-i", os.path.join(piezas, img + ".jpeg"), "-filter_complex",
       "scale=%d:%d:flags=lanczos:force_original_aspect_ratio=increase,crop=%d:%d,"
       "zoompan=z='%s':x='%s':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=%d,setsar=1,format=yuv420p"
       % (sw, sh, sw, sh, z, x, frames, W, H, FPS),
       "-frames:v", str(frames), "-c:v", "libx264", "-crf", "12", out)
    return out


def clip_montaje(piezas, trabajo, inicio_vo14, inicio_vo15):
    """Cierre: imágenes rápidas bajo negro al 68 %, logo y tagline encima."""
    lista = os.path.join(trabajo, "montaje.txt")
    orden = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "12", "11", "13"]
    largo = MONTAJE + FUNDIDO_CIERRE
    n = int(math.ceil(largo / CAMBIO))
    with open(lista, "w") as f:
        for i in range(n):
            f.write("file '%s'\nduration %.3f\n" % (os.path.join(piezas, orden[i % len(orden)] + ".jpeg"), CAMBIO))
        f.write("file '%s'\n" % os.path.join(piezas, orden[(n - 1) % len(orden)] + ".jpeg"))
    out = os.path.join(trabajo, "montaje.mp4")
    ff("-f", "concat", "-safe", "0", "-i", lista,
       "-loop", "1", "-i", os.path.join(AQUI, "cierre-logo.png"),
       "-loop", "1", "-i", os.path.join(AQUI, "cierre-tagline.png"),
       "-filter_complex",
       "[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d,"
       "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.68:t=fill,setsar=1[fondo];"
       "[1:v]format=rgba,fade=t=in:st=%.2f:d=1.2:alpha=1[logo];"
       "[2:v]format=rgba,fade=t=in:st=%.2f:d=1.2:alpha=1[tag];"
       "[fondo][logo]overlay=0:0:shortest=1[a];[a][tag]overlay=0:0:shortest=1,"
       "fade=t=out:st=%.2f:d=1.6,format=yuv420p"
       % (W, H, W, H, FPS, inicio_vo14 - 0.35, inicio_vo15 - 0.3, largo - 1.6),
       "-t", "%.3f" % largo, "-c:v", "libx264", "-crf", "12", out)
    return out


def video(piezas, trabajo, inicio, fin_tomas, total, vo_ini):
    clips = []
    for k in range(len(TOMAS)):
        fin = inicio[k + 1] if k + 1 < len(TOMAS) else fin_tomas
        # el clip empieza con su propio fundido de entrada y acaba cuando la
        # siguiente toma ya está completa
        largo = fin - inicio[k] + TOMAS[k][3]
        clips.append((clip_toma(piezas, trabajo, k, largo), largo))
    arranque = fin_tomas - FUNDIDO_CIERRE           # el cierre entra fundiendo
    rel = vo_ini[14] - arranque, vo_ini[15] - arranque
    clips.append((clip_montaje(piezas, trabajo, *rel), MONTAJE + FUNDIDO_CIERRE))
    fundidos = [t[3] for t in TOMAS[1:]] + [FUNDIDO_CIERRE]

    args, filtros = [], []
    for c, _ in clips:
        args += ["-i", c]
    previo, acumulado = "0:v", clips[0][1]
    for k in range(1, len(clips)):
        xf = fundidos[k - 1]
        offset = acumulado - xf
        filtros.append("[%s][%d:v]xfade=transition=fade:duration=%.3f:offset=%.3f[x%d]"
                       % (previo, k, xf, offset, k))
        acumulado = offset + clips[k][1]
        previo = "x%d" % k
    # Acabado: color, viñeta, grano y franjas cinemascope
    filtros.append(
        "[%s]eq=contrast=1.05:saturation=0.93:gamma=0.98,vignette=angle=PI/5,"
        "noise=alls=6:allf=t+u,drawbox=x=0:y=0:w=iw:h=%d:color=black:t=fill,"
        "drawbox=x=0:y=ih-%d:w=iw:h=%d:color=black:t=fill,format=yuv420p[video]"
        % (previo, BARRA, BARRA, BARRA))
    out = os.path.join(trabajo, "video.mp4")
    ff(*args, "-filter_complex", ";".join(filtros), "-map", "[video]", "-t", "%.3f" % total,
       "-c:v", "libx264", "-crf", "14", "-preset", "slow", out)
    return out


# ------------------------------------------------------------------ audio
def wav(nombre, trabajo, graph, largo, entradas=()):
    out = os.path.join(trabajo, nombre + ".wav")
    args = []
    for e in entradas:
        args += ["-f", "lavfi", "-i", e]
    ff(*args, "-filter_complex", graph + ",aresample=%d,aformat=channel_layouts=stereo,"
       "apad,atrim=0:%.3f[o]" % (SR, largo), "-map", "[o]", out)
    return out


def reverb_ir(trabajo, largo=3.2, nombre="ir"):
    out = os.path.join(trabajo, nombre + ".wav")
    ff("-f", "lavfi", "-i", "anoisesrc=d=%.2f:c=white:a=0.6:seed=7" % largo,
       "-f", "lavfi", "-i", "anoisesrc=d=%.2f:c=white:a=0.6:seed=11" % largo,
       "-filter_complex", "[0][1]join=inputs=2:channel_layout=stereo,"
       "afade=t=out:st=0:d=%.2f:curve=exp,lowpass=f=7000,highpass=f=120" % largo,
       "-ar", str(SR), out)
    return out


def con_reverb(entrada, ir, salida, seco=1.0, humedo=0.35):
    ff("-i", entrada, "-i", ir, "-filter_complex",
       "[0]asplit[s][r];[r][1]afir=gtype=gn,volume=%.3f[w];[s]volume=%.3f[d];"
       "[d][w]amix=inputs=2:normalize=0:duration=first" % (humedo, seco), salida)


def envolvente(puntos):
    """Expresión de volumen lineal por tramos a partir de (t, v)."""
    expr = "%.4f" % puntos[-1][1]
    for (t0, v0), (t1, v1) in reversed(list(zip(puntos, puntos[1:]))):
        tramo = "%.4f+(%.4f)*(t-%.3f)/%.3f" % (v0, v1 - v0, t0, max(t1 - t0, 1e-3))
        expr = "if(lt(t,%.3f),%s,%s)" % (t1, tramo, expr)
    return "if(lt(t,%.3f),%.4f,%s)" % (puntos[0][0], puntos[0][1], expr)


ACORDES = [  # re mayor: D(add9) – Bm(add9) – Gmaj7 – A(sus2)
    [146.83, 220.00, 293.66, 329.63, 369.99],
    [123.47, 185.00, 246.94, 293.66, 369.99],
    [98.00, 146.83, 246.94, 293.66, 369.99],
    [110.00, 164.81, 220.00, 246.94, 329.63],
]
MELODIA = [739.99, 659.26, 587.33, 493.88, 440.00, 587.33, 659.26, 739.99, 880.00,
           659.26, 587.33, 493.88, 440.00, 880.00]


def musica(trabajo, inicio, fin_tomas, total, ir):
    seg, solape = 8.0, 3.0
    partes = []
    n = int(math.ceil(total / seg)) + 1
    for i in range(n):
        notas = ACORDES[i % len(ACORDES)]
        expr = "+".join("%.3f*sin(2*PI*%.3f*t)+%.3f*sin(2*PI*%.3f*t)+%.3f*sin(4*PI*%.3f*t)"
                        % (0.05, f, 0.05, f * 1.0025, 0.012, f) for f in notas)
        partes.append(wav("pad%02d" % i, trabajo,
                          "[0]lowpass=f=1600,afade=t=in:d=%.1f,afade=t=out:st=%.1f:d=%.1f,"
                          "adelay=%d|%d" % (solape, seg, solape, int(i * seg * 1000), int(i * seg * 1000)),
                          total, ["aevalsrc='%s':s=%d:d=%.1f" % (expr, SR, seg + solape)]))
    # Piano suave: una nota en cada corte con imagen
    notas = []
    for k, toma in enumerate(TOMAS):
        if toma[0] is None or toma[5] == "espera":
            continue
        f = MELODIA[min(len(notas), len(MELODIA) - 1)]
        expr = ("0.22*(sin(2*PI*%.2f*t)+0.3*sin(4*PI*%.2f*t)+0.1*sin(6*PI*%.2f*t))"
                "*exp(-1.6*t)*(1-exp(-180*t))" % (f, f, f))
        ms = int((inicio[k] + 0.05) * 1000)
        notas.append(wav("nota%02d" % k, trabajo, "[0]lowpass=f=2600,adelay=%d|%d" % (ms, ms),
                         total, ["aevalsrc='%s':s=%d:d=5" % (expr, SR)]))
    # Acorde final más brillante sobre la aurora y el cierre
    brillo = "+".join("0.035*sin(2*PI*%.2f*t)" % f for f in [587.33, 739.99, 880.0, 1174.66])
    ms = int(inicio[-1] * 1000)
    notas.append(wav("brillo", trabajo, "[0]afade=t=in:d=2.5,adelay=%d|%d" % (ms, ms), total,
                     ["aevalsrc='%s':s=%d:d=%.2f" % (brillo, SR, total - inicio[-1])]))
    bruto = os.path.join(trabajo, "musica_bruta.wav")
    ff(*sum((["-i", p] for p in partes + notas), []), "-filter_complex",
       "amix=inputs=%d:normalize=0" % len(partes + notas), bruto)
    # Dinámica: desaparece en "nothing", crece en "everything", se apaga en el
    # sobre, estalla en la aurora y llena el cierre
    s = inicio
    env = envolvente([
        (0, 0), (3.0, 0.55), (s[3] - 0.05, 0.55), (s[3], 0.0), (s[4] - 0.05, 0.0),
        (s[4], 0.9), (s[5] + 1.0, 0.6), (s[9], 0.65), (s[12], 0.8), (s[13], 0.25),
        (s[14] - 0.05, 0.2), (s[14], 1.0), (fin_tomas + 1.0, 1.0), (total - 2.0, 0.85), (total, 0),
    ])
    seca = os.path.join(trabajo, "musica_seca.wav")
    ff("-i", bruto, "-af", "asetnsamples=n=256,volume=eval=frame:volume='%s'" % env, seca)
    out = os.path.join(trabajo, "musica.wav")
    con_reverb(seca, ir, out, seco=0.8, humedo=0.55)
    return out


def efectos(trabajo, inicio, fin_tomas, total, ir):
    """Efectos sintetizados, cada uno en su toma."""
    def ruido(c, seed, a=0.5):
        return "anoisesrc=d=%.2f:c=%s:a=%.2f:seed=%d:r=%d" % (total, c, a, seed, SR)
    capas = []

    def capa(nombre, k, graph, srcs, extra=0.0, vol=1.0):
        ini = max(inicio[k] - TOMAS[k][3], 0)
        fin = (inicio[k + 1] if k + 1 < len(TOMAS) else fin_tomas) + 0.6 + extra
        largo = fin - ini
        ms = int(ini * 1000)
        capas.append(wav("sfx_" + nombre, trabajo,
                         graph + ",atrim=0:%.3f,afade=t=in:d=0.35,afade=t=out:st=%.3f:d=0.7,"
                         "volume=%.2f,adelay=%d|%d" % (largo, max(largo - 0.7, 0), vol, ms, ms),
                         total, srcs))

    k = {t[5]: i for i, t in enumerate(TOMAS) if t[5]}
    capa("lago", k["lago"], "[0]lowpass=f=500,tremolo=f=0.3:d=0.7", [ruido("pink", 1)], vol=0.5)
    capa("viento", k["viento"], "[0][1]amix=inputs=2,bandpass=f=650:w=900,tremolo=f=0.12:d=0.6",
         [ruido("brown", 2, 0.8), ruido("pink", 3)], vol=0.9)
    grillos = ("0.06*sin(2*PI*4650*t)*gt(sin(2*PI*31*t),0)*gt(mod(t,0.62),0.47)"
               "+0.04*sin(2*PI*4320*t)*gt(sin(2*PI*27*t),0)*gt(mod(t+0.21,0.81),0.6)")
    capa("grillos", k["grillos"], "[0][1]amix=inputs=2:normalize=0",
         ["aevalsrc='%s':s=%d:d=%.2f" % (grillos, SR, total), ruido("brown", 4, 0.05)], vol=1.0)
    # Fuegos: tres estallidos con retumbe grave y chisporroteo
    est = []
    for i, d in enumerate([0.1, 1.15, 2.25]):
        est.append("[%d]lowpass=f=260,afade=t=out:st=0:d=1.8:curve=exp,volume=2.2,adelay=%d|%d[b%d];"
                   "[%d]highpass=f=2500,afade=t=out:st=0.15:d=1.4:curve=exp,volume=0.5,adelay=%d|%d[c%d]"
                   % (2 * i, int(d * 1000) + 0, int(d * 1000), i, 2 * i + 1, int(d * 1000) + 180,
                      int(d * 1000) + 180, i))
    srcs = []
    for i in range(3):
        srcs += ["anoisesrc=d=2:c=brown:a=0.9:seed=%d:r=%d" % (20 + i, SR),
                 "anoisesrc=d=2:c=velvet:a=0.5:seed=%d:r=%d" % (30 + i, SR)]
    capa("fuegos", k["fuegos"], ";".join(est) + ";[b0][c0][b1][c1][b2][c2]amix=inputs=6:normalize=0",
         srcs, vol=0.9)
    capa("ciudad", k["ciudad"], "[0]lowpass=f=140,volume=1.6", [ruido("brown", 5)], vol=0.6)
    capa("ola", k["ola"], "[0][1]amix=inputs=2,lowpass=f=1500,"
         "volume=eval=frame:volume='if(lt(t,1.3),t/1.3,exp(-(t-1.3)*0.9))'",
         [ruido("pink", 6, 0.9), ruido("brown", 7, 0.9)], vol=1.0)
    clink = "0.18*(sin(2*PI*2630*t)+0.6*sin(2*PI*3890*t))*exp(-9*t)"
    capa("mesa", k["mesa"], "[0]highpass=f=1200,lowpass=f=5000,volume=0.25[f];"
         "[1]adelay=1600|1600[c];[f][c]amix=inputs=2:normalize=0",
         [ruido("velvet", 8), "aevalsrc='%s':s=%d:d=2" % (clink, SR)], vol=0.7)
    gota = "0.25*sin(2*PI*(700+1800*exp(-28*t))*t)*exp(-14*t)"
    capa("quieto", k["quieto"], "[0]lowpass=f=260,volume=1.2[u];[1]adelay=900|900[g1];"
         "[2]adelay=2600|2600[g2];[u][g1][g2]amix=inputs=3:normalize=0",
         [ruido("brown", 9), "aevalsrc='%s':s=%d:d=1.5" % (gota, SR),
          "aevalsrc='%s':s=%d:d=1.5" % (gota.replace("700", "620"), SR)], vol=0.7)
    galope = ("(exp(-38*mod(t,0.42))+0.8*exp(-38*mod(t+0.42-0.09,0.42))"
              "+0.9*exp(-38*mod(t+0.42-0.18,0.42)))*sin(2*PI*58*t)*0.5")
    capa("galope", k["galope"], "[0][1]amix=inputs=2:normalize=0,lowpass=f=320",
         ["aevalsrc='%s':s=%d:d=%.2f" % (galope, SR, total), ruido("brown", 10, 0.3)], vol=1.4)
    tren = "(exp(-60*mod(t,0.55))+exp(-60*mod(t+0.55-0.12,0.55)))*sin(2*PI*140*t)*0.25"
    capa("tren", k["tren"], "[0]lowpass=f=900[r];[1]highpass=f=3500,volume=0.25[ll];"
         "[r][ll]amix=inputs=2:normalize=0",
         ["aevalsrc='%s':s=%d:d=%.2f" % (tren, SR, total), ruido("white", 11)], vol=0.8)
    capa("olas", k["olas"], "[0]lowpass=f=900,tremolo=f=0.2:d=0.85", [ruido("pink", 12, 0.9)], vol=0.7)
    capa("aeropuerto", k["aeropuerto"], "[0]lowpass=f=180,volume=1.4[h];"
         "[1]bandpass=f=900:w=1400,volume=eval=frame:volume='if(lt(t,1),0,if(lt(t,2.4),(t-1)/1.4,exp(-(t-2.4)*1.2)))'[j];"
         "[h][j]amix=inputs=2:normalize=0", [ruido("brown", 13), ruido("pink", 14, 0.9)], vol=0.7)
    # La espera: un soplo inverso que crece hasta el golpe de la aurora
    capa("espera", k["espera"], "[0]highpass=f=400,lowpass=f=6000,"
         "volume=eval=frame:volume='pow(t/2.9,3)'", [ruido("pink", 15, 0.8)], extra=-0.6, vol=0.9)
    # Golpes graves: aurora y aparición del logo
    golpe = "0.6*sin(2*PI*(30+28*exp(-3*t))*t)*exp(-1.4*t)*(1-exp(-300*t))"
    for nombre, t in (("golpe1", inicio[k["aurora"]]), ("golpe2", fin_tomas - 0.1)):
        ms = int(t * 1000)
        capas.append(wav(nombre, trabajo, "[0]lowpass=f=120,adelay=%d|%d" % (ms, ms), total,
                         ["aevalsrc='%s':s=%d:d=4.5" % (golpe, SR)]))
    capa("aurora", k["aurora"], "[0]highpass=f=1800,lowpass=f=4000,tremolo=f=0.4:d=0.5,volume=0.12",
         [ruido("pink", 16)], vol=0.6)

    bruto = os.path.join(trabajo, "efectos_secos.wav")
    ff(*sum((["-i", c] for c in capas), []), "-filter_complex",
       "amix=inputs=%d:normalize=0" % len(capas), bruto)
    out = os.path.join(trabajo, "efectos.wav")
    con_reverb(bruto, ir, out, seco=0.9, humedo=0.4)
    return out


def voz(piezas, trabajo, vo_ini, total, ir_corta):
    capas = []
    for n, t in sorted(vo_ini.items()):
        ms = int(t * 1000)
        capas.append(wav("vo%02d" % n, trabajo,
                         "[0]highpass=f=75,lowshelf=f=180:g=2,highshelf=f=7000:g=1.5,"
                         "acompressor=threshold=0.1:ratio=2.5:attack=8:release=160,adelay=%d|%d"
                         % (ms, ms), total, ["amovie=%s" % os.path.join(piezas, "vo", "%02d.wav" % n)]))
    seca = os.path.join(trabajo, "voz_seca.wav")
    ff(*sum((["-i", c] for c in capas), []), "-filter_complex",
       "amix=inputs=%d:normalize=0" % len(capas), seca)
    out = os.path.join(trabajo, "voz.wav")
    con_reverb(seca, ir_corta, out, seco=1.0, humedo=0.12)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("piezas")
    ap.add_argument("trabajo")
    ap.add_argument("--salida", default="off-the-list-film-v2.mp4")
    ap.add_argument("--solo-audio", action="store_true",
                    help="rehace la mezcla y reutiliza TRABAJO/video.mp4")
    a = ap.parse_args()
    os.makedirs(a.trabajo, exist_ok=True)

    inicio, fin_tomas, total = tiempos()
    vo_ini = {t[2]: inicio[k] + ENTRADA_VOZ for k, t in enumerate(TOMAS) if t[2]}
    vo_ini[3] = inicio[3] + 0.9                      # "nothing": más silencio antes
    vo_ini[13] = inicio[14] + 1.0                    # "surprised": tras el golpe
    vo_ini[14] = fin_tomas + 0.6                     # "Off The List"
    vo_ini[15] = vo_ini[14] + dur(os.path.join(a.piezas, "vo", "14.wav")) + 1.0
    print("Total %.1f s" % total)

    ir = reverb_ir(a.trabajo)
    ir_corta = reverb_ir(a.trabajo, 0.9, "ir_corta")
    pista_voz = voz(a.piezas, a.trabajo, vo_ini, total, ir_corta)
    pista_musica = musica(a.trabajo, inicio, fin_tomas, total, ir)
    pista_efectos = efectos(a.trabajo, inicio, fin_tomas, total, ir)
    mezcla = os.path.join(a.trabajo, "mezcla.wav")
    ff("-i", pista_voz, "-i", pista_musica, "-i", pista_efectos, "-filter_complex",
       "[0]asplit=3[v][sc][sc2];[1]volume=0.4[m];[m][sc]sidechaincompress=threshold=0.015:ratio=6:"
       "attack=40:release=650[md];[2]volume=0.36[e0];[e0][sc2]sidechaincompress=threshold=0.02:"
       "ratio=3:attack=40:release=500[e];[v][md][e]amix=inputs=3:normalize=0,"
       "alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), mezcla)
    pista_video = os.path.join(a.trabajo, "video.mp4")
    if not (a.solo_audio and os.path.exists(pista_video)):
        pista_video = video(a.piezas, a.trabajo, inicio, fin_tomas, total, vo_ini)
    ff("-i", pista_video, "-i", mezcla, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
       "-c:a", "aac", "-b:a", "320k", "-t", "%.3f" % total, "-movflags", "+faststart", a.salida)
    print("Listo:", a.salida)


if __name__ == "__main__":
    main()
