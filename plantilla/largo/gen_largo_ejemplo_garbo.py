import html, json, math, os, re, subprocess, sys

ROOT = '/home/claude/largo'
W, H = 1920, 1080
T = json.load(open(f'{ROOT}/timing.json'))
G = {c['id']: c for c in json.load(open(f'{ROOT}/guion.json'))}
CL = json.load(open(f'{ROOT}/clips.json'))

AMBAR = '#f2b33d'; ROJO = '#d23a2a'; PAPEL = '#e9dfc6'; VERDE = '#0f1a14'; TINTA = '#1b1f1a'

def norm(s):
    s = s.lower()
    for a, b in zip('áéíóúü', 'aeiouu'): s = s.replace(a, b)
    return re.sub(r'[^a-z0-9ñ]', '', s)

class Comp:
    def __init__(self, cid, num, title):
        self.cid, self.num, self.title = cid, num, title
        self.OFF = 0.0 if num == 1 else 2.4
        d = T[cid]
        self.vdur = d['dur']
        self.words = [(w, s + self.OFF, e + self.OFF) for w, s, e in d['words']]
        self.DUR = round(self.OFF + self.vdur + (2.2 if num == 9 else 0.9), 2)
        self.H = []; self.J = []; self.n = 0; self.flash = []; self.shakes = []; self.sfx = []
        self.keys = set()

    def at(self, phrase, occ=1):
        toks = [norm(t) for t in phrase.split()]
        ws = [norm(w) for w, _, _ in self.words]
        c = 0
        for i in range(len(ws) - len(toks) + 1):
            if ws[i:i + len(toks)] == toks:
                c += 1
                if c == occ: return self.words[i][1]
        raise ValueError(f'{self.cid}: no encuentro "{phrase}"')

    def end_of(self, phrase):
        toks = [norm(t) for t in phrase.split()]
        ws = [norm(w) for w, _, _ in self.words]
        for i in range(len(ws) - len(toks) + 1):
            if ws[i:i + len(toks)] == toks:
                return self.words[i + len(toks) - 1][2]
        raise ValueError(phrase)

    def uid(self, p='e'):
        self.n += 1; return f'{p}{self.n}'

    def el(self, inner, s, d, cls='', style=''):
        i = self.uid()
        self.H.append(f'<div id="{i}" class="clip {cls}" style="{style}" data-start="{s:.2f}" data-duration="{d:.2f}"><div id="{i}i" class="inner">{inner}</div></div>\n')
        return i

    def pop(self, i, s, d, frm='{opacity:0, scale:.8, y:40}', ease='back.out(1.6)', out=True):
        self.J.append(f'tl.fromTo("#{i}i", {frm}, {{opacity:1, scale:1, y:0, x:0, rotation:0, duration:.45, ease:"{ease}"}}, {s + .02:.2f});')
        if out: self.J.append(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s + d - .28:.2f});')

    def js(self, line): self.J.append(line)

# ---------------- componentes ----------------

def big_text(C, s, d, lines, size=150, top=220, stamp=None, sub=None):
    spans = ''.join(f'<span class="bl" style="color:{c}">{html.escape(t)}</span>' for t, c in lines)
    extra = f'<div class="sub">{html.escape(sub)}</div>' if sub else ''
    dm = C.uid('dm')
    C.H.append(f'<div id="{dm}" class="clip dimcard" data-start="{s:.2f}" data-duration="{d:.2f}"></div>\n')
    C.js(f'tl.fromTo("#{dm}", {{opacity:0}}, {{opacity:1, duration:.3}}, {s:.2f}); tl.to("#{dm}", {{opacity:0, duration:.3}}, {s+d-.3:.2f});')
    i = C.el(f'<div class="bigt" style="font-size:{size}px">{spans}</div>{extra}', s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .bl", {{opacity:0, y:80, skewY:6}}, {{opacity:1, y:0, skewY:0, duration:.5, stagger:.18, ease:"power3.out"}}, {s+.02:.2f});')
    if sub: C.js(f'tl.fromTo("#{i}i .sub", {{opacity:0}}, {{opacity:1, duration:.4}}, {s+.5:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
    if stamp: stamp_on(C, s + stamp[1], d - stamp[1], stamp[0], top + 40)
    return i

def stamp_on(C, s, d, text, top=300, color=ROJO, rot=-12, left=None):
    style = f'top:{top}px;' + (f'left:{left}px;' if left is not None else 'left:0;right:0;text-align:center;')
    i = C.el(f'<span class="stamp" style="color:{color};border-color:{color}">{html.escape(text)}</span>', s, d, 'free', style + 'z-index:9')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, scale:3, rotation:{rot-20}}}, {{opacity:1, scale:1, rotation:{rot}, duration:.18, ease:"power4.in"}}, {s:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.2}}, {s+d-.22:.2f});')
    C.shakes.append(s + .18); C.sfx.append(('boom', s + .15, .5))

def date_card(C, s, d, place, year, left=110, top=150):
    inner = f'<div class="tag"><div class="tag-l">{html.escape(place)}</div><div class="tag-y">{html.escape(year)}</div></div>'
    i = C.el(inner, s, d, 'free', f'left:{left}px;top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, x:-120}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .tag-y", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:.6, ease:"steps(6)"}}, {s+.35:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, x:-60, duration:.3}}, {s+d-.32:.2f});')

def counter(C, s, d, to, label, prefix='', suffix='', top=230, fmt_thousands=False):
    i = C.el(f'<div class="cnt"><b>{prefix}<span class="num">0</span>{suffix}</b><small>{html.escape(label)}</small></div>', s, d, 'card', f'top:{top}px')
    C.pop(i, s, d)
    f = 'Math.round(o.v).toLocaleString("es-ES")' if fmt_thousands else 'Math.round(o.v)'
    C.js(f'(()=>{{const o={{v:0}}; tl.to(o, {{v:{to}, duration:1.4, ease:"power2.out", onUpdate:()=>{{document.querySelector("#{i}i .num").textContent={f}}}}}, {s+.2:.2f});}})();')
    C.sfx.append(('whoosh', s, .6))
    return i

def paper(C, s, d, title, body, stamp=None, top=170, w=1000, rot=-2, typed=True, cls='paper'):
    inner = f'<div class="{cls}" style="width:{w}px"><div class="p-h">{html.escape(title)}</div><div class="p-b">{body}</div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, y:500, rotation:{rot+8}}}, {{opacity:1, y:0, rotation:{rot}, duration:.6, ease:"power3.out"}}, {s+.02:.2f});')
    if typed:
        C.js(f'tl.fromTo("#{i}i .p-b", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:1.2, ease:"steps(8)"}}, {s+.5:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, y:-60, duration:.3}}, {s+d-.32:.2f});')
    C.sfx.append(('whoosh', s, .6))
    if stamp:
        stamp_on(C, s + stamp[1], d - stamp[1], stamp[0], top + 160)
    return i

CITIES = {'Barcelona': (1010, 820), 'Madrid': (800, 850), 'Lisboa': (520, 900), 'Londres': (930, 330), 'Glasgow': (800, 150),
          'Liverpool': (850, 260), 'Swansea': (780, 330), 'Calais': (1040, 400), 'Normandía': (930, 470), 'Berlín': (1400, 300)}

