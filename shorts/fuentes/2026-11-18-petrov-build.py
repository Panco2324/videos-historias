import html, math, random

W, H = 1080, 1920
VOZ = 54.83
DUR = round(VOZ + 1.6, 2)
OUT = "/home/claude/short/index.html"

segs = [
    (0.05, 3.79, "Su pantalla mostró 5 misiles nucleares rumbo a su país."),
    (4.30, 5.72, "Y decidió no avisar."),
    (6.36, 7.41, "Unión Soviética,"),
    (7.73, 9.44, "1983."),
    (10.29, 13.24, "Pasada la medianoche, en un búnker al sur de Moscú,"),
    (13.57, 17.53, "el teniente coronel Stanislav Petrov vigila los satélites de alerta."),
    (18.11, 19.78, "De pronto, suena la alarma."),
    (20.25, 22.49, "Un misil lanzado desde Estados Unidos."),
    (22.98, 23.75, "Luego otro."),
    (24.23, 25.09, "Luego cinco."),
    (25.66, 27.53, "Su deber era avisar a sus jefes."),
    (27.95, 30.34, "Y eso podía desatar la respuesta nuclear."),
    (31.00, 32.18, "Pero algo no cuadraba."),
    (32.66, 35.81, "Un ataque real sería una lluvia de misiles, no 5."),
    (36.31, 38.73, "Y los radares de tierra no confirmaban nada."),
    (39.38, 41.43, "Petrov lo reportó como falsa alarma."),
    (41.92, 42.67, "Tenía razón."),
    (43.11, 47.14, "El satélite había confundido el reflejo del sol en las nubes con misiles."),
    (47.73, 48.31, "¿Su premio?"),
    (48.80, 49.31, "Ninguno."),
    (49.78, 51.97, "El caso fue secreto más de 10 años."),
    (52.55, 53.58, "¿Tú habrías avisado?"),
    (54.11, 54.55, "Sígueme."),
]
KEY = {"5", "nucleares", "no", "avisar.", "1983.", "búnker", "Moscú,", "Stanislav", "Petrov", "alarma.", "Estados", "Unidos.",
       "otro.", "cinco.", "avisar", "nuclear.", "cuadraba.", "lluvia", "nada.", "falsa", "razón.", "sol", "nubes",
       "Ninguno.", "secreto", "10", "avisado?", "Sígueme."}

groups = []
for s, e, text in segs:
    words = text.split()
    lens = [len(w) + 1 for w in words]
    tot = sum(lens)
    t = s
    timed = []
    for w, l in zip(words, lens):
        d = (e - s) * l / tot
        timed.append((w, t, t + d))
        t += d
    for i in range(0, len(timed), 3):
        chunk = timed[i:i + 3]
        groups.append((chunk[0][1], chunk[-1][2], chunk))

# (archivo, inicio, duración, offset, zoom de, zoom a, filtro css)
clips = [
    ("c_5523891.mp4", 0.0, 6.36, 0.0, 1.25, 1.05, "brightness(1.4) saturate(1.3)"),
    ("c_10942670.mp4", 6.36, 3.93, 0.5, 1.05, 1.18, "saturate(.6) contrast(1.1)"),
    ("c_18866694.mp4", 10.29, 3.28, 0.0, 1.15, 1.0, "none"),
    ("c_20349219.mp4", 13.57, 4.54, 0.0, 1.0, 1.15, "none"),
    ("c_6976215.mp4", 18.11, 7.55, 0.0, 1.1, 1.25, "hue-rotate(70deg) saturate(.7) brightness(.55)"),
    ("c_5097124.mp4", 25.66, 7.0, 0.0, 1.0, 1.15, "saturate(.7) brightness(.7)"),
    ("c_12279768.mp4", 32.66, 6.72, 0.0, 1.15, 1.0, "brightness(.6)"),
    ("c_12278380.mp4", 39.38, 8.35, 3.0, 1.0, 1.15, "none"),
    ("c_6549528.mp4", 47.73, DUR - 47.73, 2.0, 1.12, 1.0, "saturate(.6) brightness(.7)"),
]
flash_times = [6.36, 10.29, 13.57, 18.11, 25.66, 31.0, 32.66, 39.38, 47.73]
RED_FLASH = {18.11, 31.0}

