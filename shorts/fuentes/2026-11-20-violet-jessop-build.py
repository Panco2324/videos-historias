import html, math, random

W, H = 1080, 1920
VOZ = 52.58
DUR = round(VOZ + 0.6, 2)
OUT = "/home/claude/short/index.html"

segs = [
    (0.00, 1.84, "Sobrevivió al Titanic…"),
    (2.44, 3.22, "y a sus 2 barcos gemelos."),
    (3.48, 4.43, "Tres barcos, tres desastres,"),
    (4.81, 6.17, "y la misma mujer a bordo."),
    (6.71, 8.35, "Se llamaba Violet Jessop."),
    (8.86, 12.25, "Nació en Argentina y trabajaba como camarera en barcos."),
    (12.85, 14.18, "En 1911,"),
    (14.18, 16.57, "el Olympic chocó contra un buque de guerra."),
    (17.12, 18.31, "Ella salió ilesa."),
    (18.87, 21.57, "Meses después pasó a su gemelo más famoso:"),
    (21.93, 22.60, "el Titanic."),
    (23.20, 26.00, "La noche del iceberg la subieron a un bote salvavidas,"),
    (26.29, 27.91, "con un bebé ajeno en los brazos."),
    (28.43, 29.18, "Sobrevivió."),
    (29.74, 31.32, "Pero faltaba el tercer gemelo."),
    (31.86, 33.39, "En 1916,"),
    (33.65, 34.39, "el Britannic,"),
    (34.39, 36.04, "convertido en barco hospital,"),
    (36.35, 38.15, "chocó con una mina en el mar Egeo."),
    (38.76, 42.43, "Violet saltó al agua mientras las hélices arrastraban los botes."),
    (42.91, 44.07, "Se golpeó la cabeza…"),
    (44.61, 45.93, "y sobrevivió otra vez."),
    (46.48, 48.54, "Siguió navegando más de 30 años"),
    (48.54, 49.97, "y murió en tierra firme,"),
    (49.97, 51.17, "a los 83."),
    (51.67, 52.58, "Porque ella…"),
]
KEY = {"Sobrevivió", "Titanic…", "2", "gemelos.", "Tres", "tres", "desastres,", "misma", "Violet", "Jessop.", "Argentina",
       "camarera", "1911,", "Olympic", "chocó", "guerra.", "ilesa.", "famoso:", "Titanic.", "iceberg", "salvavidas,",
       "bebé", "Sobrevivió.", "tercer", "gemelo.", "1916,", "Britannic,", "hospital,", "mina", "Egeo.", "saltó",
       "hélices", "cabeza…", "sobrevivió", "vez.", "30", "tierra", "firme,", "83.", "ella…"}

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
    ("c5_olas.mp4", 0.0, 3.48, 2.0, 1.22, 1.08, "saturate(.55) brightness(.6) contrast(1.15)"),
    ("c2_mastil.mp4", 3.48, 5.38, 0.0, 1.05, 1.2, "saturate(.35) sepia(.35) brightness(.62)"),
    ("c3_cubierta.mp4", 8.86, 3.99, 0.0, 1.15, 1.02, "saturate(.6) brightness(.6)"),
    ("c9_cielo.mp4", 12.85, 6.02, 0.0, 1.0, 1.15, "saturate(.4) brightness(.55)"),
    ("c8_salvavidas.mp4", 18.87, 4.33, 0.0, 1.12, 1.0, "saturate(.5) brightness(.55)"),
    ("c1_hielo.mp4", 23.2, 5.23, 1.0, 1.0, 1.15, "brightness(.5) saturate(.7) hue-rotate(-10deg)"),
    ("c4_bote.mp4", 28.43, 3.43, 0.0, 1.15, 1.02, "saturate(.5) brightness(.55)"),
    ("c7_agua.mp4", 31.86, 6.9, 0.0, 1.0, 1.15, "saturate(.6) brightness(.55)"),
    ("c6_burbujas.mp4", 38.76, 7.72, 2.0, 1.2, 1.02, "brightness(.6) saturate(.8)"),
    ("c10_cabana.mp4", 46.48, 5.19, 0.0, 1.0, 1.14, "saturate(.6) brightness(.6) sepia(.2)"),
]
flash_times = [3.48, 8.86, 12.85, 18.87, 23.2, 28.43, 31.86, 38.76, 46.48, 51.67]
RED_FLASH = {15.2, 37.3, 42.91}

