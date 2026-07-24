#!/usr/bin/env python3
"""
============================================================
 ETERNAL BEAT MEDIOS - Pipeline de Renderizado de Video
============================================================
Combina automáticamente (sin grabar pantalla):
  - Tu pista de audio (el DJ set / mezcla ya exportada)
  - Un video o imagen de fondo en loop (carretera, túnel, etc.)
  - Un espectro/ecualizador reactivo generado directamente por FFmpeg
    a partir del audio, coloreado en RGB estilo waveform de DJ
    (Traktor/Serato/Rekordbox: rojo=graves, verde=medios, azul=agudos)
  - Un marco estilo "fibra de carbono" con acento papaya
  - (Opcional) tu logo centrado, con un "latido" sutil sincronizado
  - (Opcional) un segundo logo que se alterna con el primero cada 5
    minutos en loop durante todo el video (--logo-b)

Requiere: Python 3.8+ y FFmpeg instalado y disponible en el PATH.

USO BÁSICO:
    python3 render.py --audio mezcla.mp3 --background carretera.mp4 \
        --logo logo.png --output ../output/sesion01.mp4

USO CON DOS LOGOS ALTERNADOS (cada 5 minutos, en loop):
    python3 render.py --audio mezcla.mp3 --background carretera.mp4 \
        --logo logo.png --logo-b logo-dj.png --output ../output/sesion01.mp4

PRUEBA RÁPIDA (solo primeros 20 segundos, para revisar el resultado
antes de renderizar 1-2 horas completas):
    python3 render.py --audio mezcla.mp3 --background carretera.mp4 \
        --output ../output/preview.mp4 --test-seconds 20
============================================================
"""

import argparse
import os
import shutil
import subprocess
import sys

WIDTH = 1920
HEIGHT = 1080

# Paleta de marca (identidad real del canal: Negro Carbono / Naranja Papaya / Gris Acero)
CARBON = "0x0a0a0d"
PAPAYA = "0xFF6A13"
STEEL = "0xC9CDD3"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "ERROR: no se encontró 'ffmpeg' en el PATH.\n"
            "Instalalo desde https://ffmpeg.org/download.html "
            "o (en Windows) con 'winget install ffmpeg'."
        )