cards = [
    ("hook", 0.0, 6.2, '<div class="hook"><span class="r">5 MISILES</span><span>NUCLEARES</span><span class="y sm">…Y NO AVISÓ</span></div>'),
    ("fecha", 6.4, 3.8, '<div class="dateb"><small>UNIÓN SOVIÉTICA</small><b>26 SEP</b><b class="y">1983</b></div>'),
    ("lugar", 10.35, 3.1, '<div class="tag"><i>●</i> BÚNKER SECRETO<br><small>AL SUR DE MOSCÚ · MEDIANOCHE</small></div>'),
    ("quien", 13.65, 4.3, '<div class="idc"><small>OFICIAL DE GUARDIA</small><b>STANISLAV<br>PETROV</b><em>TENIENTE CORONEL</em></div>'),
    ("alarma", 18.15, 2.0, '<div class="hook"><span class="r">¡ALARMA!</span><span class="sm">ATAQUE DETECTADO</span></div>'),
    ("deber", 25.7, 2.2, '<div class="tag">SU DEBER:<br><span class="y">AVISAR</span></div>'),
    ("pero", 31.0, 1.6, '<div class="hook"><span class="sm">PERO ALGO</span><span class="y">NO CUADRABA</span></div>'),
    ("radar0", 36.35, 2.9, '<div class="tag">RADARES DE TIERRA<br><span class="g">0 MISILES</span></div>'),
    ("razon", 41.9, 1.2, '<div class="hook"><span class="g">TENÍA RAZÓN</span></div>'),
    ("premio", 47.75, 1.9, '<div class="big"><small>SU PREMIO</small><b>NINGUNO</b></div>'),
    ("cta", 52.5, DUR - 52.5, '<div class="hook"><span class="sm">¿TÚ HABRÍAS</span><span class="y">AVISADO?</span></div><div class="pill">SÍGUEME →</div>'),
]

CSS = f'''
:root {{ --ground:#06090b; --ink:#ffffff; --aji:#ffc629; --rojo:#ff2b2b; --fos:#3dff8b; --acero:#1b2328; --papel:#efe6cf; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--ground); }}
#root {{ position:relative; width:{W}px; height:{H}px; font-family:"Montserrat", sans-serif; }}
#cam {{ position:absolute; inset:-40px; z-index:1; }}
.bg {{ position:absolute; inset:40px; width:{W}px; height:{H}px; object-fit:cover; z-index:1; }}
.shade {{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg, rgba(6,9,11,.70) 0%, rgba(6,9,11,.30) 32%, rgba(6,9,11,.10) 50%, rgba(6,9,11,.70) 76%, rgba(6,9,11,.92) 100%); }}
.scan {{ position:absolute; inset:0; z-index:3; background:repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 2px, transparent 2px 6px); pointer-events:none; }}
.vign {{ position:absolute; inset:0; z-index:3; background:radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,.65) 100%); }}
.card {{ position:absolute; left:0; right:0; top:250px; z-index:6; text-align:center; }}
.hook span {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:170px; line-height:1.0; color:var(--ink); text-transform:uppercase; text-shadow:0 6px 30px rgba(0,0,0,.8); }}
.hook .sm {{ font-size:110px; }}
.y {{ color:var(--aji) !important; }}
.r {{ color:var(--rojo) !important; }}
.g {{ color:var(--fos) !important; }}
.dateb small, .idc small {{ display:block; font-family:"Space Mono", monospace; font-weight:700; font-size:46px; letter-spacing:.2em; color:var(--fos); text-shadow:0 0 18px rgba(61,255,139,.6); }}
.dateb b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:230px; line-height:1; color:#fff; text-shadow:0 8px 40px rgba(0,0,0,.8); }}
.tag {{ display:inline-block; padding:34px 54px; background:rgba(6,9,11,.82); border:5px solid var(--fos); border-radius:18px; font-family:"Oswald", sans-serif; font-weight:700; font-size:96px; line-height:1.05; color:#fff; box-shadow:0 0 40px rgba(61,255,139,.35); }}
.tag i {{ font-style:normal; color:var(--rojo); }}
.tag small {{ display:block; margin-top:12px; font-family:"Space Mono", monospace; font-size:40px; color:var(--fos); letter-spacing:.08em; }}
.idc {{ display:inline-block; padding:40px 60px; background:var(--papel); border-radius:16px; color:#1b2328; transform:rotate(-3deg); box-shadow:0 30px 70px rgba(0,0,0,.6); }}
.idc small {{ color:#8a1b1b; text-shadow:none; font-size:38px; }}
.idc b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:150px; line-height:1; margin:14px 0; }}
.idc em {{ display:block; font-style:normal; font-family:"Space Mono", monospace; font-weight:700; font-size:40px; letter-spacing:.1em; }}
.big small {{ display:block; font-family:"Space Mono", monospace; font-weight:700; font-size:56px; letter-spacing:.2em; color:#fff; }}
.big b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:220px; line-height:1; color:var(--rojo); text-shadow:0 8px 40px rgba(0,0,0,.8); }}
.pill {{ display:inline-block; margin-top:120px; padding:28px 64px; border-radius:999px; background:var(--aji); color:#06090b; font-weight:900; font-size:80px; }}
.cap {{ position:absolute; left:40px; right:40px; top:1440px; z-index:9; display:flex; flex-wrap:wrap; justify-content:center; gap:6px 0; }}
.cap span {{ display:inline-block; padding:0 14px; font-weight:900; line-height:1.1; color:var(--ink); text-transform:uppercase; -webkit-text-stroke:3px #06090b; paint-order:stroke fill; text-shadow:0 6px 22px rgba(0,0,0,.85); }}
.cap span.k {{ color:var(--aji); }}
.flash {{ position:absolute; inset:0; z-index:10; background:#fff; opacity:0; }}
.flash.red {{ background:var(--rojo); }}
.fx {{ position:absolute; z-index:5; overflow:visible; }}
.dim {{ position:absolute; inset:0; z-index:4; background:rgba(6,9,11,.55); opacity:0; }}
.redwash {{ position:absolute; inset:0; z-index:4; background:radial-gradient(ellipse at center, rgba(255,43,43,.0) 30%, rgba(255,43,43,.55) 100%); opacity:0; }}
#radar {{ left:200px; top:720px; width:680px; height:680px; }}
#map {{ left:40px; top:300px; width:1000px; height:760px; }}
#mcount {{ position:absolute; left:0; right:0; top:1080px; z-index:6; text-align:center; font-family:"Oswald", sans-serif; font-weight:700; font-size:150px; color:var(--rojo); text-shadow:0 0 30px rgba(255,43,43,.6); }}
#phone {{ left:300px; top:560px; width:480px; height:420px; }}
#nukew {{ position:absolute; left:0; right:0; top:330px; z-index:6; text-align:center; }}
#nukew div {{ display:inline-block; padding:24px 50px; background:var(--rojo); color:#fff; font-family:"Oswald", sans-serif; font-weight:700; font-size:92px; border-radius:14px; }}
#rain {{ left:0; top:0; width:1080px; height:1100px; }}
#five {{ left:80px; top:300px; width:920px; height:780px; }}
#stamp {{ position:absolute; left:170px; top:470px; z-index:7; padding:18px 40px; border:12px solid #c40d0d; border-radius:18px; color:#c40d0d; font-family:"Oswald", sans-serif; font-weight:700; font-size:120px; line-height:1; background:rgba(239,230,207,.92); }}
#sat {{ left:40px; top:260px; width:1000px; height:880px; }}
#folder {{ left:190px; top:300px; width:700px; height:760px; }}
'''