cards = [
    ("hook", 0.0, 3.4, '<div class="hook"><span>SOBREVIVIÓ</span><span>AL TITANIC</span><span class="y sm">…Y A SUS 2 GEMELOS</span></div>'),
    ("tres", 3.48, 1.3, '<div class="hook"><span class="sm">3 BARCOS</span><span class="r">3 DESASTRES</span></div>'),
    ("misma", 4.8, 1.85, '<div class="hook"><span class="sm">LA MISMA</span><span class="y">MUJER</span><span class="sm">A BORDO</span></div>'),
    ("name", 6.71, 2.1, '<div class="brass"><small>TRIPULACIÓN</small><b>VIOLET<br>JESSOP</b><em>CAMARERA</em></div>'),
    ("arg", 8.86, 1.35, '<div class="log">NACIÓ EN <span class="cel">ARGENTINA</span><small>AÑO 1887</small></div>'),
    ("cam", 10.25, 2.5, '<div class="log">CAMARERA<br>EN BARCOS<small>DE LÍNEA ENTRE CONTINENTES</small></div>'),
    ("d1911", 12.85, 1.3, '<div class="dateb"><small>BARCO N.º 1</small><b>1911</b><b class="sm2 y">OLYMPIC</b></div>'),
    ("ilesa", 17.12, 1.65, '<div class="hook"><span class="g">ILESA</span></div>'),
    ("famoso", 18.87, 2.95, '<div class="hook"><span class="sm">SU GEMELO</span><span class="y">MÁS FAMOSO</span></div>'),
    ("tit", 21.9, 1.3, '<div class="dateb"><small>BARCO N.º 2 · 1912</small><b class="ice">TITANIC</b></div>'),
    ("noche", 23.2, 2.9, '<div class="log">LA NOCHE<br>DEL ICEBERG</div>'),
    ("bebe", 26.29, 2.0, '<div class="log">CON UN BEBÉ<br><span class="y2">AJENO</span> EN BRAZOS</div>'),
    ("sobre2", 28.43, 1.25, '<div class="hook"><span class="g">SOBREVIVIÓ</span></div>'),
    ("pero", 29.74, 1.95, '<div class="hook"><span class="sm">PERO FALTABA</span><span class="r">EL TERCERO</span></div>'),
    ("d1916", 31.86, 1.75, '<div class="dateb"><small>BARCO N.º 3</small><b>1916</b><b class="sm2 y">BRITANNIC</b></div>'),
    ("hosp", 33.65, 2.6, '<div class="log">BARCO<br><span class="r2">HOSPITAL</span><small>PRIMERA GUERRA MUNDIAL</small></div>'),
    ("egeo", 36.35, 2.3, '<div class="log">MAR EGEO<small>UNA MINA EN SU CAMINO</small></div>'),
    ("salta", 38.76, 3.6, '<div class="hook"><span class="sm">¡SALTÓ</span><span class="y">AL AGUA!</span></div>'),
    ("golpe", 42.91, 1.6, '<div class="hook"><span class="sm">GOLPE EN</span><span class="r">LA CABEZA</span></div>'),
    ("otra", 44.61, 1.8, '<div class="hook"><span class="g">OTRA VEZ</span></div>'),
    ("mar30", 46.48, 2.0, '<div class="brass"><small>SIGUIÓ NAVEGANDO</small><b>+30 AÑOS</b><em>EN EL MAR</em></div>'),
    ("tierra", 48.54, 2.75, '<div class="log">MURIÓ EN<br><span class="y2">TIERRA FIRME</span></div>'),
    ("fin", 51.67, DUR - 51.67, '<div class="hook"><span class="sm">PORQUE</span><span class="y">ELLA…</span></div>'),
]

