# Plantilla de Shorts animados (HyperFrames)

- `build_short_ejemplo.py`: ejemplo TÉCNICO de cómo se arma un Short (subtítulos, tarjetas, clips, línea de tiempo). No copies sus animaciones ni sus clips: cada historia lleva dibujos nuevos.
- `sfx/`: efectos de sonido propios (trueno, golpe, viento, lluvia, whoosh, ambiente) para mezclar con ffmpeg en `assets/sfx.wav`.
- Render: `export HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome` y luego `npx --yes hyperframes@0.9.41 check`, `snapshot --at ...`, `render`.
- Los videos finales van en `shorts/AAAA-MM-DD-tema.mp4` (rama `videos`).
- `usados.md`: registro de clips y animaciones ya usados. Nada se repite en 14 días.
