import html, json, math, os, re, subprocess, sys

ROOT = '/home/claude/largo'
W, H = 1920, 1080
T = json.load(open(f'{ROOT}/timing.json'))
G = {c['id']: c for c in json.load(open(f'{ROOT}/guion.json'))}
CL = json.load(open(f'{ROOT}/clips.json'))

AMBAR = '#e8c547'; ROJO = '#d4372c'; PAPEL = '#efe6d3'; VERDE = '#071318'; TINTA = '#1a1c18'; MUSGO = '#7fae6a'; CIELO = '#8fc3d9'

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

def stamp_on(C, s, d, text, top=300, color=ROJO, rot=-12, left=None, size=None):
    style = f'top:{top}px;' + (f'left:{left}px;' if left is not None else 'left:0;right:0;text-align:center;')
    i = C.el(f'<span class="stamp" style="color:{color};border-color:{color};{f'font-size:{size}px' if size else ''}">{html.escape(text)}</span>', s, d, 'free', style + 'z-index:9')
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
def icon_row(C, s, d, items, top=300, title=None):
    cells = ''.join(f'<div class="ic"><div class="ic-s">{svg}</div><div class="ic-t">{html.escape(t)}</div></div>' for svg, t in items)
    tt = f'<div class="rowtitle">{html.escape(title)}</div>' if title else ''
    i = C.el(f'{tt}<div class="icrow">{cells}</div>', s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .ic", {{opacity:0, y:60, scale:.6}}, {{opacity:1, y:0, scale:1, duration:.45, stagger:{min(.9, (d-1.5)/max(1,len(items))):.2f}, ease:"back.out(1.8)"}}, {s+.15:.2f});')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')
def subscribe(C, s, d):
    i = C.el('<div class="cta"><span class="bell">🔔</span> SUSCRÍBETE</div>', s, d, 'card', 'top:560px')
    C.pop(i, s, d)
    C.js(f'tl.to("#{i}i .cta", {{scale:1.07, duration:.4, yoyo:true, repeat:{int(d/0.4)-2}, ease:"sine.inOut"}}, {s+.6:.2f});')
    C.js(f'tl.to("#{i}i .bell", {{rotation:18, duration:.12, yoyo:true, repeat:{int(d/0.12)-4}, ease:"sine.inOut", transformOrigin:"50% 0%"}}, {s+.6:.2f});')
def title_card(C):
    i = C.el(f'<div class="chap"><div class="ch-n">CAPÍTULO {C.num - 1}</div><div class="ch-t">{html.escape(C.title.upper())}</div><div class="ch-l"></div></div>', 0, C.OFF, 'card', 'top:330px;z-index:9')
    C.js(f'tl.fromTo("#{i}i .ch-n", {{opacity:0, scaleX:1.6}}, {{opacity:1, scaleX:1, duration:.8, ease:"power3.out"}}, .05);')
    C.js(f'tl.fromTo("#{i}i .ch-t", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.6, ease:"power3.out"}}, .3);')
    C.js(f'tl.fromTo("#{i}i .ch-l", {{scaleX:0}}, {{scaleX:1, duration:.8, ease:"power3.out"}}, .5);')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {C.OFF-.35:.2f});')
    C.H.append(f'<div id="tcdim" class="clip" style="position:absolute;inset:0;z-index:8;background:rgba(10,14,10,.72)" data-start="0" data-duration="{C.OFF:.2f}"></div>\n')
    C.js(f'tl.to("#tcdim", {{opacity:0, duration:.35}}, {C.OFF-.4:.2f});')
    C.sfx.append(('boom', .05, .35)); C.sfx.append(('whoosh', C.OFF - .45, .6))


# ---------------- componentes nuevos (Onoda) ----------------

def fade_out(C, i, s, d):
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.25}}, {s+d-.28:.2f});')

def year_counter(C, s, d, y0, y1, label, top=150):
    inner = (f'<div class="cal"><div class="cal-top"><i></i><i></i></div><div class="cal-n">{y0}</div>'
             f'<div class="cal-l">{html.escape(label)}</div></div>')
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, rotationX:-80, transformPerspective:900, transformOrigin:"50% 0%"}}, {{opacity:1, rotationX:0, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    span = max(1.0, min(d - 1.2, 2.6))
    C.js(f'(()=>{{const o={{v:{y0}}}; tl.to(o, {{v:{y1}, duration:{span:.2f}, ease:"power1.in", onUpdate:()=>{{document.querySelector("#{i}i .cal-n").textContent=Math.round(o.v)}}}}, {s+.4:.2f});}})();')
    C.js(f'tl.fromTo("#{i}i .cal-n", {{y:-6}}, {{y:6, duration:.08, yoyo:true, repeat:{int(span/0.08)}, ease:"none"}}, {s+.4:.2f});')
    C.sfx.append(('whoosh', s, .6))
    fade_out(C, i, s, d)
    return i

def world_vs(C, s, d, left, right, lsub='', rsub=''):
    inner = (f'<div class="wvs"><div class="wv-c wv-l"><b>{html.escape(left)}</b><small>{html.escape(lsub)}</small></div>'
             f'<div class="wv-c wv-r"><b>{html.escape(right)}</b><small>{html.escape(rsub)}</small></div></div>')
    i = C.el(inner, s, d, 'card', 'top:250px')
    C.js(f'tl.fromTo("#{i}i .wv-l", {{opacity:0, x:-700}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .wv-r", {{opacity:0, x:700}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {s+.5:.2f});')
    C.sfx.append(('whoosh', s + .5, .5))
    fade_out(C, i, s, d)

SOLDIER = ('<g class="sold"><circle cx="150" cy="70" r="30" fill="#0a0d0b"/><path d="M112 62 q38 -40 76 0 l10 6 h-96z" fill="#0a0d0b"/>'
           '<path d="M118 102 h64 l14 120 h-26 l-6 130 h-26 l-4 -100 l-4 100 h-26 l-6 -130 h-26z" fill="#0a0d0b"/>'
           '<rect x="70" y="80" width="12" height="230" rx="5" fill="#0a0d0b" transform="rotate(-14 76 195)"/>'
           '<path d="M118 110 l-40 70 l14 8 l40 -62z" fill="#0a0d0b"/></g>')

def leaves_svg(n=9, seed=3):
    import random
    random.seed(seed)
    out = ''
    for k in range(n):
        x = random.randint(-40, 1880); y = random.randint(-60, 160) if k % 2 else random.randint(600, 900)
        r = random.randint(-60, 60); sc = random.uniform(.8, 1.6)
        out += f'<path class="lf" d="M0 0 q60 -50 140 0 q-80 50 -140 0z" fill="#0d2a1c" opacity=".92" transform="translate({x} {y}) rotate({r}) scale({sc:.2f})"/>'
    return out

def soldier(C, s, d, labels):
    tags = ''.join(f'<div class="sd-t">{html.escape(t)}</div>' for t in labels)
    inner = (f'<div class="sd"><svg viewBox="0 0 300 360" width="330">{SOLDIER}</svg><div class="sd-tags">{tags}</div></div>')
    i = C.el(inner, s, d, 'card', 'top:170px')
    C.js(f'tl.fromTo("#{i}i .sold", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.6, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .sd-t", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:.35, stagger:{min(.9,(d-1)/max(1,len(labels))):.2f}, ease:"back.out(1.7)"}}, {s+.4:.2f});')
    fade_out(C, i, s, d)

def leaflets(C, s, d, items, top=0):
    import random
    random.seed(len(items) * 7 + int(s))
    papers = ''
    for k, t in enumerate(items):
        x = 140 + k * (1600 // max(1, len(items))) + random.randint(-30, 30)
        papers += f'<div class="lfp" style="left:{x}px">{html.escape(t)}</div>'
    i = C.el(papers, s, d, 'free', f'left:0;top:{top}px;width:1920px;height:880px')
    C.js(f'tl.fromTo("#{i}i .lfp", {{y:-420, rotation:(k)=>[-30,25,-15,35,-25][k%5]}}, {{y:(k)=>[230,330,180,300,250][k%5], rotation:(k)=>[-8,6,-4,9,-6][k%5], duration:1.6, stagger:.35, ease:"power2.out"}}, {s+.02:.2f});')
    C.js(f'tl.to("#{i}i .lfp", {{x:"+=18", duration:.9, yoyo:true, repeat:{max(1,int(d/0.9)-2)}, ease:"sine.inOut"}}, {s+1.6:.2f});')
    C.sfx.append(('whoosh', s, .5))
    fade_out(C, i, s, d)

def mystery(C, s, d, l1, l2):
    inner = (f'<div class="mys"><svg viewBox="0 0 300 360" width="300"><circle cx="150" cy="90" r="62" fill="rgba(239,230,211,.85)"/><path d="M40 360 q110 -220 220 0z" fill="rgba(239,230,211,.85)"/>'
             f'<text x="150" y="122" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="110" fill="#071318">?</text></svg>'
             f'<div class="mys-t"><b>{html.escape(l1)}</b><span>{html.escape(l2)}</span></div></div>')
    i = C.el(inner, s, d, 'card', 'top:200px')
    C.js(f'tl.fromTo("#{i}i svg", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.5, ease:"back.out(1.8)"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .mys-t b, #{i}i .mys-t span", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:.4, stagger:1.2, ease:"power3.out"}}, {s+.3:.2f});')
    fade_out(C, i, s, d)

# mapa esquemático de Asia oriental (no a escala)
PTS = {'JAPÓN': (1480, 260), 'WAKAYAMA': (1430, 330), 'WUHAN': (930, 300), 'MANILA': (1110, 700), 'LUBANG': (1040, 760),
       'TOKIO': (1560, 250), 'CHINA': (800, 220), 'FILIPINAS': (1200, 640)}

def asia_map(C, s, d, points, route=None, title=None, pulse=None):
    i = C.uid('map')
    shapes = ('<path d="M300 80 L1150 80 Q1180 200 1120 300 Q1060 420 960 470 Q900 520 820 560 L300 560Z" fill="rgba(239,230,211,.10)" stroke="rgba(239,230,211,.4)" stroke-width="3"/>'
              '<path d="M1380 380 Q1420 330 1470 300 Q1520 240 1560 200 Q1600 150 1640 130 L1660 160 Q1620 220 1590 270 Q1540 330 1480 360 Q1420 400 1390 400Z" fill="rgba(239,230,211,.16)" stroke="rgba(239,230,211,.55)" stroke-width="3"/>'
              '<path d="M1080 500 q20 -20 30 10 q-10 40 -30 30z" fill="rgba(239,230,211,.16)" stroke="rgba(239,230,211,.5)" stroke-width="3"/>'
              '<path d="M1090 600 Q1140 580 1160 620 Q1170 680 1150 720 Q1170 760 1140 790 Q1110 760 1100 720 Q1080 660 1090 600Z" fill="rgba(239,230,211,.16)" stroke="rgba(239,230,211,.55)" stroke-width="3"/>'
              '<path d="M1150 790 Q1200 810 1230 860 L1200 880 Q1160 840 1140 810Z" fill="rgba(239,230,211,.14)" stroke="rgba(239,230,211,.5)" stroke-width="3"/>'
              '<ellipse cx="1040" cy="760" rx="16" ry="9" fill="rgba(239,230,211,.4)" stroke="#efe6d3" stroke-width="2"/>')
    parts = [f'<svg viewBox="0 0 1920 1080" width="1920" height="1080">',
             '<defs><pattern id="gr%s" width="80" height="80" patternUnits="userSpaceOnUse"><path d="M80 0H0V80" fill="none" stroke="rgba(239,230,211,.06)" stroke-width="2"/></pattern></defs>' % i,
             f'<rect width="1920" height="1080" fill="url(#gr{i})"/>', '<g transform="translate(-60,-40)">', shapes]
    if route:
        pts = [PTS[c] for c in route]
        dp = 'M' + ' '.join(f'{"Q" if 0 < k < len(pts) else ""}{x} {y}' if False else f'{"L" if k else ""}{x} {y}' for k, (x, y) in enumerate(pts))
        parts.append(f'<path id="{i}r" d="{dp}" fill="none" stroke="{ROJO}" stroke-width="7" stroke-linecap="round" stroke-dasharray="16 12"/>')
    for k, c in enumerate(points):
        x, y = PTS[c]
        col = ROJO if c == pulse else PAPEL
        anchor = 'end' if x > 1500 else 'start'
        tx = x - 34 if anchor == 'end' else x + 34
        parts.append(f'<g id="{i}c{k}"><circle cx="{x}" cy="{y}" r="13" fill="{col}"/><circle class="pl" cx="{x}" cy="{y}" r="30" fill="none" stroke="{col}" stroke-width="4" opacity=".6"/>'
                     f'<text x="{tx}" y="{y+14}" text-anchor="{anchor}" font-family="Oswald" font-weight="700" font-size="46" fill="{col}" stroke="#071318" stroke-width="8" paint-order="stroke">{html.escape(c)}</text></g>')
    parts.append('</g></svg>')
    t = f'<div class="maptitle">{html.escape(title)}</div>' if title else ''
    C.H.append(f'<div id="{i}" class="clip mapbox" data-start="{s:.2f}" data-duration="{d:.2f}"><div id="{i}i" class="inner">{"".join(parts)}{t}<div class="mapnote">ESQUEMA · NO A ESCALA</div></div></div>\n')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, duration:.5}}, {s+.02:.2f});')
    for k in range(len(points)):
        C.js(f'tl.fromTo("#{i}c{k}", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {s+.3+k*.35:.2f});')
    C.js(f'tl.fromTo("#{i}i .pl", {{scale:.6, transformOrigin:"50% 50%"}}, {{scale:1.4, opacity:0, duration:1.1, repeat:{max(1,int(d/1.1)-1)}, ease:"power1.out"}}, {s+.6:.2f});')
    if route:
        C.js(f'(()=>{{const p=document.getElementById("{i}r"); const L=p.getTotalLength(); p.style.strokeDasharray=L; tl.fromTo(p, {{strokeDashoffset:L}}, {{strokeDashoffset:0, duration:{min(2.2, d*.4):.2f}, ease:"power1.inOut"}}, {s+.5:.2f}); tl.set(p, {{strokeDasharray:"16 12"}}, {s+.5+min(2.2, d*.4):.2f});}})();')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {s+d-.32:.2f});')

