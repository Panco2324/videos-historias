import html, math

W, H, DUR = 1080, 1920, 32.0
OUT = "/home/claude/hf/short3/index.html"

segs = [
    (0.10, 1.64, "1971."),
    (2.68, 5.24, "El cineasta Werner Herzog está en Lima,"),
    (5.69, 8.43, "a punto de subir al vuelo 508 de LANSA."),
    (9.50, 10.08, "No sube."),
    (11.08, 13.81, "Ese avión se parte en el aire sobre la selva peruana."),
    (14.84, 16.43, "Mueren 91 personas."),
    (17.14, 19.63, "Solo sobrevive una chica de 17 años."),
    (21.00, 21.92, "Décadas después,"),
    (22.29, 24.67, "Herzog vuelve con ella al lugar del accidente."),
    (25.75, 26.78, "¿Conoces su historia?"),
    (27.86, 28.34, "Sígueme,"),
    (28.77, 30.35, "la cuento completa en mi canal."),
]
KEY = {"1971.", "Herzog", "508", "No", "sube.", "parte", "91", "Solo", "17", "Décadas", "vuelve", "historia?", "Sígueme,", "completa"}

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

# (archivo, inicio, duración, offset, zoom de, zoom a)
clips = [
    ("raw1.mp4", 0.0, 2.6, 1.0, 1.25, 1.05),
    ("air1b.mp4", 2.6, 8.4, 0.0, 1.0, 1.12),
    ("raw2.mp4", 11.0, 3.8, 0.0, 1.15, 1.0),
    ("raw4.mp4", 14.8, 2.3, 3.0, 1.0, 1.1),
    ("raw5.mp4", 17.1, 3.8, 0.0, 1.12, 1.0),
    ("cam1b.mp4", 20.9, 4.8, 0.0, 1.0, 1.1),
    ("raw6.mp4", 25.7, 6.3, 4.0, 1.1, 1.0),
]
flash_times = [2.6, 9.5, 11.0, 11.9, 12.6, 14.8, 17.1, 20.9, 25.7]

cards = [
    ("hook", 0.0, 2.5, '<div class="hook"><span>Iba a subir</span><span class="y">a ese avión</span></div>'),
    ("m91", 14.9, 2.1, '<div class="big"><b><span id="cnt">0</span></b><small>personas murieron</small></div>'),
    ("uno", 17.2, 3.5, '<div class="big"><b>1</b><small>sobreviviente · 17 años</small></div>'),
    ("dec", 20.95, 4.6, '<div class="dec"><div class="rec"><i id="recdot"></i>REC</div><span>Décadas</span><span class="y">después</span></div>'),
    ("cta", 27.6, 4.4, '<div class="pill">SÍGUEME →</div>'),
]