CSS = f'''
:root {{ --noche:#060c16; --hueso:#f3ead8; --aji:#ffc629; --rojo:#ff3b2b; --mar:#6fc3e8; --laton:#c9a24a; --verde:#52e38a; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--noche); }}
#root {{ position:relative; width:{W}px; height:{H}px; font-family:"Montserrat", sans-serif; background:var(--noche); }}
#cam {{ position:absolute; inset:-40px; z-index:1; }}
.bg {{ position:absolute; inset:40px; width:{W}px; height:{H}px; object-fit:cover; z-index:1; }}
.shade {{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg, rgba(6,12,22,.78) 0%, rgba(6,12,22,.35) 30%, rgba(6,12,22,.15) 50%, rgba(6,12,22,.72) 74%, rgba(6,12,22,.95) 100%); }}
.grain {{ position:absolute; inset:0; z-index:3; background:repeating-linear-gradient(90deg, rgba(255,255,255,.025) 0 1px, transparent 1px 4px); }}
.vign {{ position:absolute; inset:0; z-index:3; background:radial-gradient(ellipse at center, rgba(0,0,0,0) 52%, rgba(0,0,0,.7) 100%); }}
.card {{ position:absolute; left:0; right:0; top:200px; z-index:6; text-align:center; }}
.hook span {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:160px; line-height:1.0; color:#fff; text-transform:uppercase; text-shadow:0 6px 30px rgba(0,0,0,.85); }}
.hook .sm {{ font-size:96px; }}
.y {{ color:var(--aji) !important; }}
.r {{ color:var(--rojo) !important; }}
.g {{ color:var(--verde) !important; }}
.dateb small {{ display:block; font-family:"Space Mono", monospace; font-weight:700; font-size:44px; letter-spacing:.22em; color:var(--mar); }}
.dateb b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:220px; line-height:1; color:#fff; text-shadow:0 8px 40px rgba(0,0,0,.85); }}
.dateb b.sm2 {{ font-size:110px; letter-spacing:.06em; }}
.dateb b.ice {{ font-size:200px; color:#dff4ff; letter-spacing:.04em; text-shadow:0 0 40px rgba(111,195,232,.9), 0 8px 30px rgba(0,0,0,.8); }}
.brass {{ display:inline-block; position:relative; padding:40px 70px; border-radius:22px; background:linear-gradient(160deg,#e9c873 0%,#b98f35 45%,#8a6522 100%); border:6px solid #5a3f12; color:#2a1c06; box-shadow:0 30px 70px rgba(0,0,0,.65), inset 0 2px 0 rgba(255,255,255,.5); }}
.brass:before, .brass:after {{ content:""; position:absolute; top:22px; width:22px; height:22px; border-radius:50%; background:#5a3f12; box-shadow:0 0 0 4px #e9c873 inset; }}
.brass:before {{ left:22px; }} .brass:after {{ right:22px; }}
.brass small {{ display:block; font-family:"Space Mono", monospace; font-weight:700; font-size:38px; letter-spacing:.2em; }}
.brass b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:140px; line-height:1; margin:12px 0; }}
.brass em {{ display:block; font-style:normal; font-family:"Space Mono", monospace; font-weight:700; font-size:42px; letter-spacing:.14em; }}
.log {{ display:inline-block; padding:34px 56px; background:var(--hueso); color:#13202e; border-left:18px solid var(--rojo); font-family:"Oswald", sans-serif; font-weight:700; font-size:100px; line-height:1.02; text-align:left; transform:rotate(-2deg); box-shadow:0 26px 60px rgba(0,0,0,.6); }}
.log small {{ display:block; margin-top:12px; font-family:"Space Mono", monospace; font-size:36px; letter-spacing:.06em; color:#7a2a1c; }}
.log .cel {{ color:#2b7fb8; }}
.log .y2 {{ color:#c4581c; }}
.log .r2 {{ color:#c41d1d; }}
.cap {{ position:absolute; left:40px; right:40px; top:1450px; z-index:9; display:flex; flex-wrap:wrap; justify-content:center; gap:6px 0; }}
.cap span {{ display:inline-block; padding:0 14px; font-weight:900; line-height:1.1; color:#fff; text-transform:uppercase; -webkit-text-stroke:3px #060c16; paint-order:stroke fill; text-shadow:0 6px 22px rgba(0,0,0,.85); }}
.cap span.k {{ color:var(--aji); }}
.flash {{ position:absolute; inset:0; z-index:10; background:#fff; opacity:0; }}
.flash.red {{ background:var(--rojo); }}
.fx {{ position:absolute; z-index:5; overflow:visible; }}
.dim {{ position:absolute; inset:0; z-index:4; background:rgba(6,12,22,.6); opacity:0; }}
#ships, #ships2 {{ left:40px; top:760px; width:1000px; height:560px; }}
#map {{ left:90px; top:640px; width:900px; height:760px; }}
#crash {{ left:20px; top:650px; width:1040px; height:700px; }}
#buoy {{ left:290px; top:700px; width:500px; height:620px; }}
#ice {{ left:40px; top:620px; width:1000px; height:780px; }}
#mine {{ left:190px; top:640px; width:700px; height:740px; }}
#prop {{ left:40px; top:600px; width:1000px; height:820px; }}
#age {{ position:absolute; left:0; right:0; top:820px; z-index:6; text-align:center; font-family:"Oswald", sans-serif; font-weight:700; font-size:230px; color:#fff; text-shadow:0 8px 40px rgba(0,0,0,.85); }}
#age small {{ font-size:90px; color:var(--aji); }}
'''


def liner(gid, x, y, s, label=None, sub=None, extra=""):
    g = [f'<g id="{gid}" transform="translate({x} {y}) scale({s})" {extra}>']
    g.append('<path d="M-10 40 L0 18 M0 18 L0 -40 M270 18 L270 -40" stroke="#c8d3da" stroke-width="3"/>')
    g.append('<path d="M-30 30 L300 30 L290 30 L278 78 L-6 78 Z" fill="#0e1a24" stroke="#c8d3da" stroke-width="3"/>')
    g.append('<path d="M-6 66 L280 66" stroke="#b33" stroke-width="7"/>')
    g.append('<rect x="20" y="12" width="230" height="18" fill="#f3ead8"/>')
    for k in range(10):
        g.append(f'<circle cx="{-5 + k*28}" cy="44" r="3.2" fill="#ffd77a"/>')
    for k, fx in enumerate((50, 102, 154, 206)):
        g.append(f'<path d="M{fx} 12 L{fx+4} -38 L{fx+30} -38 L{fx+30} 12 Z" fill="#d9a441" stroke="#0e1a24" stroke-width="3"/>')
        g.append(f'<rect x="{fx+3}" y="-38" width="27" height="9" fill="#0e1a24"/>')
    if label:
        g.append(f'<text x="135" y="122" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="40" fill="#fff">{label}</text>')
    if sub:
        g.append(f'<text x="135" y="162" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="28" fill="#ffc629">{sub}</text>')
    g.append('</g>')
    return "".join(g)