def orders(C, s, d, title, items, top=130):
    rows = ''.join(f'<div class="or-r"><span class="or-n">{k+1}</span><span class="or-t">{html.escape(t)}</span><span class="or-x">{x}</span></div>' for k, (t, x) in enumerate(items))
    inner = f'<div class="ord"><div class="or-h">{html.escape(title)}</div>{rows}</div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .ord", {{opacity:0, scaleY:.05, transformOrigin:"50% 0%"}}, {{opacity:1, scaleY:1, duration:.55, ease:"power3.out"}}, {s+.02:.2f});')
    gap = min(1.6, (d - 1.2) / max(1, len(items)))
    C.js(f'tl.fromTo("#{i}i .or-r", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.35, stagger:{gap:.2f}}}, {s+.5:.2f});')
    C.js(f'tl.fromTo("#{i}i .or-x", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.2, stagger:{gap:.2f}, ease:"power4.in"}}, {s+.75:.2f});')
    C.sfx.append(('whoosh', s, .5))
    fade_out(C, i, s, d)

def quote(C, s, d, text, who, top=170):
    inner = (f'<div class="qt"><div class="qt-seal">PROMESA</div><div class="qt-b">«{html.escape(text)}»</div><div class="qt-w">— {html.escape(who)}</div></div>')
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .qt", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .qt-b", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{min(3.0, d*.5):.2f}, ease:"steps(30)"}}, {s+.4:.2f});')
    C.js(f'tl.fromTo("#{i}i .qt-seal", {{opacity:0, scale:3, rotation:-30}}, {{opacity:1, scale:1, rotation:-8, duration:.2, ease:"power4.in"}}, {s+min(3.2, d*.55):.2f});')
    C.sfx.append(('boom', s + min(3.2, d * .55), .35))
    fade_out(C, i, s, d)

FIG = '<svg viewBox="0 0 100 150"><circle cx="50" cy="30" r="22" fill="currentColor"/><path d="M24 22 q26 -28 52 0 l6 4 h-64z" fill="currentColor"/><path d="M18 150 q0 -90 32 -90 q32 0 32 90z" fill="currentColor"/></svg>'

def squad(C, s, d, names, events, title=None, top=150):
    """events: lista de (t, idx, etiqueta, color) → la figura idx se apaga y muestra etiqueta."""
    cells = ''.join(f'<div class="sq-c" id="SQ{k}"><div class="sq-f">{FIG}</div><div class="sq-n">{html.escape(n)}</div><div class="sq-l"></div></div>' for k, n in enumerate(names))
    tt = f'<div class="rowtitle">{html.escape(title)}</div>' if title else ''
    i = C.el(f'{tt}<div class="sq">{cells}</div>', s, d, 'card', f'top:{top}px')
    C.H[-1] = C.H[-1].replace('id="SQ', f'id="{i}q')
    C.js(f'tl.fromTo("#{i}i .sq-c", {{opacity:0, y:80}}, {{opacity:1, y:0, duration:.4, stagger:.25, ease:"back.out(1.6)"}}, {s+.02:.2f});')
    for t, k, lab, col in events:
        C.js(f'tl.to("#{i}q{k} .sq-f", {{color:"#3a3f3a", opacity:.45, duration:.4}}, {t:.2f});')
        C.js(f'tl.set("#{i}q{k} .sq-l", {{textContent:"{lab}", color:"{col}", borderColor:"{col}"}}, {t:.2f}); tl.fromTo("#{i}q{k} .sq-l", {{opacity:0, scale:2.5}}, {{opacity:1, scale:1, duration:.2, ease:"power4.in"}}, {t:.2f});')
        C.sfx.append(('boom', t, .35))
    fade_out(C, i, s, d)

def volante(C, s, d, head, lines, stamp=None, top=150, label='RESUMEN'):
    body = '<br>'.join(html.escape(l) for l in lines)
    inner = f'<div class="vol"><div class="vol-tag">{html.escape(label)}</div><div class="vol-h">{html.escape(head)}</div><div class="vol-b">{body}</div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0, y:-500, rotation:-14}}, {{opacity:1, y:0, rotation:-2, duration:1.0, ease:"power2.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .vol-b", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:1.0, ease:"steps(6)"}}, {s+.8:.2f});')
    C.sfx.append(('whoosh', s, .6))
    fade_out(C, i, s, d)
    if stamp: stamp_on(C, s + stamp[1], d - stamp[1], stamp[0], top + 170)

