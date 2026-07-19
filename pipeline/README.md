# Pipeline de Renderizado — Eternal Beat Medios

Script en Python que usa **FFmpeg** para generar el video final combinando:
- Tu audio (la mezcla del DJ set)
- Un fondo en loop (video o imagen: carretera, túnel, etc.)
- Un ecualizador/espectro reactivo generado automáticamente desde el audio
  (coloreado en la paleta de marca)
- Tu logo centrado (opcional)
- El marco estilo "fibra de carbono" con línea Naranja Papaya
- Un título de texto superpuesto (opcional)

Este script **fue probado end-to-end** en este entorno con archivos de prueba
(audio, video de fondo e imagen de fondo) y generó correctamente video MP4
1920x1080 a 30fps con audio AAC.

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

⚠️ Un render de 1-2 horas en calidad completa puede tardar bastante
(dependiendo de tu CPU, entre 20 minutos y varias horas). Corré la
previsualización primero para no perder tiempo si algo está mal configurado.

### Parámetros disponibles

| Parámetro         | Obligatorio | Descripción                                                             |
|--------------------|:-----------:|---------------------------------------------------------------------------|
| `--audio`          | Sí          | Ruta al archivo de audio (mp3/wav) de tu mezcla.                         |
| `--background`     | Sí          | Ruta a un video (mp4) o imagen (png/jpg) de fondo. Se repite en loop.    |
| `--logo`           | No          | Ruta a un PNG con transparencia, se centra en pantalla.                 |
| `--title`          | No          | Texto a mostrar en la esquina inferior izquierda.                       |
| `--output`         | Sí          | Ruta del archivo MP4 final.                                              |
| `--test-seconds`   | No          | Renderiza solo los primeros N segundos (para previsualizar).            |
| `--crf`            | No          | Calidad de video, 18 por defecto (más bajo = mejor calidad, más pesado).|

## Notas importantes

- **El fondo se repite en loop automáticamente** si tu video de fondo es más
  corto que el audio (usando `-stream_loop -1`), así que podés usar un clip
  corto de 10-30 segundos de carretera/túnel y se repetirá durante toda la mezcla.
- **El espectro reactivo** se genera con el filtro `showcqt` de FFmpeg, que
  analiza el audio real (no es un efecto genérico) — reacciona a los bajos,
  kicks y a la energía general de la mezcla, tal como se buscaba con el
  concepto de "tacómetro".
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