P = []
P.append(f'''<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<audio id="voz" class="clip" src="assets/voz.mp3" data-start="0" data-duration="{VOZ}" data-volume="1"></audio>
<audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="{DUR}" data-volume="0.45"></audio>
<div id="cam">
''')
for i, (f, s, d, off, z0, z1, flt) in enumerate(clips):
    P.append(f'<video id="bg{i}" class="clip bg" style="filter:{flt}" src="assets/{f}" data-start="{s}" data-duration="{d:.2f}" data-media-start="{off}" muted playsinline></video>\n')
P.append('</div>\n')
P.append(f'<div id="shade" class="clip shade" data-start="0" data-duration="{DUR}"></div>\n')
P.append(f'<div id="scan" class="clip scan" data-start="0" data-duration="{DUR}"></div>\n')
P.append(f'<div id="vign" class="clip vign" data-start="0" data-duration="{DUR}"></div>\n')
for k, t in enumerate(flash_times):
    cls = "flash red" if t in RED_FLASH else "flash"
    P.append(f'<div id="fl{k}" class="clip {cls}" data-start="{max(t-0.05,0):.2f}" data-duration="0.5"></div>\n')

# capas de oscurecido/alarma
P.append('<div id="dimA" class="clip dim" data-start="18.1" data-duration="7.6"></div>\n')
P.append('<div id="redw" class="clip redwash" data-start="18.1" data-duration="7.6"></div>\n')
P.append('<div id="dimB" class="clip dim" data-start="32.6" data-duration="6.8"></div>\n')
P.append('<div id="dimC" class="clip dim" data-start="43.0" data-duration="4.7"></div>\n')
P.append('<div id="dimD" class="clip dim" data-start="49.7" data-duration="2.8"></div>\n')

# 1) RADAR CRT (gancho, segundo 0)
blips = [(250, 190), (440, 230), (300, 420), (470, 400), (380, 300)]
rad = ['<svg id="radar" class="clip fx" data-start="0" data-duration="6.3" viewBox="0 0 700 700">',
       '<defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#0d3a22"/><stop offset="1" stop-color="#031208"/></radialGradient>',
       '<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3dff8b" stop-opacity="0"/><stop offset="1" stop-color="#3dff8b" stop-opacity=".75"/></linearGradient></defs>',
       '<rect x="10" y="10" width="680" height="680" rx="60" fill="#1b2328" stroke="#3a464d" stroke-width="10"/>',
       '<circle cx="350" cy="350" r="300" fill="url(#rg)" stroke="#3dff8b" stroke-width="4"/>']