def magnifier(C, s, d, title, verdict):
    inner = (f'<div class="mag"><div class="mag-doc"><div class="mag-h">{html.escape(title)}</div><i></i><i></i><i></i><i></i><i></i><i class="s"></i></div>'
             f'<svg class="mag-g" viewBox="0 0 200 200" width="260"><circle cx="80" cy="80" r="62" fill="rgba(143,195,217,.18)" stroke="{AMBAR}" stroke-width="14"/><rect x="122" y="130" width="70" height="26" rx="12" fill="{AMBAR}" transform="rotate(45 122 130)"/></svg></div>')
    i = C.el(inner, s, d, 'card', 'top:140px')
    C.pop(i, s, d, out=False)
    C.js(f'tl.fromTo("#{i}i .mag-g", {{x:-260, y:-60}}, {{x:260, y:180, duration:{max(1.2, d*.5):.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, {s+.4:.2f});')
    fade_out(C, i, s, d)
    stamp_on(C, s + d * .62, d * .38, verdict, 380)

def years_strip(C, s, d, years, top=300):
    cells = ''.join(f'<b>{html.escape(y)}</b>' for y in years)
    i = C.el(f'<div class="ys">{cells}</div>', s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .ys b", {{opacity:0, y:-120, scale:1.6}}, {{opacity:1, y:0, scale:1, duration:.3, stagger:{min(1.0,(d-.8)/len(years)):.2f}, ease:"back.out(2)"}}, {s+.02:.2f});')
    fade_out(C, i, s, d)

def photo_drop(C, s, d, stamp='¿TRUCO?'):
    fam = ('<svg viewBox="0 0 300 200" width="420"><rect width="300" height="200" fill="#c9bea4"/>'
           '<g fill="#5b5446"><circle cx="80" cy="70" r="24"/><path d="M40 200 q40 -110 80 0z"/><circle cx="150" cy="60" r="26"/><path d="M106 200 q44 -120 88 0z"/><circle cx="222" cy="78" r="20"/><path d="M190 200 q32 -90 64 0z"/></g></svg>')
    inner = (f'<div class="pd"><div class="pd-ph">{fam}<div class="pd-c">FAMILIA</div></div>'
             f'<div class="pd-env"><svg viewBox="0 0 200 130" width="300"><rect width="200" height="130" fill="{PAPEL}"/><path d="M0 0 L100 70 L200 0" fill="none" stroke="#8b7f66" stroke-width="5"/></svg><div class="pd-c">CARTAS</div></div></div>')
    i = C.el(inner, s, d, 'card', 'top:150px')
    C.js(f'tl.fromTo("#{i}i .pd-ph", {{opacity:0, y:-600, rotation:-25}}, {{opacity:1, y:0, rotation:-5, duration:1.1, ease:"power2.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .pd-env", {{opacity:0, y:-600, rotation:20}}, {{opacity:1, y:0, rotation:6, duration:1.1, ease:"power2.out"}}, {s+.5:.2f});')
    C.sfx.append(('whoosh', s, .6))
    fade_out(C, i, s, d)
    if stamp: stamp_on(C, s + d * .6, d * .4, stamp, 600)

def belief(C, s, d, rows, top=170):
    r = ''.join(f'<div class="bf-r"><div class="bf-a">{html.escape(a)}</div><div class="bf-m">→</div><div class="bf-b">{html.escape(b)}</div></div>' for a, b in rows)
    inner = f'<div class="bf"><div class="bf-h"><span>LO QUE PASABA</span><span>LO QUE ÉL CREÍA</span></div>{r}</div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .bf-h", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    gap = (d - 1.5) / max(1, len(rows))
    for k in range(len(rows)):
        C.js(f'tl.fromTo("#{i}i .bf-r:nth-of-type({k+2}) .bf-a", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.35}}, {s+.3+k*gap:.2f});')
        C.js(f'tl.fromTo("#{i}i .bf-r:nth-of-type({k+2}) .bf-m, #{i}i .bf-r:nth-of-type({k+2}) .bf-b", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:.35, stagger:.15}}, {s+.3+k*gap+gap*.45:.2f});')
    fade_out(C, i, s, d)

def figures(C, s, d, n, label, sub, top=170):
    cells = ''.join(f'<i>{FIG}</i>' for _ in range(n))
    inner = f'<div class="fg"><div class="fg-g">{cells}</div><div class="fg-l">{html.escape(label)}</div><div class="fg-s">{html.escape(sub)}</div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .fg-g i", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.25, stagger:{min(.08,(d-2)/n):.3f}}}, {s+.1:.2f});')
    C.js(f'tl.fromTo("#{i}i .fg-l, #{i}i .fg-s", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, stagger:.3}}, {s+.3+n*min(.08,(d-2)/n):.2f});')
    fade_out(C, i, s, d)

def fire_rice(C, s, d, label):
    stalks = ''.join(f'<path d="M{60+k*46} 300 q{(-1)**k*8} -90 {(-1)**k*4} -170" stroke="#c8a64a" stroke-width="7" fill="none"/><ellipse cx="{60+k*46+(-1)**k*4}" cy="125" rx="9" ry="22" fill="#d9b85a"/>' for k in range(18))
    flames = ''.join(f'<path class="fl{k%3}" d="M{40+k*70} 300 q-34 -60 0 -130 q8 40 26 50 q16 -40 4 -90 q56 60 30 170z" fill="{["#ff7a1a","#ffb534","#d4372c"][k%3]}" opacity=".9"/>' for k in range(13))
    inner = f'<div class="fr"><svg viewBox="0 0 900 300" width="1150">{stalks}<g class="fls">{flames}</g></svg><div class="lbl">{html.escape(label)}</div></div>'
    i = C.el(inner, s, d, 'card', 'top:250px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .fls path", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.5, stagger:.08, ease:"power2.out"}}, {s+.6:.2f});')
    C.js(f'tl.to("#{i}i .fls path", {{scaleY:.75, duration:.18, yoyo:true, repeat:{int(d/0.18)}, stagger:.05, ease:"sine.inOut", transformOrigin:"50% 100%"}}, {s+1.4:.2f});')
    C.sfx.append(('whoosh', s + .6, .5))
    fade_out(C, i, s, d)

def checklist(C, s, d, items, ticks, top=170, title='SU LISTA'):
    rows = ''.join(f'<div class="ck-r"><span class="ck-b"><b class="ck-m">✓</b></span><span class="ck-t">{k+1}. {html.escape(t)}</span></div>' for k, t in enumerate(items))
    inner = f'<div class="ck"><div class="ck-h">{html.escape(title)}</div>{rows}</div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .ck", {{opacity:0, rotation:6, y:200}}, {{opacity:1, rotation:-2, y:0, duration:.6, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .ck-r", {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:.3, stagger:{min(1.4,(d-1)/len(items)):.2f}}}, {s+.5:.2f});')
    for t, k, mark in ticks:
        C.js(f'tl.set("#{i}i .ck-r:nth-of-type({k+2}) .ck-m", {{textContent:"{mark}", color:"{"#2e8b57" if mark == "✓" else ROJO}"}}, {t:.2f}); tl.fromTo("#{i}i .ck-r:nth-of-type({k+2}) .ck-m", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.2, ease:"power4.in"}}, {t:.2f});')
        C.sfx.append(('boom', t, .3))
    fade_out(C, i, s, d)

def polaroid(C, s, d, caption):
    inner = (f'<div class="pol"><div class="pol-ph"><svg viewBox="0 0 300 300" width="460"><rect width="300" height="300" fill="#2c3b2c"/>{leaves_svg(0)}'
             f'<path d="M0 230 q80 -40 160 -10 q80 30 140 -20 v100 h-300z" fill="#1a2a1a"/><g transform="translate(70,30) scale(.55)">{SOLDIER}</g>'
             f'<path d="M0 0 q60 40 40 120 M300 0 q-50 50 -30 110" stroke="#1a2a1a" stroke-width="30" fill="none"/></svg></div>'
             f'<div class="pol-c">{html.escape(caption)}</div></div>')
    i = C.el(inner, s, d, 'card', 'top:120px')
    fl = C.uid('pf')
    C.H.append(f'<div id="{fl}" class="clip flash" data-start="{s:.2f}" data-duration=".6"></div>\n')
    C.js(f'tl.fromTo("#{fl}", {{opacity:0}}, {{opacity:.9, duration:.05}}, {s:.2f}); tl.to("#{fl}", {{opacity:0, duration:.45}}, {s+.06:.2f});')
    C.js(f'tl.fromTo("#{i}i .pol", {{opacity:0, scale:1.4, rotation:-12}}, {{opacity:1, scale:1, rotation:-4, duration:.6, ease:"power3.out"}}, {s+.15:.2f});')
    C.js(f'tl.fromTo("#{i}i .pol-ph", {{filter:"brightness(3)"}}, {{filter:"brightness(1)", duration:1.4}}, {s+.15:.2f});')
    C.sfx.append(('boom', s, .3))
    fade_out(C, i, s, d)

def morph(C, s, d, a, b, top=260):
    inner = f'<div class="mo"><div class="mo-a">{html.escape(a)}<i class="vx"></i></div><div class="fl-a">→</div><div class="mo-b">{html.escape(b)}</div></div>'
    i = C.el(inner, s, d, 'card', f'top:{top}px')
    C.js(f'tl.fromTo("#{i}i .mo-a", {{opacity:0, x:-300}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .vx", {{opacity:0, scale:2.5}}, {{opacity:1, scale:1, duration:.2, ease:"power4.in"}}, {s+d*.35:.2f});')
    C.js(f'tl.fromTo("#{i}i .fl-a, #{i}i .mo-b", {{opacity:0, x:200}}, {{opacity:1, x:0, duration:.45, stagger:.2, ease:"back.out(1.6)"}}, {s+d*.42:.2f});')
    C.sfx.append(('boom', s + d * .35, .35))
    fade_out(C, i, s, d)