P = []
P.append(f'''<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
:root {{ --ground:#05161c; --ink:#ffffff; --aji:#ffc629; --rojo:#e23b2e; --papel:#f3e9d2; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--ground); }}
#root {{ position:relative; width:{W}px; height:{H}px; font-family:"Montserrat", sans-serif; }}
#cam {{ position:absolute; inset:-40px; z-index:1; }}
.bg {{ position:absolute; inset:40px; width:{W}px; height:{H}px; object-fit:cover; z-index:1; }}
.shade {{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg, rgba(5,22,28,.72) 0%, rgba(5,22,28,.35) 35%, rgba(5,22,28,.05) 50%, rgba(5,22,28,.75) 78%, rgba(5,22,28,.92) 100%); }}
.card {{ position:absolute; left:0; right:0; top:330px; z-index:5; text-align:center; }}
.hook span, .dec span {{ display:block; font-family:"League Gothic", sans-serif; font-size:190px; line-height:.9; color:var(--ink); text-transform:uppercase; text-shadow:0 6px 30px rgba(0,0,0,.6); }}
.hook .y, .dec .y {{ color:var(--aji); font-size:150px; }}
.big b {{ display:block; font-family:"League Gothic", sans-serif; font-weight:400; font-size:320px; line-height:.85; color:var(--aji); text-shadow:0 8px 40px rgba(0,0,0,.65); font-variant-numeric:tabular-nums; }}
.big small {{ display:block; margin-top:10px; font-weight:900; font-size:54px; letter-spacing:.06em; text-transform:uppercase; color:var(--ink); text-shadow:0 4px 18px rgba(0,0,0,.7); }}
.rec {{ display:inline-flex; align-items:center; gap:18px; margin-bottom:26px; padding:10px 28px; border:4px solid #fff; border-radius:14px; font-weight:900; font-size:48px; color:#fff; letter-spacing:.08em; }}
.rec i {{ display:block; width:30px; height:30px; border-radius:50%; background:var(--rojo); }}
.pill {{ display:inline-block; margin-top:200px; padding:28px 60px; border-radius:999px; background:var(--aji); color:#05161c; font-weight:900; font-size:78px; }}
.cap {{ position:absolute; left:40px; right:40px; top:1110px; z-index:6; display:flex; flex-wrap:wrap; justify-content:center; gap:6px 0; overflow:visible; }}
.cap span {{ display:inline-block; padding:0 14px; font-weight:900; font-size:inherit; line-height:1.1; color:var(--ink); text-transform:uppercase; -webkit-text-stroke:3px #05161c; paint-order:stroke fill; text-shadow:0 6px 22px rgba(0,0,0,.8); }}
.cap span.k {{ color:var(--aji); }}
.flash {{ position:absolute; inset:0; z-index:8; background:#fff; opacity:0; }}
.fx {{ position:absolute; z-index:4; }}
/* pase de abordar */
#pass {{ position:absolute; left:90px; top:300px; width:900px; height:470px; z-index:5; }}
#passin {{ position:relative; width:900px; height:470px; background:var(--papel); border-radius:28px; box-shadow:0 30px 70px rgba(0,0,0,.55); overflow:hidden; color:#1d2a30; }}
#passin .top {{ height:96px; background:#0d3b4c; color:#fff; display:flex; align-items:center; justify-content:space-between; padding:0 40px; font-weight:900; font-size:46px; letter-spacing:.1em; }}
#passin .top em {{ font-style:normal; font-size:30px; letter-spacing:.14em; opacity:.85; }}
#passin .row {{ display:flex; align-items:flex-end; justify-content:space-between; padding:34px 40px 0; }}
#passin .city {{ font-family:"League Gothic", sans-serif; font-size:130px; line-height:.9; }}
#passin .city small {{ display:block; font-family:"Montserrat", sans-serif; font-weight:700; font-size:26px; letter-spacing:.12em; opacity:.6; }}
#passin .arrow {{ font-size:80px; font-weight:900; color:#0d3b4c; padding-bottom:10px; }}
#passin .meta {{ display:flex; gap:56px; padding:30px 40px 0; font-weight:900; font-size:40px; }}
#passin .meta small {{ display:block; font-weight:700; font-size:22px; letter-spacing:.12em; opacity:.6; }}
#passin .bar {{ position:absolute; right:40px; bottom:34px; width:230px; height:90px; background:repeating-linear-gradient(90deg, #1d2a30 0 6px, transparent 6px 10px, #1d2a30 10px 13px, transparent 13px 21px); }}
#stamp {{ position:absolute; left:150px; top:150px; z-index:6; padding:14px 44px; border:12px solid var(--rojo); border-radius:20px; color:var(--rojo); font-family:"League Gothic", sans-serif; font-size:190px; line-height:1; letter-spacing:.04em; background:rgba(243,233,210,.6); }}
/* tormenta y avión */
#plane {{ left:280px; top:420px; width:520px; height:260px; overflow:visible; }}
#bolt {{ left:496px; top:30px; width:240px; height:520px; z-index:7; }}
.sp {{ position:absolute; z-index:6; width:22px; height:22px; border-radius:50%; background:#ffc629; box-shadow:0 0 18px 6px rgba(255,140,0,.8); left:529px; top:539px; }}
.tint {{ position:absolute; inset:0; z-index:2; background:rgba(10,40,70,.38); }}
.cloud {{ position:absolute; width:900px; height:300px; border-radius:50%; background:radial-gradient(closest-side, rgba(160,175,185,.55), rgba(160,175,185,0)); }}
.cb {{ z-index:3; }} .cf {{ z-index:6; }}
.rain {{ position:absolute; z-index:6; width:3px; height:90px; background:linear-gradient(rgba(255,255,255,0), rgba(220,235,245,.55)); top:-120px; }}
.smk {{ position:absolute; z-index:4; width:70px; height:70px; border-radius:50%; background:radial-gradient(closest-side, rgba(70,70,75,.85), rgba(70,70,75,0)); left:505px; top:515px; }}
.spd {{ position:absolute; z-index:3; width:5px; height:220px; background:linear-gradient(rgba(255,255,255,0), rgba(255,255,255,.5), rgba(255,255,255,0)); top:1950px; }}
#seat {{ left:400px; top:-340px; width:280px; height:336px; overflow:visible; }}
#camico {{ left:390px; top:760px; width:300px; height:240px; overflow:visible; z-index:5; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<audio id="voz" class="clip" src="assets/voz.mp3" data-start="0" data-duration="30.35" data-volume="1"></audio>
<audio id="sfx" class="clip" src="assets/sfx.wav" data-start="0" data-duration="32" data-volume="0.45"></audio>
<div id="cam">
''')
for i, (f, s, d, off, z0, z1) in enumerate(clips):
    P.append(f'<video id="bg{i}" class="clip bg" src="assets/{f}" data-start="{s}" data-duration="{d}" data-media-start="{off}" muted playsinline></video>\n')
