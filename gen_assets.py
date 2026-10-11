#!/usr/bin/env python3
"""Generates the animated SVG assets for the profile README (SMIL only, no scripts).

Every animation has a complete static fallback: if animation is unsupported, the
first frame shows all text and shapes in their final positions.
"""
import math
import os
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#07060E"
INK = "#F4F1FF"
CY = "#25E8FF"
MG = "#FF3DA5"
LM = "#B6FF3B"
MUTE = "#8A86A6"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

DEFS = (
    '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="1" fill="#fff" fill-opacity=".05"/></pattern>'
    '<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
    f'<path d="M32 0H0V32" fill="none" stroke="{CY}" stroke-opacity=".07"/></pattern>'
    '<radialGradient id="vig" cx="50%" cy="50%" r="75%">'
    '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
    '<stop offset="100%" stop-color="#000" stop-opacity=".6"/></radialGradient>'
    '<filter id="glow" x="-40%" y="-40%" width="180%" height="180%">'
    '<feGaussianBlur stdDeviation="2.5" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    '<linearGradient id="sweep" x1="0" x2="1">'
    f'<stop offset="0" stop-color="{LM}" stop-opacity="0"/>'
    f'<stop offset=".5" stop-color="{LM}"/>'
    f'<stop offset="1" stop-color="{LM}" stop-opacity="0"/></linearGradient>'
)


def esc(s):
    return s.replace("&", "&amp;")


def svg(w, h, body, title, desc, extra_defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">\n<title id="t">{esc(title)}</title>'
        f'<desc id="d">{esc(desc)}</desc>\n<defs>{DEFS}{extra_defs}</defs>\n{body}\n</svg>\n'
    )


def base(w, h):
    return (f'<rect width="{w}" height="{h}" fill="{BG}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#grid)"/>')


def overlay(w, h):
    return (f'<rect width="{w}" height="{h}" fill="url(#scan)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#vig)"/>')


def frame(w, h, col=CY):
    L = 22
    s = (f'<rect x="10" y="10" width="{w-20}" height="{h-20}" fill="none" stroke="{col}" '
         f'stroke-opacity=".4" stroke-width="1"/>')
    c = (f"M10 {10+L}V10H{10+L}M{w-10-L} 10H{w-10}V{10+L}"
         f"M10 {h-10-L}V{h-10}H{10+L}M{w-10-L} {h-10}H{w-10}V{h-10-L}")
    return s + f'<path d="{c}" fill="none" stroke="{MG}" stroke-width="2.2"/>'


def text(x, y, s, size=13, fill=INK, anchor="start", weight="normal", spacing=0, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{spacing}" {extra}>{s}</text>')


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name}: {len(content)} bytes")


def glitch(x, y, body, size, dur=5.0, anchor="start", spread=3):
    """RGB-split headline: magenta and cyan ghosts burst apart for a moment each cycle."""
    kt = "0;0.78;0.80;0.83;0.86;0.88;1"

    def layer(color, vals, opacity):
        first = vals.split(";")[0]
        return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="bold" '
                f'text-anchor="{anchor}" fill="{color}" fill-opacity="{opacity}" transform="translate({first})">'
                f'{body}<animateTransform attributeName="transform" type="translate" values="{vals}" '
                f'keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></text>')

    s = spread
    mg = f"{-s} 0;{-s} 0;{-4*s} {s};{3*s} {-s};{-2*s} 1;{-s} 0;{-s} 0"
    cy = f"{s} 0;{s} 0;{4*s} {-s};{-3*s} {s};{2*s} -1;{s} 0;{s} 0"
    mn = "0 0;0 0;-2 0;2 0;-1 0;0 0;0 0"
    return (layer(MG, mg, ".9") + layer(CY, cy, ".9") + layer(INK, mn, "1"))


def typed(i, x, y, content, nchars, start, end, cycle, size=16):
    """Wipe-in line. content holds markup; nchars sets the reveal width."""
    w = round(nchars * size * 0.6 + 8, 1)
    kt = f"0;{start/cycle:.4f};{end/cycle:.4f};0.95;1"
    clip = (f'<clipPath id="tc{i}"><rect x="{x-2}" y="{y-size}" width="{w}" height="{size+8}">'
            f'<animate attributeName="width" values="0;0;{w};{w};0" keyTimes="{kt}" dur="{cycle}s" '
            f'repeatCount="indefinite"/></rect></clipPath>')
    t = (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{INK}" '
         f'clip-path="url(#tc{i})">{content}</text>')
    return clip + t


