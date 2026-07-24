# Thumbnail — Eternal Beat Medios

Plantilla de miniatura en **SVG editable** (`thumbnail.svg`), 1280x720 (proporción
oficial de miniaturas de YouTube). Ya renderizada y verificada visualmente en
`thumbnail_preview.png`.

## Qué incluye (adaptado a la identidad real del canal)

- **POV de cabina deportiva**: marco tipo parabrisas + pilares A en fibra de carbono.
- **Tablero digital en Gris Acero**: tacómetro (RPM) a la izquierda, velocímetro
  a la derecha, display central "NIGHT DRIVE".
- **Carretera nocturna / túnel** con líneas de fuga hacia un punto de fuga con
  resplandor gris/plateado, y estelas de velocidad (motion blur) en blanco/gris.
- **Marco exterior de fibra de carbono** con línea de acento Naranja Papaya.
- **Título "Night Drive"** en tipografía cursiva estilo racing, color Naranja Papaya
  con efecto de resplandor (glow).
- **"SESSION #01"** y el subtítulo de género musical, en blanco/gris acero.
- **Logo real del canal** (ícono de onda de audio) embebido arriba del título.
- Marca de texto "ETERNAL BEAT MEDIOS" en la esquina inferior derecha.

## Cómo editarla

El archivo `thumbnail.svg` es texto plano — se puede abrir y editar con:

1. **Editor de código** (VS Code, Notepad++, etc.) — modificá directamente los
   valores de texto, por ejemplo:
   ```xml
   <text ...>Night Drive</text>
   <text ...>SESSION #01</text>
   ```
2. **Inkscape** (gratis) o **Figma** (importando el SVG) — para editar visualmente,
   mover elementos, cambiar fuentes, etc.
3. **Illustrator / Affinity Designer** — también abren SVG directamente.

### Cambios más comunes

- **Cambiar el número de sesión**: buscá `SESSION #01` y reemplazá el número.
- **Usar una fuente cursiva real de "racing"**: el SVG usa `'Brush Script MT', 'Segoe Script', cursive`
  como fallback. Para un resultado idéntico al de referencias de canales grandes,
  descargá una fuente tipo "Racing Sans One" o "Monoton" de Google Fonts y
  reemplazá el `font-family` del título.
- **Cambiar el logo**: el logo real ya está embebido dentro del SVG como imagen
  en base64 (buscá el tag `<image ... xlink:href="data:image/png;base64,...">`
  cerca del final del archivo). Para reemplazarlo por una versión nueva, generá
  el base64 de tu PNG (`base64 -w0 tu_logo.png`) y reemplazá el contenido entre
  `base64,` y la comilla de cierre en ambos atributos `href` y `xlink:href`.
- **Cambiar colores**: los degradados están definidos arriba en `<defs>`
  (`papayaText`, `dashGlow`, `streakBlue`, etc.) — modificá los valores `stop-color`.

## Cómo exportar a PNG/JPG para subir a YouTube

Si tenés Inkscape instalado:
```bash
inkscape thumbnail.svg --export-type=png --export-filename=thumbnail_final.png -w 1280 -h 720
```

O con `rsvg-convert` (usado para generar la preview de este proyecto):
```bash
rsvg-convert -w 1280 -h 720 thumbnail.svg -o thumbnail_final.png
```

YouTube requiere: JPG/PNG/GIF/BMP, menor a 2MB, mínimo 1280x720, proporción 16:9.
Este archivo ya cumple esos requisitos.