P.append('</div>\n')
P.append(f'<div id="shade" class="clip shade" data-start="0" data-duration="{DUR}"></div>\n')
for k, t in enumerate(flash_times):
    P.append(f'<div id="fl{k}" class="clip flash" data-start="{max(t-0.05,0):.2f}" data-duration="0.5"></div>\n')

# pase de abordar + sello
P.append('''<div id="pass" class="clip" data-start="5.6" data-duration="5.4"><div id="passin"><div class="top"><span>LANSA</span><em>PASE DE ABORDAR</em></div><div class="row"><div class="city"><small>DESDE</small>LIMA</div><div class="arrow">→</div><div class="city"><small>HACIA</small>PUCALLPA</div></div><div class="meta"><div><small>VUELO</small>508</div><div><small>FECHA</small>24 DIC 1971</div></div><div class="bar"></div></div><div id="stamp">NO SUBIÓ</div></div>\n''')

# avión, rayo, chispas, humo, nubes, lluvia
P.append("""<svg id="plane" class="clip fx" data-start="11.0" data-duration="3.8" viewBox="0 0 200 100" overflow="visible"><g id="pr"><path d="M100 40 L28 40 Q14 40 10 30 L4 8 L18 8 L34 30 L100 30 Z" fill="#dfe7ea"/><path d="M60 46 L96 46 L80 70 L66 70 Z" fill="#b9c6cb"/><rect x="40" y="32" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="52" y="32" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="64" y="32" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="76" y="32" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="88" y="32" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="10" y="24" width="90" height="2" fill="#0d3b4c" opacity=".35"/></g><g id="pf"><path d="M100 30 L160 30 Q188 30 196 38 Q188 46 160 46 L100 46 Z" fill="#eef3f4"/><path d="M104 46 L140 46 L120 84 L106 84 Z" fill="#c7d3d6"/><path d="M168 33 Q178 33 184 37 L168 37 Z" fill="#5d7a86"/><rect x="106" y="34" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="118" y="34" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="130" y="34" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="142" y="34" width="6" height="5" rx="1" fill="#5d7a86"/><rect x="100" y="28" width="96" height="2" fill="#0d3b4c" opacity=".35"/></g><path id="crack" d="M100 28 L94 34 L104 38 L96 44 L102 48" stroke="#ff5a4a" stroke-width="3" fill="none" opacity="0"/></svg>\n""")
for k in range(10):
    P.append(f'<div id="sp{k}" class="clip sp" data-start="11.8" data-duration="3.0"></div>\n')
P.append('<svg id="bolt" class="clip fx" data-start="11.8" data-duration="1.4" viewBox="0 0 120 220"><path d="M70 0 L28 110 L58 110 L22 220 L98 86 L64 86 L96 0 Z" fill="#fff6c2" stroke="#ffc629" stroke-width="4"/></svg>\n')
P.append('<div id="tint" class="clip tint" data-start="11.0" data-duration="3.8"></div>\n')
for k in range(3):
    P.append(f'<div id="cb{k}" class="clip cloud cb" style="left:-900px; top:{300+k*170}px" data-start="11.0" data-duration="3.8"></div>\n')
    P.append(f'<div id="cf{k}" class="clip cloud cf" style="left:-900px; top:{180+k*260}px" data-start="11.0" data-duration="3.8"></div>\n')
for k in range(26):
    P.append(f'<div id="rn{k}" class="clip rain" style="left:{(k*197)%1080}px" data-start="11.0" data-duration="3.8"></div>\n')
for k in range(12):
    P.append(f'<div id="sm{k}" class="clip smk" data-start="12.6" data-duration="2.2"></div>\n')