def europe_map(C, s, d, cities, route=None, cross=None, arrows=None, title=None, dim=None):
    """Mapa estilizado: puntos de ciudades, ruta punteada que se dibuja, flechas."""
    i = C.uid('map')
    parts = [f'<svg viewBox="0 0 1920 1080" width="1920" height="1080">',
             '<defs><pattern id="grid%s" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0H0V60" fill="none" stroke="rgba(233,223,198,.07)" stroke-width="2"/></pattern></defs>' % i,
             f'<rect width="1920" height="1080" fill="url(#grid{i})"/>',
             # costas esquemáticas
             '<path d="M720 120 Q780 60 860 110 Q900 180 880 250 Q960 300 990 360 Q960 420 870 410 Q800 380 760 340 Q790 300 760 250 Q740 180 720 120Z" fill="rgba(233,223,198,.13)" stroke="rgba(233,223,198,.45)" stroke-width="3"/>',
             '<path d="M880 440 Q1000 420 1100 380 Q1250 300 1500 260 L1700 300 L1700 760 Q1400 700 1200 720 Q1100 700 1060 760 Q1000 740 980 700 Q900 640 860 560 Q850 500 880 440Z" fill="rgba(233,223,198,.10)" stroke="rgba(233,223,198,.4)" stroke-width="3"/>',
             '<path d="M500 760 Q620 720 760 740 Q900 730 1060 770 Q1080 840 1000 900 Q900 980 760 990 Q620 1000 520 960 Q480 860 500 760Z" fill="rgba(233,223,198,.13)" stroke="rgba(233,223,198,.45)" stroke-width="3"/>']
    if route:
        pts = [CITIES[c] for c in route]
        dpath = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
        parts.append(f'<path id="{i}r" d="{dpath}" fill="none" stroke="{AMBAR}" stroke-width="7" stroke-dasharray="18 14" stroke-linecap="round"/>')
    if arrows:
        for k, (a, b, col) in enumerate(arrows):
            (x1, y1), (x2, y2) = CITIES[a], CITIES[b]
            parts.append(f'<g id="{i}a{k}"><line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="14" stroke-linecap="round"/>'
                         f'<circle cx="{x2}" cy="{y2}" r="26" fill="{col}"/></g>')
    for k, c in enumerate(cities):
        x, y = CITIES[c]
        op = .35 if dim and c in dim else 1
        parts.append(f'<g id="{i}c{k}" opacity="{op}"><circle cx="{x}" cy="{y}" r="15" fill="{PAPEL}"/><circle cx="{x}" cy="{y}" r="30" fill="none" stroke="{PAPEL}" stroke-width="3" opacity=".5"/>'
                     f'<text x="{x+40}" y="{y+14}" font-family="Oswald" font-weight="700" font-size="44" fill="{PAPEL}">{html.escape(c.upper())}</text></g>')
    if cross:
        x, y = CITIES[cross]
        parts.append(f'<g id="{i}x"><line x1="{x-55}" y1="{y-55}" x2="{x+55}" y2="{y+55}" stroke="{ROJO}" stroke-width="16" stroke-linecap="round"/><line x1="{x+55}" y1="{y-55}" x2="{x-55}" y2="{y+55}" stroke="{ROJO}" stroke-width="16" stroke-linecap="round"/></g>')
    parts.insert(4, '<g transform="translate(0,-130)">')
    parts.append('</g></svg>')
    t = f'<div class="maptitle">{html.escape(title)}</div>' if title else ''
    C.H.append(f'<div id="{i}" class="clip mapbox" data-start="{s:.2f}" data-duration="{d:.2f}"><div id="{i}i" class="inner">{"".join(parts)}{t}</div></div>\n')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, scale:1.08}}, {{opacity:1, scale:1, duration:.5}}, {s+.02:.2f});')
    for k in range(len(cities)):
        C.js(f'tl.fromTo("#{i}c{k}", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:.35, ease:"back.out(2)"}}, {s+.3+k*.2:.2f});')
    if route:
        C.js(f'(()=>{{const p=document.getElementById("{i}r"); const L=p.getTotalLength(); p.style.strokeDasharray=L; tl.fromTo(p, {{strokeDashoffset:L}}, {{strokeDashoffset:0, duration:{min(2.5, d*.4):.2f}, ease:"power1.inOut"}}, {s+.6:.2f}); tl.set(p, {{strokeDasharray:"18 14"}}, {s+.6+min(2.5, d*.4):.2f});}})();')
    if arrows:
        for k in range(len(arrows)):
            C.js(f'tl.fromTo("#{i}a{k}", {{opacity:0, scale:.2, transformOrigin:"0% 0%"}}, {{opacity:1, scale:1, duration:.6, ease:"power2.out"}}, {s+.8+k*1.0:.2f});')
    if cross:
        C.js(f'tl.fromTo("#{i}x", {{opacity:0, scale:2, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.2, ease:"power4.in"}}, {s+d*.55:.2f});')
        C.sfx.append(('boom', s + d * .55, .45))
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {s+d-.32:.2f});')
    return i