def cursor(color=LM):
    return (f'<tspan fill="{color}"> |<animate attributeName="fill" values="{color};none" dur="1s" '
            f'calcMode="discrete" repeatCount="indefinite"/></tspan>')


def rain(w, h, cols, seed, opacity=0.15):
    rng = random.Random(seed)
    chars = "01{}<>/=;:+*#$%&"
    out = []
    for i in range(cols):
        x = round(16 + i * (w - 32) / (cols - 1), 1)
        n = rng.randint(7, 14)
        tsp = "".join(
            f'<tspan x="{x}" dy="16">{esc(rng.choice(chars)).replace("<", "&lt;").replace(">", "&gt;")}</tspan>'
            for _ in range(n))
        dur = round(rng.uniform(7, 15), 1)
        begin = -round(rng.uniform(0, dur), 1)
        col = CY if i % 3 else LM
        out.append(
            f'<text x="{x}" y="0" font-family="{MONO}" font-size="14" fill="{col}" fill-opacity="{opacity}">'
            f'{tsp}<animateTransform attributeName="transform" type="translate" from="0 {-n*16}" '
            f'to="0 {h+16}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></text>')
    return "".join(out)


def ticker(y, h, items, fill, ink, direction=1, length=1500, dur=30, cid="tk", w=1000):
    sep = "  //  "  # non-breaking spaces survive XML whitespace collapsing
    s = sep.join(items) + sep
    one = lambda x: (f'<text x="{x}" y="{y+h*0.66:.1f}" font-family="{MONO}" font-size="15" font-weight="bold" '
                     f'fill="{ink}" textLength="{length}" lengthAdjust="spacing">{s}</text>')
    frm, to = (0, -length) if direction == 1 else (-length, 0)
    return (f'<clipPath id="{cid}"><rect x="10" y="{y}" width="{w-20}" height="{h}"/></clipPath>'
            f'<rect x="10" y="{y}" width="{w-20}" height="{h}" fill="{fill}"/>'
            f'<g clip-path="url(#{cid})"><g>{one(10)}{one(10+length)}'
            f'<animateTransform attributeName="transform" type="translate" from="{frm} 0" to="{to} 0" '
            f'dur="{dur}s" repeatCount="indefinite"/></g></g>')


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1000, 560
    b = [base(W, H), rain(W, H, 30, 216, 0.14), frame(W, H)]

    b.append(f'<circle cx="38" cy="38" r="4" fill="{LM}"><animate attributeName="opacity" values="1;0.2;1" '
             f'dur="1.4s" repeatCount="indefinite"/></circle>')
    b.append(text(50, 42, "LIVE // kavya-216", 12, INK, spacing=2))
    b.append(text(962, 42, "PUBLIC REPOS ONLY", 12, MUTE, "end", spacing=2))

    # ---- neural network (right)
    layers = [(590, [270]), (685, [150, 230, 310, 390]),
              (780, [120, 195, 270, 345, 420]), (870, [165, 270, 375])]
    for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
        for y1 in ya:
            for y2 in yb:
                b.append(f'<path d="M{xa} {y1}L{xb} {y2}" stroke="{CY}" stroke-opacity=".17" stroke-width="1"/>')
    rng = random.Random(7)
    colors = [CY, MG, LM]
    for k in range(10):
        h1 = rng.choice(layers[1][1]); h2 = rng.choice(layers[2][1]); o = rng.choice(layers[3][1])
        path = f"M590 270L685 {h1}L780 {h2}L870 {o}"
        beg = round(k * 0.55, 2)
        b.append(
            f'<circle r="3.6" fill="{colors[k % 3]}" opacity="0" filter="url(#glow)">'
            f'<animateMotion path="{path}" dur="2.6s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="2.6s" '
            f'begin="{beg}s" repeatCount="indefinite"/></circle>')
    for x, ys in layers[1:3]:
        for y in ys:
            b.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{BG}" stroke="{CY}" stroke-width="1.6"/>')
    b.append(f'<circle cx="590" cy="270" r="10" fill="{LM}" filter="url(#glow)"/>')
    b.append(text(590, 244, "what if…", 14, LM, "middle", "bold"))
    for j, (name, y) in enumerate(zip(["BUG", "FEATURE", "WHY?"], layers[3][1])):
        b.append(
            f'<circle cx="870" cy="{y}" r="12" fill="none" stroke="{MG}" stroke-width="2" opacity="0">'
            f'<animate attributeName="r" values="12;12;30" keyTimes="0;.3;1" dur="3.3s" begin="{j*1.1}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.3;1" dur="3.3s" begin="{j*1.1}s" repeatCount="indefinite"/></circle>')
        b.append(f'<circle cx="870" cy="{y}" r="12" fill="{BG}" stroke="{MG}" stroke-width="2.5" filter="url(#glow)"/>')
        b.append(f'<circle cx="870" cy="{y}" r="5" fill="{MG}"/>')
        b.append(text(890, y + 5, name, 15, INK, weight="bold"))
    b.append(text(730, 474, "// tiny network, big ambitions", 12, MUTE, "middle"))

    # ---- headline (left)
    b.append(text(44, 148, "HELLO,", 54, INK, weight="bold", spacing=2))
    b.append(glitch(40, 262, f'STALKER<tspan fill="{LM}">.</tspan>', 100, dur=5, spread=3))
    b.append(f'<rect x="44" y="284" width="96" height="28" fill="{MG}"/>')
    b.append(text(92, 304, "KAVYA", 16, BG, "middle", "bold", 4))
    b.append(text(154, 304, "CSE undergrad · Honours · AI/ML · backend", 13, MUTE))

    cyc = 12
    b.append(typed(1, 44, 352, f'<tspan fill="{MG}">//</tspan> I only index public repositories.', 36, 0.5, 2.0, cyc))
    b.append(typed(2, 44, 380, f'<tspan fill="{MG}">//</tspan> status: curious (self-reported)', 34, 2.6, 4.0, cyc))
    b.append(typed(3, 44, 408, f'<tspan fill="{MG}">//</tspan> ask me: what if…{cursor()}', 22, 4.6, 5.8, cyc))

    # ---- ticker
    b.append(ticker(498, 36, ["AI/ML", "RAG", "BACKEND", "COMPUTER VISION", "ACCESSIBILITY",
                              "NEURAL NETWORKS", "DATABASES", "USEFUL SOFTWARE", "ODD EXPERIMENTS"],
                    CY, BG, 1, 1500, 30))
    b.append(overlay(W, H))
    desc = ("Glitching headline 'HELLO, STALKER.' beside an animated neural network. Signals travel from the "
            "query 'what if…' to three outputs: bug, feature and why. A ticker lists AI/ML, RAG, backend, "
            "computer vision and accessibility.")
    write("hero.svg", svg(W, H, "\n".join(b), "Hello, stalker — Kavya", desc))