# asiento cayendo
for k in range(12):
    P.append(f'<div id="sd{k}" class="clip spd" style="left:{(k*173+60)%1040}px" data-start="17.1" data-duration="3.8"></div>\n')
P.append('<svg id="seat" class="clip fx" data-start="17.1" data-duration="3.8" viewBox="0 0 100 120" overflow="visible"><g id="hair"><path d="M40 16 Q30 -6 18 -14 Q34 -10 44 4 Q46 -12 40 -22 Q54 -10 54 6 Q62 -8 74 -12 Q64 0 62 16 Z" fill="#3b2418"/></g><g id="armL"><path d="M36 44 L14 26" stroke="#d9a07a" stroke-width="6" stroke-linecap="round"/></g><g id="armR"><path d="M64 44 L86 26" stroke="#d9a07a" stroke-width="6" stroke-linecap="round"/></g><g fill="#c7d3d6" stroke="#05161c" stroke-width="3"><rect x="28" y="30" width="44" height="58" rx="10"/><rect x="18" y="82" width="64" height="20" rx="8"/><rect x="24" y="102" width="8" height="16"/><rect x="68" y="102" width="8" height="16"/></g><path d="M38 40 Q50 36 62 40 L66 86 L34 86 Z" fill="#e8768f"/><circle cx="50" cy="24" r="11" fill="#d9a07a"/><path d="M40 20 Q50 10 60 20 Q56 14 50 14 Q44 14 40 20 Z" fill="#3b2418"/><circle cx="46" cy="25" r="1.5" fill="#05161c"/><circle cx="54" cy="25" r="1.5" fill="#05161c"/><ellipse cx="50" cy="31" rx="2.5" ry="3" fill="#05161c"/><g id="legs"><path d="M42 86 L38 108 M58 86 L62 108" stroke="#d9a07a" stroke-width="6" stroke-linecap="round"/></g><path d="M32 70 Q50 80 68 70" stroke="#ff5a4a" stroke-width="5" fill="none"/></svg>\n')
# cámara de cine
P.append('<svg id="camico" class="clip fx" data-start="20.95" data-duration="4.6" viewBox="0 0 150 120" overflow="visible"><g id="reel1"><circle cx="45" cy="28" r="24" fill="#1d2a30" stroke="#fff" stroke-width="4"/><circle cx="45" cy="14" r="5" fill="#fff"/><circle cx="33" cy="35" r="5" fill="#fff"/><circle cx="57" cy="35" r="5" fill="#fff"/></g><g id="reel2"><circle cx="92" cy="32" r="20" fill="#1d2a30" stroke="#fff" stroke-width="4"/><circle cx="92" cy="20" r="4" fill="#fff"/><circle cx="82" cy="38" r="4" fill="#fff"/><circle cx="102" cy="38" r="4" fill="#fff"/></g><rect x="20" y="52" width="92" height="56" rx="8" fill="#ffc629" stroke="#05161c" stroke-width="4"/><path d="M112 68 L146 52 L146 108 L112 92 Z" fill="#ffc629" stroke="#05161c" stroke-width="4"/><circle cx="40" cy="70" r="6" fill="#e23b2e"/></svg>\n')

for cid, s, d, inner in cards:
    P.append(f'<div id="c_{cid}" class="clip card" data-start="{s}" data-duration="{d}"><div id="ci_{cid}">{inner}</div></div>\n')
for gi, (gs, ge, chunk) in enumerate(groups):
    nxt = groups[gi+1][0] if gi+1 < len(groups) else DUR
    gdur = min(ge + 0.15, nxt) - gs
    ws = "".join(f'<span id="g{gi}w{j}" class="{"k" if w in KEY else ""}">{html.escape(w)}</span>' for j, (w, a, b) in enumerate(chunk))
    nch = sum(len(w) for w, _, _ in chunk)
    fs = 96 if nch <= 12 else (84 if nch <= 16 else 72)
    P.append(f'<div id="g{gi}" style="font-size:{fs}px" class="clip cap" data-start="{gs:.2f}" data-duration="{gdur:.2f}">{ws}</div>\n')

J = ["const tl = gsap.timeline({ paused: true });"]
for i, (f, s, d, off, z0, z1) in enumerate(clips):
    J.append(f'tl.fromTo("#bg{i}", {{scale:{z0}}}, {{scale:{z1}, duration:{d}, ease:"none"}}, {s});')
