#!/usr/bin/env python3
"""Generates the custom SVG assets for the profile README. Static output, no scripts."""
import math
import os
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#14161A"
PAPER = "#F1ECE0"
ACC = "#E4572E"
MUTE = "#6B665C"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SERIF = "Georgia,'Times New Roman',serif"

GRID = (
    '<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse">'
    f'<path d="M40 0H0V40" fill="none" stroke="{INK}" stroke-opacity=".07"/></pattern>'
)


def esc(s):
    return s.replace("&", "&amp;")


def svg(w, h, body, title, desc, defs=GRID):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">\n'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>\n'
        f"<defs>{defs}</defs>\n{body}\n</svg>\n"
    )


def frame(w, h):
    s = (
        f'<rect width="{w}" height="{h}" fill="{PAPER}"/>'
        f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
        f'<rect x="12" y="12" width="{w-24}" height="{h-24}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
    )
    marks = (
        f"M0 12H6M12 0V6M{w} 12H{w-6}M{w-12} 0V6"
        f"M0 {h-12}H6M12 {h}V{h-6}M{w} {h-12}H{w-6}M{w-12} {h}V{h-6}"
    )
    return s + f'<path d="{marks}" stroke="{INK}" stroke-width="1" fill="none"/>'


def text(x, y, s, size=12, fill=INK, anchor="start", family=MONO, weight="normal",
         spacing=0, style="normal", extra=""):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{spacing}" '
        f'font-style="{style}" {extra}>{s}</text>'
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{name}: {len(content)} bytes")


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1000, 520
    q = (775, 275)
    nodes = {"MITRA": (690, 215, 14), "UDAAN": (885, 215, 10), "ECOSENTRY": (700, 405, 10)}

    avoid_pts = [(q[0], q[1], 40)] + [(x, y, 34) for x, y, _ in nodes.values()]
    avoid_pts += [(600, 320, 16), (616, 336, 16), (596, 344, 16), (952, 414, 20)]
    avoid_rects = [
        (630, 172, 750, 200), (835, 172, 935, 200), (650, 418, 750, 442),
        (770, 250, 920, 306), (730, 96, 820, 118), (570, 352, 720, 372),
        (570, 448, 800, 470), (860, 424, 970, 446),
    ]
    rng = random.Random(216)
    dots = []
    tries = 0
    while len(dots) < 44 and tries < 8000:
        tries += 1
        x, y = rng.uniform(580, 962), rng.uniform(76, 440)
        if any(math.hypot(x - px, y - py) < r for px, py, r in avoid_pts):
            continue
        if any(a <= x <= c and b <= y <= d for a, b, c, d in avoid_rects):
            continue
        if any(math.hypot(x - a, y - b) < 24 for a, b, _, _ in dots):
            continue
        dots.append((round(x, 1), round(y, 1), rng.choice([2, 2.4, 2.8, 3.2]), round(rng.uniform(.3, .62), 2)))

    b = [frame(W, H)]

    # header strip
    b.append(text(44, 42, "FIG. 01 · A PROFILE, TREATED AS AN EXPERIMENT", 12, INK, spacing=2))
    b.append(text(956, 42, "SUBJECT n=1 (SELF-REPORTED)", 12, MUTE, "end", spacing=2))
    b.append(f'<path d="M12 56H988" stroke="{INK}" stroke-width="1"/>')

    # left: typography
    b.append(text(44, 142, "Hello,", 46, INK, family=SERIF, style="italic"))
    b.append(
        f'<text x="38" y="262" font-family="{SERIF}" font-size="136" font-style="italic" fill="{INK}" '
        f'letter-spacing="-3">stalker<tspan fill="{ACC}">.</tspan></text>'
    )
    b.append(text(44, 304, "Don’t worry — I only index public repositories.", 15, INK))
    b.append(f'<path d="M44 330H84" stroke="{ACC}" stroke-width="3"/>')
    b.append(text(44, 356, "KAVYA", 16, INK, weight="bold", spacing=7))
    b.append(text(44, 378, "CSE undergrad, Honours", 13, INK))
    b.append(text(44, 396, "AI/ML · backend · useful software · odd experiments", 13, MUTE))
    b.append(
        f'<text x="44" y="452" font-family="{MONO}" font-size="16" fill="{INK}">query ›  '
        f'<tspan fill="{ACC}">“what if…”</tspan>'
        f'<tspan fill="{ACC}"> |<animate attributeName="fill" values="{ACC};none" dur="1.1s" '
        f'calcMode="discrete" repeatCount="indefinite"/></tspan></text>'
    )

    # plot: faint crosshair
    b.append(f'<path d="M575 {q[1]}H965M{q[0]} 72V468" stroke="{INK}" stroke-opacity=".16" stroke-dasharray="1 4"/>')

    # embedding-space dots
    for x, y, r, o in dots:
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}" fill-opacity="{o}"/>')

    # hollow = unshipped ideas
    for x, y in [(600, 320), (616, 336), (596, 344)]:
        b.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="none" stroke="{INK}" stroke-opacity=".7"/>')
    b.append(text(582, 366, "unshipped ideas", 12, MUTE))

    # the one that is a bug
    b.append(f'<circle cx="952" cy="414" r="3.4" fill="{ACC}"/>')
    b.append(text(966, 436, "↑ a known issue", 12, ACC, "end"))

    # top-k boundary, slowly rotating
    b.append(
        f'<circle cx="{q[0]}" cy="{q[1]}" r="160" fill="none" stroke="{INK}" stroke-opacity=".55" '
        f'stroke-dasharray="2 7"><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {q[0]} {q[1]}" to="360 {q[0]} {q[1]}" dur="90s" repeatCount="indefinite"/></circle>'
    )
    b.append(text(q[0], 104, "top-k = 3", 12, MUTE, "middle"))

    # retrieval lines (query -> project), dashes flow outward
    for name, (x, y, r) in nodes.items():
        b.append(
            f'<path d="M{q[0]} {q[1]}L{x} {y}" stroke="{ACC}" stroke-width="1.4" stroke-dasharray="5 5" fill="none">'
            f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.4s" repeatCount="indefinite"/></path>'
        )

    # project nodes
    ranks = {"MITRA": "#1", "UDAAN": "#2", "ECOSENTRY": "#3"}
    for name, (x, y, r) in nodes.items():
        if name == "MITRA":
            b.append(f'<circle cx="{x}" cy="{y}" r="{r+6}" fill="none" stroke="{ACC}" stroke-width="1.4"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{round(r*0.3,1)}" fill="{PAPER}"/>')
        ly = y - r - (12 if name == "MITRA" else 10) if name != "ECOSENTRY" else y + r + 18
        b.append(
            f'<text x="{x}" y="{ly}" font-family="{MONO}" font-size="14" font-weight="bold" fill="{INK}" '
            f'text-anchor="middle"><tspan fill="{ACC}">{ranks[name]}</tspan> {name}</text>'
        )

    # query point + pulse
    b.append(
        f'<circle cx="{q[0]}" cy="{q[1]}" r="7" fill="none" stroke="{ACC}" stroke-width="1.5">'
        f'<animate attributeName="r" values="7;38" dur="2.6s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0" dur="2.6s" repeatCount="indefinite"/></circle>'
    )
    b.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="7" fill="{ACC}"/>')
    b.append(text(q[0] + 14, q[1] + 24, "q = what if…", 13, ACC, weight="bold"))

    b.append(text(575, 462, "embedding space — not to scale", 12, MUTE))

    # footer
    b.append(f'<path d="M12 476H988" stroke="{INK}" stroke-width="1"/>')
    b.append(text(44, 497, "↓ SCROLL FOR RESULTS", 12, INK, spacing=2))
    b.append(text(956, 497, "3 RESULTS RETURNED · NO EMBEDDINGS WERE HARMED", 12, MUTE, "end", spacing=1.5))

    desc = ("The words 'Hello, stalker.' in large italic type beside a scatter plot of an embedding space. "
            "A query, 'what if…', retrieves three projects: Mitra, Udaan and EcoSentry.")
    write("hero.svg", svg(W, H, "\n".join(b), "Hello, stalker — Kavya", desc))


