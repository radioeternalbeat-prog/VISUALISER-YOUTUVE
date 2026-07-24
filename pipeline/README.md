# Pipeline de Renderizado — Eternal Beat Medios

Script en Python que usa **FFmpeg** para generar el video final combinando:
- Tu audio (la mezcla del DJ set)
- Un fondo en loop (video o imagen: carretera, túnel, etc.)
- Un ecualizador/espectro reactivo generado automáticamente desde el audio,
  coloreado en **RGB estilo waveform de DJ** (Traktor/Serato/Rekordbox):
  rojo = graves, verde = medios, azul = agudos
- Tu logo centrado (opcional), con un "latido" sutil sincronizado
- Un segundo logo opcional que se alterna con el primero cada 5 minutos
  en loop durante todo el video (`--logo-b`)
- El marco estilo "fibra de carbono" con línea Naranja Papaya
- Un título de texto superpuesto (opcional)

Este script **fue probado end-to-end** en este entorno con archivos de prueba
y con una canción real, y generó correctamente video MP4 1920x1080 a 30fps
con audio AAC, con los 3 colores del espectro verificados visualmente
(rojo/verde/azul sólidos, sin mezclas raras de color).

## Requisitos

- **Python 3.8+**
- **FFmpeg** instalado y disponible en el PATH del sistema.
  - Windows: `winget install ffmpeg` o descargar de https://ffmpeg.org/download.html
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` (Debian/Ubuntu) o el gestor de paquetes de tu distro.

Verificá que esté instalado con:
```
ffmpeg -version
```

## Uso

### 1. Previsualización rápida (recomendado primero)

Antes de renderizar 1-2 horas completas, probá con unos segundos para revisar
que los colores, el logo y el fondo se vean bien:

```bash
python3 render.py \
  --audio "ruta/a/tu_mezcla.mp3" \
  --background "ruta/a/tu_fondo.mp4" \
  --logo "ruta/a/logo.png" \
  --title "Sesion 01" \
  --output "../output/preview.mp4" \
  --test-seconds 20
```

Abrí `../output/preview.mp4` y confirmá que se vea bien.

### 2. Render final completo (1-2 horas)

Una vez que estés conforme con la previsualización, quitá `--test-seconds`
para renderizar el archivo completo (usa la duración total de tu audio):

```bash
python3 render.py \
  --audio "ruta/a/tu_mezcla.mp3" \
  --background "ruta/a/tu_fondo.mp4" \
  --logo "ruta/a/logo.png" \
  --title "Sesion 01" \
  --output "../output/sesion01_final.mp4"
```

### 3. Con dos logos alternados cada 5 minutos (opcional)

Si tenés dos logos (por ejemplo, el logo del canal y un logo de DJ personal),
podés hacer que se alternen automáticamente cada 5 minutos durante todo el
video, con el mismo efecto de "latido":

```bash
python3 render.py \
  --audio "ruta/a/tu_mezcla.mp3" \
  --background "ruta/a/tu_fondo.mp4" \
  --logo "ruta/a/logo_canal.png" \
  --logo-b "ruta/a/logo_dj.png" \
  --title "Sesion 01" \
  --output "../output/sesion01_final.mp4"