for r in (75, 150, 225):
    rad.append(f'<circle cx="350" cy="350" r="{r}" fill="none" stroke="#3dff8b" stroke-opacity=".35" stroke-width="2"/>')
rad.append('<path d="M50 350 H650 M350 50 V650" stroke="#3dff8b" stroke-opacity=".35" stroke-width="2"/>')
rad.append('<g id="sweep"><path d="M350 350 L650 350 A300 300 0 0 0 562 138 Z" fill="url(#sw)" opacity=".7"/><path d="M350 350 L650 350" stroke="#9dffc4" stroke-width="4"/></g>')
for k, (x, y) in enumerate(blips):
    rad.append(f'<g id="bl{k}" opacity="0"><circle cx="{x}" cy="{y}" r="16" fill="#ff2b2b"/><circle id="blr{k}" cx="{x}" cy="{y}" r="16" fill="none" stroke="#ff2b2b" stroke-width="4"/></g>')
rad.append('<text x="350" y="690" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="34" fill="#ff2b2b" id="radtxt">ALERTA · ATAQUE</text>')
rad.append('</svg>\n')
P.append("".join(rad))

# 2) MAPA ESQUEMÁTICO EE.UU. -> URSS con 5 trayectorias (20.25 – 25.6)
mp = ['<svg id="map" class="clip fx" data-start="20.2" data-duration="5.45" viewBox="0 0 1000 760">',
      '<rect x="0" y="0" width="1000" height="760" rx="30" fill="#03130a" fill-opacity=".88" stroke="#3dff8b" stroke-width="4"/>']
for gx in range(100, 1000, 100):
    mp.append(f'<path d="M{gx} 20 V740" stroke="#3dff8b" stroke-opacity=".12" stroke-width="2"/>')
for gy in range(100, 760, 100):
    mp.append(f'<path d="M20 {gy} H980" stroke="#3dff8b" stroke-opacity=".12" stroke-width="2"/>')
mp.append('<path d="M60 470 Q90 380 180 360 Q260 330 300 380 Q330 430 290 500 Q230 560 150 540 Q80 530 60 470 Z" fill="#3dff8b" fill-opacity=".18" stroke="#3dff8b" stroke-width="3"/>')
mp.append('<path d="M600 250 Q700 180 860 200 Q960 230 950 320 Q930 400 820 410 Q700 420 640 380 Q580 330 600 250 Z" fill="#3dff8b" fill-opacity=".18" stroke="#3dff8b" stroke-width="3"/>')
mp.append('<text x="180" y="610" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="40" fill="#3dff8b">EE.UU.</text>')
mp.append('<text x="780" y="470" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="40" fill="#3dff8b">URSS</text>')
mp.append('<circle cx="760" cy="300" r="12" fill="#ffc629"/><text x="760" y="270" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="28" fill="#ffc629">MOSCÚ</text>')
for k in range(5):
    sx, sy = 170 + k * 18, 440 + (k % 2) * 30
    ex, ey = 720 + k * 22, 290 + (k % 3) * 18
    cx, cy = (sx + ex) / 2, 60 + k * 25
    mp.append(f'<path id="tr{k}" d="M{sx} {sy} Q{cx} {cy} {ex} {ey}" fill="none" stroke="#ff2b2b" stroke-width="6" stroke-linecap="round" stroke-dasharray="1000" stroke-dashoffset="1000"/>')
    mp.append(f'<circle id="tp{k}" cx="{sx}" cy="{sy}" r="11" fill="#ff2b2b" opacity="0"/>')
mp.append('</svg>\n')
P.append("".join(mp))
P.append('<div id="mcount" class="clip" data-start="20.2" data-duration="5.45">MISILES: <span id="mc">0</span></div>\n')

# 3) TELÉFONO ROJO + aviso de respuesta nuclear (25.66 – 30.34)
P.append('''<svg id="phone" class="clip fx" data-start="25.66" data-duration="4.7" viewBox="0 0 240 210"><g id="ph">
<path d="M40 90 Q40 60 120 60 Q200 60 200 90 L210 180 Q210 196 194 196 L46 196 Q30 196 30 180 Z" fill="#c81d1d" stroke="#06090b" stroke-width="5"/>
<g id="hand"><path d="M20 50 Q20 20 120 20 Q220 20 220 50 L220 62 Q220 72 200 72 L180 72 Q170 72 170 60 L170 50 L70 50 L70 60 Q70 72 60 72 L40 72 Q20 72 20 62 Z" fill="#e23030" stroke="#06090b" stroke-width="5"/></g>
<circle cx="120" cy="140" r="38" fill="#ef4444" stroke="#06090b" stroke-width="5"/>
<g fill="#06090b"><circle cx="120" cy="112" r="6"/><circle cx="146" cy="128" r="6"/><circle cx="146" cy="152" r="6"/><circle cx="120" cy="168" r="6"/><circle cx="94" cy="152" r="6"/><circle cx="94" cy="128" r="6"/></g>
</g><g id="rings" stroke="#ffc629" stroke-width="6" fill="none" stroke-linecap="round"><path id="rg1" d="M8 20 Q-4 40 8 60"/><path id="rg2" d="M232 20 Q244 40 232 60"/></g></svg>\n''')
P.append('<div id="nukew" class="clip" data-start="27.95" data-duration="2.4"><div>☢ RESPUESTA NUCLEAR</div></div>\n')

