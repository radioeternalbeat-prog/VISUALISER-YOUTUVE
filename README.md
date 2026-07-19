# Eternal Beat Medios — Kit de Lanzamiento "Sesión #01"

Kit técnico completo para producir y publicar el primer video del canal de
YouTube de tu radio online, con la identidad visual estilo McLaren (fibra de
carbono + naranja papaya + azul eléctrico) y el concepto "Night Drive".

```
eternal-beat-medios/
├── visualizer/     → App web para visualizar tu mezcla en vivo (tacómetro reactivo)
├── pipeline/       → Script automático que genera el video final (audio+fondo+overlay)
├── thumbnail/      → Miniatura SVG editable, ya renderizada y verificada
├── metadata/       → Título, descripción, tags y checklist SEO para YouTube
├── assets/
│   ├── backgrounds/ → Poné aquí tus videos/imágenes de fondo (carretera, túnel)
│   └── logo/         → Poné aquí el logo de Eternal Beat Medios
└── output/          → Los videos finales renderizados van a parar aquí
```

---

## Flujo de trabajo paso a paso (de la mezcla al video publicado)

### Paso 0 — Lo que necesitás tener listo antes de empezar
- [ ] Tu mezcla de DJ set exportada en audio (mp3 o wav), de mínimo 1 hora.
- [ ] Un video o imagen de fondo tipo "carretera nocturna / túnel" (podés
      conseguir clips libres de derechos en Pexels, Pixabay o Coverr — buscá
      "night drive", "highway night", "tunnel lights").
- [ ] (Opcional pero recomendado) el logo de Eternal Beat Medios en PNG con
      fondo transparente.
- [ ] El tracklist de tu mezcla (artista + nombre de track + minuto en que
      empieza cada uno) — lo vas a necesitar para la descripción de YouTube.

### Paso 1 — Elegí cómo generar el video final
Tenés **dos caminos**, no hace falta usar los dos:

**Camino A — Visualizer interactivo + grabación de pantalla (más elaborado)**
Usá `visualizer/index.html`. Tiene el diseño más fiel al brief original:
tacómetro circular con aguja, zona roja, ecualizador de barras alrededor,
logo vibrando al ritmo del bajo. Se reproduce en el navegador y lo grabás
con OBS Studio mientras suena tu mezcla completa.
→ Ver instrucciones detalladas en `visualizer/README.md`.

**Camino B — Pipeline automático con FFmpeg (más rápido, sin grabar pantalla)**
Usá `pipeline/render.py`. Le pasás tu audio + tu video de fondo (+ logo
opcional) y te genera el MP4 final automáticamente, con un espectro
reactivo real generado desde tu audio.
→ Ver instrucciones detalladas en `pipeline/README.md`.

*Recomendación: probá el Camino B primero (es más rápido de iterar), y si
querés el efecto más elaborado del tacómetro con aguja, usá el Camino A para
el video definitivo.*

### Paso 2 — Generá y revisá una previsualización corta
No renders de 1-2 horas a la primera. Generá 15-30 segundos, mirá que los
colores, el logo y el fondo se vean como esperás, y ajustá antes de hacer
el render completo (que puede tardar bastante tiempo).

### Paso 3 — Renderizá el video final completo
Una vez conforme con la preview, generá el archivo completo. Guardalo en
`output/`.

### Paso 4 — Prepará la miniatura
Abrí `thumbnail/thumbnail.svg`, personalizalo si querés (número de sesión,
logo real, fuente cursiva definitiva), y exportalo a PNG:
```bash
rsvg-convert -w 1280 -h 720 thumbnail/thumbnail.svg -o thumbnail/thumbnail_final.png
```
→ Más detalles en `thumbnail/README.md`.

### Paso 5 — Completá los metadatos y subí a YouTube
Abrí `metadata/sesion01_metadata.md` y:
1. Reemplazá el tracklist de ejemplo por el real, con timestamps.
2. Completá tus links reales de redes sociales y email de contacto.
3. Copiá el título, la descripción y los tags directo a YouTube Studio.
4. Subí el video de `output/` y la miniatura de `thumbnail/`.
5. Repasá el checklist final antes de publicar (derechos de los tracks,
   playlist creada, etc.)

---

## Resumen de las herramientas (qué hace cada una)

| Carpeta | Qué es | Cuándo usarla |
|---|---|---|
| `visualizer/` | Web app HTML/JS, corre en el navegador | Para el efecto visual más elaborado (tacómetro con aguja), grabando con OBS |
| `pipeline/` | Script Python que usa FFmpeg | Para generar el video automáticamente sin grabar pantalla |
| `thumbnail/` | Plantilla SVG editable | Para la miniatura del video, editable en cualquier editor de SVG |
| `metadata/` | Documento de texto con título/descripción/tags | Para copiar y pegar al publicar en YouTube |

## Sobre la estética de marca (para mantener consistencia en futuros videos)

- **Naranja Papaya**: `#FF6A13` (acentos, título, marco)
- **Azul Eléctrico**: `#00B4FF` (tablero, datos digitales, glow)
- **Fibra de Carbono / Carbón**: `#0a0a0d` (fondos, marcos, estructura)
- **Tipografía título**: cursiva estilo racing (ver notas de fuente en `thumbnail/README.md`)
- **Concepto**: "Night Drive" — velocidad, cabina de auto deportivo, ciudad/carretera nocturna

Guardá esta paleta para que todos los videos futuros del canal mantengan la
misma identidad visual y el algoritmo/audiencia empiece a reconocer tu
"marca" en el feed.

## Cosas importantes que NO están automatizadas (a propósito)

- **Derechos de los tracks**: este kit no verifica licencias de música. Sos
  vos quien tiene que confirmar que tenés derecho a usar cada track (compra,
  licencia, royalty-free, o que sean producciones propias/de tu sello).
- **Calidad de la mezcla de audio**: el pipeline no mezcla ni masteriza tu
  audio, solo lo combina con el video. La mezcla en sí la hacés vos (o el DJ)
  en tu software habitual (Traktor, Serato, Ableton, etc.)
- **Publicación real en YouTube**: estas herramientas preparan todos los
  archivos, pero la subida final y configuración en YouTube Studio la hacés
  vos manualmente (o me pedís que te guíe paso a paso cuando llegues a esa parte).