def get_duration_seconds(path):
    """Usa ffprobe para obtener la duración de un archivo de audio/video."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


# Paleta RGB estilo waveform de DJ (Traktor / Serato / Rekordbox)
# Convencion estandar: graves = rojo, medios = verde, agudos = azul.
#
# El parametro cscheme de showcqt colorea cada barra por AMPLITUD (degradado
# vertical dentro de la barra), no por posicion de frecuencia -- por eso un
# cscheme "rojo->verde" simple se ve amarillo (mezcla) en vez de barras rojas
# solidas en graves. Para lograr el efecto real de "colorear por banda de
# frecuencia" (como el waveform de un reproductor DJ), se generan TRES capas
# de espectro por separado, cada una alimentada con el audio filtrado a una
# banda de frecuencia (graves/medios/agudos) y coloreada de forma SOLIDA
# (mismo color en ambos extremos de cscheme), y se combinan con mezcla
# aditiva (blend=addition). Asi cada banda "ilumina" su propio color solo
# donde tiene energia real, igual que un analizador de espectro de DJ.
DJ_BASS_HZ = 200      # graves: 40-200 Hz aprox
DJ_MID_HZ = 2000      # medios: 200-2000 Hz aprox (agudos: 2000-9000 Hz)
DJ_CSCHEME_RED   = "1|0|0|1|0|0"   # rojo solido (graves)
DJ_CSCHEME_GREEN = "0|1|0|0|1|0"   # verde solido (medios)
DJ_CSCHEME_BLUE  = "0|0.2|1|0|0.2|1"  # azul solido (agudos)

# Cada cuanto tiempo alternar entre logo A y logo B, en el render final (segundos)
LOGO_SWITCH_INTERVAL_S = 5 * 60  # 5 minutos
LOGO_SWITCH_FADE_S = 0.6         # duracion del fundido cruzado entre logos
LOGO_BASE_SCALE = 280            # ancho en px del logo dentro del video


def build_filter_complex(has_logo, has_logo_b, has_background_image, title_text, duration, output_scale=None):
    """
    Construye la cadena de filtros de FFmpeg:
      [0:v] fondo (video o imagen en loop) -> escalado/cropeado a 1920x1080
      [1:a] audio -> genera espectro reactivo (showcqt) colorizado en RGB estilo DJ
      overlay del espectro (con clave de color negro = transparente) sobre el fondo
      overlay del/los logo(s) centrado(s), con "latido" y alternancia cada 5 min si hay 2
      marco tipo fibra de carbono con acento papaya
      (opcional) texto del título en la esquina inferior
    """
    parts = []

    # 1. Fondo: escalar y recortar a 1920x1080, oscurecer un poco para que
    #    el visualizer y el texto resalten (estética "night drive").
    parts.append(
        f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},eq=brightness=-0.08:saturation=1.25[bg]"
    )

    # 2. Espectro reactivo generado desde el audio (showcqt = Constant-Q Transform,
    #    similar a un ecualizador de barras), coloreado en RGB estilo waveform de
    #    DJ (rojo=graves, verde=medios, azul=agudos). Se generan TRES capas de
    #    espectro, cada una alimentada con el audio ya filtrado a su banda de
    #    frecuencia (graves/medios/agudos) y coloreada de forma solida, y se
    #    combinan con mezcla aditiva para que solo brille el color de la banda
    #    con energia real en cada punto -- igual que un analizador de espectro
    #    de DJ real, no un degrade generico.
    parts.append(f"[1:a]asplit=3[a_bass][a_mid][a_treble]")
    parts.append(f"[a_bass]lowpass=f={DJ_BASS_HZ}[a_bass_f]")
    parts.append(f"[a_mid]bandpass=f={(DJ_BASS_HZ+DJ_MID_HZ)//2}:width_type=h:w={DJ_MID_HZ-DJ_BASS_HZ}[a_mid_f]")
    parts.append(f"[a_treble]highpass=f={DJ_MID_HZ}[a_treble_f]")

    # sono_h=0 desactiva el "sonograma" (historial de espectro que showcqt
    # dibuja debajo de las barras) -- sin esto, al sumar 3 capas con blend
    # aditivo, el sonograma de cada capa se saturaba y pintaba toda la
    # pantalla de un color solido (magenta), tapando el fondo por completo.
    parts.append(
        f"[a_bass_f]showcqt=s={WIDTH}x{HEIGHT}:bar_g=1.5:sono_h=0:basefreq=40:"
        f"endfreq=9000:tc=0.33:count=1:cscheme={DJ_CSCHEME_RED}[cqt_bass]"
    )
    parts.append(
        f"[a_mid_f]showcqt=s={WIDTH}x{HEIGHT}:bar_g=1.5:sono_h=0:basefreq=40:"
        f"endfreq=9000:tc=0.33:count=1:cscheme={DJ_CSCHEME_GREEN}[cqt_mid]"
    )
    parts.append(
        f"[a_treble_f]showcqt=s={WIDTH}x{HEIGHT}:bar_g=1.5:sono_h=0:basefreq=40:"
        f"endfreq=9000:tc=0.33:count=1:cscheme={DJ_CSCHEME_BLUE}[cqt_treble]"
    )
    # IMPORTANTE: convertir cada capa a RGB (format=gbrp) antes de blend=addition.
    # El filtro 'blend' opera en el espacio de color nativo del input; si se
    # deja en YUV, sumar los canales de crominancia genera artefactos de
    # color saturado (aparecia todo en magenta). Convirtiendo a RGB primero,
    # la suma es aditiva real por canal R/G/B, como se espera.
    parts.append(f"[cqt_bass]format=gbrp[cqt_bass_rgb]")
    parts.append(f"[cqt_mid]format=gbrp[cqt_mid_rgb]")
    parts.append(f"[cqt_treble]format=gbrp[cqt_treble_rgb]")
    parts.append(
        f"[cqt_bass_rgb][cqt_mid_rgb]blend=all_mode=addition[cqt_bm]"
    )
    parts.append(
        f"[cqt_bm][cqt_treble_rgb]blend=all_mode=addition,"
        f"format=rgba,"
        f"colorkey=0x000000:0.12:0.06[cqt_keyed]"
    )

    # 3. Superponer el espectro sobre el fondo.
    parts.append("[bg][cqt_keyed]overlay=0:0:shortest=1[stage1]")

    last = "stage1"

    # 4. Logo(s): "latido" sutil sincronizado a un pulso periodico (simulando el
    #    ritmo, ya que FFmpeg no puede leer el nivel de bajo en tiempo real como
    #    el visualizer JS) + alternancia cada 5 minutos si hay 2 logos.
    if has_logo and has_logo_b:
        # Dos logos: cada uno escalado con un "latido" (zoom sinusoidal),
        # y alternados con fade cada LOGO_SWITCH_INTERVAL_S segundos.
        # eval=frame es necesario para que 'scale' pueda usar la variable de tiempo 't'.
        parts.append(
            f"[2:v]scale={LOGO_BASE_SCALE}:-1,"
            f"scale=w='iw*(1+0.05*sin(2*PI*t/1.2))':h='ih*(1+0.05*sin(2*PI*t/1.2))':eval=frame"
            f"[logoA_pulse]"
        )
        parts.append(
            f"[3:v]scale={LOGO_BASE_SCALE}:-1,"
            f"scale=w='iw*(1+0.05*sin(2*PI*t/1.2))':h='ih*(1+0.05*sin(2*PI*t/1.2))':eval=frame"
            f"[logoB_pulse]"
        )
        # Alternancia por tiempo: A visible en el tramo [0, 5min), B en [5min, 10min), etc.
        # Se usa 'enable' con una expresion modulo para que se repita en loop durante todo el video.
        cycle = LOGO_SWITCH_INTERVAL_S * 2
        enable_a = f"lt(mod(t\\,{cycle})\\,{LOGO_SWITCH_INTERVAL_S})"
        enable_b = f"gte(mod(t\\,{cycle})\\,{LOGO_SWITCH_INTERVAL_S})"
        parts.append(
            f"[{last}][logoA_pulse]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:"
            f"enable='{enable_a}'[stage_logoA]"
        )
        parts.append(
            f"[stage_logoA][logoB_pulse]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:"
            f"enable='{enable_b}'[stage2]"
        )
        last = "stage2"
    elif has_logo:
        # Un solo logo: mismo "latido" sutil, sin alternancia.
        parts.append(
            f"[2:v]scale={LOGO_BASE_SCALE}:-1,"
            f"scale=w='iw*(1+0.05*sin(2*PI*t/1.2))':h='ih*(1+0.05*sin(2*PI*t/1.2))':eval=frame"
            f"[logo_pulse]"
        )
        parts.append(
            f"[{last}][logo_pulse]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[stage2]"
        )
        last = "stage2"

    # 5. Marco "fibra de carbono": borde oscuro grueso + línea papaya interior.
    parts.append(
        f"[{last}]drawbox=x=0:y=0:w={WIDTH}:h={HEIGHT}:color={CARBON}:t=18,"
        f"drawbox=x=18:y=18:w={WIDTH-36}:h={HEIGHT-36}:color={PAPAYA}:t=4[framed]"
    )
    last = "framed"

    # 6. Título opcional (esquina inferior izquierda), solo si hay fuente
    #    disponible en el sistema y el usuario pasó --title.
    if title_text:
        font = find_system_font()
        if font:
            safe_text = title_text.replace(":", r"\:").replace("'", r"\'")
            parts.append(
                f"[{last}]drawtext=fontfile='{font}':text='{safe_text}':"
                f"x=40:y=main_h-80:fontsize=42:fontcolor={PAPAYA}:"
                f"shadowcolor=black:shadowx=2:shadowy=2[titled]"
            )
            last = "titled"

    # 7. Downscale final opcional (para previews livianos: menos píxeles a
    #    codificar = archivo más chico y render más rápido, sin tocar el
    #    resto de la composición que sigue calculándose en HD).
    if output_scale:
        parts.append(f"[{last}]scale={output_scale}[scaled_out]")
        last = "scaled_out"

    filter_complex = ";".join(parts)
    return filter_complex, last


def find_system_font():
    """Busca una fuente TTF común disponible en el sistema (best-effort)."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Renderiza el video final de Eternal Beat Medios (audio + fondo + visualizer + marco)."
    )
    ap.add_argument("--audio", required=True, help="Ruta al archivo de audio (mp3/wav) del DJ set.")
    ap.add_argument("--background", required=True, help="Ruta al video o imagen de fondo en loop.")
    ap.add_argument("--logo", required=False, default=None, help="Ruta al logo principal (PNG con transparencia). Opcional.")
    ap.add_argument("--logo-b", required=False, default=None,
                     help="Ruta a un segundo logo (ej. logo de DJ). Si se especifica junto con --logo, "
                          "ambos se alternan cada 5 minutos en loop durante todo el video, con un latido sutil.")
    ap.add_argument("--title", required=False, default=None, help="Texto de título a mostrar (opcional).")
    ap.add_argument("--output", required=True, help="Ruta del archivo MP4 final.")
    ap.add_argument(
        "--test-seconds", type=float, default=None,
        help="Si se especifica, renderiza solo los primeros N segundos (para previsualizar rápido)."
    )
    ap.add_argument(
        "--crf", type=int, default=18,
        help="Calidad de video (menor = mejor calidad, mayor peso). Default 18 (alta calidad)."
    )
    ap.add_argument(
        "--audio-bitrate", type=str, default="320k",
        help="Bitrate del audio de salida (ej. '320k', '128k'). Default 320k."
    )
    ap.add_argument(
        "--output-scale", type=str, default=None,
        help="Escala de salida final, ej. '1280:720', para generar previews livianos "
             "(reduce el tamaño de archivo y el tiempo de render, sin afectar la composición interna)."
    )
    ap.add_argument("--maxrate", type=str, default="50000k", help="Bitrate máximo de video (limita el peso del archivo).")
    ap.add_argument("--bufsize", type=str, default="50000k", help="Tamaño de buffer para --maxrate.")
    ap.add_argument("--fps", type=int, default=30, help="Frames por segundo de salida. Bajalo (ej. 20) para previews más livianos.")
    args = ap.parse_args()

    check_ffmpeg()

    for p, label in [(args.audio, "audio"), (args.background, "background")]:
        if not os.path.exists(p):
            sys.exit(f"ERROR: no se encontró el archivo de {label}: {p}")
    if args.logo and not os.path.exists(args.logo):
        sys.exit(f"ERROR: no se encontró el logo: {args.logo}")
    if args.logo_b and not os.path.exists(args.logo_b):
        sys.exit(f"ERROR: no se encontró el segundo logo (--logo-b): {args.logo_b}")
    if args.logo_b and not args.logo:
        sys.exit("ERROR: --logo-b requiere que tambien especifiques --logo (el logo principal).")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)

    duration = get_duration_seconds(args.audio)
    if args.test_seconds:
        duration = min(duration, args.test_seconds)

    bg_is_image = os.path.splitext(args.background)[1].lower() in IMAGE_EXTS

    filter_complex, final_label = build_filter_complex(
        has_logo=bool(args.logo),
        has_logo_b=bool(args.logo_b),
        has_background_image=bg_is_image,
        title_text=args.title,
        duration=duration,
        output_scale=args.output_scale,
    )

    cmd = ["ffmpeg", "-y"]

    # Input 0: fondo
    if bg_is_image:
        cmd += ["-loop", "1", "-i", args.background]
    else:
        cmd += ["-stream_loop", "-1", "-i", args.background]

    # Input 1: audio
    cmd += ["-i", args.audio]

    # Input 2: logo principal (opcional)
    if args.logo:
        cmd += ["-loop", "1", "-i", args.logo]

    # Input 3: segundo logo, para alternancia cada 5 min (opcional)
    if args.logo_b:
        cmd += ["-loop", "1", "-i", args.logo_b]

    cmd += [
        "-filter_complex", filter_complex,
        "-map", f"[{final_label}]",
        "-map", "1:a",
        "-t", str(duration),
        "-r", str(args.fps),
        "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", args.audio_bitrate,
        "-movflags", "+faststart",
        "-maxrate", args.maxrate, "-bufsize", args.bufsize,
        args.output,
    ]

    print("Ejecutando FFmpeg...\n")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit("\nERROR: FFmpeg falló. Revisá el mensaje de error arriba.")

    print(f"\n✅ Listo. Video generado en: {args.output}")
    print(f"   Duración: {duration:.1f} segundos")


if __name__ == "__main__":
    main()