# --------------------------------------------------------------------------- section headers
def section(fname, num, label, aside):
    W, H = 1000, 72
    b = [base(W, H)]
    b.append(text(24, 46, f"// {num}", 22, MG, weight="bold"))
    b.append(glitch(112, 49, label, 30, dur=6, spread=2))
    b.append(text(976, 36, aside, 13, MUTE, "end"))
    b.append(f'<path d="M24 62H976" stroke="{CY}" stroke-opacity=".35"/>')
    b.append(f'<rect x="24" y="60" width="120" height="3" fill="url(#sweep)">'
             f'<animate attributeName="x" from="24" to="856" dur="3.2s" repeatCount="indefinite"/></rect>')
    b.append(overlay(W, H))
    write(fname, svg(W, H, "\n".join(b), f"{num} {label}", f"Section header: {label}"))


# --------------------------------------------------------------------------- protocol loop
def method():
    W, H = 1000, 176
    b = [base(W, H), frame(W, H)]
    b.append(text(40, 40, "PROTOCOL", 12, INK, spacing=3))
    b.append(text(960, 40, "RUNS UNTIL IT STOPS BEING WRONG", 12, MUTE, "end", spacing=2))
    labels = ["question", "prototype", "break", "understand", "ship"]
    xs = [110, 305, 500, 695, 890]
    py, ph = 58, 48
    for i, (lab, cx) in enumerate(zip(labels, xs)):
        hot = lab == "break"
        shake = ""
        if hot:
            shake = ('<animateTransform attributeName="transform" type="translate" '
                     'values="0 0;0 0;-4 0;4 0;-3 0;0 0;0 0" keyTimes="0;.45;.47;.49;.51;.53;1" '
                     'dur="8s" repeatCount="indefinite"/>')
        b.append(f'<g>{shake}<rect x="{cx-76}" y="{py}" width="152" height="{ph}" rx="24" '
                 f'fill="{MG if hot else BG}" stroke="{MG if hot else CY}" stroke-width="1.8"/>'
                 + text(cx, py + 30, lab, 15, BG if hot else INK, "middle", "bold") + "</g>")
        p = (195 * i) / 1660
        if i == 0:
            vals, kts = "0.5;0;0", "0;0.06;1"
        else:
            vals, kts = "0;0;0.5;0;0", f"0;{max(p-0.03,0.001):.4f};{p:.4f};{p+0.06:.4f};1"
        b.append(f'<rect x="{cx-76}" y="{py}" width="152" height="{ph}" rx="24" fill="{LM}" opacity="0">'
                 f'<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="8s" repeatCount="indefinite"/></rect>')
        if i < len(labels) - 1:
            x0, x1 = cx + 84, xs[i + 1] - 84
            b.append(f'<path d="M{x0} {py+24}H{x1-6}" stroke="{CY}" stroke-width="1.6"/>')
            b.append(f'<path d="M{x1-8} {py+19}L{x1} {py+24}L{x1-8} {py+29}Z" fill="{CY}"/>')
    b.append(f'<path d="M890 {py+ph+4}V136H110V{py+ph+8}" fill="none" stroke="{MG}" stroke-width="1.6" stroke-dasharray="6 6">'
             f'<animate attributeName="stroke-dashoffset" from="24" to="0" dur="1.2s" repeatCount="indefinite"/></path>')
    b.append(f'<path d="M104 {py+ph+10}L110 {py+ph+2}L116 {py+ph+10}Z" fill="{MG}"/>')
    b.append(f'<rect x="372" y="127" width="256" height="18" fill="{BG}"/>')
    b.append(text(500, 141, "repeat // with a better question", 12, MG, "middle"))
    b.append(f'<circle r="5" fill="{LM}" filter="url(#glow)"><animateMotion path="M110 {py+24}H890V136H110Z" '
             f'dur="8s" repeatCount="indefinite"/></circle>')
    b.append(overlay(W, H))
    write("method.svg", svg(W, H, "\n".join(b), "Protocol: question, prototype, break, understand, ship",
                            "An animated loop: question, prototype, break, understand, ship, then back to question."))