# 4) LLUVIA DE MISILES vs 5 (32.66 – 35.8)
rn = ['<svg id="rain" class="clip fx" data-start="32.66" data-duration="1.9" viewBox="0 0 1080 1100">']
random.seed(7)
for k in range(60):
    x = random.randint(20, 1060); y = random.randint(-200, 300)
    rn.append(f'<g id="m{k}" transform="translate({x} {y}) rotate(200)" opacity="0"><path d="M0 -24 L6 -12 L6 14 L10 22 L-10 22 L-6 14 L-6 -12 Z" fill="#dfe5e8"/><path d="M-3 22 L0 40 L3 22 Z" fill="#ff8a2b"/></g>')
rn.append('</svg>\n')
P.append("".join(rn))
P.append('<div id="c_lluvia" class="clip card" data-start="32.7" data-duration="1.9"><div id="ci_lluvia" class="hook"><span class="sm">ATAQUE REAL:</span><span class="y">UNA LLUVIA</span></div></div>\n')
fv = ['<svg id="five" class="clip fx" data-start="34.6" data-duration="1.25" viewBox="0 0 920 780">']
for k in range(5):
    fv.append(f'<g id="f{k}" transform="translate({140 + k*160} 380) scale(3)" opacity="0"><path d="M0 -24 L6 -12 L6 14 L10 22 L-10 22 L-6 14 L-6 -12 Z" fill="#ff2b2b"/><path d="M-3 22 L0 40 L3 22 Z" fill="#ffc629"/></g>')
fv.append('<text x="460" y="650" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="150" fill="#fff">¿SOLO 5?</text>')
fv.append('</svg>\n')
P.append("".join(fv))

# 5) SELLO "FALSA ALARMA" sobre parte (39.38 – 41.5)
P.append('<div id="c_rep" class="clip card" data-start="39.38" data-duration="2.2"><div id="ci_rep" class="idc" data-layout-allow-occlusion data-layout-allow-overlap style="transform:rotate(2deg)"><small>INFORME DE GUARDIA</small><b style="font-size:110px">ALERTA<br>DE ATAQUE</b><em>SERPUJOV-15</em></div></div>\n')
P.append('<div id="stamp" class="clip" data-layout-allow-overlap data-layout-allow-occlusion data-start="40.0" data-duration="1.55">FALSA ALARMA</div>\n')

# 6) SATÉLITE + SOL + NUBES (43.11 – 47.6)
st = ['<svg id="sat" class="clip fx" data-start="43.05" data-duration="4.6" viewBox="0 0 1000 880">',
      '<defs><radialGradient id="sun" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff7cc"/><stop offset=".4" stop-color="#ffc629"/><stop offset="1" stop-color="#ffc629" stop-opacity="0"/></radialGradient>',
      '<radialGradient id="glare" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient></defs>',
      '<circle id="sunb" cx="120" cy="120" r="110" fill="url(#sun)"/>',
      '<g id="satg"><rect x="700" y="90" width="80" height="60" rx="8" fill="#c9d1d6" stroke="#06090b" stroke-width="4"/>',
      '<rect x="560" y="100" width="130" height="40" fill="#1e4b8f" stroke="#06090b" stroke-width="4"/><rect x="790" y="100" width="130" height="40" fill="#1e4b8f" stroke="#06090b" stroke-width="4"/>',
      '<path d="M600 100 V140 M640 100 V140 M830 100 V140 M870 100 V140" stroke="#6fa0e0" stroke-width="3"/>',
      '<path d="M740 150 L740 175" stroke="#c9d1d6" stroke-width="5"/><path d="M718 175 Q740 200 762 175 Z" fill="#c9d1d6" stroke="#06090b" stroke-width="3"/>',
      '<text x="740" y="65" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="34" fill="#fff">SATÉLITE OKO</text></g>',
      '<path id="ray1" d="M170 170 L430 650" stroke="#ffc629" stroke-width="10" stroke-linecap="round" stroke-dasharray="600" stroke-dashoffset="600"/>',
      '<path id="ray2" d="M430 650 L735 200" stroke="#ffc629" stroke-width="10" stroke-linecap="round" stroke-dasharray="600" stroke-dashoffset="600"/>']