def ships_svg(sid, start, dur, prefix):
    sv = [f'<svg id="{sid}" class="clip fx" data-start="{start}" data-duration="{dur:.2f}" viewBox="0 0 1000 560">']
    sv.append('<path d="M0 330 Q125 312 250 330 T500 330 T750 330 T1000 330 L1000 560 L0 560 Z" fill="#0b2a40" fill-opacity=".85"/>')
    sv.append(f'<path id="{prefix}wave" d="M0 340 Q60 328 120 340 T240 340 T360 340 T480 340 T600 340 T720 340 T840 340 T960 340 T1080 340" fill="none" stroke="#6fc3e8" stroke-width="4" stroke-opacity=".7"/>')
    names = [("OLYMPIC", "1911"), ("TITANIC", "1912"), ("BRITANNIC", "1916")]
    for k, (n, yv) in enumerate(names):
        sv.append(liner(f"{prefix}s{k}", 30 + k * 330, 262, 1.0, n, yv))
        bx, by = 30 + k * 330 + 135, 300
        pts = []
        for a in range(16):
            r = 70 if a % 2 == 0 else 30
            pts.append(f"{bx + r*math.cos(a*math.pi/8):.0f},{by + r*math.sin(a*math.pi/8):.0f}")
        sv.append(f'<polygon id="{prefix}b{k}" points="{" ".join(pts)}" fill="#ff3b2b" stroke="#ffc629" stroke-width="5" opacity="0"/>')
    sv.append(f'<g id="{prefix}her" opacity="0"><circle cx="0" cy="0" r="20" fill="#ffc629" stroke="#060c16" stroke-width="4"/><text x="0" y="-34" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="40" fill="#ffc629">VIOLET</text></g>')
    sv.append('</svg>\n')
    return "".join(sv)


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
P.append(f'<div id="grain" class="clip grain" data-start="0" data-duration="{DUR}"></div>\n')
P.append(f'<div id="vign" class="clip vign" data-start="0" data-duration="{DUR}"></div>\n')
for k, t in enumerate(flash_times + sorted(RED_FLASH)):
    cls = "flash red" if t in RED_FLASH else "flash"
    P.append(f'<div id="fl{k}" class="clip {cls}" data-start="{max(t-0.05,0):.2f}" data-duration="0.5"></div>\n')
for did, s, d in [("dimA", 14.1, 2.6), ("dimB", 23.15, 4.9), ("dimC", 36.3, 6.2), ("dimD", 51.6, DUR - 51.6)]:
    P.append(f'<div id="{did}" class="clip dim" data-start="{s}" data-duration="{d:.2f}"></div>\n')

# 1) TRES BARCOS GEMELOS (gancho, segundo 0) y su eco al final (bucle)
P.append(ships_svg("ships", 0.0, 6.65, "a"))
P.append(ships_svg("ships2", 51.67, DUR - 51.67, "z"))

# 2) MAPA: Argentina -> Europa (8.86 – 12.8)
mp = ['<svg id="map" class="clip fx" data-start="8.86" data-duration="3.95" viewBox="0 0 900 760">',
      '<rect x="0" y="0" width="900" height="760" rx="28" fill="#0a1d2e" fill-opacity=".86" stroke="#6fc3e8" stroke-width="4"/>']
for gx in range(90, 900, 90):
    mp.append(f'<path d="M{gx} 16 V744" stroke="#6fc3e8" stroke-opacity=".1" stroke-width="2"/>')
for gy in range(95, 760, 95):
    mp.append(f'<path d="M16 {gy} H884" stroke="#6fc3e8" stroke-opacity=".1" stroke-width="2"/>')
mp.append('<path d="M150 150 Q240 130 300 190 Q340 260 300 330 Q270 400 245 480 Q225 560 210 640 Q190 690 180 640 Q170 560 160 470 Q140 380 120 300 Q105 210 150 150 Z" fill="#6fc3e8" fill-opacity=".2" stroke="#6fc3e8" stroke-width="3"/>')
mp.append('<path d="M620 120 Q700 90 780 120 Q820 170 790 220 Q760 260 700 250 Q640 240 620 200 Q600 160 620 120 Z" fill="#6fc3e8" fill-opacity=".2" stroke="#6fc3e8" stroke-width="3"/>')
mp.append('<text x="700" y="300" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="34" fill="#6fc3e8">EUROPA</text>')
mp.append('<text x="470" y="470" text-anchor="middle" font-family="Space Mono" font-weight="700" font-size="30" fill="#6fc3e8" fill-opacity=".7">OCÉANO ATLÁNTICO</text>')
mp.append('<g id="pin"><path d="M225 520 C205 490 205 465 225 455 C245 465 245 490 225 520 Z" fill="#ff3b2b" stroke="#fff" stroke-width="3"/><circle cx="225" cy="472" r="7" fill="#fff"/></g>')
mp.append('<text id="pint" x="250" y="560" font-family="Oswald" font-weight="700" font-size="46" fill="#ffc629">ARGENTINA</text>')
mp.append('<path id="route" d="M240 470 Q420 260 680 200" fill="none" stroke="#ffc629" stroke-width="7" stroke-dasharray="16 14" stroke-linecap="round"/>')
mp.append('<rect id="routemask" x="0" y="0" width="0" height="0"/>')
mp.append('<g id="boat"><path d="M-30 0 L30 0 L22 14 L-22 14 Z" fill="#f3ead8"/><rect x="-10" y="-14" width="8" height="14" fill="#d9a441"/><rect x="4" y="-14" width="8" height="14" fill="#d9a441"/></g>')
mp.append('</svg>\n')
P.append("".join(mp))