# --------------------------------------------------------------------------- Mitra
def mitra():
    W, H = 1000, 360
    b = [base(W, H), frame(W, H, MG)]
    b.append(text(40, 42, "CASE 01 // LEAD RESULT", 12, MUTE, spacing=3))
    b.append(glitch(38, 118, "MITRA", 76, dur=6, spread=3))
    b.append(text(42, 152, "Legal &amp; Mental Aid Platform for Women", 15, INK))

    b.append(
        f'<g transform="translate(822 92) rotate(-6)" filter="url(#glow)">'
        f'<rect x="-132" y="-38" width="264" height="76" fill="none" stroke="{LM}" stroke-width="2.4"/>'
        f'<rect x="-124" y="-30" width="248" height="60" fill="none" stroke="{LM}" stroke-width=".8"/>'
        f'<text x="0" y="-2" text-anchor="middle" font-family="{MONO}" font-size="22" font-weight="bold" fill="{LM}" letter-spacing="4">RUNNER-UP</text>'
        f'<text x="0" y="20" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{LM}" letter-spacing="2">SHEBUILDS HACKATHON</text>'
        f'<animate attributeName="opacity" values="1;0.65;1" dur="2.4s" repeatCount="indefinite"/></g>')

    y0, hh = 204, 70

    def box(x, w, title, sub):
        return (f'<rect x="{x}" y="{y0}" width="{w}" height="{hh}" fill="{BG}" stroke="{CY}" stroke-width="1.6"/>'
                + text(x + w / 2, y0 + 30, title, 15, INK, "middle", "bold")
                + text(x + w / 2, y0 + 52, sub, 12, MUTE, "middle"))

    def arrow(x0, x1):
        yc = y0 + hh / 2
        return (f'<path d="M{x0} {yc}H{x1-7}" stroke="{CY}" stroke-width="1.6"/>'
                f'<path d="M{x1-9} {yc-5}L{x1} {yc}L{x1-9} {yc+5}Z" fill="{CY}"/>')

    b.append(box(40, 170, "a question", "legal · mental health"))
    b.append(arrow(210, 258))
    b.append(box(258, 180, "retrieval", "Python · RAG"))
    b.append(arrow(438, 486))
    cx0, cw = 486, 348
    b.append(f'<rect x="{cx0}" y="{y0-28}" width="{cw}" height="{hh+56}" fill="{MG}" fill-opacity=".1" '
             f'stroke="{MG}" stroke-width="2" stroke-dasharray="8 5"><animate attributeName="stroke-dashoffset" '
             f'from="26" to="0" dur="1.6s" repeatCount="indefinite"/></rect>')
    b.append(text(cx0 + 12, y0 - 10, "SUPABASE // DATA LAYER", 12, MG, weight="bold", spacing=1.5))
    b.append(text(cx0 + cw - 12, y0 - 10, "← my part", 12, MG, "end", "bold"))
    b.append(f'<rect x="{cx0+12}" y="{y0+10}" width="152" height="50" fill="{BG}" stroke="{INK}" stroke-opacity=".7"/>')
    b.append(text(cx0 + 88, y0 + 40, "legal resources", 13, INK, "middle"))
    b.append(f'<rect x="{cx0+184}" y="{y0+10}" width="152" height="50" fill="{BG}" stroke="{INK}" stroke-opacity=".7"/>')
    b.append(text(cx0 + 260, y0 + 40, "mental-health support", 11, INK, "middle"))
    b.append(arrow(834, 878))
    b.append(box(878, 100, "answer", "grounded"))
    yc = y0 + hh / 2
    b.append(f'<circle r="4.5" fill="{LM}" filter="url(#glow)"><animateMotion path="M44 {yc}H960" dur="4.5s" repeatCount="indefinite"/></circle>')
    b.append(text(40, 334, "simplified sketch // highlighted block = the part I built", 12, MUTE))
    b.append(overlay(W, H))
    write("mitra.svg", svg(W, H, "\n".join(b), "Mitra — Legal & Mental Aid Platform for Women",
                            "Animated case plate for Mitra, runner-up at the SheBuilds Hackathon. A pulse travels a simplified flow: "
                            "question, retrieval, a Supabase data layer with legal resources and mental-health support, then a grounded answer."))