SV = {
 'coco': '<svg viewBox="0 0 100 100"><circle cx="50" cy="56" r="34" fill="#6b4a2b"/><circle cx="40" cy="44" r="5" fill="#2b1d10"/><circle cx="56" cy="44" r="5" fill="#2b1d10"/><circle cx="48" cy="58" r="5" fill="#2b1d10"/></svg>',
 'platano': '<svg viewBox="0 0 100 100"><path d="M20 30 q10 50 60 50 q10 -4 4 -10 q-40 0 -52 -44z" fill="#e8c547" stroke="#8a6a1a" stroke-width="3"/><rect x="16" y="22" width="8" height="12" fill="#5b4a2a"/></svg>',
 'arroz': '<svg viewBox="0 0 100 100"><path d="M18 50 h64 q-4 34 -32 34 q-28 0 -32 -34z" fill="#efe6d3"/><g fill="#fff"><ellipse cx="38" cy="46" rx="6" ry="3"/><ellipse cx="52" cy="42" rx="6" ry="3"/><ellipse cx="64" cy="47" rx="6" ry="3"/><ellipse cx="46" cy="38" rx="6" ry="3"/></g><path d="M18 50 h64" stroke="#8b7f66" stroke-width="3"/></svg>',
 'vaca': '<svg viewBox="0 0 100 100"><rect x="18" y="38" width="56" height="32" rx="12" fill="#8b5a3c"/><rect x="66" y="28" width="22" height="22" rx="7" fill="#8b5a3c"/><path d="M68 28 l-6 -8 M86 28 l6 -8" stroke="#efe6d3" stroke-width="4"/><g fill="#5e3b26"><rect x="24" y="66" width="7" height="20"/><rect x="38" y="66" width="7" height="20"/><rect x="54" y="66" width="7" height="20"/><rect x="64" y="66" width="7" height="20"/></g></svg>',
 'espada': '<svg viewBox="0 0 100 100"><path d="M20 84 Q50 50 84 14 l4 4 Q54 56 26 90z" fill="#d9dde0" stroke="#6b7378" stroke-width="2"/><rect x="18" y="74" width="20" height="7" fill="#e8c547" transform="rotate(-45 28 78)"/><path d="M10 92 l14 -14 l6 6 l-14 14z" fill="#3a2a1c"/></svg>',
 'fusil': '<svg viewBox="0 0 100 100"><path d="M6 60 h56 l30 -6 v8 l-30 8 h-18 l-10 16 h-12 l6 -16 h-22z" fill="#5b3b22"/><rect x="40" y="52" width="56" height="5" fill="#2a2a2a"/></svg>',
 'balas': '<svg viewBox="0 0 100 100"><g fill="#c9a24a"><rect x="18" y="38" width="12" height="44" rx="2"/><rect x="36" y="38" width="12" height="44" rx="2"/><rect x="54" y="38" width="12" height="44" rx="2"/><rect x="72" y="38" width="12" height="44" rx="2"/></g><g fill="#8a6a2a"><path d="M18 38 q6 -20 12 0z"/><path d="M36 38 q6 -20 12 0z"/><path d="M54 38 q6 -20 12 0z"/><path d="M72 38 q6 -20 12 0z"/></g></svg>',
 'granada': '<svg viewBox="0 0 100 100"><ellipse cx="50" cy="60" rx="26" ry="30" fill="#4d5a3a"/><g stroke="#2f3824" stroke-width="3"><path d="M26 52 h48 M26 68 h48 M50 30 v60"/></g><rect x="42" y="20" width="16" height="12" fill="#6b6b6b"/><path d="M58 24 q16 -6 14 12" stroke="#9a9a9a" stroke-width="4" fill="none"/></svg>',
 'punal': '<svg viewBox="0 0 100 100"><path d="M50 8 l10 54 h-20z" fill="#d9dde0" stroke="#6b7378" stroke-width="2"/><rect x="34" y="62" width="32" height="7" fill="#e8c547"/><rect x="44" y="69" width="12" height="24" rx="3" fill="#3a2a1c"/></svg>',
 'libro': '<svg viewBox="0 0 100 100"><path d="M10 24 q20 -8 40 4 q20 -12 40 -4 v58 q-20 -8 -40 4 q-20 -12 -40 -4z" fill="#efe6d3" stroke="#8b7f66" stroke-width="3"/><path d="M50 28 v58" stroke="#8b7f66" stroke-width="3"/></svg>',
 'vaca2': '',
}

def ages(C, s, d, a, la, b, lb):
    inner = (f'<div class="ag"><div class="ag-c"><b class="na">{a}</b><small>{html.escape(la)}</small></div>'
             f'<div class="ag-h"><svg viewBox="0 0 100 160" width="120"><path d="M14 8 h72 M14 152 h72" stroke="{PAPEL}" stroke-width="8"/><path d="M22 12 q0 50 28 68 q-28 18 -28 68 h56 q0 -50 -28 -68 q28 -18 28 -68z" fill="rgba(239,230,211,.12)" stroke="{PAPEL}" stroke-width="5"/>'
             f'<path class="sand" d="M30 140 h40 l-20 -30z" fill="{AMBAR}"/></svg></div>'
             f'<div class="ag-c"><b class="nb">{a}</b><small>{html.escape(lb)}</small></div></div>')
    i = C.el(inner, s, d, 'card', 'top:230px')
    C.pop(i, s, d)
    C.js(f'(()=>{{const o={{v:{a}}}; tl.to(o, {{v:{b}, duration:1.8, ease:"power2.out", onUpdate:()=>{{document.querySelector("#{i}i .nb").textContent=Math.round(o.v)}}}}, {s+.6:.2f});}})();')
    C.js(f'tl.fromTo("#{i}i .ag-h svg", {{rotation:0}}, {{rotation:180, duration:.6, ease:"power2.inOut", transformOrigin:"50% 50%"}}, {s+.3:.2f});')

def world_route(C, s, d, a, b, title):
    i = C.uid('wr')
    svg = (f'<svg viewBox="0 0 1920 1080" width="1920" height="1080"><g fill="none" stroke="rgba(239,230,211,.12)" stroke-width="2">'
           + ''.join(f'<ellipse cx="960" cy="470" rx="{r}" ry="380"/>' for r in (120, 260, 400, 540, 680)) +
           ''.join(f'<path d="M280 {y} H1640"/>' for y in (170, 320, 470, 620, 770)) + '</g>'
           f'<path id="{i}r" d="M1450 330 Q960 -40 520 640" fill="none" stroke="{AMBAR}" stroke-width="8" stroke-dasharray="18 14" stroke-linecap="round"/>'
           f'<g class="wp"><circle cx="1450" cy="330" r="16" fill="{ROJO}"/><text x="1490" y="346" font-family="Oswald" font-weight="700" font-size="56" fill="{PAPEL}">{html.escape(a)}</text></g>'
           f'<g class="wp"><circle cx="520" cy="640" r="16" fill="{MUSGO}"/><text x="480" y="656" text-anchor="end" font-family="Oswald" font-weight="700" font-size="56" fill="{PAPEL}">{html.escape(b)}</text></g></svg>')
    C.H.append(f'<div id="{i}" class="clip mapbox" data-start="{s:.2f}" data-duration="{d:.2f}"><div id="{i}i" class="inner">{svg}<div class="maptitle">{html.escape(title)}</div></div></div>\n')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.4}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .wp", {{opacity:0, scale:0, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.35, stagger:1.2, ease:"back.out(2)"}}, {s+.3:.2f});')
    C.js(f'(()=>{{const p=document.getElementById("{i}r"); const L=p.getTotalLength(); p.style.strokeDasharray=L; tl.fromTo(p, {{strokeDashoffset:L}}, {{strokeDashoffset:0, duration:1.4, ease:"power1.inOut"}}, {s+.5:.2f}); tl.set(p, {{strokeDasharray:"18 14"}}, {s+1.9:.2f});}})();')
    C.js(f'tl.to("#{i}i", {{opacity:0, duration:.3}}, {s+d-.32:.2f});')

def timeline(C, s, d, marks, title):
    n = len(marks)
    pts = ''.join(f'<div class="tm-p" style="left:{k*100/(n-1):.1f}%"><i></i><b>{html.escape(y)}</b><small>{html.escape(t)}</small></div>' for k, (y, t) in enumerate(marks))
    inner = f'<div class="tm"><div class="tm-h">{html.escape(title)}</div><div class="tm-bar"><div class="tm-fill"></div>{pts}</div></div>'
    i = C.el(inner, s, d, 'card', 'top:250px')
    C.js(f'tl.fromTo("#{i}i", {{opacity:0}}, {{opacity:1, duration:.3}}, {s+.02:.2f});')
    C.js(f'tl.fromTo("#{i}i .tm-fill", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:{min(3.5, d*.6):.2f}, ease:"none"}}, {s+.3:.2f});')
    C.js(f'tl.fromTo("#{i}i .tm-p", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3, stagger:{min(3.5, d*.6)/(n-1):.2f}}}, {s+.3:.2f});')
    fade_out(C, i, s, d)


HOJA = '<svg viewBox="0 0 100 100"><path d="M14 86 Q10 20 86 14 Q90 80 14 86z" fill="#3f7a4a"/><path d="M14 86 L80 20" stroke="#cfe3b8" stroke-width="3"/></svg>'