# 3) CHOQUE: Olympic vs buque de guerra (14.18 – 16.6)
cr = ['<svg id="crash" class="clip fx" data-start="14.15" data-duration="2.5" viewBox="0 0 1040 700">',
      '<path d="M0 420 Q130 400 260 420 T520 420 T780 420 T1040 420 L1040 700 L0 700 Z" fill="#0b2a40" fill-opacity=".9"/>',
      liner("oly", 420, 300, 1.75, None, None),
      '<text x="660" y="520" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="52" fill="#fff">OLYMPIC</text>',
      '<g id="war"><path d="M-260 380 L120 380 L230 405 L120 440 L-260 440 Z" fill="#5d6a72" stroke="#d6dde1" stroke-width="4"/>',
      '<rect x="-120" y="350" width="120" height="30" fill="#5d6a72" stroke="#d6dde1" stroke-width="3"/><rect x="-60" y="320" width="34" height="30" fill="#5d6a72" stroke="#d6dde1" stroke-width="3"/>',
      '<path d="M0 362 L80 350" stroke="#d6dde1" stroke-width="8"/>',
      '<text x="40" y="500" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="44" fill="#d6dde1">BUQUE DE GUERRA</text></g>']
pts = []
for a in range(18):
    r = 120 if a % 2 == 0 else 50
    pts.append(f"{470 + r*math.cos(a*math.pi/9):.0f},{405 + r*math.sin(a*math.pi/9):.0f}")
cr.append(f'<polygon id="boom1" points="{" ".join(pts)}" fill="#ffc629" stroke="#ff3b2b" stroke-width="8" opacity="0"/>')
cr.append('<g id="choque" opacity="0"><rect x="300" y="120" width="440" height="120" rx="16" fill="#ff3b2b"/><text x="520" y="208" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="92" fill="#fff">¡CHOQUE!</text></g>')
cr.append('</svg>\n')
P.append("".join(cr))

# 4) SALVAVIDAS CONTADOR (17.12, 28.43, 44.61)
bu = ['<svg id="buoy" class="clip fx" data-start="17.1" data-duration="29.2" viewBox="0 0 500 620">',
      '<defs><mask id="bm"><rect width="500" height="620" fill="#fff"/><circle cx="250" cy="250" r="110" fill="#000"/></mask></defs>',
      '<g id="ring"><circle cx="250" cy="250" r="220" fill="#f3ead8" mask="url(#bm)" stroke="#060c16" stroke-width="6"/>']
for k in range(4):
    a0 = k * 90 + 25
    bu.append(f'<path d="M{250+220*math.cos(math.radians(a0)):.1f} {250+220*math.sin(math.radians(a0)):.1f} A220 220 0 0 1 {250+220*math.cos(math.radians(a0+40)):.1f} {250+220*math.sin(math.radians(a0+40)):.1f} L{250+110*math.cos(math.radians(a0+40)):.1f} {250+110*math.sin(math.radians(a0+40)):.1f} A110 110 0 0 0 {250+110*math.cos(math.radians(a0)):.1f} {250+110*math.sin(math.radians(a0)):.1f} Z" fill="#ff3b2b"/>')
bu.append('<circle cx="250" cy="250" r="165" fill="none" stroke="#7a5a2a" stroke-width="7" stroke-dasharray="20 14"/>')
bu.append('<circle cx="250" cy="250" r="110" fill="none" stroke="#060c16" stroke-width="6"/></g>')
bu.append('<text id="bnum" x="250" y="300" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="150" fill="#ffc629" stroke="#060c16" stroke-width="5" paint-order="stroke">1</text>')
bu.append('<text x="250" y="560" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="64" fill="#fff" stroke="#060c16" stroke-width="5" paint-order="stroke">DE 3</text>')
bu.append('</svg>\n')
P.append("".join(bu))

# 5) ICEBERG + BOTE CON BEBÉ (23.2 – 28.2)
ic = ['<svg id="ice" class="clip fx" data-start="23.2" data-duration="5.0" viewBox="0 0 1000 780">',
      '<path d="M0 470 Q120 455 250 470 T500 470 T750 470 T1000 470 L1000 780 L0 780 Z" fill="#071d2e" fill-opacity=".92"/>',
      '<g id="berg"><path d="M60 470 L150 300 L190 340 L250 230 L330 470 Z" fill="#e6f6ff" stroke="#9fd7f0" stroke-width="4"/><path d="M40 470 L330 470 L280 640 L90 620 Z" fill="#9fd7f0" fill-opacity=".35"/></g>',
      '<g id="tship">' + liner("tsh", 430, 360, 1.7, None, None) + '</g>',
      '<path id="rope1" d="M600 470 L600 470" stroke="#f3ead8" stroke-width="4"/><path id="rope2" d="M720 470 L720 470" stroke="#f3ead8" stroke-width="4"/>',
      '<g id="lb"><path d="M560 0 L760 0 L735 40 L585 40 Z" fill="#f3ead8" stroke="#060c16" stroke-width="4"/></g>',
      '<g id="baby" opacity="0"><circle cx="660" cy="-30" r="34" fill="#ffc629" fill-opacity=".35"/><ellipse cx="660" cy="-28" rx="22" ry="14" fill="#f3ead8" stroke="#ffc629" stroke-width="4"/><circle cx="676" cy="-30" r="8" fill="#f2c9a0"/>',
      '<text x="660" y="-80" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="48" fill="#ffc629">BEBÉ</text></g>',
      '</svg>\n']
P.append("".join(ic))