# --------------------------------------------------------------------------- section headers
def section(fname, num, label, aside):
    W, H = 1000, 68
    b = [frame(W, H).replace(f'<rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="{INK}" stroke-width="1.2"/>', "")]
    b[0] = b[0].split('<path d=')[0]  # drop crop marks for slim strips
    b.append(text(24, 42, num, 24, ACC, weight="bold", spacing=1))
    b.append(text(74, 42, label, 24, INK, weight="bold", spacing=7))
    b.append(text(976, 40, aside, 13, MUTE, "end"))
    b.append(f'<path d="M24 56H976" stroke="{INK}" stroke-width="1"/>')
    ticks = "".join(
        f"M{24+i} 56v-{7 if i % 40 == 0 else 3}" for i in range(0, 953, 8)
    )
    b.append(f'<path d="{ticks}" stroke="{INK}" stroke-width="1" fill="none"/>')
    b.append(f'<rect x="24" y="55" width="36" height="3" fill="{ACC}"/>')
    write(fname, svg(W, H, "\n".join(b), f"{num} {label}", f"Section header: {label}"))


# --------------------------------------------------------------------------- protocol / loop
def method():
    W, H = 1000, 150
    b = [frame(W, H)]
    b.append(text(44, 40, "FIG. 02 · PROTOCOL", 11, INK, spacing=2))
    b.append(text(956, 40, "RUNS UNTIL IT STOPS BEING WRONG", 11, MUTE, "end", spacing=2))
    labels = ["question", "prototype", "break", "understand", "ship"]
    xs = [110, 305, 500, 695, 890]
    for i, (lab, cx) in enumerate(zip(labels, xs)):
        hot = lab == "break"
        fill = ACC if hot else "none"
        tcol = PAPER if hot else INK
        b.append(f'<rect x="{cx-75}" y="56" width="150" height="38" rx="19" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>')
        b.append(text(cx, 80, lab, 14, tcol, "middle", weight="bold"))
        if i < len(labels) - 1:
            x0, x1 = cx + 82, xs[i + 1] - 82
            b.append(f'<path d="M{x0} 75H{x1-6}" stroke="{INK}" stroke-width="1.2"/>')
            b.append(f'<path d="M{x1-7} 71L{x1} 75L{x1-7} 79Z" fill="{INK}"/>')
    b.append(
        f'<path d="M890 96V122H110V102" stroke="{ACC}" stroke-width="1.4" fill="none" stroke-dasharray="5 5">'
        f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.4s" repeatCount="indefinite"/></path>'
    )
    b.append(f'<path d="M105 104L110 97L115 104Z" fill="{ACC}"/>')
    b.append(f'<rect x="380" y="113" width="240" height="18" fill="{PAPER}"/>')
    b.append(text(500, 126, "repeat — with a better question", 12, ACC, "middle"))
    write("method.svg", svg(W, H, "\n".join(b), "Protocol: question, prototype, break, understand, ship",
                            "A loop: question, prototype, break, understand, ship, then back to question."))