for k, (x, y, r) in enumerate([(300, 680, 120), (440, 650, 140), (590, 690, 120), (200, 720, 100), (700, 720, 110)]):
    st.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9eef2" fill-opacity=".92"/>')
st.append('<circle id="glr" cx="430" cy="640" r="90" fill="url(#glare)" opacity="0"/>')
st.append('<g id="fakeb" opacity="0"><rect x="250" y="770" width="500" height="80" rx="14" fill="#ff2b2b"/><text x="500" y="826" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="54" fill="#fff">REFLEJO = "MISIL"</text></g>')
st.append('</svg>\n')
P.append("".join(st))

# 7) CARPETA CLASIFICADA (49.78 – 52.4)
P.append('''<svg id="folder" class="clip fx" data-start="49.75" data-duration="2.7" viewBox="0 0 700 760">
<path d="M30 80 L260 80 L300 130 L670 130 L670 730 L30 730 Z" fill="#c9a76a" stroke="#06090b" stroke-width="6"/>
<rect x="70" y="170" width="560" height="520" fill="#efe6cf" stroke="#06090b" stroke-width="4"/>
<text x="350" y="240" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="40" fill="#1b2328">26.09.1983</text>
<g id="redact" fill="#06090b"><rect id="rd0" x="110" y="290" width="480" height="34"/><rect id="rd1" x="110" y="350" width="400" height="34"/><rect id="rd2" x="110" y="410" width="450" height="34"/><rect id="rd3" x="110" y="470" width="360" height="34"/><rect id="rd4" x="110" y="530" width="420" height="34"/></g>
<g id="secst" opacity="0"><rect x="120" y="560" width="460" height="120" rx="12" fill="none" stroke="#ff2b2b" stroke-width="10" transform="rotate(-8 350 620)"/><text x="350" y="650" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="84" fill="#ff2b2b" transform="rotate(-8 350 620)">SECRETO</text></g>
</svg>\n''')
P.append('<div id="c_diez" class="clip" style="position:absolute;left:0;right:0;top:1080px;z-index:6;text-align:center" data-start="50.6" data-duration="1.85"><div id="ci_diez" class="tag" style="padding:16px 40px;font-size:80px">+10 AÑOS</div></div>\n')

for cid, s, d, inner in cards:
    P.append(f'<div id="c_{cid}" class="clip card" data-start="{s}" data-duration="{d:.2f}"><div id="ci_{cid}">{inner}</div></div>\n')
for gi, (gs, ge, chunk) in enumerate(groups):
    nxt = groups[gi + 1][0] if gi + 1 < len(groups) else DUR
    gdur = min(ge + 0.15, nxt) - gs
    ws = "".join(f'<span id="g{gi}w{j}" class="{"k" if w in KEY else ""}">{html.escape(w)}</span>' for j, (w, a, b) in enumerate(chunk))
    nch = sum(len(w) for w, _, _ in chunk)
    fs = 92 if nch <= 12 else (80 if nch <= 16 else 68)
    P.append(f'<div id="g{gi}" style="font-size:{fs}px" class="clip cap" data-start="{gs:.2f}" data-duration="{gdur:.2f}">{ws}</div>\n')

J = ["const tl = gsap.timeline({ paused: true });"]
for i, (f, s, d, off, z0, z1, flt) in enumerate(clips):
    J.append(f'tl.fromTo("#bg{i}", {{scale:{z0}}}, {{scale:{z1}, duration:{d:.2f}, ease:"none"}}, {s});')
for cid, s, d, inner in cards:
    if cid == "hook":
        J.append('tl.set("#ci_hook", {opacity:1});')
        J.append('tl.fromTo("#ci_hook span", {scale:1.25}, {scale:1, duration:.5, ease:"power3.out", stagger:.08}, 0);')
    else:
        J.append(f'tl.fromTo("#ci_{cid}", {{opacity:0, scale:.85, y:30}}, {{opacity:1, scale:1, y:0, duration:.35, ease:"back.out(1.7)"}}, {s});')
    J.append(f'tl.to("#ci_{cid}", {{opacity:0, duration:.2, ease:"power2.in"}}, {s + d - 0.25:.2f});')
for cid, s, d in [("lluvia", 32.7, 1.9), ("rep", 39.38, 2.2), ("diez", 50.6, 1.85)]:
    J.append(f'tl.fromTo("#ci_{cid}", {{opacity:0, scale:.85}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(1.7)"}}, {s});')
    J.append(f'tl.to("#ci_{cid}", {{opacity:0, duration:.2}}, {s + d - 0.25:.2f});')