# 6) MINA NAVAL (36.35 – 38.7)
mn = ['<svg id="mine" class="clip fx" data-start="36.35" data-duration="2.35" viewBox="0 0 700 740">',
      '<path d="M0 200 Q90 185 175 200 T350 200 T525 200 T700 200" fill="none" stroke="#6fc3e8" stroke-width="5"/>',
      '<path d="M0 200 L700 200 L700 740 L0 740 Z" fill="#06263b" fill-opacity=".55"/>',
      '<path d="M350 470 L350 740" stroke="#8a8f93" stroke-width="5" stroke-dasharray="10 8"/>',
      '<g id="mball">']
for a in range(10):
    ang = a * 36
    x1, y1 = 350 + 120 * math.cos(math.radians(ang)), 360 + 120 * math.sin(math.radians(ang))
    x2, y2 = 350 + 160 * math.cos(math.radians(ang)), 360 + 160 * math.sin(math.radians(ang))
    mn.append(f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="#2b3238" stroke-width="16" stroke-linecap="round"/>')
mn.append('<circle cx="350" cy="360" r="125" fill="#3a434a" stroke="#11171b" stroke-width="6"/><circle cx="310" cy="320" r="30" fill="#5c6870"/>')
mn.append('<text x="350" y="380" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="60" fill="#ffc629">MINA</text></g>')
pts = []
for a in range(22):
    r = 330 if a % 2 == 0 else 140
    pts.append(f"{350 + r*math.cos(a*math.pi/11):.0f},{360 + r*math.sin(a*math.pi/11):.0f}")
mn.append(f'<polygon id="mboom" points="{" ".join(pts)}" fill="#ff4a1c" stroke="#ffd34d" stroke-width="12" opacity="0"/>')
mn.append('<circle id="mcore" cx="350" cy="360" r="40" fill="#ffffff" opacity="0"/>')
mn.append('</svg>\n')
P.append("".join(mn))

# 7) HÉLICE QUE ARRASTRA LOS BOTES (38.76 – 42.5)
pr = ['<svg id="prop" class="clip fx" data-start="38.76" data-duration="3.75" viewBox="0 0 1000 820">',
      '<path d="M0 230 Q125 215 250 230 T500 230 T750 230 T1000 230" fill="none" stroke="#6fc3e8" stroke-width="5"/>',
      '<path d="M0 230 L1000 230 L1000 820 L0 820 Z" fill="#06263b" fill-opacity=".5"/>',
      '<path d="M880 300 L1000 300 L1000 640 L880 640 Z" fill="#0e1a24" stroke="#c8d3da" stroke-width="4"/>',
      '<path d="M880 470 L790 470" stroke="#9aa3a8" stroke-width="20"/>',
      '<g id="blades">']
for a in range(3):
    pr.append(f'<path d="M720 470 Q760 360 720 300 Q680 360 720 470 Z" fill="#c79a3c" stroke="#5a3f12" stroke-width="4" transform="rotate({a*120} 720 470)"/>')
pr.append('<circle cx="720" cy="470" r="34" fill="#8a6522" stroke="#5a3f12" stroke-width="4"/></g>')
for k in range(3):
    pr.append(f'<path id="sw{k}" d="M{120 + k*40} {300 + k*130} Q{420} {360 + k*60} 690 470" fill="none" stroke="#6fc3e8" stroke-width="5" stroke-dasharray="18 14" stroke-opacity=".8"/>')
for k, (bx, by) in enumerate([(120, 228), (330, 228)]):
    pr.append(f'<g id="pb{k}" transform="translate({bx} {by})"><path d="M-70 -10 L70 -10 L54 22 L-54 22 Z" fill="#f3ead8" stroke="#060c16" stroke-width="4"/></g>')
pr.append('<g id="viol" transform="translate(120 200)"><circle cx="0" cy="0" r="18" fill="#ffc629" stroke="#060c16" stroke-width="4"/><text x="0" y="-30" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="40" fill="#ffc629">VIOLET</text></g>')
pr.append('<text x="720" y="700" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="56" fill="#fff" stroke="#060c16" stroke-width="4" paint-order="stroke">HÉLICES</text>')
pr.append('</svg>\n')
P.append("".join(pr))

P.append('<div id="age" class="clip" data-start="49.95" data-duration="1.7"><span id="agen">0</span> <small>AÑOS</small></div>\n')

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
        J.append('tl.fromTo("#ci_hook span", {scale:1.2}, {scale:1, duration:.45, ease:"power3.out", stagger:.06}, 0);')
    else:
        J.append(f'tl.fromTo("#ci_{cid}", {{opacity:0, scale:.85, y:30}}, {{opacity:1, scale:1, y:0, duration:.3, ease:"back.out(1.7)"}}, {s});')
    if cid != "fin":
        J.append(f'tl.to("#ci_{cid}", {{opacity:0, duration:.2, ease:"power2.in"}}, {s + d - 0.22:.2f});')
for gi, (gs, ge, chunk) in enumerate(groups):
    for j, (w, a, b) in enumerate(chunk):
        J.append(f'tl.fromTo("#g{gi}w{j}", {{opacity:0, y:40, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.2, ease:"back.out(2.5)"}}, {a:.2f});')
for k, t in enumerate(flash_times + sorted(RED_FLASH)):
    peak = .55 if t in RED_FLASH else .4
    J.append(f'tl.fromTo("#fl{k}", {{opacity:0}}, {{opacity:{peak}, duration:.06}}, {max(t-0.04,0):.2f});')
    J.append(f'tl.to("#fl{k}", {{opacity:0, duration:.3, ease:"power2.out"}}, {t+0.03:.2f});')
for did, s, d in [("dimA", 14.1, 2.6), ("dimB", 23.15, 4.9), ("dimC", 36.3, 6.2), ("dimD", 51.6, DUR - 51.6)]:
    J.append(f'tl.to("#{did}", {{opacity:1, duration:.2}}, {s});')
    if did != "dimD":
        J.append(f'tl.to("#{did}", {{opacity:0, duration:.2}}, {s + d - 0.22:.2f});')


def shake(t, n=6, a=18):
    for k in range(n):
        J.append(f'tl.to("#cam", {{x:{a*math.sin(k*2.3+t):.1f}, y:{a*math.cos(k*1.7+t):.1f}, duration:.06}}, {t + k*0.06:.2f});')
    J.append(f'tl.to("#cam", {{x:0, y:0, duration:.12}}, {t + n*0.06:.2f});')


def ships_anim(p, t0, intro):
    J.append(f'tl.fromTo("#{p}wave", {{x:0}}, {{x:-120, duration:6.5, ease:"none"}}, {t0});')
    for k in range(3):
        J.append(f'tl.fromTo("#{p}s{k}", {{y:0}}, {{y:-8, duration:.9, yoyo:true, repeat:7, ease:"sine.inOut"}}, {t0 + k*0.3:.2f});')
    if intro:
        J.append(f'tl.fromTo("#ships", {{scale:.9, opacity:1}}, {{scale:1, duration:3.4, ease:"none", transformOrigin:"50% 50%"}}, 0);')


ships_anim("a", 0, True)
# impactos 1, 2, 3 y la misma mujer saltando de barco en barco
for k, t in enumerate([3.5, 3.82, 4.14]):
    J.append(f'tl.fromTo("#ab{k}", {{opacity:0, scale:.2, transformOrigin:"50% 50%"}}, {{opacity:.9, scale:1, duration:.14, ease:"power4.out"}}, {t});')
    J.append(f'tl.to("#ab{k}", {{opacity:0, duration:.3}}, {t+0.45:.2f});')
    J.append(f'tl.to("#as{k}", {{rotation:{[6,-8,10][k]}, svgOrigin:"{165 + k*330} 300", duration:.25, yoyo:true, repeat:1}}, {t:.2f});')
    shake(t, 3, 10)
J.append('tl.set("#aher", {opacity:1, x:165, y:190}, 4.85);')
for k in range(3):
    J.append(f'tl.to("#aher", {{keyframes:[{{x:{165 + k*330 + 165}, y:90, duration:.28, ease:"power1.out"}}, {{x:{165 + (k+1)*330 if k < 2 else 825}, y:190, duration:.28, ease:"power1.in"}}]}}, {4.9 + k*0.55:.2f});') if k < 2 else None
J.append('tl.to("#ships", {opacity:0, duration:.25}, 6.4);')

# mapa
J.append('tl.fromTo("#map", {opacity:0, scale:.92}, {opacity:1, scale:1, duration:.35, ease:"back.out(1.6)", transformOrigin:"50% 50%"}, 8.9);')
J.append('tl.fromTo("#pin", {y:-120, opacity:0}, {y:0, opacity:1, duration:.4, ease:"bounce.out"}, 9.1);')
J.append('tl.fromTo("#pint", {opacity:0}, {opacity:1, duration:.3}, 9.4);')
J.append('tl.fromTo("#route", {attr:{"stroke-dashoffset":800}}, {attr:{"stroke-dashoffset":0}, duration:2.2, ease:"none"}, 10.2);')
J.append('tl.fromTo("#boat", {x:240, y:470, opacity:0}, {x:680, y:200, opacity:1, duration:2.2, ease:"power1.inOut"}, 10.2);')
J.append('tl.to("#map", {opacity:0, duration:.25}, 12.55);')

# choque
J.append('tl.fromTo("#crash", {opacity:0}, {opacity:1, duration:.25}, 14.18);')
J.append('tl.fromTo("#war", {x:-120}, {x:250, duration:1.0, ease:"power2.in"}, 14.2);')
J.append('tl.to("#war", {x:220, duration:.3, ease:"power2.out"}, 15.2);')
J.append('tl.fromTo("#boom1", {opacity:0, scale:.2, transformOrigin:"50% 50%"}, {opacity:1, scale:1, duration:.15, ease:"power4.out"}, 15.2);')
J.append('tl.to("#boom1", {opacity:0, duration:.5}, 15.6);')
J.append('tl.to("#oly", {rotation:-4, svgOrigin:"660 400", duration:.3, yoyo:true, repeat:1}, 15.2);')
J.append('tl.fromTo("#choque", {opacity:0, scale:2.5}, {opacity:1, scale:1, svgOrigin:"520 180", duration:.18, ease:"power4.in"}, 15.25);')
shake(15.2, 8, 28)
J.append('tl.to("#crash", {opacity:0, duration:.25}, 16.4);')

# salvavidas contador
J.append('tl.set("#buoy", {opacity:0}, 17.1);')
for t, n, dur in [(17.15, 1, 1.55), (28.45, 2, 1.2), (44.63, 3, 1.75)]:
    J.append(f'tl.set("#bnum", {{textContent:"{n}"}}, {t});')
    J.append(f'tl.fromTo("#buoy", {{opacity:0, y:200, rotation:-40}}, {{opacity:1, y:0, rotation:0, duration:.45, ease:"back.out(1.6)", transformOrigin:"50% 40%"}}, {t});')
    J.append(f'tl.fromTo("#bnum", {{scale:2.2}}, {{scale:1, svgOrigin:"250 250", duration:.3, ease:"back.out(2)"}}, {t + 0.25:.2f});')
    J.append(f'tl.to("#ring", {{rotation:20, svgOrigin:"250 250", duration:{dur:.2f}, ease:"none"}}, {t});')
    J.append(f'tl.to("#buoy", {{opacity:0, duration:.2}}, {t + dur - 0.2:.2f});')

# iceberg y bote
J.append('tl.fromTo("#ice", {opacity:0}, {opacity:1, duration:.3}, 23.2);')
J.append('tl.to("#tship", {rotation:7, svgOrigin:"700 470", y:30, duration:4.8, ease:"power1.in"}, 23.2);')
J.append('tl.fromTo("#berg", {x:-30}, {x:10, duration:4.8, ease:"none"}, 23.2);')
J.append('tl.fromTo("#lb", {y:340}, {y:560, duration:2.4, ease:"power1.inOut"}, 23.7);')
J.append('tl.fromTo("#rope1", {attr:{d:"M600 340 L600 340"}}, {attr:{d:"M600 340 L600 560"}, duration:2.4}, 23.7);')
J.append('tl.fromTo("#rope2", {attr:{d:"M720 340 L720 340"}}, {attr:{d:"M720 340 L720 560"}, duration:2.4}, 23.7);')
J.append('tl.fromTo("#baby", {opacity:0, y:300}, {opacity:1, y:560, duration:.4, ease:"back.out(2)"}, 26.3);')
J.append('tl.to("#baby", {scale:1.12, svgOrigin:"660 530", duration:.3, yoyo:true, repeat:3}, 26.8);')
J.append('tl.to("#ice", {opacity:0, duration:.25}, 27.95);')

# mina
J.append('tl.fromTo("#mine", {opacity:0}, {opacity:1, duration:.25}, 36.35);')
J.append('tl.fromTo("#mball", {y:60}, {y:0, duration:.9, ease:"sine.inOut"}, 36.35);')
J.append('tl.fromTo("#mcore", {opacity:0, attr:{r:20}}, {opacity:1, attr:{r:200}, duration:.2, ease:"power4.out"}, 37.3);')
J.append('tl.fromTo("#mboom", {opacity:0, scale:.2, svgOrigin:"350 360"}, {opacity:1, scale:1, duration:.2, ease:"power4.out"}, 37.3);')
J.append('tl.to("#mball", {opacity:0, duration:.1}, 37.32);')
J.append('tl.to("#mboom", {scale:1.2, opacity:0, svgOrigin:"350 360", duration:.7}, 37.6);')
J.append('tl.to("#mcore", {opacity:0, duration:.6}, 37.6);')
shake(37.3, 9, 30)

# hélice (máxima tensión)
J.append('tl.fromTo("#prop", {opacity:0}, {opacity:1, duration:.25}, 38.76);')
J.append('tl.to("#blades", {rotation:1440, svgOrigin:"720 470", duration:3.7, ease:"power1.in"}, 38.76);')
for k in range(3):
    J.append(f'tl.fromTo("#sw{k}", {{attr:{{"stroke-dashoffset":0}}}}, {{attr:{{"stroke-dashoffset":-320}}, duration:3.6, ease:"none"}}, 38.76);')
J.append('tl.to("#viol", {keyframes:[{x:200, y:120, duration:.3, ease:"power1.out"}, {x:260, y:420, duration:.45, ease:"power2.in"}]}, 39.4);')
J.append('tl.to("#viol", {x:230, y:620, duration:2.0, ease:"sine.out"}, 40.2);')
J.append('tl.to("#pb0", {x:600, y:420, rotation:35, duration:2.6, ease:"power2.in"}, 39.6);')
J.append('tl.to("#pb1", {x:660, y:400, rotation:-30, duration:2.0, ease:"power2.in"}, 40.1);')
shake(40.5, 10, 26)
shake(41.6, 6, 20)
J.append('tl.to("#prop", {opacity:0, duration:.25}, 42.25);')
shake(42.91, 7, 34)

# edad final
J.append('tl.fromTo("#age", {opacity:0, scale:.8}, {opacity:1, scale:1, duration:.3, ease:"back.out(1.7)"}, 49.97);')
J.append('tl.fromTo("#agen", {textContent:0}, {textContent:83, duration:.8, snap:{textContent:1}, ease:"power2.out"}, 50.0);')
J.append('tl.to("#age", {opacity:0, duration:.2}, 51.45);')

# final en bucle: vuelven los tres gemelos como en el primer cuadro
J.append('tl.fromTo("#ships2", {opacity:0, scale:.95}, {opacity:1, scale:1, duration:.4, transformOrigin:"50% 50%"}, 51.67);')
ships_anim("z", 51.67, False)
J.append('window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;')
P.append("</div>\n<script>\n" + "\n".join(J) + "\n</script>\n</body>\n</html>\n")
open(OUT, "w").write("".join(P))
print(len(groups), "grupos", DUR)
