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

## Logo(s) y alternancia cada 5 minutos

El visualizer soporta **dos logos** que se alternan automáticamente cada 5
minutos en loop mientras el audio se reproduce:

- **Logo A** (principal): `../assets/logo/logo.png` — el logo del canal.
- **Logo B** (secundario): `../assets/logo/logo-dj.png` — el logo de DJ
  personal (ej. "DJ Danilo Gonzalez"). Ya integrado y verificado.

El contenedor del logo (`#logoLabel`) usa `object-fit: contain`, así que
acepta logos con **cualquier proporción** (cuadrados como el del canal, o
anchos/rectangulares como el de DJ) sin deformarlos — cada imagen se ajusta
manteniendo su relación de aspecto original dentro del mismo espacio.

Ambos logos:
- **Pulsan/laten sutilmente al ritmo del bajo/kick** en todo momento.
- Al momento de alternar entre uno y otro, se genera un **"latido" extra**
  (doble pulso rápido) además del fade cruzado entre imágenes.
- Tienen un **aura de energía** detrás (canvas `#logoAura`) que se mimetiza
  con los mismos colores RGB del ecualizador circular (ver sección de abajo).

Si `logo-dj.png` no existe, el visualizer detecta el error de carga
automáticamente y **no alterna** — se queda mostrando solo el logo A sin
romperse visualmente. Si ninguno de los dos logos carga, cae en un texto de
respaldo ("ETERNAL BEAT / MEDIOS").

⚠️ **Importante sobre cómo abrir el archivo**: los logos se cargan con rutas
relativas (`../assets/logo/...`). Esto funciona perfecto si abrís `index.html`
directamente por doble clic (protocolo `file://`) o si servís *toda la carpeta
del repositorio* con un servidor local. Si servís solo la carpeta `visualizer/`
de forma aislada, esas rutas relativas no van a encontrar las imágenes.

## Colores RGB estilo waveform de DJ (Traktor / Serato / Rekordbox)

El ecualizador circular y el arco del tacómetro ya no usan un solo color —
cada barra se colorea según su banda de frecuencia, con la convención
estándar de las formas de onda de reproductores de DJ:

- 🔴 **Rojo** = graves (bass/kick)
- 🟢 **Verde** = medios (voces, melodías, la mayoría de los instrumentos)
- 🔵 **Azul** = agudos (hi-hats, platillos, brillos)

Esto se calcula en la función `freqToColor(t)` — interpola entre rojo, verde
y azul según la posición de cada barra en el espectro de frecuencias.

## Personalización rápida

Abrí `index.html` con un editor de texto y buscá estas partes:

- **Colores RGB**: constantes `RGB_BASS`, `RGB_MID`, `RGB_TREBLE` (arrays `[R,G,B]`)
  cerca de la sección "Paleta RGB estilo waveform de DJ".
- **Colores de marca**: constantes `PAPAYA`, `PAPAYA_BRIGHT`, `STEEL`.
- **Tamaño del logo**: `width:150px; height:150px;` en el selector `#logoLabel`.
- **Intervalo de alternancia entre logos**: constante `LOGO_SWITCH_INTERVAL_MS`
  (por defecto `5 * 60 * 1000` = 5 minutos).
- **Intensidad del pulso/latido del logo**: en la función `draw()`, la línea
  `const logoScale = 1 + bassSmooth * 0.18 + ...` — subí el `0.18` si querés que
  vibre más fuerte, o el `heartbeatPulse * 0.15` para el latido del cambio de logo.
- **Intensidad del aura**: función `drawLogoAura()` — ajustá los valores de
  `radiusMul` y la opacidad en `rgbToCss(band.color, 0.35 + ...)`.
- **Sensibilidad al bajo**: variable `bassBins` (cuántas frecuencias bajas se usan) y el
  multiplicador `* 1.4` / `* 1.3` en el cálculo del "RPM" — subilo si querés que reaccione más fuerte.

## Notas técnicas

- Todo corre localmente en el navegador, no sube tu audio a ningún servidor.
- El canvas está fijo en 1920x1080 y se escala automáticamente a la ventana (`fitStage()`),
  así que lo que grabás en pantalla completa siempre sale a resolución completa.
- Si preferís generar el video sin grabar pantalla (más prolijo, sin bordes de OBS),
  usá el pipeline de `../pipeline/` — ese enfoque combina audio + fondo + overlay
  directamente con FFmpeg, pero requiere exportar frames del visualizer (ver notas ahí).