for gi, (gs, ge, chunk) in enumerate(groups):
    for j, (w, a, b) in enumerate(chunk):
        J.append(f'tl.fromTo("#g{gi}w{j}", {{opacity:0, y:40, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.22, ease:"back.out(2.5)"}}, {a:.2f});')
        if w not in KEY:
            J.append(f'tl.to("#g{gi}w{j}", {{color:"#ffc629", duration:.05}}, {a:.2f}); tl.to("#g{gi}w{j}", {{color:"#ffffff", duration:.1}}, {b:.2f});')
for k, t in enumerate(flash_times):
    peak = .55 if t in RED_FLASH else .45
    J.append(f'tl.fromTo("#fl{k}", {{opacity:0}}, {{opacity:{peak}, duration:.06}}, {max(t-0.04,0):.2f});')
    J.append(f'tl.to("#fl{k}", {{opacity:0, duration:.3, ease:"power2.out"}}, {t+0.03:.2f});')

# radar: visible desde el segundo 0 con los 5 puntos
J.append('tl.to("#sweep", {rotation:720, svgOrigin:"350 350", duration:6.3, ease:"none"}, 0);')
for k in range(5):
    J.append(f'tl.set("#bl{k}", {{opacity:1}}, {0.02 + k*0.0:.2f});')
    J.append(f'tl.fromTo("#blr{k}", {{attr:{{r:16}}, opacity:1}}, {{attr:{{r:60}}, opacity:0, duration:.9, repeat:6, ease:"power1.out"}}, {k*0.15:.2f});')
J.append('tl.to("#radtxt", {opacity:.2, duration:.3, yoyo:true, repeat:19, ease:"steps(1)"}, 0);')
J.append('tl.fromTo("#radar", {scale:.92}, {scale:1.0, duration:6, ease:"none", transformOrigin:"50% 50%"}, 0);')
J.append('tl.to("#radar", {opacity:0, duration:.25}, 6.0);')

# alarma: lavado rojo intermitente + sacudida fuerte (momento de mayor tensión)
J.append('tl.to("#dimA", {opacity:1, duration:.2}, 18.1); tl.to("#dimA", {opacity:0, duration:.2}, 25.4);')
for k in range(10):
    J.append(f'tl.fromTo("#redw", {{opacity:0}}, {{opacity:1, duration:.25, yoyo:true, repeat:1, ease:"sine.inOut"}}, {18.11 + k*0.72:.2f});')
for k in range(12):
    a = 26 if k < 6 else 10
    J.append(f'tl.to("#cam", {{x:{a*math.sin(k*2.3):.1f}, y:{a*math.cos(k*1.7):.1f}, duration:.07}}, {18.12 + k*0.07:.2f});')
J.append('tl.to("#cam", {x:0, y:0, duration:.15}, 19.0);')
# sacudidas por cada misil
for t in (20.3, 23.0, 24.25):
    for k in range(4):
        J.append(f'tl.to("#cam", {{x:{14*math.sin(k*2.1+t):.1f}, y:{14*math.cos(k*1.9+t):.1f}, duration:.06}}, {t + k*0.06:.2f});')
    J.append(f'tl.to("#cam", {{x:0, y:0, duration:.1}}, {t+0.26:.2f});')

# mapa
J.append('tl.fromTo("#map", {opacity:0, scale:.9}, {opacity:1, scale:1, duration:.35, ease:"back.out(1.6)", transformOrigin:"50% 50%"}, 20.2);')
J.append('tl.fromTo("#mcount", {opacity:0}, {opacity:1, duration:.2}, 20.3);')
starts = [20.4, 23.0, 24.25, 24.4, 24.55]
for k, t in enumerate(starts):
    J.append(f'tl.to("#tr{k}", {{attr:{{"stroke-dashoffset":0}}, duration:.9, ease:"power1.inOut"}}, {t});')
J.append('tl.set("#mc", {textContent:"1"}, 20.5); tl.set("#mc", {textContent:"2"}, 23.05); tl.set("#mc", {textContent:"3"}, 24.3); tl.set("#mc", {textContent:"4"}, 24.45); tl.set("#mc", {textContent:"5"}, 24.6);')
J.append('tl.fromTo("#mcount", {scale:1.35}, {scale:1, duration:.25}, 24.6);')
J.append('tl.to("#map", {opacity:0, duration:.25}, 25.35); tl.to("#mcount", {opacity:0, duration:.25}, 25.35);')

# teléfono
J.append('tl.fromTo("#phone", {opacity:0, y:80}, {opacity:1, y:0, duration:.35, ease:"back.out(1.7)"}, 25.7);')
for k in range(14):
    J.append(f'tl.to("#hand", {{y:{-10 if k%2 else 0}, rotation:{4 if k%2 else -4}, svgOrigin:"120 50", duration:.08}}, {26.0 + k*0.09:.2f});')
