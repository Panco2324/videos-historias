# Cómo se hizo el primer video largo (Garbo, nov 2026) — guía técnica

El primer largo («Engañó a Hitler y vivió para contarlo», 11:43, 9 capítulos) se hizo con estos archivos.
Úsalos como máquina técnica; las animaciones y tarjetas de cada historia se diseñan de nuevo.

## Archivos
- `guion_ejemplo.json`: formato del guion (lista de capítulos con id c1..cN, titulo y texto; c1 es el gancho sin portada).
- `align_pausas.py` y luego `align_frases.py`: calculan el tiempo de cada palabra a partir de las pausas de la voz
  (silencedetect + alineación de frases). Generan `timing.json`. Precisión aproximada de ±0,5 s.
- `gen_largo_ejemplo_garbo.py`: generador HyperFrames 1920x1080 por capítulo (portada de capítulo de 2,4 s,
  clips de fondo repartidos sin repetir, subtítulos abajo en grupos de hasta 5 palabras, componentes:
  textos grandes, sellos, tarjetas de fecha, contadores, mapas esquemáticos, telegramas, íconos, etc.).
  `chapter_events()` es lo único específico de la historia: reescríbelo entero para cada video.
- `mezcla_sfx.py`: mezcla drone + música + whoosh/boom por capítulo (cambia la ruta de la música a
  `plantilla/sfx/musica_suspenso.mp3`).
- `render_capitulos.sh`: renderiza capítulo por capítulo (un render de 12 min de una vez es frágil).
- `grain.png`: textura de grano.
Las rutas internas de los scripts apuntan a /home/claude/largo: crea esa carpeta o ajústalas.

## Lecciones (errores que ya pasaron, no repetir)
- Fuentes que funcionan en el render: Oswald, Montserrat, Space Mono. «Special Elite» NO existe.
- Toda capa oscura (.dimcard) debe tener opacity:0 en el CSS; si no, aparece un velo gris antes de su animación.
- La función `at(frase)` toma la PRIMERA aparición: si la frase se repite en el capítulo, usa `at(frase, 2)`.
- Los mapas deben quedar por encima de los subtítulos (zona y > 880 libre).
- Revisa con `hyperframes check` y `snapshot` (8 momentos por capítulo) ANTES de renderizar, y mira las hojas.
- Tiempos de render en este servidor (2 núcleos): unas 7–8 veces la duración. Un largo de 12 min ≈ 1 h 40 min.
- GitHub: NO se pueden crear Releases ni usar Git LFS desde aquí. Un archivo normal debe pesar < 100 MB.
  Compresión que funcionó (una sola pasada, 96 MB para 11:43):
  `ffmpeg -i junto.mp4 -c:v libx264 -preset medium -crf 23 -maxrate 1000k -bufsize 2000k -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 96k -ar 48000 -movflags +faststart final.mp4`
  (la compresión en dos pasadas falló). Para videos de más de 12:30 baja -maxrate a 900k.
- vidIQ: los archivos de `vidiq_generate_music` y `vidiq_generate_thumbnail` (servidores S3 de vidIQ) NO se
  pueden descargar desde aquí: se gastaron 72 créditos en vano. No los uses. Música: `plantilla/sfx/musica_suspenso.mp3`.
  La voz (assets.vidiq.com) y los clips de Pexels sí se descargan.
- Miniatura: hazla SIEMPRE en Canva (create-design, format "YouTube Thumbnail"), exporta JPG, descárgala
  (export-download.canva.com sí funciona), súbela a GitHub y pásala a Metricool en videoThumbnailUrl (funcionó).
- Datos: nada inventado en pantalla (cifras, textos de periódicos, telegramas). Si una tarjeta resume un
  mensaje, que diga «resumen». Solo detalles confirmados en al menos 2 fuentes.
- Clips: evita imágenes claramente modernas para hechos históricos (tanques de guerras actuales, autos modernos).