# --------------------------------------------------------------------------- small cards
def udaan():
    W, H = 480, 150
    b = [base(W, H), frame(W, H)]
    cx, cy = 140, 78
    L = 16
    x0, y0, x1, y1 = cx - 72, cy - 44, cx + 72, cy + 44
    for (px, py, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        b.append(f'<path d="M{px} {py+dy*L}V{py}H{px+dx*L}" stroke="{MG}" stroke-width="2.6" fill="none">'
                 f'<animate attributeName="stroke-opacity" values="1;.4;1" dur="1.8s" repeatCount="indefinite"/></path>')
    pts = [(110, 62), (140, 50), (172, 64), (122, 92), (156, 100), (140, 74)]
    edges = [(0, 1), (1, 2), (2, 4), (4, 3), (3, 0), (5, 0), (5, 2), (5, 3), (5, 4)]
    for a, c in edges:
        b.append(f'<path d="M{pts[a][0]} {pts[a][1]}L{pts[c][0]} {pts[c][1]}" stroke="{CY}" stroke-opacity=".55"/>')
    for i, (x, y) in enumerate(pts):
        b.append(f'<circle cx="{x}" cy="{y}" r="4.4" fill="{LM}"><animate attributeName="r" values="4.4;6.4;4.4" '
                 f'dur="2s" begin="{i*0.3}s" repeatCount="indefinite"/></circle>')
    b.append(f'<rect x="{x0+4}" y="{y0}" width="{x1-x0-8}" height="2" fill="{LM}" opacity="0" filter="url(#glow)">'
             f'<animate attributeName="y" values="{y0};{y1}" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.1;.9;1" dur="2.4s" repeatCount="indefinite"/></rect>')
    b.append(text(256, 70, "ACCESSIBILITY", 13, CY, weight="bold", spacing=2))
    b.append(text(256, 92, "COMPUTER VISION", 12, MUTE, spacing=2))
    b.append(overlay(W, H))
    write("udaan.svg", svg(W, H, "\n".join(b), "Udaan glyph", "Viewfinder corners and a scanning line over a small keypoint graph."))


def ecosentry():
    W, H = 480, 150
    b = [base(W, H), frame(W, H)]
    rng = random.Random(7)
    base_y = 78
    x = 36
    while x < 290:
        env = math.exp(-((x - 180) / 62) ** 2)
        amp = 5 + 40 * env * rng.uniform(.5, 1.0) + rng.uniform(0, 5)
        amp2 = max(4, amp * rng.uniform(.35, 1.4))
        hot = 160 <= x <= 204
        col = MG if hot else CY
        h1, h2 = amp * 2, amp2 * 2
        dur = round(rng.uniform(.7, 1.6), 2)
        b.append(
            f'<rect x="{x}" y="{base_y-h1/2:.1f}" width="3.4" height="{h1:.1f}" rx="1.7" fill="{col}" fill-opacity="{1 if hot else .75}">'
            f'<animate attributeName="height" values="{h1:.1f};{h2:.1f};{h1:.1f}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{base_y-h1/2:.1f};{base_y-h2/2:.1f};{base_y-h1/2:.1f}" dur="{dur}s" repeatCount="indefinite"/></rect>')
        x += 8
    b.append(text(312, 70, "ENVIRONMENTAL", 13, CY, weight="bold", spacing=2))
    b.append(text(312, 92, "AUDIO SIGNALS", 12, MUTE, spacing=2))
    b.append(overlay(W, H))
    write("ecosentry.svg", svg(W, H, "\n".join(b), "EcoSentry glyph", "A live-moving audio waveform with one highlighted event."))


# --------------------------------------------------------------------------- ending
def ending():
    W, H = 1000, 300
    b = [base(W, H), rain(W, H, 30, 99, 0.12), frame(W, H)]
    b.append(text(40, 42, "END OF TRANSMISSION", 12, MUTE, spacing=3))
    b.append(glitch(38, 150, f'BYE, STALKER<tspan fill="{LM}">.</tspan>', 84, dur=5, spread=3))
    cyc = 10
    b.append(typed(1, 44, 196, f'<tspan fill="{MG}">//</tspan> you have been indexed.', 25, 0.5, 1.8, cyc))
    b.append(typed(2, 44, 224, f'<tspan fill="{MG}">//</tspan> got a better query? you know where to find me.{cursor()}', 52, 2.4, 4.6, cyc))

    q = (870, 100)
    for x, y in [(800, 62), (950, 80), (920, 170)]:
        b.append(f'<path d="M{q[0]} {q[1]}L{x} {y}" stroke="{MG}" stroke-width="1.3" stroke-dasharray="5 5" fill="none">'
                 f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.4s" repeatCount="indefinite"/></path>')
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{BG}" stroke="{CY}" stroke-width="2"/>')
    b.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="8" fill="none" stroke="{LM}" stroke-width="1.6">'
             f'<animate attributeName="r" values="8;38" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0" dur="2.4s" repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="8" fill="{LM}" filter="url(#glow)"/>')
    b.append(text(q[0], 206, "q = what if…", 12, LM, "middle", "bold"))

    b.append(ticker(256, 28, ["NO FURTHER RESULTS", "RERUN WITH A BETTER QUERY", "THANKS FOR STALKING"] * 2,
                    MG, BG, -1, 1450, 34, cid="tk2"))
    b.append(overlay(W, H))
    write("ending.svg", svg(W, H, "\n".join(b), "Bye, stalker",
                            "Glitching 'BYE, STALKER.' over falling code, with the query point and its three results from the top of the page."))


if __name__ == "__main__":
    hero()
    section("sec-results.svg", "01", "RESULTS", "ranked by relevance, not by date")
    section("sec-toolkit.svg", "02", "TOOLKIT", "what's on the bench")
    method()
    mitra()
    udaan()
    ecosentry()
    ending()
