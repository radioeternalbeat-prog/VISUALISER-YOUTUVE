# Visualizer — Eternal Beat Medios

Visualizador audio-reactivo en HTML5 Canvas + Web Audio API. Simula un tacómetro
circular (estilo McLaren) que reacciona al bajo/kick de tu mezcla de Progressive/Melodic House.

## Cómo usarlo

1. Abrí `index.html` directamente en Chrome o Edge (doble clic, o arrastralo al navegador).
2. En los controles de abajo:
   - Cargá tu **archivo de audio** (la mezcla ya exportada en mp3/wav).
   - (Opcional) Cargá un **video de fondo en loop** (carretera nocturna, túnel, etc.).
3. Apretá **PLAY**.
4. Apretá **PANTALLA COMPLETA** para que ocupe toda la pantalla en 1920x1080.
5. Grabá la pantalla completa con **OBS Studio** (gratis) mientras se reproduce el set completo.
   - Configurá OBS a 1920x1080, 30fps, y grabá "Captura de Pantalla" o "Captura de Ventana".
   - Esto te da el archivo de video final con el visualizer ya sincronizado al audio.

## Logo

El logo real del canal (`../assets/logo/logo.png`) ya está integrado en el centro
del tacómetro y **pulsa/vibra sutilmente al ritmo del bajo/kick** (efecto descrito
en la ficha técnica original). Si el archivo no se encuentra, cae automáticamente
en un texto de respaldo ("ETERNAL BEAT / MEDIOS") para que el visualizer nunca se
rompa visualmente.

⚠️ **Importante sobre cómo abrir el archivo**: el logo se carga con una ruta
relativa (`../assets/logo/logo.png`). Esto funciona perfecto si abrís `index.html`
directamente por doble clic (protocolo `file://`) o si servís *toda la carpeta del
repositorio* con un servidor local. Si servís solo la carpeta `visualizer/` de forma
aislada, esa ruta relativa no va a encontrar la imagen y verás el texto de respaldo.

Para reemplazar el logo por una versión nueva, simplemente sobrescribí
`assets/logo/logo.png` (mismo nombre de archivo) o cambiá la ruta en el atributo
`src` del `<img id="logoImg">` dentro de `index.html`.

## Personalización rápida

Abrí `index.html` con un editor de texto y buscá estas partes:

- **Colores**: constantes `PAPAYA`, `PAPAYA_BRIGHT`, `STEEL` cerca de la línea 190.
- **Tamaño del logo**: `width:150px; height:150px;` en el selector `#logoLabel`.
- **Intensidad del pulso del logo**: en la función `draw()`, la línea
  `const logoScale = 1 + bassSmooth * 0.18 + ...` — subí el `0.18` si querés que
  vibre más fuerte.
- **Sensibilidad al bajo**: variable `bassBins` (cuántas frecuencias bajas se usan) y el
  multiplicador `* 1.4` / `* 1.3` en el cálculo del "RPM" — subilo si querés que reaccione más fuerte.

## Notas técnicas

- Todo corre localmente en el navegador, no sube tu audio a ningún servidor.
- El canvas está fijo en 1920x1080 y se escala automáticamente a la ventana (`fitStage()`),
  así que lo que grabás en pantalla completa siempre sale a resolución completa.
- Si preferís generar el video sin grabar pantalla (más prolijo, sin bordes de OBS),
  usá el pipeline de `../pipeline/` — ese enfoque combina audio + fondo + overlay
  directamente con FFmpeg, pero requiere exportar frames del visualizer (ver notas ahí).