J.append('tl.fromTo("#rings", {opacity:0}, {opacity:1, duration:.12, yoyo:true, repeat:9}, 26.0);')
J.append('tl.to("#phone", {y:-200, scale:.7, duration:.4, ease:"power2.inOut", transformOrigin:"50% 50%"}, 27.9);')
J.append('tl.fromTo("#nukew div", {scale:0}, {scale:1, duration:.3, ease:"back.out(2)"}, 28.0);')
J.append('tl.to("#nukew div", {opacity:.35, duration:.2, yoyo:true, repeat:7, ease:"steps(1)"}, 28.4);')
J.append('tl.to("#phone", {opacity:0, duration:.25}, 30.1);')

# lluvia de misiles
J.append('tl.to("#dimB", {opacity:1, duration:.2}, 32.6); tl.to("#dimB", {opacity:0, duration:.2}, 39.2);')
random.seed(11)
for k in range(60):
    t = 32.66 + random.random() * 1.2
    J.append(f'tl.fromTo("#m{k}", {{opacity:1, y:0}}, {{y:1300, x:-260, duration:.8, ease:"none"}}, {t:.2f});')
J.append('tl.to("#rain", {opacity:0, duration:.2}, 34.35);')
for k in range(5):
    J.append(f'tl.fromTo("#f{k}", {{opacity:0, y:-60}}, {{opacity:1, y:0, duration:.18, ease:"back.out(2)"}}, {34.62 + k*0.06:.2f});')
J.append('tl.to("#five", {opacity:0, duration:.2}, 35.6);')

# informe + sello
J.append('tl.fromTo("#stamp", {opacity:0, scale:3, rotation:-30}, {opacity:1, scale:1, rotation:-10, duration:.16, ease:"power4.in"}, 40.0);')
for k in range(5):
    J.append(f'tl.to("#cam", {{x:{18*math.sin(k*2.3):.1f}, y:{18*math.cos(k*1.7):.1f}, duration:.06}}, {40.17+k*0.06:.2f});')
J.append('tl.to("#cam", {x:0, y:0, duration:.12}, 40.5);')
J.append('tl.to("#stamp", {opacity:0, duration:.2}, 41.35);')

# satélite y reflejo
J.append('tl.to("#dimC", {opacity:1, duration:.2}, 43.0); tl.to("#dimC", {opacity:0, duration:.2}, 47.4);')
J.append('tl.fromTo("#sat", {opacity:0}, {opacity:1, duration:.3}, 43.1);')
J.append('tl.fromTo("#satg", {x:200}, {x:0, duration:1.0, ease:"power2.out"}, 43.1);')
J.append('tl.fromTo("#sunb", {scale:.6}, {scale:1.15, duration:.6, yoyo:true, repeat:5, ease:"sine.inOut", svgOrigin:"120 120"}, 43.1);')
J.append('tl.to("#ray1", {attr:{"stroke-dashoffset":0}, duration:.7, ease:"none"}, 44.0);')
J.append('tl.fromTo("#glr", {opacity:0, attr:{r:20}}, {opacity:1, attr:{r:150}, duration:.3, ease:"power3.out"}, 44.7);')
J.append('tl.to("#ray2", {attr:{"stroke-dashoffset":0}, duration:.6, ease:"none"}, 44.85);')
J.append('tl.fromTo("#fakeb", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, ease:"back.out(2)"}, 45.6);')
J.append('tl.to("#sat", {opacity:0, duration:.25}, 47.35);')

# carpeta secreta
J.append('tl.to("#dimD", {opacity:1, duration:.2}, 49.7); tl.to("#dimD", {opacity:0, duration:.2}, 52.3);')
J.append('tl.fromTo("#folder", {opacity:0, y:120, rotation:6}, {opacity:1, y:0, rotation:-2, duration:.4, ease:"back.out(1.5)", transformOrigin:"50% 50%"}, 49.78);')
for k in range(5):
    J.append(f'tl.fromTo("#rd{k}", {{attr:{{width:0}}}}, {{attr:{{width:{[480,400,450,360,420][k]}}}, duration:.18, ease:"power2.out"}}, {50.0 + k*0.12:.2f});')
J.append('tl.fromTo("#secst", {opacity:0, scale:2.4}, {opacity:1, scale:1, svgOrigin:"350 620", duration:.15, ease:"power4.in"}, 50.75);')
J.append('tl.to("#folder", {opacity:0, duration:.25}, 52.2);')

# CTA
J.append(f'tl.to("#ci_cta .pill", {{scale:1.08, duration:.35, yoyo:true, repeat:5, ease:"sine.inOut"}}, 53.0);')
J.append('window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;')
P.append("</div>\n<script>\n" + "\n".join(J) + "\n</script>\n</body>\n</html>\n")
open(OUT, "w").write("".join(P))
print(len(groups), "grupos", DUR)