for cid, s, d, inner in cards:
    J.append(f'tl.fromTo("#ci_{cid}", {{opacity:0, scale:.85, y:30}}, {{opacity:1, scale:1, y:0, duration:.35, ease:"back.out(1.7)"}}, {s});')
    J.append(f'tl.to("#ci_{cid}", {{opacity:0, duration:.2, ease:"power2.in"}}, {s + d - 0.25:.2f});')
for gi, (gs, ge, chunk) in enumerate(groups):
    for j, (w, a, b) in enumerate(chunk):
        J.append(f'tl.fromTo("#g{gi}w{j}", {{opacity:0, y:40, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.22, ease:"back.out(2.5)"}}, {a:.2f});')
        if w not in KEY:
            J.append(f'tl.to("#g{gi}w{j}", {{color:"#ffc629", duration:.05}}, {a:.2f}); tl.to("#g{gi}w{j}", {{color:"#ffffff", duration:.1}}, {b:.2f});')
for k, t in enumerate(flash_times):
    peak = .9 if t in (9.5, 11.9, 12.6) else .5
    J.append(f'tl.fromTo("#fl{k}", {{opacity:0}}, {{opacity:{peak}, duration:.06}}, {max(t-0.04,0):.2f});')
    J.append(f'tl.to("#fl{k}", {{opacity:0, duration:.3, ease:"power2.out"}}, {t+0.03:.2f});')
# pase entra, flota, sello
J.append('tl.fromTo("#passin", {x:1100, rotation:14}, {x:0, rotation:-3, duration:.7, ease:"back.out(1.4)"}, 5.65);')
J.append('tl.to("#passin", {y:-14, rotation:-1.5, duration:1.5, ease:"sine.inOut", yoyo:true, repeat:1}, 6.4);')
J.append('tl.fromTo("#stamp", {opacity:0, scale:3.2, rotation:-28}, {opacity:1, scale:1, rotation:-12, duration:.16, ease:"power4.in"}, 9.38);')
J.append('tl.to("#pass", {y:60, opacity:0, duration:.3, ease:"power2.in"}, 10.65);')
for k in range(5):
    J.append(f'tl.to("#cam", {{x:{20*math.sin(k*2.3):.1f}, y:{20*math.cos(k*1.7):.1f}, duration:.07}}, {9.54+k*0.07:.2f});')
J.append('tl.to("#cam", {x:0, y:0, duration:.15}, 9.9);')
# tormenta
for k in range(17):
    t = 11.0 + k*0.2; a = 18 if 11.8 < t < 13.2 else 7
    J.append(f'tl.to("#cam", {{x:{a*math.sin(k*2.3):.1f}, y:{a*math.cos(k*1.7):.1f}, duration:.2, ease:"sine.inOut"}}, {t:.2f});')
J.append('tl.to("#cam", {x:0, y:0, duration:.3}, 14.45);')
J.append('tl.fromTo("#plane", {x:-760, y:40, rotation:-4}, {x:0, y:0, rotation:0, duration:.85, ease:"power2.out"}, 11.02);')
J.append('tl.to("#crack", {opacity:1, duration:.05}, 11.95);')
J.append('tl.to("#pf", {x:90, y:420, rotation:38, svgOrigin:"100 40", duration:2.0, ease:"power2.in"}, 12.6);')
J.append('tl.to("#pr", {x:-90, y:420, rotation:-32, svgOrigin:"100 40", duration:2.0, ease:"power2.in"}, 12.6);')
J.append('tl.to("#crack", {opacity:0, duration:.1}, 12.6);')
J.append('tl.to("#plane", {opacity:0, duration:.3}, 14.4);')
J.append('tl.fromTo("#bolt", {opacity:0, scaleY:.2, transformOrigin:"50% 0%"}, {opacity:1, scaleY:1, duration:.12, ease:"power4.out"}, 11.88);')
J.append('tl.to("#bolt", {opacity:.2, duration:.08}, 12.1); tl.to("#bolt", {opacity:1, duration:.06}, 12.2); tl.to("#bolt", {opacity:0, duration:.35}, 12.6);')
for k in range(10):
    ang = k*36*math.pi/180
    dx, dy = 260*math.cos(ang), 260*math.sin(ang)+180
    J.append(f'tl.set("#sp{k}", {{opacity:0}}, 11.8);')
    J.append(f'tl.fromTo("#sp{k}", {{x:0, y:0, opacity:0, scale:1.4}}, {{x:{dx:.0f}, y:{dy:.0f}, opacity:1, scale:.3, duration:1.3, ease:"power2.out"}}, {12.6 + (k%3)*0.05:.2f});')
    J.append(f'tl.to("#sp{k}", {{opacity:0, duration:.3}}, {13.9 + (k%3)*0.05:.2f});')