# --------------------------------------------------------------------------- Mitra plate
def mitra():
    W, H = 1000, 320
    b = [frame(W, H)]
    b.append(text(44, 40, "CASE 01 · LEAD RESULT", 11, INK, spacing=2))
    b.append(text(44, 118, "Mitra", 84, INK, family=SERIF, style="italic"))
    b.append(text(48, 148, "Legal &amp; Mental Aid Platform for Women", 14, INK))

    # stamp
    b.append(
        f'<g transform="translate(822 86) rotate(-7)">'
        f'<rect x="-128" y="-36" width="256" height="72" fill="none" stroke="{ACC}" stroke-width="2.2"/>'
        f'<rect x="-121" y="-29" width="242" height="58" fill="none" stroke="{ACC}" stroke-width=".8"/>'
        f'<text x="0" y="-3" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="bold" fill="{ACC}" letter-spacing="4">RUNNER-UP</text>'
        f'<text x="0" y="18" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ACC}" letter-spacing="2">SHEBUILDS HACKATHON</text>'
        f"</g>"
    )

    # simplified flow
    y0, hh = 188, 64

    def box(x, w, title, sub, hot=False):
        s = f'<rect x="{x}" y="{y0}" width="{w}" height="{hh}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
        s += text(x + w / 2, y0 + 28, title, 14, INK, "middle", weight="bold")
        s += text(x + w / 2, y0 + 48, sub, 11, MUTE, "middle")
        return s

    def arrow(x0, x1):
        yc = y0 + hh / 2
        return (f'<path d="M{x0} {yc}H{x1-7}" stroke="{INK}" stroke-width="1.2"/>'
                f'<path d="M{x1-8} {yc-4}L{x1} {yc}L{x1-8} {yc+4}Z" fill="{INK}"/>')

    b.append(box(44, 170, "a question", "legal · mental health"))
    b.append(arrow(214, 262))
    b.append(box(262, 180, "retrieval", "Python · RAG"))
    b.append(arrow(442, 490))

    cx0, cw = 490, 344
    b.append(f'<rect x="{cx0}" y="{y0-26}" width="{cw}" height="{hh+52}" fill="{ACC}" fill-opacity=".09" stroke="{ACC}" stroke-width="1.6"/>')
    b.append(text(cx0 + 12, y0 - 8, "SUPABASE · DATA LAYER", 11, ACC, weight="bold", spacing=1.5))
    b.append(text(cx0 + cw - 12, y0 - 8, "← my part", 11, ACC, "end", weight="bold"))
    b.append(f'<rect x="{cx0+12}" y="{y0+8}" width="152" height="46" fill="{PAPER}" stroke="{INK}"/>')
    b.append(text(cx0 + 88, y0 + 36, "legal resources", 12, INK, "middle"))
    b.append(f'<rect x="{cx0+180}" y="{y0+8}" width="152" height="46" fill="{PAPER}" stroke="{INK}"/>')
    b.append(text(cx0 + 256, y0 + 36, "mental-health support", 11, INK, "middle"))

    b.append(arrow(834, 876))
    b.append(box(876, 100, "answer", "grounded"))

    b.append(text(44, 296, "simplified sketch · highlighted block = the part I built", 11, MUTE))
    write("mitra.svg", svg(W, H, "\n".join(b), "Mitra — Legal & Mental Aid Platform for Women",
                            "Case plate for Mitra, runner-up at the SheBuilds Hackathon, with a simplified flow from a "
                            "question through retrieval to a Supabase data layer holding legal resources and mental-health support."))


