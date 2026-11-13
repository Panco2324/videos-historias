# Plantilla de Shorts animados (HyperFrames)

- `build_short_ejemplo.py`: genera `index.html` (1080x1920) con subtítulos palabra por palabra, tarjetas, clips de fondo y animaciones SVG. Es el Short del 13 nov 2026; adáptalo a cada historia (segmentos de voz, palabras clave, clips, tarjetas y animaciones).
- `sfx/`: efectos de sonido propios (trueno, golpe, viento, lluvia, whoosh, ambiente) para mezclar con ffmpeg en `assets/sfx.wav`.
- Render: `export HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome` y luego `npx --yes hyperframes@0.9.41 check`, `snapshot --at ...`, `render`.
- Los videos finales van en `shorts/AAAA-MM-DD-tema.mp4` (rama `videos`).