for k in range(3):
    J.append(f'tl.fromTo("#cb{k}", {{x:0}}, {{x:2100, duration:{3.7-k*0.5:.1f}, ease:"none"}}, {11.0+k*0.2:.2f});')
    J.append(f'tl.fromTo("#cf{k}", {{x:2100, opacity:.8}}, {{x:0, duration:{2.6+k*0.4:.1f}, ease:"none"}}, {11.0+k*0.3:.2f});')
for k in range(26):
    for r in range(6):
        J.append(f'tl.fromTo("#rn{k}", {{y:0, x:0}}, {{y:2150, x:-260, duration:.5, ease:"none"}}, {11.0 + r*0.62 + (k*0.137)%0.6:.2f});')
for k in range(12):
    side = 1 if k % 2 else -1
    t0 = 12.7 + (k//2)*0.25
    J.append(f'tl.fromTo("#sm{k}", {{x:{side*40}, y:{(k//2)*60}, scale:.5, opacity:0}}, {{x:{side*(90+k*6)}, y:{(k//2)*60-140}, scale:2.6, opacity:.9, duration:.45, ease:"power1.out"}}, {t0:.2f});')
    J.append(f'tl.to("#sm{k}", {{opacity:0, scale:3.4, duration:.5}}, {t0+0.45:.2f});')
# contador 91
J.append('const k1={v:0}; tl.to(k1, {v:91, duration:1.1, ease:"power2.out", onUpdate:()=>{document.getElementById("cnt").textContent=Math.round(k1.v)}}, 15.0);')
# asiento
J.append('tl.fromTo("#seat", {y:0, rotation:-25, scale:1.2, opacity:1}, {y:1450, rotation:300, scale:.4, duration:3.5, ease:"power1.in"}, 17.15);')
J.append('tl.to("#seat", {opacity:0, duration:.25}, 20.6);')
for k in range(14):
    t = 17.15 + k*0.26
    J.append(f'tl.to("#hair", {{rotation:{(14 if k%2 else -14)}, svgOrigin:"50 16", duration:.26, ease:"sine.inOut"}}, {t:.2f});')
    J.append(f'tl.to("#armL", {{rotation:{(22 if k%2 else -18)}, svgOrigin:"36 44", duration:.26, ease:"sine.inOut"}}, {t:.2f});')
    J.append(f'tl.to("#armR", {{rotation:{(-22 if k%2 else 18)}, svgOrigin:"64 44", duration:.26, ease:"sine.inOut"}}, {t:.2f});')
    J.append(f'tl.to("#legs", {{rotation:{(8 if k%2 else -8)}, svgOrigin:"50 86", duration:.26, ease:"sine.inOut"}}, {t:.2f});')
for k in range(12):
    for r in range(6):
        J.append(f'tl.fromTo("#sd{k}", {{y:0}}, {{y:-2300, duration:.45, ease:"none"}}, {17.15 + r*0.56 + (k*0.083)%0.5:.2f});')
# cámara de cine
J.append('tl.fromTo("#camico", {opacity:0, scale:.5}, {opacity:1, scale:1, duration:.4, ease:"back.out(1.8)"}, 21.2);')
J.append('tl.to("#reel1", {rotation:720, svgOrigin:"45 28", duration:4.2, ease:"none"}, 21.2);')
J.append('tl.to("#reel2", {rotation:-900, svgOrigin:"92 32", duration:4.2, ease:"none"}, 21.2);')
J.append('tl.to("#camico", {opacity:0, duration:.2}, 25.3);')
J.append('tl.to("#recdot", {opacity:.15, duration:.4, yoyo:true, repeat:9, ease:"steps(1)"}, 21.2);')
# botón final
J.append('tl.to("#ci_cta .pill", {scale:1.08, duration:.35, yoyo:true, repeat:9, ease:"sine.inOut"}, 28.0);')
J.append('window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;')
P.append("</div>\n<script>\n" + "\n".join(J) + "\n</script>\n</body>\n</html>\n")
open(OUT, "w").write("".join(P))
print(len(groups), "grupos")