```

⚠️ Un render de 1-2 horas en calidad completa puede tardar bastante
(dependiendo de tu CPU, entre 20 minutos y varias horas). Corré la
previsualización primero para no perder tiempo si algo está mal configurado.

### Parámetros disponibles

| Parámetro         | Obligatorio | Descripción                                                             |
|--------------------|:-----------:|---------------------------------------------------------------------------|
| `--audio`          | Sí          | Ruta al archivo de audio (mp3/wav) de tu mezcla.                         |
| `--background`     | Sí          | Ruta a un video (mp4) o imagen (png/jpg) de fondo. Se repite en loop.    |
| `--logo`           | No          | Ruta a un PNG con transparencia, se centra en pantalla.                 |
| `--logo-b`         | No          | Ruta a un segundo logo. Requiere `--logo`. Se alterna con el logo principal cada 5 minutos en loop. |
| `--title`          | No          | Texto a mostrar en la esquina inferior izquierda.                       |
| `--output`         | Sí          | Ruta del archivo MP4 final.                                              |
| `--test-seconds`   | No          | Renderiza solo los primeros N segundos (para previsualizar).            |
| `--crf`            | No          | Calidad de video, 18 por defecto (más bajo = mejor calidad, más pesado).|
| `--audio-bitrate`  | No          | Bitrate del audio (ej. `320k`, `128k`). Default `320k`.                 |
| `--output-scale`   | No          | Resolución final, ej. `960:540`. Útil para previews livianos que quepan en GitHub (<100MB). |
| `--maxrate` / `--bufsize` | No   | Límite de bitrate de video, para acotar el peso del archivo final.      |
| `--fps`            | No          | Frames por segundo de salida. Default 30. Bajalo (ej. 24) para previews más livianos. |

### Ejemplo: preview largo (~10 min) liviano para compartir

Para generar un preview de varios minutos que pese poco (para subir a GitHub,
WhatsApp, etc.), combiná `--output-scale`, `--fps` y `--maxrate` reducidos:

```bash
python3 render.py \
  --audio "tu_mezcla.mp3" \
  --background "tu_fondo.mp4" \
  --logo "logo_canal.png" --logo-b "logo_dj.png" \
  --output "../output/preview_10min.mp4" \
  --crf 28 --audio-bitrate 128k --output-scale 960:540 \
  --maxrate 900k --bufsize 1800k --fps 24
```

Esto genera aproximadamente 8MB por minuto de video (≈75MB para 9-10 minutos),
manteniendo buena legibilidad del logo, el espectro RGB y el marco de marca.
Para el render **final** en alta calidad (1080p), usá los valores por defecto
sin estas banderas de compresión.

## Notas importantes

- **El fondo se repite en loop automáticamente** si tu video de fondo es más
  corto que el audio (usando `-stream_loop -1`), así que podés usar un clip
  corto de 10-30 segundos de carretera/túnel y se repetirá durante toda la mezcla.
- **El espectro reactivo** se genera con el filtro `showcqt` de FFmpeg, que
  analiza el audio real (no es un efecto genérico) — reacciona a los bajos,
  kicks y a la energía general de la mezcla. Internamente, el audio se separa
  en 3 bandas (graves/medios/agudos) con filtros `lowpass`/`bandpass`/`highpass`,
  cada banda genera su propio espectro coloreado sólido (rojo/verde/azul), y
  se combinan con mezcla aditiva en espacio RGB — así cada color aparece solo
  donde hay energía real en esa banda, igual que el waveform de un reproductor
  DJ (Traktor, Serato, Rekordbox).
- **El "latido" del logo** es un zoom sinusoidal sutil (`scale` con `eval=frame`)
  con un ciclo de ~1.2 segundos, para simular el pulso audio-reactivo del
  visualizer JS (FFmpeg no puede leer el nivel de bajo en tiempo real tan
  fácilmente como JavaScript, así que se usa un pulso periódico consistente).
- **La alternancia de dos logos** (`--logo-b`) usa la opción `enable` de
  `overlay` con una expresión `mod(t, 600)` para mostrar el logo A los
  primeros 5 minutos de cada ciclo de 10 minutos, y el logo B los siguientes
  5 — repitiéndose en loop durante toda la duración del video.
- Si no tenés un logo aún, simplemente omití `--logo` y el video se genera igual
  (sin logo centrado). El marco de fibra de carbono y el espectro se ven de todas formas.
- Si querés el efecto exacto del **visualizer circular tipo tacómetro** (con aguja,
  zona roja, y el logo vibrando), usá en cambio la carpeta `../visualizer/`
  y grabá la pantalla con OBS — ese visualizer HTML tiene el diseño más elaborado
  descrito en la ficha técnica. Este pipeline de FFmpeg es la alternativa
  "100% automática, sin grabar pantalla", con un espectro más simple pero
  igual de reactivo al audio real.

## Solución de problemas

- **"no se encontró 'ffmpeg' en el PATH"** → instalá FFmpeg (ver Requisitos arriba).
- **El texto del título no aparece** → tu sistema no tiene una fuente TTF en las
  rutas que el script busca automáticamente. Editá la función `find_system_font()`
  en `render.py` y agregá la ruta a una fuente `.ttf` que tengas instalada
  (por ejemplo, una fuente cursiva estilo "racing" si conseguís una en Google Fonts).
- **El render tarda demasiado** → bajá la calidad temporalmente con `--crf 23` para
  pruebas, y volvé a `--crf 18` (o menor) solo para el render final.