def chapter_events(C):
    a = C.at; e = C.end_of
    cid = C.cid
    R = '#ff4a3a'
    if cid == 'c1':
        big_text(C, 0.0, a('El problema') - .05, [('29 AÑOS', AMBAR), ('EN GUERRA', PAPEL)], size=200, top=230)
        C.flash.append(0.0); C.shakes.append(0.15)
        big_text(C, a('El problema'), a('Mientras') - a('El problema'), [('PERO LA GUERRA', PAPEL), ('YA HABÍA TERMINADO', AMBAR)], size=130, top=230)
        stamp_on(C, a('casi al principio'), a('Mientras') - a('casi al principio'), '1945', 600)
        world_vs(C, a('Mientras'), a('con su uniforme') - a('Mientras'), 'PAZ', 'GUERRA', 'EL MUNDO', 'ÉL')
        soldier(C, a('con su uniforme'), a('hasta mil') - a('con su uniforme'), ['UNIFORME', 'FUSIL', 'ÓRDENES'])
        year_counter(C, a('hasta mil'), a('Le tiraron') - a('hasta mil'), 1945, 1974, 'Y SIGUIÓ PELEANDO')
        leaflets(C, a('Le tiraron'), a('No creyó') - a('Le tiraron'), ['VOLANTES', 'PERIÓDICOS', 'FOTOS DE SU FAMILIA', 'VOLANTES'])
        stamp_on(C, a('No creyó'), a('Entonces') - a('No creyó'), 'NO CREYÓ NADA', 330)
        big_text(C, a('Entonces'), a('Y lo más loco') - a('Entonces'), [('¿QUÉ HIZO FALTA', PAPEL), ('PARA QUE BAJARA EL ARMA?', AMBAR)], size=110, top=270)
        big_text(C, a('Y lo más loco'), a('Es quién') - a('Y lo más loco'), [('Y LO MÁS LOCO', PAPEL), ('NO ES ESO…', AMBAR)], size=150, top=270)
        mystery(C, a('Es quién'), C.DUR - a('Es quién'), '¿QUIÉN LO ENCONTRÓ?', '¿Y QUÉ BUSCABA?')
        C.keys |= {'veintinueve', 'terminado', 'paz,', 'selva,', 'cuatro.', 'familia.', 'nada.', 'arma?', 'encontró', 'buscando'}
    elif cid == 'c2':
        C.cuts = [('34675926',0),('32111766',a('Pero Japón')),('7125226',a('Lo eligieron')),('39553457',a('En diciembre')),('3952410',a('Su misión')),('30770305',a('Su comandante'))]
        date_card(C, a('Nació'), 5.5, 'WAKAYAMA · JAPÓN', '1922')
        asia_map(C, a('A los diecisiete'), a('Pero Japón') - a('A los diecisiete'), ['WAKAYAMA', 'WUHAN'], route=['WAKAYAMA', 'WUHAN'], title='A LOS 17 AÑOS: A CHINA')
        big_text(C, a('Lo eligieron'), a('Ahí no le') - a('Lo eligieron'), [('ESCUELA NAKANO', AMBAR), ('ESPÍAS Y GUERRILLA', PAPEL)], size=130, top=260)
        icon_row(C, a('Le enseñaron'), a('Lo prepararon') - a('Le enseñaron'), [(HOJA, 'ESCONDERSE'), (SV['coco'], 'SOBREVIVIR SOLO'), (SV['fusil'], 'PELEAR TRAS LAS LÍNEAS')], top=240, title='LO QUE APRENDIÓ')
        big_text(C, a('Lo prepararon'), a('En diciembre') - a('Lo prepararon'), [('PARA NO', PAPEL), ('RENDIRSE JAMÁS', AMBAR)], size=160, top=260)
        asia_map(C, a('En diciembre'), a('Su misión') - a('En diciembre'), ['JAPÓN', 'MANILA', 'LUBANG'], route=['JAPÓN', 'LUBANG'], title='DICIEMBRE 1944 · ISLA LUBANG', pulse='LUBANG')
        orders(C, a('Su misión'), a('Su comandante') - a('Su misión'), 'SUS ÓRDENES', [('DESTRUIR PISTA Y MUELLE', '✓'), ('PROHIBIDO RENDIRSE', '✕'), ('PROHIBIDO QUITARSE LA VIDA', '✕')])
        quote(C, a('Su comandante'), a('Hiroo se lo') - a('Su comandante'), 'Puede tomar tres años, puede tomar cinco, pero pase lo que pase, volveremos por ti', 'MAYOR YOSHIMI TANIGUCHI')
        big_text(C, a('Hiroo se lo'), a('Lo que nadie') - a('Hiroo se lo'), [('IBA A', PAPEL), ('ESPERAR', AMBAR)], size=170, top=270)
        big_text(C, a('Lo que nadie'), C.DUR - a('Lo que nadie'), [('¿CUÁNTO TIEMPO', PAPEL), ('IBA A SER?', AMBAR)], size=150, top=270)
        C.keys |= {'Onoda.', 'Wakayama,', 'China,', 'Nakano,', 'espías', 'jamás.', 'Lubang,', 'rendirse.', 'vida.', 'Taniguchi,', 'ti».', 'esperar.'}
    elif cid == 'c3':
        C.cuts = [('6473454',0),('31546654',a('Pero Onoda hizo')),('40716302',a('Cuatro japoneses')),('39619981',a('Lo que no sabían')),('30716160',a('En agosto')),('5476221',a('Menos para cuatro'))]
        date_card(C, a('El veintiocho'), 6.0, 'LUBANG · FILIPINAS', '28 FEB 1945')
        big_text(C, a('Pero Onoda hizo'), a('Con él') - a('Pero Onoda hizo'), [('SUBIÓ A', PAPEL), ('LAS MONTAÑAS', AMBAR)], size=170, top=260)
        squad(C, a('Con él'), a('Se movían') - a('Con él'), ['ONODA', 'AKATSU', 'SHIMADA', 'KOZUKA'], [], title='LOS CUATRO')
        big_text(C, a('Se movían'), a('Lo que no sabían') - a('Se movían'), [('NUNCA EN EL', PAPEL), ('MISMO LUGAR', AMBAR)], size=150, top=280)
        date_card(C, a('En agosto'), a('Y el quince') - a('En agosto'), 'HIROSHIMA Y NAGASAKI', 'AGOSTO 1945')
        big_text(C, a('Y el quince'), a('Para casi') - a('Y el quince'), [('15 DE AGOSTO DE 1945', PAPEL), ('JAPÓN SE RINDE', AMBAR)], size=120, top=270)
        C.flash.append(a('Y el quince'))
        world_vs(C, a('Para casi'), a('Pero un par') - a('Para casi'), 'PAZ', 'GUERRA', 'EL PLANETA', '4 HOMBRES EN LUBANG')
        big_text(C, a('Pero un par'), C.DUR - a('Pero un par'), [('LA NOTICIA', PAPEL), ('CAYÓ DEL CIELO', AMBAR)], size=160, top=270)
        C.keys |= {'Lubang.', 'montañas.', 'Akatsu,', 'Shimada', 'Kozuka.', 'Hiroshima', 'Nagasaki.', 'rindió.', 'terminado.', 'isla.', 'Literalmente.'}
    elif cid == 'c4':
        C.cuts = [('37218117',0),('1494250',a('Y en la cabeza')),('3725910',a('Comían')),('3969240',a('De vez en cuando')),('30159552',a('Y cuidaban')),('34781953',a('Pasaron'))]
        volante(C, a('En octubre'), a('Cualquiera') - a('En octubre'), 'OCTUBRE 1945 · VOLANTE', ['LA GUERRA TERMINÓ EL 15 DE AGOSTO.', 'BAJEN DE LAS MONTAÑAS.'])
        big_text(C, a('Cualquiera'), a('Lo leyó') - a('Cualquiera'), [('¿CELEBRAR?', PAPEL), ('ONODA NO', AMBAR)], size=170, top=270)
        big_text(C, a('si la guerra'), a('Para él') - a('si la guerra'), [('¿POR QUÉ LES SEGUÍAN', PAPEL), ('DISPARANDO?', AMBAR)], size=120, top=270)
        stamp_on(C, a('Para él'), a('Y en la cabeza') - a('Para él'), 'PROPAGANDA', 330)
        big_text(C, a('Y en la cabeza'), a('A fines') - a('Y en la cabeza'), [('TODO LO DEL ENEMIGO', PAPEL), ('ES MENTIRA', AMBAR)], size=120, top=270)
        leaflets(C, a('A fines'), a('Los cuatro') - a('A fines'), ['ORDEN DE RENDICIÓN', 'GRAL. YAMASHITA', 'ORDEN DE RENDICIÓN', 'GRAL. YAMASHITA'])
        magnifier(C, a('Los cuatro'), a('Así que') - a('Los cuatro'), 'ORDEN DE RENDICIÓN', 'FALSA')
        icon_row(C, a('Comían'), a('Y cuidaban') - a('Comían'), [(SV['coco'], 'COCOS'), (SV['platano'], 'PLÁTANOS'), (SV['arroz'], 'ARROZ ROBADO'), (SV['vaca'], 'CARNE SECA')], top=240, title='CÓMO SOBREVIVÍAN')
        big_text(C, a('Y cuidaban'), a('Pasaron') - a('Y cuidaban'), [('PARA ELLOS', PAPEL), ('LA GUERRA SEGUÍA', AMBAR)], size=140, top=270)
        years_strip(C, a('Pasaron'), a('Y entonces, uno') - a('Pasaron'), ['1946', '1947', '1948', '1949'])
        squad(C, a('Y entonces, uno'), C.DUR - a('Y entonces, uno'), ['ONODA', 'AKATSU', 'SHIMADA', 'KOZUKA'], [(a('desapareció'), 1, '?', AMBAR)])
        C.keys |= {'volante.', 'Onoda', 'disparando?', 'Propaganda.', 'Yamashita,', 'falsos.', 'cocos', 'plátanos.', 'arroz', 'vaca', 'seguía.', 'desapareció.'}
    elif cid == 'c5':
        C.cuts = [('19366764',0),('28499216',a('En mil novecientos cincuenta y dos')),('6851677',a('Les pedían')),('10660700',a('Pensaron que')),('27607538',a('En mil novecientos cincuenta y cuatro')),('7592798',a('Cuando encontraba'))]
        squad(C, C.OFF, a('Para Onoda, eso') - C.OFF, ['ONODA', 'AKATSU', 'SHIMADA', 'KOZUKA'], [(a('se rindió'), 1, 'SE RINDE · 1950', AMBAR)], title='1949: AKATSU SE VA')
        big_text(C, a('Era una amenaza'), a('Y entonces llegó') - a('Era una amenaza'), [('¿Y SI AHORA', PAPEL), ('LOS DELATABA?', AMBAR)], size=150, top=270)
        photo_drop(C, a('En mil novecientos cincuenta y dos'), a('Pensaron que') - a('En mil novecientos cincuenta y dos'), '¿TRUCO?')
        big_text(C, a('Pensaron que'), a('En mil novecientos cincuenta y cuatro') - a('Pensaron que'), [('OTRO TRUCO', PAPEL), ('DEL ENEMIGO', AMBAR)], size=160, top=270)
        squad(C, a('En mil novecientos cincuenta y cuatro'), a('Y en Japón') - a('En mil novecientos cincuenta y cuatro'), ['ONODA', 'AKATSU', 'SHIMADA', 'KOZUKA'],
              [(a('En mil novecientos cincuenta y cuatro') + .3, 1, 'SE RINDIÓ', AMBAR), (a('Shimada murió'), 2, 'MUERE · 1954', R)], title='YA SOLO QUEDABAN DOS')
        big_text(C, a('Y en Japón'), a('Pero estaba vivo') - a('Y en Japón'), [('JAPÓN, 1959:', PAPEL), ('DECLARADO MUERTO', AMBAR)], size=140, top=250)
        stamp_on(C, a('Pero estaba vivo'), a('Y tenía') - a('Pero estaba vivo'), 'ESTABA VIVO', 330, color='#3fbf6a')
        belief(C, a('Cuando oía'), a('Cada prueba') - a('Cuando oía'), [('AVIONES DE GUERRA · COREA', 'CONTRAOFENSIVA JAPONESA'), ('PERIÓDICOS', 'PROPAGANDA YANQUI')])
        big_text(C, a('Cada prueba'), a('Pero esa guerra') - a('Cada prueba'), [('CADA PRUEBA', PAPEL), ('LA VOLTEABA', AMBAR)], size=160, top=270)
        big_text(C, a('Pero esa guerra'), C.DUR - a('Pero esa guerra'), [('VÍCTIMAS', R), ('MUY REALES', PAPEL)], size=170, top=270)
        C.shakes.append(a('Pero esa guerra') + .3)
        C.keys |= {'Akatsu', 'amenaza:', 'familias.', 'creyeron.', 'Shimada', 'muerto.', 'vivo.', 'Corea,', 'yanqui.', 'víctimas', 'reales.'}
    elif cid == 'c6':
        C.cuts = [('36088984',0),('34999648',a('Según los')),('8365851',a('Para la gente')),('36088986',a('Kozuka y Onoda bajaron')),('36344044',a('Se organizaron')),('40476024',a('Y al final'))]
        big_text(C, C.OFF + .05, a('Durante esos') - C.OFF - .05, [('PARA ELLOS,', PAPEL), ('TODOS ERAN ENEMIGOS', AMBAR)], size=120, top=270)
        fire_rice(C, a('Durante esos'), a('Según los') - a('Durante esos'), 'COSECHAS QUEMADAS · GANADO ROBADO')
        figures(C, a('Según los'), a('Para la gente') - a('Según los'), 30, 'UNAS 30 PERSONAS MUERTAS', 'SEGÚN INFORMES FILIPINOS · MUCHOS ERAN AGRICULTORES')
        big_text(C, a('Para la gente'), a('Y ese miedo') - a('Para la gente'), [('NO ERAN HÉROES.', PAPEL), ('ERAN UN MIEDO', R)], size=150, top=270)
        date_card(C, a('Y ese miedo'), a('La policía') - a('Y ese miedo'), 'LUBANG', 'OCTUBRE 1972')
        squad(C, a('La policía'), a('La noticia') - a('La policía'), ['ONODA', 'AKATSU', 'SHIMADA', 'KOZUKA'],
              [(a('La policía') + .2, 1, 'SE RINDIÓ', AMBAR), (a('La policía') + .3, 2, 'MURIÓ', R), (a('Kozuka murió'), 3, 'MUERE · 1972', R)], title='ONODA, SOLO')
        big_text(C, a('La noticia'), a('Se organizaron') - a('La noticia'), [('¿ONODA', PAPEL), ('ESTÁ VIVO?', AMBAR)], size=190, top=250)
        C.flash.append(a('La noticia')); C.shakes.append(a('La noticia') + .2)
        stamp_on(C, a('No lo encontraron'), a('Onoda tenía') - a('No lo encontraron'), 'NADA', 330)
        counter(C, a('Onoda tenía'), a('Y al final') - a('Onoda tenía'), 28, 'AÑOS EN LA SELVA (CASI)', top=200)
        mystery(C, a('Y al final'), C.DUR - a('Y al final'), 'NO FUE UN EJÉRCITO', 'FUE UN MUCHACHO…')
        C.keys |= {'enemigo.', 'arroz', 'treinta', 'agricultores.', 'miedo', 'policía', 'murió', 'solo.', 'vivo.', 'fantasma.', 'muchacho', 'cosa.'}
    elif cid == 'c7':
        C.cuts = [('18006397',0),('39633714',a('un panda')),('38450146',a('Abominable Hombre')),('37832574',a('No era soldado')),('6871466',a('Llegó a Lubang')),('7348276',a('Y el veinte')),('6350206',a('Los dos hablaron')),('11427642',a('Suzuki le tomó')),('4047523',a('Ahora todo')),('35461824',a('Había que encontrar'))]
        big_text(C, C.OFF + .05, a('Y tenía un plan') - C.OFF - .05, [('NORIO SUZUKI', AMBAR), ('24 AÑOS · AVENTURERO', PAPEL)], size=130, top=260)
        checklist(C, a('Según contó'), a('No era soldado') - a('Según contó'), ['EL TENIENTE ONODA', 'UN PANDA', 'EL ABOMINABLE HOMBRE DE LAS NIEVES'], [], title='SU PLAN (EN ESE ORDEN)')
        big_text(C, a('No era soldado'), a('Llegó a Lubang') - a('No era soldado'), [('UNA MOCHILA', PAPEL), ('Y MUCHA TERQUEDAD', AMBAR)], size=140, top=270)
        date_card(C, a('Y el veinte'), a('El fantasma') - a('Y el veinte'), 'LUBANG', '20 FEB 1974')
        soldier(C, a('El fantasma'), a('Suzuki le contó') - a('El fantasma'), ['EL FANTASMA', 'DE LA ISLA'])
        big_text(C, a('Suzuki le contó'), a('Pero Onoda le dio') - a('Suzuki le contó'), [('LA GUERRA TERMINÓ', PAPEL), ('HACE CASI 30 AÑOS', AMBAR)], size=130, top=270)
        big_text(C, a('no pensaba rendirse'), a('Suzuki le tomó') - a('no pensaba rendirse'), [('SOLO SI LO ORDENA', PAPEL), ('MI COMANDANTE', AMBAR)], size=140, top=250)
        polaroid(C, a('Suzuki le tomó'), a('Había que encontrar') - a('Suzuki le tomó'), 'ESTÁ VIVO · (ILUSTRACIÓN)')
        mystery(C, a('Había que encontrar'), C.DUR - a('Había que encontrar'), 'EL COMANDANTE', '¿DÓNDE ESTÁ?')
        C.keys |= {'Suzuki.', 'chiste.', 'panda', 'Nieves...', 'terquedad.', 'Onoda', 'fusil.', 'comandante.', 'fotos,', 'vivo.', 'soldado.'}
    elif cid == 'c8':
        C.cuts = [('11769112',0),('3772777',a('Se ganaba')),('8567117',a('El gobierno japonés')),('31546677',a('El nueve de marzo')),('6003342',a('En resumen')),('12293805',a('Entregó')),('4096040',a('El once de marzo')),('15753271',a('Y Marcos')),('36365117',a('Al día siguiente')),('31387301',a('Y el país'))]
        morph(C, a('Yoshimi Taniguchi'), a('El gobierno japonés') - a('Yoshimi Taniguchi'), 'MAYOR', 'LIBRERO')
        asia_map(C, a('El gobierno japonés'), a('El nueve de marzo') - a('El gobierno japonés'), ['JAPÓN', 'LUBANG'], route=['JAPÓN', 'LUBANG'], title='DE VUELTA A LUBANG', pulse='LUBANG')
        date_card(C, a('El nueve de marzo'), a('En resumen') - a('El nueve de marzo'), 'LUBANG', '9 MAR 1974')
        volante(C, a('En resumen'), a('Casi treinta') - a('En resumen'), 'LA ORDEN · 9 DE MARZO DE 1974', ['EL EJÉRCITO DEJÓ DE COMBATIR.', 'ONODA QUEDA LIBRE DE SU MISIÓN.'], top=170)
        big_text(C, a('Casi treinta'), a('Onoda contó') - a('Casi treinta'), [('CASI 30 AÑOS', AMBAR), ('ESPERANDO ESTO', PAPEL)], size=150, top=260)
        C.flash.append(a('Casi treinta'))
        big_text(C, a('Onoda contó'), a('Entregó') - a('Onoda contó'), [('DE VERDAD', PAPEL), ('HABÍAN PERDIDO', R)], size=160, top=270)
        icon_row(C, a('Entregó'), a('El once de marzo') - a('Entregó'), [(SV['espada'], 'ESPADA'), (SV['fusil'], 'FUSIL'), (SV['balas'], '500 BALAS'), (SV['granada'], 'GRANADAS'), (SV['punal'], 'PUÑAL DE SU MADRE')], top=240, title='LO QUE ENTREGÓ')
        asia_map(C, a('El once de marzo'), a('Al día siguiente') - a('El once de marzo'), ['MANILA'], title='11 MAR 1974 · MANILA', pulse='MANILA')
        stamp_on(C, a('Y Marcos le'), a('Al día siguiente') - a('Y Marcos le'), 'PERDONADO', 380, color='#3fbf6a')
        asia_map(C, a('Al día siguiente'), a('Tenía cincuenta') - a('Al día siguiente'), ['MANILA', 'TOKIO'], route=['MANILA', 'TOKIO'], title='12 MAR 1974 · REGRESO A JAPÓN', pulse='TOKIO')
        ages(C, a('Tenía cincuenta'), a('Y el país') - a('Tenía cincuenta'), 22, 'AL IRSE · 1944', 52, 'AL VOLVER · 1974')
        big_text(C, a('Y el país'), C.DUR - a('Y el país'), [('YA NO ERA', PAPEL), ('EL MISMO PAÍS', AMBAR)], size=150, top=270)
        C.keys |= {'libros.', 'Lubang.', 'orden.', 'misión.', 'guerra.', 'espada,', 'quinientas', 'granadas', 'puñal', 'Marcos.', 'perdón.', 'veintidós.'}
    elif cid == 'c9':
        C.cuts = [('31313620',0),('31418620',a('Pero a Onoda')),('7630636',a('En mil novecientos setenta y cinco')),('27554045',a('Al año siguiente')),('8083195',a('Y en mil')),('11449132',a('¿Y Norio')),('36511231',a('murió en una avalancha')),('32320584',a('Hiroo Onoda murió')),('32314209',a('Solo lo convenció'))]
        big_text(C, C.OFF + .05, a('Pero a Onoda') - C.OFF - .05, [('RECIBIDO COMO', PAPEL), ('UNA CELEBRIDAD', AMBAR)], size=140, top=270)
        big_text(C, a('Pero a Onoda'), a('En mil novecientos setenta y cinco') - a('Pero a Onoda'), [('UN PAÍS', PAPEL), ('DEMASIADO NUEVO', AMBAR)], size=150, top=270)
        world_route(C, a('En mil novecientos setenta y cinco'), a('Al año siguiente') - a('En mil novecientos setenta y cinco'), 'JAPÓN', 'BRASIL', '1975 · CRIADOR DE GANADO')
        date_card(C, a('Al año siguiente'), a('Y en mil') - a('Al año siguiente'), 'SE CASA', '1976')
        big_text(C, a('Y en mil'), a('¿Y Norio') - a('Y en mil'), [('1984: ESCUELA', AMBAR), ('DE NATURALEZA', PAPEL)], size=140, top=270)
        checklist(C, a('¿Y Norio'), a('Hiroo Onoda murió') - a('¿Y Norio'), ['EL TENIENTE ONODA', 'UN PANDA', 'EL ABOMINABLE HOMBRE DE LAS NIEVES'], [(a('¿Y Norio') + .8, 0, '✓')], title='LA LISTA DE SUZUKI', top=110)
        stamp_on(C, a('murió en una avalancha'), a('Hiroo Onoda murió') - a('murió en una avalancha'), 'HIMALAYA · 1986', 700, rot=-5, size=96)
        timeline(C, a('Hiroo Onoda murió'), a('Años antes') - a('Hiroo Onoda murió'), [('1922', 'NACE'), ('1944', 'LLEGA A LUBANG'), ('1974', 'SE RINDE'), ('2014', 'MUERE · 91 AÑOS')], 'HIROO ONODA')
        big_text(C, a('Años antes'), a('Y así se responde') - a('Años antes'), [('«NO FUE UNA', PAPEL), ('PÉRDIDA DE TIEMPO»', AMBAR)], size=140, top=250, sub='(paráfrasis)')
        orders(C, a('No lo convencieron'), a('Solo lo convenció') - a('No lo convencieron'), 'LO QUE NO FUNCIONÓ', [('VOLANTES', '✕'), ('PERIÓDICOS', '✕'), ('FOTOS DE SU FAMILIA', '✕')])
        big_text(C, a('Solo lo convenció'), a('Ahora dime') - a('Solo lo convenció'), [('SOLO UNA ORDEN', AMBAR), ('DE SU COMANDANTE', PAPEL)], size=140, top=270)
        C.flash.append(a('Solo lo convenció'))
        big_text(C, a('Ahora dime'), a('Y si te gustan') - a('Ahora dime'), [('¿SOLDADO LEAL…', PAPEL), ('…O DEBIÓ RENDIRSE ANTES?', AMBAR)], size=110, top=250)
        subscribe(C, a('Y si te gustan'), C.DUR - a('Y si te gustan'))
        C.keys |= {'celebridad.', 'Brasil,', 'ganado.', 'naturaleza,', 'Suzuki,', 'Himalaya...', 'Nieves.', 'Tokio', 'volantes.', 'orden,', 'volver.', 'leal', 'antes?', 'suscríbete.'}

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
.bg {{ filter:saturate(.7) contrast(1.08) brightness(.95) hue-rotate(-6deg) !important; }}
.shade {{ background:radial-gradient(ellipse at center, rgba(7,19,24,.10) 0%, rgba(7,19,24,.5) 70%, rgba(3,9,12,.9) 100%), linear-gradient(180deg, rgba(3,9,12,.35) 0%, rgba(3,9,12,0) 30%, rgba(3,9,12,0) 62%, rgba(3,9,12,.88) 100%) !important; }}
.dimcard {{ background:rgba(4,12,16,.55) !important; }}
.mapbox {{ background:rgba(6,18,24,.9) !important; }}
.mapnote {{ position:absolute; right:90px; top:86px; font-family:"Space Mono", monospace; font-size:30px; color:rgba(239,230,211,.6); }}
.cal {{ width:560px; background:var(--papel); box-shadow:0 30px 80px rgba(0,0,0,.6); padding-bottom:26px; }}
.cal-top {{ height:90px; background:var(--rojo); display:flex; justify-content:space-around; align-items:center; }}
.cal-top i {{ width:26px; height:26px; border-radius:50%; background:#071318; }}
.cal-n {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:250px; line-height:1.05; color:var(--tinta); font-variant-numeric:tabular-nums; }}
.cal-l {{ font-weight:900; font-size:44px; color:var(--rojo); letter-spacing:.05em; }}
.wvs {{ display:flex; gap:0; }}
.wv-c {{ width:760px; height:420px; display:flex; flex-direction:column; justify-content:center; align-items:center; border:6px solid var(--papel); }}
.wv-l {{ background:rgba(143,195,217,.88); color:#06202b; }} .wv-r {{ background:rgba(110,20,16,.92); color:var(--papel); border-left:none; }}
.wv-c b {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:170px; line-height:1; }}
.wv-c small {{ font-family:"Space Mono", monospace; font-size:44px; margin-top:16px; font-weight:700; }}
.sd {{ display:flex; align-items:center; gap:60px; }}
.sd svg {{ filter:drop-shadow(0 0 30px rgba(232,197,71,.35)); }}
.sd-tags {{ display:flex; flex-direction:column; gap:26px; align-items:flex-start; }}
.sd-t {{ background:var(--papel); color:var(--tinta); font-family:"Oswald", sans-serif; font-weight:700; font-size:72px; padding:8px 34px; border-left:16px solid var(--rojo); box-shadow:0 14px 40px rgba(0,0,0,.5); }}
.lfp {{ position:absolute; top:0; width:330px; min-height:200px; padding:34px 26px; background:#f3ecd9; color:var(--tinta); font-family:"Oswald", sans-serif; font-weight:700; font-size:50px; line-height:1.05; text-align:center; box-shadow:0 20px 50px rgba(0,0,0,.55); border-top:14px solid var(--rojo); }}
.mys {{ display:flex; align-items:center; gap:60px; }}
.mys-t {{ text-align:left; }}
.mys-t b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:110px; color:var(--papel); text-shadow:0 8px 30px rgba(0,0,0,.8); line-height:1.05; }}
.mys-t span {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:96px; color:var(--ambar); text-shadow:0 8px 30px rgba(0,0,0,.8); }}
.ord {{ width:1300px; background:var(--papel); color:var(--tinta); box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:left; padding-bottom:20px; }}
.or-h {{ background:var(--tinta); color:var(--ambar); font-family:"Oswald", sans-serif; font-weight:700; font-size:64px; letter-spacing:.1em; padding:14px 46px; }}
.or-r {{ display:flex; align-items:center; gap:30px; padding:22px 46px; border-bottom:3px dashed rgba(26,28,24,.25); }}
.or-n {{ font-family:"Space Mono", monospace; font-size:50px; color:var(--rojo); font-weight:700; }}
.or-t {{ flex:1; font-family:"Oswald", sans-serif; font-weight:700; font-size:76px; }}
.or-x {{ font-size:90px; font-weight:900; color:var(--rojo); width:90px; text-align:center; }}
.qt {{ position:relative; width:1400px; background:rgba(7,19,24,.9); border:5px solid var(--papel); padding:60px 80px 50px; text-align:left; box-shadow:0 30px 80px rgba(0,0,0,.6); }}
.qt-b {{ font-family:"Montserrat", sans-serif; font-weight:900; font-size:72px; line-height:1.2; color:var(--papel); }}
.qt-w {{ margin-top:26px; font-family:"Space Mono", monospace; font-size:40px; color:var(--ambar); }}
.qt-seal {{ position:absolute; right:-40px; top:-60px; background:var(--rojo); color:#fff; font-family:"Oswald", sans-serif; font-weight:700; font-size:54px; padding:16px 26px; border:6px double #fff; }}
.sq {{ display:flex; gap:70px; justify-content:center; }}
.sq-c {{ width:280px; text-align:center; }}
.sq-f {{ color:#0a0d0b; width:230px; height:300px; margin:0 auto; background:rgba(239,230,211,.88); border-radius:24px; padding:30px 30px 0; }}
.sq-f svg {{ width:100%; height:100%; }}
.sq-n {{ margin-top:16px; font-family:"Oswald", sans-serif; font-weight:700; font-size:58px; color:var(--papel); text-shadow:0 6px 20px rgba(0,0,0,.9); }}
.sq-l {{ display:inline-block; margin-top:10px; min-height:60px; font-family:"Oswald", sans-serif; font-weight:700; font-size:44px; padding:2px 14px; border:5px solid transparent; background:rgba(7,19,24,.85); opacity:0; }}
.vol {{ position:relative; width:1300px; background:#f3ecd9; color:var(--tinta); padding:40px 60px 50px; box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:left; border-top:20px solid var(--rojo); }}
.vol-tag {{ position:absolute; right:40px; top:26px; font-family:"Space Mono", monospace; font-size:34px; color:#fff; background:var(--tinta); padding:4px 16px; }}
.vol-h {{ font-family:"Space Mono", monospace; font-size:44px; font-weight:700; color:var(--rojo); }}
.vol-b {{ margin-top:20px; font-family:"Oswald", sans-serif; font-weight:700; font-size:88px; line-height:1.12; }}
.mag {{ position:relative; }}
.mag-doc {{ width:980px; height:600px; background:#f3ecd9; padding:50px 70px; box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:left; }}
.mag-h {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:76px; color:var(--tinta); border-bottom:6px solid var(--tinta); padding-bottom:16px; margin-bottom:34px; }}
.mag-doc i {{ display:block; height:22px; margin:0 0 28px; background:rgba(26,28,24,.35); }}
.mag-doc i.s {{ width:40%; }}
.mag-g {{ position:absolute; left:340px; top:120px; }}
.ys {{ display:flex; gap:60px; }}
.ys b {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:200px; color:var(--papel); text-shadow:0 10px 40px rgba(0,0,0,.8); }}
.ys b:last-child {{ color:var(--ambar); }}
.pd {{ display:flex; gap:80px; align-items:center; }}
.pd-ph {{ background:#efe6d3; padding:24px 24px 16px; box-shadow:0 30px 70px rgba(0,0,0,.6); }}
.pd-env {{ background:transparent; }}
.pd-c {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:56px; color:var(--tinta); margin-top:10px; }}
.pd-env .pd-c {{ color:var(--papel); text-shadow:0 6px 20px rgba(0,0,0,.9); }}
.bf {{ width:1600px; }}
.bf-h {{ display:flex; justify-content:space-between; padding:0 60px; font-family:"Space Mono", monospace; font-weight:700; font-size:40px; color:var(--ambar); margin-bottom:26px; }}
.bf-r {{ display:flex; align-items:center; gap:30px; margin-bottom:34px; }}
.bf-a, .bf-b {{ flex:1; padding:30px 34px; font-family:"Oswald", sans-serif; font-weight:700; font-size:64px; line-height:1.05; }}
.bf-a {{ background:rgba(143,195,217,.9); color:#06202b; }}
.bf-b {{ background:var(--papel); color:var(--rojo); }}
.bf-m {{ font-size:100px; color:var(--ambar); font-weight:900; }}
.fg {{ text-align:center; }}
.fg-g {{ display:grid; grid-template-columns:repeat(15, 70px); gap:18px 22px; justify-content:center; }}
.fg-g i {{ display:block; width:70px; height:100px; color:var(--papel); opacity:.9; }}
.fg-g svg {{ width:100%; height:100%; }}
.fg-l {{ margin-top:40px; font-family:"Oswald", sans-serif; font-weight:700; font-size:110px; color:var(--papel); text-shadow:0 8px 30px rgba(0,0,0,.8); }}
.fg-s {{ font-family:"Space Mono", monospace; font-size:40px; color:var(--ambar); text-shadow:0 4px 18px rgba(0,0,0,.9); }}
.fr {{ text-align:center; }}
.ck {{ width:1350px; background:#f3ecd9; color:var(--tinta); padding:30px 60px 40px; box-shadow:0 30px 80px rgba(0,0,0,.6); text-align:left; background-image:repeating-linear-gradient(180deg, transparent 0 88px, rgba(143,195,217,.5) 88px 91px); }}
.ck-h {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:66px; color:var(--rojo); margin-bottom:20px; }}
.ck-r {{ display:flex; align-items:center; gap:34px; padding:14px 0; }}
.ck-b {{ width:84px; height:84px; border:7px solid var(--tinta); display:flex; align-items:center; justify-content:center; flex:none; }}
.ck-m {{ font-size:80px; font-weight:900; opacity:0; }}
.ck-t {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:72px; line-height:1.05; }}
.pol {{ background:#f6f3ea; padding:28px 28px 20px; box-shadow:0 30px 80px rgba(0,0,0,.65); }}
.pol-c {{ font-family:"Space Mono", monospace; font-weight:700; font-size:44px; color:var(--tinta); margin-top:16px; }}
.mo {{ display:flex; align-items:center; gap:50px; }}
.mo-a, .mo-b {{ position:relative; padding:44px 70px; font-family:"Oswald", sans-serif; font-weight:700; font-size:130px; border:6px solid var(--papel); }}
.mo-a {{ background:#3b4a32; color:var(--papel); }}
.mo-b {{ background:var(--papel); color:var(--tinta); }}
.ag {{ display:flex; align-items:center; gap:90px; }}
.ag-c b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:300px; line-height:.95; color:var(--ambar); text-shadow:0 10px 50px rgba(0,0,0,.7); }}
.ag-c small {{ display:block; font-weight:900; font-size:52px; color:var(--papel); text-shadow:0 4px 18px rgba(0,0,0,.8); }}
.tm {{ width:1600px; }}
.tm-h {{ font-family:"Oswald", sans-serif; font-weight:700; font-size:90px; color:var(--ambar); text-shadow:0 8px 30px rgba(0,0,0,.8); margin-bottom:70px; }}
.tm-bar {{ position:relative; height:16px; background:rgba(239,230,211,.25); margin:0 120px 240px; }}
.tm-fill {{ position:absolute; inset:0; background:var(--ambar); }}
.tm-p {{ position:absolute; top:-22px; width:300px; margin-left:-150px; text-align:center; }}
.tm-p i {{ display:block; width:60px; height:60px; border-radius:50%; background:var(--rojo); border:8px solid var(--papel); margin:0 auto; }}
.tm-p b {{ display:block; font-family:"Oswald", sans-serif; font-weight:700; font-size:76px; color:var(--papel); text-shadow:0 6px 20px rgba(0,0,0,.9); }}
.tm-p small {{ display:block; font-weight:900; font-size:36px; color:var(--ambar); text-shadow:0 4px 18px rgba(0,0,0,.9); }}
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
    if getattr(C, 'cuts', None):
        bg = []
        cs = C.cuts
        ids = [c[0] for c in clips]
        assert len(set(x for x, _ in cs)) == len(cs), cid
        dmap = dict(zip(ids, durs))
        for cl, _ in cs: assert cl in ids, (cid, cl)
        L = [dmap[cl] - 0.4 for cl, _ in cs]
        lb = [0.0] * len(cs)
        lb[-1] = C.DUR - L[-1]
        for k in range(len(cs) - 2, -1, -1): lb[k] = lb[k + 1] - L[k]
        starts = []
        for k, (cl, an) in enumerate(cs):
            if k == 0: st = 0.0
            else:
                ps = starts[-1]
                st = min(max(an, lb[k], ps + 2.0), ps + L[k - 1])
            starts.append(st)
        for k, (cl, _) in enumerate(cs):
            en = starts[k + 1] if k + 1 < len(cs) else C.DUR
            if en - starts[k] > dmap[cl] - 0.3: print('AVISO clip corto', cid, cl, round(en - starts[k], 1), dmap[cl])
            bg.append((cl, starts[k], en - starts[k], k % 2))
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
        subprocess.run(['cp', f'/home/claude/vh/plantilla/{f}', d])
    json.dump({'dur': C.DUR, 'off': C.OFF, 'sfx': C.sfx, 'bg': bg, 'shakes': C.shakes}, open(f'{d}/info.json', 'w'))
    print(cid, 'dur', C.DUR, 'clips', len(bg), 'subs', len(groups), 'eventos', len(C.H))

if __name__ == '__main__':
    ids = sys.argv[1:] or [f'c{i}' for i in range(1, 10)]
    for cid in ids:
        build(cid, int(cid[1:]))