# --------------------------------------------------------------------------- small glyphs
def udaan():
    W, H = 480, 130
    b = [frame(W, H)]
    cx, cy = 150, 66
    L = 14
    x0, y0, x1, y1 = cx - 70, cy - 40, cx + 70, cy + 40
    for (px, py, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        b.append(f'<path d="M{px} {py+dy*L}V{py}H{px+dx*L}" stroke="{ACC}" stroke-width="2.4" fill="none"/>')
    pts = [(120, 52), (150, 44), (176, 56), (136, 72), (164, 78), (148, 60)]
    pts = [(round(150 + (x - 150) * 1.6, 1), round(64 + (y - 64) * 1.6, 1)) for x, y in pts]
    b.append(f'<path d="M{pts[0][0]} {pts[0][1]}L{pts[1][0]} {pts[1][1]}L{pts[2][0]} {pts[2][1]}L{pts[4][0]} {pts[4][1]}L{pts[3][0]} {pts[3][1]}Z" stroke="{INK}" stroke-opacity=".55" fill="none"/>')
    b.append(f'<path d="M{pts[5][0]} {pts[5][1]}L{pts[0][0]} {pts[0][1]}M{pts[5][0]} {pts[5][1]}L{pts[2][0]} {pts[2][1]}M{pts[5][0]} {pts[5][1]}L{pts[3][0]} {pts[3][1]}" stroke="{INK}" stroke-opacity=".35"/>')
    for x, y in pts:
        b.append(f'<circle cx="{x}" cy="{y}" r="4.2" fill="{INK}"/>')
    b.append(text(260, 56, "ACCESSIBILITY", 12, INK, weight="bold", spacing=2))
    b.append(text(260, 76, "COMPUTER VISION", 12, MUTE, spacing=2))
    write("udaan.svg", svg(W, H, "\n".join(b), "Udaan glyph", "Viewfinder corners around a small keypoint graph."))


def ecosentry():
    W, H = 480, 130
    b = [frame(W, H)]
    rng = random.Random(7)
    base = 66
    x = 40
    i = 0
    while x < 300:
        envelope = math.exp(-((x - 190) / 60) ** 2)
        amp = 6 + 38 * envelope * rng.uniform(.5, 1.0) + rng.uniform(0, 6)
        hot = 168 <= x <= 214
        col = ACC if hot else INK
        op = 1 if hot else .6
        b.append(f'<path d="M{x} {base-amp:.1f}V{base+amp:.1f}" stroke="{col}" stroke-opacity="{op}" stroke-width="3" stroke-linecap="round"/>')
        x += 8
        i += 1
    b.append(text(320, 56, "ENVIRONMENTAL", 12, INK, weight="bold", spacing=2))
    b.append(text(320, 76, "AUDIO SIGNALS", 12, MUTE, spacing=2))
    write("ecosentry.svg", svg(W, H, "\n".join(b), "EcoSentry glyph", "An audio waveform with one highlighted event."))


# --------------------------------------------------------------------------- ending
def ending():
    W, H = 1000, 240
    q = (850, 104)
    b = [frame(W, H)]
    b.append(text(44, 42, "END OF FIG. 01", 11, INK, spacing=2))
    b.append(
        f'<text x="40" y="136" font-family="{SERIF}" font-size="84" font-style="italic" fill="{INK}" '
        f'letter-spacing="-2">no further results<tspan fill="{ACC}">.</tspan></text>'
    )
    b.append(text(44, 178, "You read all of it. That makes us even.", 14, INK))
    b.append(text(44, 204, "Got a better query? You know where to find me.", 12, MUTE))

    for x, y in [(790, 62), (938, 74), (900, 168)]:
        b.append(f'<path d="M{q[0]} {q[1]}L{x} {y}" stroke="{ACC}" stroke-width="1.2" stroke-dasharray="5 5" fill="none">'
                 f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.4s" repeatCount="indefinite"/></path>')
        b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{INK}"/>')
    b.append(
        f'<circle cx="{q[0]}" cy="{q[1]}" r="7" fill="none" stroke="{ACC}" stroke-width="1.5">'
        f'<animate attributeName="r" values="7;34" dur="2.6s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0" dur="2.6s" repeatCount="indefinite"/></circle>'
    )
    b.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="7" fill="{ACC}"/>')
    b.append(text(q[0], 206, "q = what if…", 12, ACC, "middle", weight="bold"))
    write("ending.svg", svg(W, H, "\n".join(b), "No further results",
                            "The query point from the hero again, with its three results, and the words 'no further results'."))


if __name__ == "__main__":
    hero()
    section("sec-results.svg", "01", "RESULTS", "ranked by relevance, not by date")
    section("sec-toolkit.svg", "02", "TOOLKIT", "what's on the bench")
    method()
    mitra()
    udaan()
    ecosentry()
    ending()
