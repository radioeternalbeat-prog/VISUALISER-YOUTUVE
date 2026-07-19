#!/usr/bin/env python3
"""
============================================================
 ETERNAL BEAT MEDIOS - Pipeline de Renderizado de Video
============================================================
Combina automáticamente (sin grabar pantalla):
  - Tu pista de audio (el DJ set / mezcla ya exportada)
  - Un video o imagen de fondo en loop (carretera, túnel, etc.)
  - Un espectro/ecualizador reactivo generado directamente por FFmpeg
    a partir del audio (colorizado en Naranja Papaya / Azul Eléctrico)
  - Un marco estilo "fibra de carbono" con acento papaya
  - (Opcional) tu logo centrado

Requiere: Python 3.8+ y FFmpeg instalado y disponible en el PATH.

USO BÁSICO:
    python3 render.py --audio mezcla.mp3 --background carretera.mp4 \
        --logo logo.png --output ../output/sesion01.mp4

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

# Paleta de marca
CARBON = "0x0a0a0d"
PAPAYA = "0xFF6A13"
BLUE = "0x00B4FF"

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


def build_filter_complex(has_logo, has_background_image, title_text):
    """
    Construye la cadena de filtros de FFmpeg:
      [0:v] fondo (video o imagen en loop) -> escalado/cropeado a 1920x1080
      [1:a] audio -> genera espectro reactivo (showcqt) colorizado
      overlay del espectro (con clave de color negro = transparente) sobre el fondo
      overlay del logo centrado (si existe)
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
    #    similar a un ecualizador de barras). Lo coloreamos manualmente y lo
    #    dejamos con fondo negro para poder recortarlo por color (colorkey).
    parts.append(
        f"[1:a]showcqt=s={WIDTH}x{HEIGHT}:bar_g=2:sono_g=3:basefreq=40:"
        f"endfreq=9000:tc=0.33:count=1,"
        f"format=rgba,"
        f"colorkey=0x000000:0.12:0.06[cqt_keyed]"
    )

    # 3. Superponer el espectro sobre el fondo.
    parts.append("[bg][cqt_keyed]overlay=0:0:shortest=1[stage1]")

    last = "stage1"

    # 4. Logo centrado (opcional).
    if has_logo:
        parts.append(f"[2:v]scale=280:-1[logo]")
        parts.append(
            f"[{last}][logo]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[stage2]"
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
    ap.add_argument("--logo", required=False, default=None, help="Ruta al logo (PNG con transparencia). Opcional.")
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
    args = ap.parse_args()

    check_ffmpeg()

    for p, label in [(args.audio, "audio"), (args.background, "background")]:
        if not os.path.exists(p):
            sys.exit(f"ERROR: no se encontró el archivo de {label}: {p}")
    if args.logo and not os.path.exists(args.logo):
        sys.exit(f"ERROR: no se encontró el logo: {args.logo}")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)

    duration = get_duration_seconds(args.audio)
    if args.test_seconds:
        duration = min(duration, args.test_seconds)

    bg_is_image = os.path.splitext(args.background)[1].lower() in IMAGE_EXTS

    filter_complex, final_label = build_filter_complex(
        has_logo=bool(args.logo),
        has_background_image=bg_is_image,
        title_text=args.title,
    )

    cmd = ["ffmpeg", "-y"]

    # Input 0: fondo
    if bg_is_image:
        cmd += ["-loop", "1", "-i", args.background]
    else:
        cmd += ["-stream_loop", "-1", "-i", args.background]

    # Input 1: audio
    cmd += ["-i", args.audio]

    # Input 2: logo (opcional)
    if args.logo:
        cmd += ["-loop", "1", "-i", args.logo]

    cmd += [
        "-filter_complex", filter_complex,
        "-map", f"[{final_label}]",
        "-map", "1:a",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
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