def icon_row(C, s, d, items, top=300, title=None):
    cells = ''.join(f'<div class="ic"><div class="ic-s">{svg}</div><div class="ic-t">{html.escape(t)}</div></div>' for svg, t in items)
    tt = f'<div class="rowtitle">{html.escape(title)}</div>' if title else ''
    i = C.el(f'{tt}<div class="icrow">{cells}</div>', s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .ic", {{opacity:0, y:60, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.45, stagger:{min(.9, (d-1.5)/max(1,len(items))):.2f}, ease:"back.out(1.8)"}}, {s+.15:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

SV = {
 'guia': '<svg viewBox="0 0 100 100"><rect x="18" y="12" width="64" height="78" rx="6" fill="#2f6b4f"/><rect x="26" y="22" width="48" height="26" rx="3" fill="#e9dfc6"/><path d="M34 40 L44 28 L52 36 L58 30 L68 40Z" fill="#2f6b4f"/><text x="50" y="72" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="14" fill="#e9dfc6">ENGLAND</text></svg>',
 'libros': '<svg viewBox="0 0 100 100"><rect x="14" y="20" width="16" height="70" fill="#8a3b2a"/><rect x="32" y="12" width="18" height="78" fill="#c99a3b"/><rect x="52" y="26" width="14" height="64" fill="#2f4b6b"/><g transform="rotate(14 80 60)"><rect x="70" y="22" width="14" height="68" fill="#5b6b2f"/></g><rect x="8" y="88" width="86" height="6" fill="#e9dfc6"/></svg>',
 'revista': '<svg viewBox="0 0 100 100"><rect x="20" y="10" width="60" height="80" fill="#e9dfc6"/><rect x="20" y="10" width="60" height="18" fill="#d23a2a"/><rect x="28" y="36" width="44" height="26" fill="#8f8f80"/><rect x="28" y="68" width="44" height="4" fill="#1b1f1a"/><rect x="28" y="76" width="30" height="4" fill="#1b1f1a"/></svg>',
 'cine': '<svg viewBox="0 0 100 100"><rect x="12" y="24" width="76" height="52" rx="4" fill="#1b1f1a" stroke="#e9dfc6" stroke-width="4"/><g fill="#e9dfc6"><rect x="16" y="28" width="6" height="6"/><rect x="16" y="66" width="6" height="6"/><rect x="78" y="28" width="6" height="6"/><rect x="78" y="66" width="6" height="6"/></g><path d="M42 38 L62 50 L42 62Z" fill="#f2b33d"/></svg>',
 'tren': '<svg viewBox="0 0 100 100"><rect x="14" y="10" width="72" height="80" fill="#e9dfc6"/><g fill="#1b1f1a"><rect x="22" y="20" width="56" height="8"/><rect x="22" y="36" width="20" height="5"/><rect x="50" y="36" width="28" height="5"/><rect x="22" y="48" width="20" height="5"/><rect x="50" y="48" width="28" height="5"/><rect x="22" y="60" width="20" height="5"/><rect x="50" y="60" width="28" height="5"/><rect x="22" y="72" width="20" height="5"/><rect x="50" y="72" width="28" height="5"/></g></svg>',
 'tinta': '<svg viewBox="0 0 100 100"><path d="M34 30 h32 v10 q14 8 14 26 v20 q0 8 -8 8 h-44 q-8 0 -8 -8 v-20 q0 -18 14 -26z" fill="rgba(170,210,255,.35)" stroke="#e9dfc6" stroke-width="4"/><rect x="36" y="14" width="28" height="16" rx="3" fill="#2a2a2a"/><path d="M26 70 q24 -10 48 0 v14 q0 6 -6 6 h-36 q-6 0 -6 -6z" fill="rgba(170,210,255,.6)"/></svg>',
 'dinero': '<svg viewBox="0 0 100 100"><rect x="10" y="28" width="80" height="44" rx="4" fill="#5c7a4a" stroke="#e9dfc6" stroke-width="3"/><circle cx="50" cy="50" r="13" fill="none" stroke="#e9dfc6" stroke-width="3"/><text x="50" y="57" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="20" fill="#e9dfc6">$</text></svg>',
 'pollo': '<svg viewBox="0 0 100 100"><ellipse cx="50" cy="60" rx="30" ry="24" fill="#f3efe2"/><circle cx="70" cy="34" r="14" fill="#f3efe2"/><path d="M66 18 q4 -10 8 0 q4 -8 7 2z" fill="#d23a2a"/><path d="M83 34 l10 4 l-10 4z" fill="#f2b33d"/><circle cx="73" cy="31" r="2.5" fill="#1b1f1a"/><path d="M40 84 v10 M56 84 v10" stroke="#f2b33d" stroke-width="4"/><path d="M24 54 q-14 -14 -4 -26 q6 10 14 14z" fill="#e2dccb"/></svg>',
 'mision': '<svg viewBox="0 0 100 100"><rect x="14" y="20" width="72" height="60" fill="#c9a76a"/><path d="M14 20 L50 52 L86 20" fill="none" stroke="#7a5a2a" stroke-width="4"/><circle cx="50" cy="62" r="10" fill="#d23a2a"/></svg>',
}

def wine_vs(C, s, d):
    inner = ('<div class="duo">'
             '<div class="duo-c"><svg viewBox="0 0 120 200" width="200"><path d="M20 10 h80 q0 70 -34 86 v70 h28 v10 h-68 v-10 h28 v-70 q-34 -16 -34 -86z" fill="rgba(233,223,198,.15)" stroke="#e9dfc6" stroke-width="5"/><path d="M24 36 h72 q-4 50 -36 56 q-32 -6 -36 -56z" fill="#8e1c2c"/></svg><div class="duo-t">1 LITRO DE VINO</div></div>'
             '<div class="duo-vs">≠</div>'
             '<div class="duo-c"><svg viewBox="0 0 120 200" width="200"><path d="M24 20 h72 l-8 166 h-56z" fill="rgba(233,223,198,.15)" stroke="#e9dfc6" stroke-width="5"/><path d="M28 48 h64 l-6 134 h-52z" fill="#d99a2b"/><path d="M24 20 h72 v28 h-72z" fill="#f3efe2"/></svg><div class="duo-t">CERVEZA Y WHISKY</div></div>'
             '</div>')
    i = C.el(inner, s, d, 'card', 'top:170px')
    C.js(f'tl.fromTo("#{i}i .duo-c", {{opacity:0, y:120}}, {{opacity:1, y:0, duration:.5, stagger:.6, ease:"back.out(1.6)"}}, {s+.05:.2f});')
    C.js(f'tl.fromTo("#{i}i .duo-vs", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.3}}, {s+.9:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def convoy(C, s, d):
    ships = ''.join(f'<g class="ship" transform="translate({160+k*330},{40+ (k%2)*50})"><path d="M0 60 h220 l-30 40 h-160z" fill="#5d6a70"/><rect x="60" y="24" width="80" height="36" fill="#7b878c"/><rect x="90" y="0" width="16" height="26" fill="#3a4448"/></g>' for k in range(4))
    inner = f'<svg viewBox="0 0 1600 260" width="1600"><path d="M0 200 Q200 180 400 200 T800 200 T1200 200 T1600 200 V260 H0Z" fill="rgba(80,140,170,.4)"/>{ships}</svg><div class="lbl">CONVOY BRITÁNICO</div>'
    i = C.el(inner, s, d, 'card', 'top:250px')
    C.js(f'tl.fromTo("#{i}i .ship", {{x:-1900}}, {{x:0, duration:1.4, stagger:.15, ease:"power2.out"}}, {s+.05:.2f});')
    C.js(f'tl.to("#{i}i .ship", {{y:"+=8", duration:.8, yoyo:true, repeat:{int(d/0.8)}, ease:"sine.inOut"}}, {s+1.5:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
    stamp_on(C, s + min(2.6, d * .5), d - min(2.6, d * .5), 'NO EXISTE', 330)

def network(C, s, d, n=27, top=110):
    import random
    random.seed(7)
    nodes = []
    for k in range(n):
        col, row = k % 9, k // 9
        nodes.append((140 + col * 200 + random.randint(-40, 40), 120 + row * 230 + random.randint(-40, 40)))
    cx, cy = 960, 450
    lines = ''.join(f'<line class="str" x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{ROJO}" stroke-width="4"/>' for x, y in nodes)
    pins = ''.join(f'<g class="nd"><rect x="{x-44}" y="{y-54}" width="88" height="108" fill="{PAPEL}" transform="rotate({(k*37)%11-5} {x} {y})"/><circle cx="{x}" cy="{y-20}" r="20" fill="#3d3d36"/><path d="M{x-30} {y+40} q30 -50 60 0z" fill="#3d3d36"/><circle cx="{x}" cy="{y-54}" r="9" fill="{ROJO}"/></g>' for k, (x, y) in enumerate(nodes))
    center = f'<g id="ctr"><circle cx="{cx}" cy="{cy}" r="78" fill="{AMBAR}"/><text x="{cx}" y="{cy+22}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="58" fill="{VERDE}">GARBO</text></g>'
    inner = f'<svg viewBox="0 0 1920 900" width="1920" height="900"><rect width="1920" height="900" fill="#5a4630" opacity=".55"/>{lines}{pins}{center}</svg>'
    i = C.el(inner, s, d, 'free', f'left:0;top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.4}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i #ctr", {{scale:0, transformOrigin:"960px 450px"}}, {{scale:1, duration:.5, ease:"back.out(2)"}}, {s+.1:.2f});')
    C.js(f'tl.fromTo("#{i}i .nd", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.25, stagger:{min(.12,(d-2)/n):.3f}, ease:"back.out(2)"}}, {s+.4:.2f});')
    C.js(f'tl.fromTo("#{i}i .str", {{opacity:0}}, {{opacity:.85, duration:.25, stagger:{min(.12,(d-2)/n):.3f}}}, {s+.45:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {s+d-.32:.2f});')
    return i

def profiles(C, s, d, people):
    cards = ''.join(f'<div class="pf"><div class="pf-ph"><svg viewBox="0 0 100 100"><circle cx="50" cy="38" r="20" fill="#3d3d36"/><path d="M14 100 q36 -60 72 0z" fill="#3d3d36"/><path d="M26 22 h48 l-6 -10 h-36z" fill="#3d3d36"/></svg></div><div class="pf-n">AGENTE {k+1}</div><div class="pf-t">{html.escape(t)}</div><div class="pf-x">FALSO</div></div>' for k, t in enumerate(people))
    i = C.el(f'<div class="pfrow">{cards}</div>', s, d, 'card', 'top:150px')
    C.js(f'tl.fromTo("#{i}i .pf", {{opacity:0, y:200, rotation:6}}, {{opacity:1, y:0, rotation:0, duration:.5, stagger:{(d*.55)/len(people):.2f}, ease:"back.out(1.5)"}}, {s+.05:.2f});')
    C.js(f'tl.fromTo("#{i}i .pf-x", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.18, stagger:.12, ease:"power4.in"}}, {s+d*.8:.2f});')
    C.shakes.append(s + d * .8 + .2); C.sfx.append(('boom', s + d * .8 + .1, .5))
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def obituary(C, s, d, head, name, body, stamp_txt=None, top=120):
    inner = f'<div class="news"><div class="nw-top">{html.escape(head)}</div><div class="nw-rule"></div><div class="nw-cross">✝</div><div class="nw-name">{html.escape(name)}</div><div class="nw-body">{html.escape(body)}</div><div class="nw-cols"><i></i><i></i><i></i></div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, rotation:-540, scale:.1}}, {{opacity:1, rotation:-3, scale:1, duration:.9, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
    C.sfx.append(('whoosh', s, .7))
    if stamp_txt: stamp_on(C, s + min(2.2, d * .55), d - min(2.2, d * .55), stamp_txt, top + 260)

def clock(C, s, d, h1, h2, label):
    ang1, ang2 = h1 * 30, h2 * 30
    ticks = ''.join(f'<rect x="147" y="18" width="6" height="22" fill="{PAPEL}" transform="rotate({k*30} 150 150)"/>' for k in range(12))
    inner = (f'<div class="clockbox"><svg viewBox="0 0 300 300" width="460"><circle cx="150" cy="150" r="140" fill="{TINTA}" stroke="{PAPEL}" stroke-width="10"/>{ticks}'
             f'<rect id="hh" x="144" y="70" width="12" height="86" rx="6" fill="{AMBAR}"/><rect id="mh" x="147" y="36" width="6" height="120" rx="3" fill="{PAPEL}"/><circle cx="150" cy="150" r="12" fill="{ROJO}"/></svg>'
             f'<div class="clk-t"><span id="clkd">{h1}:00</span><small>{html.escape(label)}</small></div></div>')
    i = C.el(inner, s, d, 'card', 'top:180px')
    C.pop(i, s, d)
    C.js(f'tl.set("#{i}i #hh", {{rotation:{ang1}, svgOrigin:"150 150"}}, {s:.2f}); tl.set("#{i}i #mh", {{rotation:0, svgOrigin:"150 150"}}, {s:.2f});')
    span = d * .55
    C.js(f'tl.to("#{i}i #hh", {{rotation:{ang2}, svgOrigin:"150 150", duration:{span:.2f}, ease:"power1.inOut"}}, {s+1:.2f});')
    C.js(f'tl.to("#{i}i #mh", {{rotation:{(h2-h1)*360}, svgOrigin:"150 150", duration:{span:.2f}, ease:"power1.inOut"}}, {s+1:.2f});')
    C.js(f'(()=>{{const o={{v:{h1}}}; tl.to(o, {{v:{h2}, duration:{span:.2f}, ease:"power1.inOut", onUpdate:()=>{{document.querySelector("#{i}i #clkd").textContent=Math.floor(o.v)+":00"}}}}, {s+1:.2f});}})();')

def medals(C, s, d):
    iron = f'<svg viewBox="0 0 200 200" width="300"><path d="M78 22 H122 L108 88 L178 78 V122 L108 112 L122 178 H78 L92 112 L22 122 V78 L92 88 Z" fill="#1b1b1b" stroke="#c9c9c9" stroke-width="7" stroke-linejoin="round"/></svg>'
    mbe = f'<svg viewBox="0 0 200 240" width="300"><path d="M70 0 h60 l-10 70 h-40z" fill="#7a1f3d"/><path d="M80 0 h8 l-4 70 h-6z M112 0 h8 l2 70 h-6z" fill="#b8b8b8"/><path d="M100 70 L124 100 L160 104 L132 130 L140 168 L100 148 L60 168 L68 130 L40 104 L76 100Z" fill="#d9b24a" stroke="#8a6a1a" stroke-width="5"/><circle cx="100" cy="122" r="20" fill="#7a1f3d" stroke="#d9b24a" stroke-width="4"/></svg>'
    inner = (f'<div class="duo"><div class="duo-c md">{iron}<div class="duo-t">CRUZ DE HIERRO</div><small>ALEMANIA · 1944</small></div>'
             f'<div class="duo-vs">+</div><div class="duo-c md">{mbe}<div class="duo-t">ORDEN DEL IMPERIO BRITÁNICO</div><small>REINO UNIDO · 1944</small></div></div>')
    i = C.el(inner, s, d, 'card', 'top:150px')
    C.js(f'tl.fromTo("#{i}i .md", {{opacity:0, y:-300, rotation:-20}}, {{opacity:1, y:0, rotation:0, duration:.7, stagger:{min(6, d*.45):.2f}, ease:"bounce.out"}}, {s+.05:.2f});')
    C.js(f'tl.fromTo("#{i}i .duo-vs", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+min(6, d*.45):.2f});')
    C.js(f'tl.to("#{i}i .md svg", {{rotation:6, duration:.9, yoyo:true, repeat:{int(d/0.9)}, ease:"sine.inOut", transformOrigin:"50% 0%"}}, {s+.8:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def disguise(C, s, d):
    inner = (f'<div class="dsg"><svg viewBox="0 0 300 340" width="420"><circle cx="150" cy="130" r="80" fill="#c99a76"/><path d="M70 110 q80 -90 160 0 q-10 -60 -80 -64 q-70 4 -80 64z" fill="#3b2a1e"/>'
             f'<g id="beard" opacity="0"><path d="M74 140 q10 110 76 120 q66 -10 76 -120 q-20 50 -76 54 q-56 -4 -76 -54z" fill="#3b2a1e"/></g>'
             f'<g id="glasses" opacity="0"><circle cx="118" cy="128" r="28" fill="rgba(255,255,255,.15)" stroke="#111" stroke-width="10"/><circle cx="182" cy="128" r="28" fill="rgba(255,255,255,.15)" stroke="#111" stroke-width="10"/><rect x="144" y="122" width="12" height="8" fill="#111"/></g>'
             f'<path d="M30 340 q120 -130 240 0z" fill="#2f4b6b"/></svg><div class="dsg-t">NUEVA IDENTIDAD</div></div>')
    i = C.el(inner, s, d, 'card', 'top:150px')
    C.pop(i, s, d)
    C.js(f'tl.fromTo("#{i}i #beard", {{opacity:0, scaleY:.2, transformOrigin:"50% 0%"}}, {{opacity:1, scaleY:1, duration:.6}}, {s+1.0:.2f});')
    C.js(f'tl.fromTo("#{i}i #glasses", {{opacity:0, y:-120}}, {{opacity:1, y:0, duration:.4, ease:"bounce.out"}}, {s+2.2:.2f});')

def subscribe(C, s, d):
    i = C.el('<div class="cta"><span class="bell">🔔</span> SUSCRÍBETE</div>', s, d, 'card', 'top:560px')
    C.pop(i, s, d)
    C.js(f'tl.to("#{i}i .cta", {{scale:1.07, duration:.4, yoyo:true, repeat:{int(d/0.4)-2}, ease:"sine.inOut"}}, {s+.6:.2f});')
    C.js(f'tl.to("#{i}i .bell", {{rotation:18, duration:.12, yoyo:true, repeat:{int(d/0.12)-4}, ease:"sine.inOut", transformOrigin:"50% 0%"}}, {s+.6:.2f});')

def versus(C, s, d, a, b):
    inner = f'<div class="vs"><div class="vs-c" style="background:#7a1f1f">{html.escape(a)}<i class="vx"></i></div><div class="vs-m">VS</div><div class="vs-c" style="background:#2b2b2b">{html.escape(b)}<i class="vx"></i></div></div>'
    i = C.el(inner, s, d, 'card', 'top:300px')
    C.js(f'tl.fromTo("#{i}i .vs-c", {{opacity:0, x:(k)=>k?600:-600}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {s+.05:.2f});')
    C.js(f'tl.fromTo("#{i}i .vs-m", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.3}}, {s+.5:.2f});')
    C.js(f'tl.fromTo("#{i}i .vx", {{opacity:0, scale:2.5}}, {{opacity:1, scale:1, duration:.18, stagger:.25, ease:"power4.in"}}, {s+d*.6:.2f});')
    C.shakes.append(s + d * .6 + .2); C.sfx.append(('boom', s + d * .6 + .1, .5))
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def door(C, s, d, n_no=2):
    inner = (f'<div class="door"><svg viewBox="0 0 400 520" width="380"><rect x="20" y="20" width="360" height="500" fill="#3a2a1c" stroke="{PAPEL}" stroke-width="8"/><rect x="60" y="70" width="120" height="180" fill="#4a3624"/><rect x="220" y="70" width="120" height="180" fill="#4a3624"/><rect x="60" y="290" width="120" height="180" fill="#4a3624"/><rect x="220" y="290" width="120" height="180" fill="#4a3624"/><circle cx="330" cy="280" r="14" fill="{AMBAR}"/></svg><div class="door-t">EMBAJADA BRITÁNICA · MADRID</div></div>')
    i = C.el(inner, s, d, 'card', 'top:120px')
    C.pop(i, s, d)
    for k in range(n_no):
        t0 = s + 1.0 + k * (d - 1.6) / n_no
        stamp_on(C, t0, s + d - t0, 'NO', 200 + k * 160, ROJO, -14 + k * 22, left=700 + k * 300)

def double_agent(C, s, d):
    inner = (f'<div class="flow"><div class="fl-b" style="background:{PAPEL};color:{TINTA}">JUAN</div><div class="fl-a">→</div>'
             f'<div class="fl-b" style="background:#2b2b2b;color:{PAPEL}">ESPÍA NAZI<small>(de mentira)</small></div><div class="fl-a">→</div>'
             f'<div class="fl-b" style="background:#24406b;color:{PAPEL}">AGENTE BRITÁNICO</div></div>')
    i = C.el(inner, s, d, 'card', 'top:330px')
    C.js(f'tl.fromTo("#{i}i .fl-b, #{i}i .fl-a", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.4, stagger:.45, ease:"power3.out"}}, {s+.05:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def telegram(C, s, d, lines, head='TELEGRAMA · URGENTE', top=200, stamp=None):
    body = '<br>'.join(html.escape(l) for l in lines)
    inner = f'<div class="tele"><div class="te-h">{html.escape(head)}</div><div class="te-b">{body}</div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, scaleY:0, transformOrigin:"50% 0%"}}, {{opacity:1, scaleY:1, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .te-b", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{min(2.2, d*.45):.2f}, ease:"steps(22)"}}, {s+.5:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
    C.sfx.append(('whoosh', s, .5))
    if stamp: stamp_on(C, s + stamp[1], d - stamp[1], stamp[0], top + 120)

def fake_army(C, s, d):
    inner = (f'<div class="army"><svg viewBox="0 0 900 360" width="1200"><g id="tank"><rect x="200" y="200" width="460" height="90" rx="40" fill="#4f6b3a"/><rect x="300" y="130" width="230" height="90" rx="30" fill="#5f7d46"/><rect x="520" y="160" width="260" height="22" rx="10" fill="#5f7d46"/>'
             f'<g fill="#2f3f22">{"".join(f"<circle cx=\"{250+k*80}\" cy=\"290\" r=\"34\"/>" for k in range(6))}</g></g>'
             f'<path id="valve" d="M640 120 q20 -40 50 -30" stroke="{PAPEL}" stroke-width="10" fill="none"/></svg><div class="army-t">EJÉRCITO FALSO · TANQUES INFLABLES</div></div>')
    i = C.el(inner, s, d, 'card', 'top:220px')
    C.pop(i, s, d)
    C.js(f'tl.fromTo("#{i}i #tank", {{scaleY:.05, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:1.2, ease:"elastic.out(1,.4)"}}, {s+.3:.2f});')
    C.js(f'tl.to("#{i}i #tank", {{scaleX:1.02, scaleY:.98, duration:.5, yoyo:true, repeat:{int(d/0.5)-3}, ease:"sine.inOut", transformOrigin:"50% 100%"}}, {s+1.6:.2f});')

def troops(C, s, d):
    # flechas de tropas que se dan la vuelta
    arrows = ''.join(f'<g class="tr" transform="translate(0,{k*90})"><path d="M200 0 h420 l0 -26 l70 46 l-70 46 l0 -26 h-420z" fill="#2b2b2b" stroke="{PAPEL}" stroke-width="4"/></g>' for k in range(4))
    inner = (f'<div class="troops"><div class="tp-l">NORMANDÍA ←</div><svg viewBox="0 0 900 360" width="1100">{arrows}</svg><div class="tp-r">→ CALAIS</div></div>')
    i = C.el(inner, s, d, 'card', 'top:300px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .tr", {{x:300, scaleX:-1, transformOrigin:"445px 20px"}}, {{x:-120, duration:1.2, stagger:.1, ease:"power1.inOut"}}, {s+.1:.2f});')
    C.js(f'tl.to("#{i}i .tr", {{scaleX:1, duration:.5, stagger:.12, ease:"back.out(1.6)", transformOrigin:"445px 20px"}}, {s+1.6:.2f});')
    C.js(f'tl.to("#{i}i .tr", {{x:360, duration:1.4, stagger:.1, ease:"power2.in"}}, {s+2.3:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
    C.sfx.append(('whoosh', s + 1.6, .6))

def book(C, s, d, title, year):
    inner = f'<div class="book"><div class="bk-c"><div class="bk-t">{html.escape(title)}</div><div class="bk-l"></div><div class="bk-y">{html.escape(year)}</div></div></div>'
    i = C.el(inner, s, d, 'card', 'top:140px')
    C.js(f'tl.fromTo("#{i}i .bk-c", {{opacity:0, rotationY:-90, transformPerspective:1200}}, {{opacity:1, rotationY:-12, duration:.8, ease:"power3.out"}}, {s+.05:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def big_number_pair(C, s, d, a, la, b, lb):
    inner = f'<div class="pair"><div><b class="na">0</b><small>{html.escape(la)}</small></div><div><b class="nb">0</b><small>{html.escape(lb)}</small></div></div>'
    i = C.el(inner, s, d, 'card', 'top:220px')
    C.pop(i, s, d)
    C.js(f'(()=>{{const o={{a:0,b:0}}; tl.to(o, {{a:{a}, b:{b}, duration:1.6, ease:"power2.out", onUpdate:()=>{{document.querySelector("#{i}i .na").textContent=Math.round(o.a);document.querySelector("#{i}i .nb").textContent=Math.round(o.b)}}}}, {s+.2:.2f});}})();')

def title_card(C):
    i = C.el(f'<div class="chap"><div class="ch-n">CAPÍTULO {C.num - 1}</div><div class="ch-t">{html.escape(C.title.upper())}</div><div class="ch-l"></div></div>', 0, C.OFF, 'card', 'top:330px;z-index:9')
    C.js(f'tl.fromTo("#{i}i .ch-n", {{opacity:0, scaleX:1.6}}, {{opacity:1, scaleX:1, duration:.8, ease:"power3.out"}}, .05);')
    C.js(f'tl.fromTo("#{i}i .ch-t", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.6, ease:"power3.out"}}, .3);')
    C.js(f'tl.fromTo("#{i}i .ch-l", {{scaleX:0}}, {{scaleX:1, duration:.8, ease:"power3.out"}}, .5);')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {C.OFF-.35:.2f});')
    C.H.append(f'<div id="tcdim" class="clip" style="position:absolute;inset:0;z-index:8;background:rgba(10,14,10,.72)" data-start="0" data-duration="{C.OFF:.2f}"></div>\n')
    C.js(f'tl.to("#tcdim", {{opacity:0, duration:.35}}, {C.OFF-.4:.2f});')
    C.sfx.append(('boom', .05, .35)); C.sfx.append(('whoosh', C.OFF - .45, .6))

# ---------------- capítulos ----------------

def chapter_events(C):
    a = C.at; e = C.end_of
    cid = C.cid
    if cid == 'c1':
        big_text(C, 0.0, a('Los nazis') - .05, [('ENGAÑÓ A HITLER', PAPEL), ('Y VIVIÓ PARA CONTARLO', AMBAR)], size=150, top=250)
        C.flash.append(0.0)
        counter(C, a('veintisiete'), a('Gracias') - a('veintisiete'), 27, 'ESPÍAS EN INGLATERRA', top=200)
        stamp_on(C, a('Ninguno existía'), a('Gracias') - a('Ninguno existía'), 'NINGUNO EXISTÍA', 640)
        europe_map(C, a('Gracias'), a('Y aun así') - a('Gracias'), ['Londres', 'Normandía', 'Calais'], arrows=[('Londres', 'Calais', ROJO)], title='EL LUGAR EQUIVOCADO')
        big_text(C, a('Es lo que tuvo'), C.DUR - a('Es lo que tuvo'), [('¿QUÉ HIZO', PAPEL), ('DESPUÉS?', AMBAR)], size=170, top=260)
        C.keys |= {'Hitler', 'veintisiete', 'Ninguno', 'equivocado...', 'increíble', 'vida.'}
    elif cid == 'c2':
        date_card(C, a('Nació'), 6.5, 'BARCELONA', '1912')
        icon_row(C, a('Antes de la guerra'), a('Entonces') - a('Antes de la guerra'), [(SV['pollo'], 'CRIÓ POLLOS'), ('<svg viewBox="0 0 100 100"><rect x="14" y="30" width="72" height="60" fill="#e9dfc6"/><path d="M8 34 L50 8 L92 34Z" fill="#d23a2a"/><g fill="#1b1f1a"><rect x="24" y="44" width="12" height="12"/><rect x="44" y="44" width="12" height="12"/><rect x="64" y="44" width="12" height="12"/><rect x="42" y="66" width="16" height="24"/></g></svg>', 'ADMINISTRÓ UN HOTEL')], top=260, title='NO ERA ESPÍA')
        versus(C, a('de un lado'), a('Cuando la guerra') - a('de un lado'), 'COMUNISTAS', 'FASCISTAS')
        date_card(C, a('En mil novecientos treinta'), 6, 'POLONIA', '1939')
        big_text(C, a('iba a pelear'), C.DUR - a('iba a pelear'), [('CONTRA HITLER.', PAPEL), ('SOLO.', AMBAR)], size=160, top=280)
        C.keys |= {'Barcelona', 'pollos', 'hotel.', 'comunistas;', 'fascistas.', 'Hitler', 'Solo.', 'Polonia'}
    elif cid == 'c3':
        door(C, a('Fue a la embajada'), a('Cualquiera') - a('Fue a la embajada'))
        big_text(C, a('Juan pensó al revés'), a('Si los británicos') - a('Juan pensó al revés'), [('PENSÓ', PAPEL), ('AL REVÉS', AMBAR)], size=170, top=280)
        double_agent(C, a('Si los británicos'), a('Se presentó') - a('Si los británicos'))
        icon_row(C, a('Le dieron un curso'), a('Había un pequeño') - a('Le dieron un curso'), [(SV['libros'], 'CURSO DE ESPÍA'), (SV['tinta'], 'TINTA INVISIBLE'), (SV['dinero'], 'DINERO'), (SV['mision'], 'MISIÓN: INGLATERRA')], top=250, title='LO QUE LE DIERON LOS NAZIS')
        big_text(C, a('Había un pequeño'), C.DUR - a('Había un pequeño'), [('NO PODÍA LLEGAR', PAPEL), ('A INGLATERRA', AMBAR)], size=130, top=300)
        C.keys |= {'despidieron.', 'no.', 'revés.', 'nazis...', 'él.', 'invisible', 'creyeron.', 'Inglaterra.'}
    elif cid == 'c4':
        europe_map(C, a('Se instaló'), a('Era mentira') - a('Se instaló') + 3.2, ['Madrid', 'Lisboa', 'Londres'], route=['Madrid', 'Lisboa', 'Londres'], cross='Londres', title='NUNCA PISÓ INGLATERRA')
        icon_row(C, a('Sus herramientas'), a('Con eso escribía') - a('Sus herramientas'), [(SV['guia'], 'GUÍA TURÍSTICA'), (SV['libros'], 'BIBLIOTECA'), (SV['revista'], 'REVISTAS'), (SV['cine'], 'NOTICIEROS'), (SV['tren'], 'HORARIO DE TRENES')], top=250, title='SUS "FUENTES SECRETAS"')
        telegram(C, a('Con eso escribía'), a('Pero cometía') - a('Con eso escribía'), ['INFORME DESDE LONDRES:', 'GASTOS DE TREN: 4 LIBRAS'], head='INFORME DEL AGENTE · ALTO SECRETO', stamp=('INVENTADO', 3.0))
        wine_vs(C, a('Y en uno de sus informes'), a('Pero los alemanes') - a('Y en uno de sus informes'))
        big_text(C, a('Pero los alemanes'), a('Para cubrir') - a('Pero los alemanes'), [('Y LE', PAPEL), ('CREYERON', AMBAR)], size=170, top=290)
        convoy(C, a('Uno de sus informes', 2), a('En Londres') - a('Uno de sus informes', 2))
        big_text(C, a('No sabían que la red'), C.DUR - a('No sabían que la red'), [('LA RED ESTABA', PAPEL), ('EN SU CABEZA', AMBAR)], size=140, top=280)
        C.keys |= {'Lisboa,', 'mentira.', 'errores.', 'Muchos.', 'litro', 'vino.', 'whisky.', 'creyeron.', 'existía...', 'cabeza'}
    elif cid == 'c5':
        date_card(C, a('En mil novecientos cuarenta y dos'), 6, 'LONDRES', '1942')
        big_text(C, a('le dieron un nombre'), a('Su nuevo jefe') - a('le dieron un nombre'), [('NOMBRE EN CLAVE:', PAPEL), ('GARBO', AMBAR)], size=160, top=240, sub='«EL MEJOR ACTOR DEL MUNDO»')
        network(C, a('Llegaron a tener'), a('Había un estudiante') - a('Llegaron a tener'))
        profiles(C, a('Había un estudiante'), a('Cuando uno de esos') - a('Había un estudiante'), ['ESTUDIANTE VENEZOLANO · GLASGOW', 'SARGENTO DE EE. UU. · HABLA DE MÁS', 'NACIONALISTA GALÉS · SWANSEA'])
        obituary(C, a('Y para cerrar'), a('Y todo ese tiempo') - a('Y para cerrar'), 'DIARIO DE LIVERPOOL', 'AGENTE DE LIVERPOOL', 'Fallecido tras una breve enfermedad. Le sobrevive su viuda.', 'NUNCA EXISTIÓ')
        counter(C, a('En total'), C.DUR - a('En total'), 340000, 'PAGADOS POR ALEMANIA PARA ESPÍAS IMAGINARIOS', prefix='$', top=230, fmt_thousands=True)
        C.keys |= {'Garbo,', 'actor', 'veintisiete', 'existía.', 'morir.', 'viuda.', 'existió.', 'fortuna...', 'imaginarios.'}
    elif cid == 'c6':
        date_card(C, a('En mil novecientos cuarenta y cuatro'), 6, 'FRANCIA', '1944')
        europe_map(C, a('Hitler sabía'), a('Para lograrlo') - a('Hitler sabía'), ['Londres', 'Normandía', 'Calais'], arrows=[('Londres', 'Calais', AMBAR)], title='¿DÓNDE SERÁ LA INVASIÓN?')
        fake_army(C, a('Para lograrlo'), a('Ahí entraba') - a('Para lograrlo'))
        counter(C, a('Entre enero'), a('Y entonces llegó') - a('Entre enero'), 500, 'MENSAJES POR RADIO · 4 AL DÍA', prefix='+', top=230)
        telegram(C, a('El cinco de junio'), a('El plan era') - a('El cinco de junio'), ['ATENTOS A LAS 3:00 AM.', 'MENSAJE URGENTE.'], head='5 DE JUNIO DE 1944 · GARBO A MADRID')
        clock(C, a('Pero a las tres'), a('Garbo fingió') - a('Pero a las tres'), 3, 8, 'NADIE RESPONDE')
        big_text(C, a('Y funcionó'), a('Tres días después') - a('Y funcionó'), [('AHORA LE CREÍAN', PAPEL), ('TODO', AMBAR)], size=150, top=280)
        telegram(C, a('En resumen decía'), a('El mensaje llegó') - a('En resumen decía'), ['NORMANDÍA ES UNA DISTRACCIÓN.', 'NO MANDEN REFUERZOS.', 'EL ATAQUE SERÁ EN CALAIS.'], head='9 DE JUNIO DE 1944 · PARA EL ALTO MANDO', top=170)
        big_text(C, a('Y Hitler le creyó'), a('Ordenó que') - a('Y Hitler le creyó'), [('HITLER', PAPEL), ('LE CREYÓ', '#ff4a3a')], size=190, top=270)
        C.shakes.append(a('Y Hitler le creyó') + .3); C.flash.append(a('Y Hitler le creyó'))
        troops(C, a('Ordenó que'), a('Y en la zona') - a('Ordenó que'))
        big_number_pair(C, a('Y en la zona'), a('Incluso un mes') - a('Y en la zona'), 2, 'DIVISIONES BLINDADAS', 19, 'DIVISIONES DE INFANTERÍA')
        europe_map(C, a('Mientras Hitler miraba'), C.DUR - a('Mientras Hitler miraba'), ['Normandía', 'Calais'], dim=['Calais'], title='LOS ALIADOS ASEGURAN LAS PLAYAS')
        C.keys |= {'Normandía,', 'Calais,', 'Calais.', 'Garbo.', 'quinientos', 'tres', 'ocho.', 'nadie', 'distracción.', 'Hitler', 'creyó.', 'diecinueve', 'liberación'}
    elif cid == 'c7':
        big_text(C, 0 + C.OFF, a('En julio') - C.OFF, [('PARECE', PAPEL), ('UN CHISTE', AMBAR)], size=170, top=290)
        medals(C, a('En julio'), a('Juan Pujol fue') - a('En julio'))
        big_text(C, a('Juan Pujol fue'), C.DUR - a('Juan Pujol fue'), [('CONDECORADO POR', PAPEL), ('LOS DOS BANDOS', AMBAR)], size=140, top=280)
        C.keys |= {'chiste.', 'Cruz', 'Hierro,', 'engañado.', 'Británico.', 'dos', 'bandos'}
    elif cid == 'c8':
        date_card(C, a('La guerra terminó'), 5, 'FIN DE LA GUERRA', '1945')
        big_text(C, a('Y si alguno'), a('Así que Juan') - a('Y si alguno'), [('SI LO DESCUBRÍAN…', PAPEL)], size=130, top=300)
        obituary(C, a('En mil novecientos cuarenta y nueve'), a('Era su último') - a('En mil novecientos cuarenta y nueve') + 2.5, 'ANGOLA · 1949', 'JUAN PUJOL GARCÍA', 'Muere de malaria en África.', None)
        stamp_on(C, a('Era su último'), 2.5, 'FALSO', 400)
        disguise(C, a('Juan se fue a Venezuela'), a('Y había una razón') - a('Juan se fue a Venezuela'))
        big_text(C, a('El hombre que engañó'), C.DUR - a('El hombre que engañó'), [('A POCAS CALLES', PAPEL), ('DE LOS NAZIS', AMBAR)], size=140, top=280)
        C.keys |= {'culpar.', 'murió.', 'malaria.', 'engaño.', 'Venezuela', 'barba,', 'lentes', 'muerto:', 'nazis'}
    elif cid == 'c9':
        counter(C, C.OFF, a('Hasta que') - C.OFF, 35, 'AÑOS «MUERTO»', top=240)
        obituary(C, a('Siguió las pistas'), a('Ese mismo año') - a('Siguió las pistas'), 'NOTICIAS · 1984', '¡GARBO ESTÁ VIVO!', 'Lo encuentran en Venezuela, 35 años después de su «muerte».', None)
        date_card(C, a('Lo recibieron'), a('Y en el cuarenta') - a('Lo recibieron'), 'PALACIO DE BUCKINGHAM', '1984')
        big_text(C, a('Y en el cuarenta'), a('Al año siguiente') - a('Y en el cuarenta'), [('40 AÑOS DEL DÍA D', PAPEL), ('SIN DISPARAR UNA BALA', AMBAR)], size=110, top=300)
        book(C, a('Al año siguiente'), a('Murió en Caracas') - a('Al año siguiente'), 'OPERACIÓN GARBO', '1985')
        date_card(C, a('Murió en Caracas'), a('Engañó a Hitler') - a('Murió en Caracas'), 'CARACAS', '1912 – 1988')
        big_text(C, a('Engañó a Hitler'), a('Y ahora dime') - a('Engañó a Hitler'), [('ENGAÑÓ A HITLER', PAPEL), ('Y VIVIÓ PARA CONTARLO', AMBAR)], size=140, top=270)
        big_text(C, a('Y ahora dime'), a('Si te gustan') - a('Y ahora dime'), [('¿TÚ LO HABRÍAS', PAPEL), ('HECHO?', AMBAR)], size=150, top=250)
        subscribe(C, a('Si te gustan'), C.DUR - a('Si te gustan'))
        C.keys |= {'Vivo.', 'Buckingham.', 'bala.', 'verdad.', 'Hitler...', 'contarlo.', 'valor', 'suscríbete.'}

# ---------------- ensamblado ----------------

CSS = f'''
:root {{ --verde:{VERDE}; --papel:{PAPEL}; --ambar:{AMBAR}; --rojo:{ROJO}; --tinta:{TINTA}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--verde); }}
#root {{ position:relative; width:{W}px; height:{H}px; font-family:"Montserrat", sans-serif; overflow:hidden; }}
#cam {{ position:absolute; inset:-30px; z-index:1; }}
.bg {{ position:absolute; left:30px; top:30px; width:{W}px; height:{H}px; object-fit:cover; z-index:1; filter:saturate(.55) contrast(1.08) sepia(.18); }}
.shade {{ position:absolute; inset:0; z-index:2; background:radial-gradient(ellipse at center, rgba(15,26,20,.12) 0%, rgba(15,26,20,.55) 70%, rgba(8,12,9,.9) 100%), linear-gradient(180deg, rgba(8,12,9,.35) 0%, rgba(8,12,9,0) 30%, rgba(8,12,9,0) 62%, rgba(8,12,9,.88) 100%); }}
.grain {{ position:absolute; inset:0; z-index:3; opacity:.10; background-image:url(assets/grain.png); mix-blend-mode:overlay; }}
.dimcard {{ position:absolute; inset:0; z-index:4; background:rgba(10,14,10,.55); opacity:0; }}
.card {{ position:absolute; left:0; right:0; z-index:6; text-align:center; display:flex; justify-content:center; }}
.free {{ position:absolute; z-index:6; }}
.inner {{ display:inline-block; }}
.mapbox {{ position:absolute; inset:0; z-index:5; background:rgba(12,20,15,.86); }}
.mapbox .inner {{ display:block; width:{W}px; height:{H}px; }}
.maptitle {{ position:absolute; left:110px; top:70px; font-family:"Oswald", sans-serif; font-weight:700; font-size:72px; color:var(--ambar); letter-spacing:.04em; }}
.bigt {{ font-family:"Oswald", sans-serif; font-weight:700; line-height:.98; text-transform:uppercase; text-shadow:0 10px 40px rgba(0,0,0,.75); }}
.bigt .bl {{ display:block; }}
.sub {{ margin-top:22px; font-family:"Space Mono", monospace; font-size:54px; color:var(--papel); text-shadow:0 4px 18px rgba(0,0,0,.8); }}
.stamp {{ display:inline-block; padding:10px 46px; border:12px solid; border-radius:16px; font-family:"Oswald", sans-serif; font-weight:700; font-size:150px; line-height:1; letter-spacing:.04em; background:rgba(233,223,198,.18); text-shadow:none; }}
.tag {{ background:var(--papel); color:var(--tinta); padding:20px 44px 24px; border-left:18px solid var(--rojo); box-shadow:0 20px 50px rgba(0,0,0,.5); text-align:left; }}
.tag-l {{ font-family:"Space Mono", monospace; font-size:44px; letter-spacing:.06em; }}
.tag-y {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:120px; line-height:1; }}
.cnt b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:300px; line-height:.95; color:var(--ambar); text-shadow:0 10px 50px rgba(0,0,0,.7); font-variant-numeric:tabular-nums; }}
.cnt small {{ display:block; margin-top:10px; font-weight:900; font-size:54px; letter-spacing:.06em; color:var(--papel); text-shadow:0 4px 18px rgba(0,0,0,.8); }}
.paper, .tele {{ background:var(--papel); color:var(--tinta); box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:left; }}
.tele {{ width:1250px; padding:0 0 40px; }}
.te-h {{ background:var(--tinta); color:var(--papel); font-family:"Oswald", sans-serif; font-weight:700; font-size:44px; letter-spacing:.08em; padding:18px 40px; }}
.te-b {{ font-family:"Space Mono", monospace; font-size:66px; line-height:1.3; padding:34px 50px 0; }}
.rowtitle {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:70px; color:var(--ambar); margin-bottom:40px; text-shadow:0 6px 24px rgba(0,0,0,.8); }}
.icrow {{ display:flex; gap:56px; justify-content:center; }}
.ic {{ width:260px; }}
.ic-s {{ width:230px; height:230px; margin:0 auto; background:rgba(15,26,20,.82); border:5px solid var(--papel); border-radius:30px; padding:26px; }}
.ic-s svg {{ width:100%; height:100%; }}
.ic-t {{ margin-top:20px; font-weight:900; font-size:36px; color:var(--papel); text-shadow:0 4px 16px rgba(0,0,0,.9); }}
.duo {{ display:flex; align-items:center; gap:70px; }}
.duo-c {{ background:rgba(15,26,20,.85); border:5px solid var(--papel); border-radius:30px; padding:40px 50px; }}
.duo-t {{ margin-top:16px; font-family:"Oswald", sans-serif; font-weight:700; font-size:50px; color:var(--papel); max-width:520px; }}
.duo-c small {{ display:block; font-family:"Space Mono", monospace; font-size:34px; color:var(--ambar); }}
.duo-vs {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:180px; color:var(--ambar); }}
.lbl {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:66px; color:var(--papel); text-shadow:0 6px 20px rgba(0,0,0,.9); }}
.pfrow {{ display:flex; gap:50px; }}
.pf {{ position:relative; width:480px; background:var(--papel); color:var(--tinta); padding:30px; box-shadow:0 24px 60px rgba(0,0,0,.6); }}
.pf-ph {{ width:220px; height:220px; margin:0 auto; background:#bfb39a; }}
.pf-ph svg {{ width:100%; height:100%; }}
.pf-n {{ margin-top:18px; font-family:"Oswald", sans-serif; font-weight:700; font-size:52px; }}
.pf-t {{ font-family:"Space Mono", monospace; font-size:34px; line-height:1.25; min-height:90px; }}
.pf-x {{ position:absolute; left:50%; top:40%; transform:translate(-50%,-50%) rotate(-14deg); padding:4px 26px; border:8px solid var(--rojo); color:var(--rojo); font-family:"Oswald", sans-serif; font-weight:700; font-size:92px; background:rgba(233,223,198,.6); }}
.news {{ width:1150px; background:#efe7d2; color:#1b1b1b; padding:36px 56px 46px; box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:center; }}
.nw-top {{ font-family:"Playfair Display", serif; font-weight:900; font-size:76px; letter-spacing:.02em; }}
.nw-rule {{ height:10px; border-top:4px solid #1b1b1b; border-bottom:2px solid #1b1b1b; margin:14px 0 22px; }}
.nw-cross {{ font-size:70px; line-height:1; }}
.nw-name {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:96px; line-height:1.05; }}
.nw-body {{ font-family:"Space Mono", monospace; font-size:42px; margin-top:12px; }}
.nw-cols {{ display:flex; gap:30px; margin-top:26px; }}
.nw-cols i {{ flex:1; height:90px; background:repeating-linear-gradient(180deg, #8a8578 0 6px, transparent 6px 16px); }}
.clockbox {{ display:flex; align-items:center; gap:70px; }}
.clk-t span {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:230px; color:var(--ambar); line-height:1; text-shadow:0 10px 40px rgba(0,0,0,.7); }}
.clk-t small {{ display:block; font-weight:900; font-size:60px; color:var(--rojo); letter-spacing:.06em; background:var(--papel); padding:6px 22px; }}
.dsg {{ text-align:center; }}
.dsg-t {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:70px; color:var(--ambar); text-shadow:0 6px 24px rgba(0,0,0,.8); }}
.cta {{ display:inline-block; padding:30px 80px; border-radius:999px; background:var(--rojo); color:#fff; font-weight:900; font-size:96px; box-shadow:0 20px 60px rgba(0,0,0,.6); }}
.bell {{ display:inline-block; }}
.vs {{ display:flex; align-items:center; gap:50px; }}
.vs-c {{ position:relative; padding:50px 70px; font-family:"Oswald", sans-serif; font-weight:700; font-size:110px; color:var(--papel); border:6px solid var(--papel); }}
.vs-m {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:120px; color:var(--ambar); }}
.vx {{ position:absolute; inset:0; background:linear-gradient(35deg, transparent 46%, var(--rojo) 46%, var(--rojo) 54%, transparent 54%), linear-gradient(-35deg, transparent 46%, var(--rojo) 46%, var(--rojo) 54%, transparent 54%); }}
.door {{ text-align:center; }}
.door-t {{ margin-top:16px; font-family:"Space Mono", monospace; font-size:46px; color:var(--papel); background:rgba(15,26,20,.85); padding:8px 26px; }}
.flow {{ display:flex; align-items:center; gap:34px; }}
.fl-b {{ padding:40px 46px; font-family:"Oswald", sans-serif; font-weight:700; font-size:76px; box-shadow:0 20px 50px rgba(0,0,0,.6); }}
.fl-b small {{ display:block; font-family:"Space Mono", monospace; font-weight:400; font-size:36px; }}
.fl-a {{ font-size:110px; color:var(--ambar); font-weight:900; }}
.army-t, .tp-l, .tp-r {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:66px; color:var(--papel); text-shadow:0 6px 20px rgba(0,0,0,.9); }}
.troops {{ display:flex; align-items:center; gap:20px; }}
.tp-l {{ color:#9fb9a6; }} .tp-r {{ color:var(--ambar); }}
.book {{ perspective:1200px; }}
.bk-c {{ width:560px; height:760px; background:linear-gradient(90deg, #4a1d1d 0 40px, #6b2a2a 40px); color:var(--papel); padding:110px 60px; box-shadow:30px 30px 80px rgba(0,0,0,.6); text-align:center; }}
.bk-t {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:110px; line-height:1; }}
.bk-l {{ height:6px; background:var(--ambar); margin:50px 40px; }}
.bk-y {{ font-family:"Space Mono", monospace; font-size:80px; color:var(--ambar); }}
.pair {{ display:flex; gap:120px; }}
.pair b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:300px; line-height:.95; color:var(--ambar); text-shadow:0 10px 50px rgba(0,0,0,.7); }}
.pair small {{ display:block; font-weight:900; font-size:48px; color:var(--papel); max-width:520px; margin:0 auto; text-shadow:0 4px 18px rgba(0,0,0,.8); }}
.chap {{ text-align:center; }}
.ch-n {{ font-family:"Space Mono", monospace; font-size:56px; color:var(--ambar); letter-spacing:14px; }}
.ch-t {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:150px; line-height:1; color:var(--papel); margin-top:14px; text-shadow:0 10px 40px rgba(0,0,0,.7); }}
.ch-l {{ height:8px; width:700px; margin:34px auto 0; background:var(--rojo); }}
.cap {{ position:absolute; left:120px; right:120px; top:900px; z-index:7; display:flex; flex-wrap:wrap; justify-content:center; }}
.cap span {{ display:inline-block; padding:0 11px; font-weight:900; font-size:62px; line-height:1.1; color:#fff; text-transform:uppercase; -webkit-text-stroke:3px #0b0f0c; paint-order:stroke fill; text-shadow:0 5px 18px rgba(0,0,0,.85); }}
.cap span.k {{ color:var(--ambar); }}
.flash {{ position:absolute; inset:0; z-index:10; background:#fff; opacity:0; }}
'''

def build(cid, num):
    C = Comp(cid, num, G[cid]['titulo'])
    if num > 1: title_card(C)
    chapter_events(C)
    # clips de fondo
    clips = CL[cid]
    durs = []
    for c in clips:
        p = f'{ROOT}/clips/{c[0]}.mp4'
        durs.append(float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p])))
    n = len(clips)
    caps = [dd - 0.3 for dd in durs]
    lo, hi = 0.0, 30.0
    for _ in range(60):
        X = (lo + hi) / 2
        if sum(min(c, X) for c in caps) < C.DUR: lo = X
        else: hi = X
    lens = [min(c, hi) for c in caps]
    bg = []
    t = 0.0
    for k, (cl, ln) in enumerate(zip(clips, lens)):
        if t >= C.DUR - 0.05: break
        ln = min(ln, C.DUR - t) if k < n - 1 else C.DUR - t
        bg.append((cl[0], t, ln, k % 2))
        t += ln
    P = []
    P.append(f'<!doctype html>\n<html lang="es"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />'
             '<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>'
             f'<style>{CSS}</style></head><body>\n'
             f'<div id="root" data-composition-id="main" data-start="0" data-duration="{C.DUR}" data-width="{W}" data-height="{H}">\n'
             f'<audio id="voz" class="clip" src="assets/voz{num}.mp3" data-start="{C.OFF}" data-duration="{C.vdur:.2f}" data-volume="1"></audio>\n'
             f'<audio id="sfx" class="clip" src="assets/sfx{num}.wav" data-start="0" data-duration="{C.DUR}" data-volume="1"></audio>\n<div id="cam">\n')
    for j, (f, s, d, z) in enumerate(bg):
        P.append(f'<video id="bg{j}" class="clip bg" src="assets/{f}.mp4" data-start="{s:.2f}" data-duration="{d:.2f}" data-media-start="0.2" muted playsinline></video>\n')
    P.append('</div>\n')
    P.append(f'<div id="shade" class="clip shade" data-start="0" data-duration="{C.DUR}"></div>\n<div id="grain" class="clip grain" data-start="0" data-duration="{C.DUR}"></div>\n')
    cutf = [s for _, s, _, _ in bg[1:]]
    allfl = sorted(set(round(x, 2) for x in cutf + C.flash))
    for k2, tt in enumerate(allfl):
        P.append(f'<div id="fl{k2}" class="clip flash" data-start="{max(tt-.05,0):.2f}" data-duration=".45"></div>\n')
    P.extend(C.H)
    # subtítulos
    groups = []
    cur = []
    for w, s, e in C.words:
        cur.append((w, s, e))
        if len(cur) >= 5 or re.search(r'[.?!…:;,]$', w) and len(cur) >= 2 or re.search(r'[.?!…]$', w):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    J = ['const tl = gsap.timeline({ paused: true });']
    for gi, gr in enumerate(groups):
        gs, ge = gr[0][1], gr[-1][2]
        nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else C.DUR
        gd = min(ge + .25, nxt) - gs
        spans = ''.join(f'<span id="g{gi}w{j}" class="{"k" if w in C.keys else ""}">{html.escape(w)}</span>' for j, (w, a, b) in enumerate(gr))
        P.append(f'<div id="g{gi}" class="clip cap" data-start="{gs:.2f}" data-duration="{gd:.2f}">{spans}</div>\n')
        for j, (w, a, b) in enumerate(gr):
            J.append(f'tl.fromTo("#g{gi}w{j}", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:.16, ease:"power2.out"}}, {a:.2f});')
    for j, (f, s, d, z) in enumerate(bg):
        z0, z1 = (1.0, 1.08) if z else (1.08, 1.0)
        J.append(f'tl.fromTo("#bg{j}", {{scale:{z0}}}, {{scale:{z1}, duration:{d:.2f}, ease:"none"}}, {s:.2f});')
    for k2, tt in enumerate(allfl):
        pk = .85 if tt in [round(x, 2) for x in C.flash] else .28
        J.append(f'tl.fromTo("#fl{k2}", {{opacity:0}}, {{opacity:{pk}, duration:.05}}, {max(tt-.04,0):.2f}); tl.to("#fl{k2}", {{opacity:0, duration:.3}}, {tt+.03:.2f});')
    for sh in C.shakes:
        for q in range(6):
            J.append(f'tl.to("#cam", {{x:{18*math.sin(q*2.3):.1f}, y:{14*math.cos(q*1.7):.1f}, duration:.06}}, {sh+q*.06:.2f});')
        J.append(f'tl.to("#cam", {{x:0, y:0, duration:.12}}, {sh+.38:.2f});')
    J.extend(C.J)
    J.append('window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;')
    P.append('</div>\n<script>\n' + '\n'.join(J) + '\n</script>\n</body></html>\n')
    d = f'{ROOT}/proj/{cid}'
    os.makedirs(f'{d}/assets', exist_ok=True)
    open(f'{d}/index.html', 'w').write(''.join(P))
    # enlaces a assets
    for f in [f'voz{num}.mp3', 'grain.png']:
        src = f'{ROOT}/assets/{f}'; dst = f'{d}/assets/{f}'
        if not os.path.exists(dst): os.symlink(src, dst)
    for c in clips:
        src = f'{ROOT}/clips/{c[0]}.mp4'; dst = f'{d}/assets/{c[0]}.mp4'
        if not os.path.exists(dst): os.symlink(src, dst)
    for f in ['hyperframes.json', 'package.json', 'meta.json']:
        subprocess.run(['cp', f'/home/claude/videos-historias/plantilla/{f}', d])
    json.dump({'dur': C.DUR, 'off': C.OFF, 'sfx': C.sfx, 'bg': bg, 'shakes': C.shakes}, open(f'{d}/info.json', 'w'))
    print(cid, 'dur', C.DUR, 'clips', len(bg), 'subs', len(groups), 'eventos', len(C.H))

if __name__ == '__main__':
    ids = sys.argv[1:] or [f'c{i}' for i in range(1, 10)]
    for cid in ids:
        build(cid, int(cid[1:]))
