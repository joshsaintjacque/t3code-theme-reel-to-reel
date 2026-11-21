"""Build the Reel to Reel theme for T3 Code: reel-to-reel.json (+ SVG previews, + index.html).

Concept: a 70s hi-fi tape deck. Walnut cheeks (sidebar), dark vinyl panel (chat), brushed-aluminium
faceplate (header, bezels), amber backlit VU meters. While a turn runs the reels turn, the needles
bounce and an LED ladder climbs the header; when it ends the needles thump and settle.
"""
import json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
AMB = "#ffb52e"
DISPLAY = '"Futura","Avenir Next Condensed","Avenir Next","Century Gothic",ui-sans-serif,sans-serif'
MONO = 'ui-monospace,"SF Mono",Menlo,monospace'
FACE = 'Futura,Avenir,Optima,sans-serif'


def f(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s or "0"


def data_uri(svg):
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C")
    return 'url("data:image/svg+xml,' + out + '")'


# ------------------------------------------------------------------ textures
def walnut_svg(w=360, h=720, seed=11):
    """Walnut: long vertical fibres from stitched fractal noise, tinted brown."""
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
        f"<filter id='w' x='0' y='0' width='100%' height='100%'>"
        f"<feTurbulence type='fractalNoise' baseFrequency='0.16 0.007' numOctaves='4' seed='{seed}' stitchTiles='stitch'/>"
        "<feColorMatrix type='matrix' values='0 0 0 0 0.05  0 0 0 0 0.02  0 0 0 0 0.008  -3.4 0 0 0 1.75'/></filter>"
        "<rect width='100%' height='100%' filter='url(#w)'/></svg>")


def brush_svg(w=320, h=80, seed=4, hi=True):
    """Brushed metal: horizontal streaks, white-ish on dark."""
    a = "0.55 0 0 0 -0.2" if hi else "-1.2 0 0 0 0.75"
    col = "1 1 1" if hi else "0 0 0"
    r, g, b = col.split()
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
        "<filter id='b' x='0' y='0' width='100%' height='100%'>"
        f"<feTurbulence type='fractalNoise' baseFrequency='0.006 0.85' numOctaves='2' seed='{seed}' stitchTiles='stitch'/>"
        f"<feColorMatrix type='matrix' values='0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  {a}'/></filter>"
        "<rect width='100%' height='100%' filter='url(#b)'/></svg>")


def vinyl_svg(w=200, h=200):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
        "<filter id='v' x='0' y='0' width='100%' height='100%'>"
        "<feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='9' stitchTiles='stitch'/>"
        "<feColorMatrix type='matrix' values='0 0 0 0 1  0 0 0 0 0.9  0 0 0 0 0.75  0.22 0 0 0 -0.08'/></filter>"
        "<rect width='100%' height='100%' filter='url(#v)'/></svg>")


# ------------------------------------------------------------------ VU meters
MW, MH = 300, 190
PIVOT = (150, 172)
WIN = (12, 12, 276, 138)          # face window inside one meter tile (x, y, w, h)
REST = -49                         # needle rest pose: parked on the "20" tick
KICK = 13                          # degrees the needle is held up while a turn runs (done beat falls from here)


def pol(a_deg, r, pivot=PIVOT):
    a = math.radians(a_deg)
    return pivot[0] + r * math.sin(a), pivot[1] - r * math.cos(a)


def meter_face(ox, oy):
    """Backlit amber face with printed scale (drawn at offset)."""
    parts = []

    def arc(a0, a1, r, **kw):
        x0, y0 = pol(a0, r); x1, y1 = pol(a1, r)
        attrs = " ".join(f"{k.replace('_','-')}='{v}'" for k, v in kw.items())
        return f"<path d='M{f(x0)} {f(y0)}A{r} {r} 0 0 1 {f(x1)} {f(y1)}' fill='none' {attrs}/>"
    parts.append(arc(-50, 4, 128, stroke="#2a1604", stroke_width=1.6))
    parts.append(arc(4, 50, 128, stroke="#b02a16", stroke_width=6))
    parts.append(arc(4, 50, 137, stroke="#b02a16", stroke_width=1.2))
    for a in range(-50, 51, 5):
        major = a in (-50, -35, -25, -15, -5, 5, 20, 35, 50)
        r0, r1 = (116, 134) if major else (123, 134)
        x0, y0 = pol(a, r0); x1, y1 = pol(a, r1)
        col = "#b02a16" if a >= 4 else "#2a1604"
        parts.append(f"<path d='M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}' stroke='{col}' stroke-width='{2 if major else 1.1}'/>")
    labels = [(-50, "20"), (-35, "10"), (-25, "7"), (-15, "5"), (-5, "3"), (5, "0"), (20, "1"), (35, "2"), (50, "3")]
    for a, t in labels:
        x, y = pol(a, 100)
        col = "#b02a16" if a >= 5 else "#2a1604"
        parts.append(f"<text x='{f(x)}' y='{f(y+4)}' text-anchor='middle' font-size='13' font-weight='600' fill='{col}'>{t}</text>")
    parts.append("<text x='150' y='108' text-anchor='middle' font-size='30' font-weight='700' letter-spacing='6' fill='#2a1604' fill-opacity='.9'>VU</text>")
    parts.append("<text x='150' y='123' text-anchor='middle' font-size='8' letter-spacing='3' fill='#2a1604' fill-opacity='.7'>VOLUME UNITS</text>")
    return (f"<g transform='translate({ox} {oy})' font-family='{FACE}'>"
            "<rect x='12' y='12' width='276' height='138' rx='6' fill='url(#f)'/>"
            "<rect x='12' y='12' width='276' height='138' rx='6' fill='url(#t)'/>" + "".join(parts) + "</g>")


def meter_cover(i, ox, oy):
    """Same face gradient painted over everything beyond the scale arc, so a needle is cut off at the arc."""
    px, py = PIVOT
    R = 141
    win = "M18 12H282A6 6 0 0 1 288 18V144A6 6 0 0 1 282 150H18A6 6 0 0 1 12 144V18A6 6 0 0 1 18 12Z"
    circ = f"M{px-R} {py}a{R} {R} 0 1 0 {2*R} 0a{R} {R} 0 1 0 {-2*R} 0Z"
    return (f"<g transform='translate({ox} {oy})'><clipPath id='k{i}'><path clip-rule='evenodd' d='{win}{circ}'/></clipPath>"
            f"<g clip-path='url(#k{i})'><rect x='12' y='12' width='276' height='138' rx='6' fill='url(#f)'/>"
            "<rect x='12' y='12' width='276' height='138' rx='6' fill='url(#t)'/></g></g>")


def meter_bezel(ox, oy, label):
    outer = "M0 14A14 14 0 0 1 14 0H286A14 14 0 0 1 300 14V176A14 14 0 0 1 286 190H14A14 14 0 0 1 0 176Z"
    win = "M18 12H282A6 6 0 0 1 288 18V144A6 6 0 0 1 282 150H18A6 6 0 0 1 12 144V18A6 6 0 0 1 18 12Z"
    return (
        f"<g transform='translate({ox} {oy})' font-family='{FACE}'>"
        f"<path fill-rule='evenodd' fill='url(#s)' d='{outer}{win}'/>"
        f"<path d='{win}' fill='none' stroke='#1c1208' stroke-width='2.4' stroke-opacity='.75'/>"
        "<path d='M1 14A13 13 0 0 1 14 1H286' fill='none' stroke='#fff' stroke-opacity='.55'/>"
        "<path d='M116.6 150A40 40 0 0 1 183.4 150Z' fill='#17100a' stroke='#050302' stroke-width='1.2'/>"
        "<path d='M120 148.6A37 37 0 0 1 180 148.6' fill='none' stroke='#fff' stroke-opacity='.18'/>"
        "<circle cx='150' cy='172' r='15' fill='url(#c)' stroke='#1c1208' stroke-opacity='.7'/>"
        "<circle cx='150' cy='172' r='6' fill='#2a2620'/><path d='M150 166v12' stroke='#8a857a' stroke-width='1.5'/>"
        "<circle cx='24' cy='171' r='4.5' fill='url(#c)' stroke='#1c1208' stroke-opacity='.6'/><path d='M21 169l6 4' stroke='#3a352d'/>"
        "<circle cx='276' cy='171' r='4.5' fill='url(#c)' stroke='#1c1208' stroke-opacity='.6'/><path d='M273 173l6-4' stroke='#3a352d'/>"
        f"<text x='60' y='176' font-size='11' font-weight='600' letter-spacing='3' fill='#3a352d'>{label}</text>"
        "<text x='240' y='176' text-anchor='end' font-size='9' letter-spacing='2' fill='#3a352d' fill-opacity='.8'>dB</text>"
        "</g>")


DEFS = (
    "<defs>"
    "<radialGradient id='f' cx='.5' cy='.92' r='.95'><stop offset='0' stop-color='#ffeab8'/><stop offset='.5' stop-color='#fbc65c'/>"
    "<stop offset='.85' stop-color='#e39a1e'/><stop offset='1' stop-color='#b8700c'/></radialGradient>"
    "<linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.4'/><stop offset='.18' stop-color='#000' stop-opacity='0'/></linearGradient>"
    "<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#c9c6bc'/><stop offset='.5' stop-color='#9f9b90'/><stop offset='1' stop-color='#b5b1a6'/></linearGradient>"
    "<radialGradient id='c' cx='.35' cy='.3' r='.8'><stop offset='0' stop-color='#f2efe6'/><stop offset='1' stop-color='#8f8b80'/></radialGradient>"
    "</defs>")

SW, SH = MW, 2 * MH + 16
OFFS = [(0, 0), (0, MH + 16)]


def meter_svgs():
    face = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SH}'>{DEFS}" + "".join(meter_face(*o) for o in OFFS) + "</svg>"
    bezel = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SH}'>{DEFS}"
             + meter_bezel(*OFFS[0], "LEFT") + meter_bezel(*OFFS[1], "RIGHT") + "</svg>")
    cover = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SH}'>{DEFS}" + "".join(meter_cover(i, *o) for i, o in enumerate(OFFS)) + "</svg>"
    return face, bezel, cover


def needle(prop, oy, w=1.7, sh=1.0):
    """A solid needle: conic wedge, hard edges (no semi-transparent shoulders, which dash at small radii), plus a soft
    offset shadow on its clockwise side. Layer box is the face window, origin below it (the pivot cover hides the root)."""
    a = f(w / 2)
    return (f"conic-gradient(from calc(var({prop}) - {a}deg) at 50% {f(oy)}%,#1b0e04 0deg,#1b0e04 {f(w)}deg,"
            f"rgba(60,24,0,.24) {f(w)}deg,rgba(60,24,0,.24) {f(w+sh)}deg,transparent {f(w+sh)}deg,transparent 360deg)")


def lamp(h):
    c = f"color-mix(in srgb,#ff5a36 calc(clamp(0,var({h}),1)*100%),#4a1c0e)"
    return f"radial-gradient(circle closest-side,{c} 0,{c} 42%,transparent 100%)"


def meter_bg():
    face, bezel, cover = meter_svgs()
    W, H = SW, SH
    wx, wy, ww, wh = WIN
    layers = [data_uri(bezel) + " 0 0/100% 100% no-repeat"]
    L = 30
    for i, (ox, oy) in enumerate(OFFS):
        lx, ly = ox + 256, oy + 16
        layers.append(lamp(f"--h{i+1}") + f" {f(lx/(W-L)*100)}% {f(ly/(H-L)*100)}%/{f(L/W*100)}% {f(L/H*100)}% no-repeat")
    layers.append(data_uri(cover) + " 0 0/100% 100% no-repeat")
    oy_pct = (PIVOT[1] - wy) / wh * 100
    for i, (ox, oy) in enumerate(OFFS):
        px = (ox + wx) / (W - ww) * 100
        py = (oy + wy) / (H - wh) * 100
        layers.append(needle(f"--vu{i+1}", oy_pct) + f" {f(px)}% {f(py)}%/{f(ww/W*100)}% {f(wh/H*100)}% no-repeat")
    layers.append(data_uri(face) + " 0 0/100% 100% no-repeat")
    return ",".join(layers)


# ------------------------------------------------------------------ reel deck plate (left gutter)
PW, PH = 420, 250
RC = [(108, 102), (312, 102)]
RR = 92   # hole radius


def plate_path(w, h, r):
    return f"M{r} 0H{w-r}A{r} {r} 0 0 1 {w} {r}V{h-r}A{r} {r} 0 0 1 {w-r} {h}H{r}A{r} {r} 0 0 1 0 {h-r}V{r}A{r} {r} 0 0 1 {r} 0Z"


def hole(cx, cy, r):
    return f"M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0Z"


def brushed_lines(w, h, seed, n):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        y = rnd.random() * h
        x0 = rnd.random() * w * .5
        x1 = x0 + rnd.random() * w * .6 + w * .2
        col = "#fff" if rnd.random() > .45 else "#000"
        out.append(f"<path d='M{f(x0)} {f(y)}H{f(x1)}' stroke='{col}' stroke-opacity='{f(.05+rnd.random()*.12)}' stroke-width='{f(.6+rnd.random()*.8)}'/>")
    return "".join(out)


def deck_plate():
    """Aluminium faceplate with two round windows (reels show through), head block, tape guides and the tape path."""
    holes = "".join(hole(cx, cy, RR) for cx, cy in RC)
    d = plate_path(PW, PH, 12) + holes
    o = ["<defs>"
         "<linearGradient id='al' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#97928a'/><stop offset='.5' stop-color='#7d786f'/><stop offset='1' stop-color='#6f6b63'/></linearGradient>"
         "<linearGradient id='rm' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ebe8df'/><stop offset='.5' stop-color='#a29e93'/><stop offset='1' stop-color='#d4d0c5'/></linearGradient>"
         "<radialGradient id='h' cx='.35' cy='.3' r='.85'><stop offset='0' stop-color='#f0ede4'/><stop offset='1' stop-color='#85817a'/></radialGradient>"
         f"<clipPath id='pc'><path clip-rule='evenodd' d='{d}'/></clipPath></defs>",
         f"<path fill-rule='evenodd' fill='url(#al)' d='{d}'/>",
         f"<g clip-path='url(#pc)'>{brushed_lines(PW, PH, 5, 90)}</g>",
         "<path d='M1.5 12A10.5 10.5 0 0 1 12 1.5H408' fill='none' stroke='#fff' stroke-opacity='.6'/>",
         f"<path d='{plate_path(PW, PH, 12)}' fill='none' stroke='#16100a' stroke-opacity='.55'/>"]
    for cx, cy in RC:
        o.append(f"<circle cx='{cx}' cy='{cy}' r='{RR-6}' fill='none' stroke='url(#rm)' stroke-width='12'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='{RR+.5}' fill='none' stroke='#16100a' stroke-width='1.6' stroke-opacity='.8'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='{RR-12}' fill='none' stroke='#16100a' stroke-width='1.2' stroke-opacity='.7'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='28' fill='url(#h)' stroke='#16100a' stroke-opacity='.8' stroke-width='1.4'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='20' fill='none' stroke='#16100a' stroke-opacity='.35'/>")
        for k in range(3):
            a = math.radians(90 + k * 120)
            o.append(f"<circle cx='{f(cx+13*math.cos(a))}' cy='{f(cy-13*math.sin(a))}' r='4' fill='#1b140d'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='6' fill='#2a2620'/><path d='M{cx} {cy-6}v12' stroke='#9a958a' stroke-width='1.5'/>")
    # head cover, guides, tape path
    o.append("<rect x='184' y='203' width='52' height='41' rx='5' fill='#2a2620' stroke='#16100a'/>"
             "<rect x='186' y='205' width='48' height='8' rx='3' fill='url(#rm)'/>"
             "<rect x='194' y='225' width='7' height='13' rx='1.5' fill='#8f8b80'/><rect x='206.5' y='225' width='7' height='13' rx='1.5' fill='#6f6b61'/><rect x='219' y='225' width='7' height='13' rx='1.5' fill='#8f8b80'/>")
    o.append("<path d='M108 174L152 222H268L312 146' fill='none' stroke='#1c0f06' stroke-width='3.6' stroke-linejoin='round'/>"
             "<path d='M108 172.4L151 220.2H269L312 144.4' fill='none' stroke='#7a5434' stroke-width='.8' stroke-opacity='.75' stroke-linejoin='round'/>")
    for gx in (152, 268):
        o.append(f"<circle cx='{gx}' cy='222' r='8' fill='url(#h)' stroke='#16100a' stroke-width='1.2'/><circle cx='{gx}' cy='222' r='2.4' fill='#2a2620'/>")
    for sx, sy in ((11, 11), (409, 11), (11, 239), (409, 239)):
        o.append(f"<circle cx='{sx}' cy='{sy}' r='4.5' fill='url(#h)' stroke='#16100a' stroke-opacity='.6'/><path d='M{sx-3} {sy-2}l6 4' stroke='#3a352d'/>")
    o.append(f"<g font-family='{FACE}' fill='#17120d' font-size='9.5' letter-spacing='3'><text x='34' y='243'>SUPPLY</text><text x='386' y='243' text-anchor='end'>TAKE-UP</text></g>")
    return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>%s</svg>" % (PW, PH, "".join(o))


def reel_wells():
    """Under the plate: dark wells and tape packs (supply pack large, take-up small)."""
    o = ["<defs><radialGradient id='p' cx='.4' cy='.35' r='.8'><stop offset='0' stop-color='#6a4128'/><stop offset='1' stop-color='#2b180b'/></radialGradient></defs>"]
    for (cx, cy), rp in zip(RC, (72, 44)):
        o.append(f"<circle cx='{cx}' cy='{cy}' r='{RR}' fill='#120c07'/><circle cx='{cx}' cy='{cy}' r='{rp}' fill='url(#p)'/>")
        o.append(f"<g fill='none' stroke='#fff' stroke-opacity='.07'><circle cx='{cx}' cy='{cy}' r='{rp-10}'/><circle cx='{cx}' cy='{cy}' r='{rp-20}'/></g>")
    return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>%s</svg>" % (PW, PH, "".join(o))


SPOKE = "#4a463f"


def spoke_conic(expr):
    c = SPOKE
    return (f"repeating-conic-gradient(from calc({expr} - 17deg) at 50% 50%,transparent 0deg,transparent .4deg,{c} .9deg,{c} 33.1deg,"
            "transparent 33.6deg,transparent 120deg)")


RB = "var(--ra)*1.33333"   # take-up reel turns 4/3 as fast, so the loop stays seamless (4 x 120deg)


def deck_layers():
    d = RR * 2
    sz = f"{f(d/PW*100)}% {f(d/PH*100)}%"
    ys = f"{f((RC[0][1]-RR)/(PH-d)*100)}%"
    xl = f"{f((RC[0][0]-RR)/(PW-d)*100)}%"
    xr = f"{f((RC[1][0]-RR)/(PW-d)*100)}%"
    sw, sh, sy = 116, 4, 220
    strip = ("repeating-linear-gradient(90deg,rgba(255,226,170,.75) 0 3px,transparent 3px 12px) "
             f"calc(50% + var(--tp)) {f(sy/(PH-sh)*100)}%/{f(sw/PW*100)}% {f(sh/PH*100)}% repeat-x")
    return ",".join([
        strip,
        data_uri(deck_plate()) + " 0 0/100% 100% no-repeat",
        spoke_conic("var(--ra)") + f" {xl} {ys}/{sz} no-repeat",
        spoke_conic(RB) + f" {xr} {ys}/{sz} no-repeat",
        data_uri(reel_wells()) + " 0 0/100% 100% no-repeat",
    ])


# ------------------------------------------------------------------ narrow dock (sidebar foot): small, simplified, in flow
DW, DH = 200, 52
DREELS = [(28, 26), (76, 26)]
DWINS = [(112, 7), (154, 7)]
DWS = 38


def dock_plate():
    holes = "".join(hole(cx, cy, 21) for cx, cy in DREELS)
    wins = "".join(f"M{x+3} {y}H{x+DWS-3}A3 3 0 0 1 {x+DWS} {y+3}V{y+DWS-3}A3 3 0 0 1 {x+DWS-3} {y+DWS}H{x+3}A3 3 0 0 1 {x} {y+DWS-3}V{y+3}A3 3 0 0 1 {x+3} {y}Z" for x, y in DWINS)
    d = plate_path(DW, DH, 7) + holes + wins
    o = ["<defs><linearGradient id='al' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#98938a'/><stop offset='.55' stop-color='#7d786f'/><stop offset='1' stop-color='#6f6b63'/></linearGradient>"
         "<linearGradient id='rm' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#ebe8df'/><stop offset='1' stop-color='#8f8b80'/></linearGradient>"
         "<radialGradient id='h' cx='.35' cy='.3' r='.85'><stop offset='0' stop-color='#f0ede4'/><stop offset='1' stop-color='#85817a'/></radialGradient></defs>",
         f"<path fill-rule='evenodd' fill='url(#al)' d='{d}'/>",
         f"<path d='{plate_path(DW, DH, 7)}' fill='none' stroke='#16100a' stroke-opacity='.6'/>",
         "<path d='M1 7A6 6 0 0 1 7 1H193' fill='none' stroke='#fff' stroke-opacity='.5'/>"]
    for cx, cy in DREELS:
        o.append(f"<circle cx='{cx}' cy='{cy}' r='19.5' fill='none' stroke='url(#rm)' stroke-width='3.4'/><circle cx='{cx}' cy='{cy}' r='21.3' fill='none' stroke='#16100a' stroke-opacity='.8'/>")
        o.append(f"<circle cx='{cx}' cy='{cy}' r='7.5' fill='url(#h)' stroke='#16100a' stroke-opacity='.8'/><circle cx='{cx}' cy='{cy}' r='2' fill='#2a2620'/>")
    for x, y in DWINS:
        o.append(f"<rect x='{x}' y='{y}' width='{DWS}' height='{DWS}' rx='3' fill='none' stroke='#1c1208' stroke-width='1.6' stroke-opacity='.8'/>")
    o.append("<path d='M52 26H100' stroke='#16100a' stroke-opacity='0'/>")
    return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>%s</svg>" % (DW, DH, "".join(o))


def dock_wells():
    o = ["<defs><radialGradient id='f' cx='.5' cy='.9' r='1'><stop offset='0' stop-color='#ffeab8'/><stop offset='.55' stop-color='#f0b345'/><stop offset='1' stop-color='#b8700c'/></radialGradient>"
         "<radialGradient id='p' cx='.4' cy='.35' r='.8'><stop offset='0' stop-color='#6a4128'/><stop offset='1' stop-color='#2b180b'/></radialGradient></defs>"]
    for (cx, cy), rp in zip(DREELS, (16, 10)):
        o.append(f"<circle cx='{cx}' cy='{cy}' r='21' fill='#120c07'/><circle cx='{cx}' cy='{cy}' r='{rp}' fill='url(#p)'/>")
    for x, y in DWINS:
        pv = (x + DWS / 2, y + DWS + 9)
        o.append(f"<rect x='{x}' y='{y}' width='{DWS}' height='{DWS}' rx='3' fill='url(#f)'/>")
        for a in range(-45, 46, 15):
            x0, y0 = pol(a, 27, pv); x1, y1 = pol(a, 33, pv)
            o.append(f"<path d='M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}' stroke='{'#b02a16' if a > 0 else '#2a1604'}' stroke-width='1.2'/>")
        xa, ya = pol(5, 33, pv); xb, yb = pol(45, 33, pv)
        o.append(f"<path d='M{f(xa)} {f(ya)}A33 33 0 0 1 {f(xb)} {f(yb)}' fill='none' stroke='#b02a16' stroke-width='3'/>")
    return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>%s</svg>" % (DW, DH, "".join(o))


def dock_bg():
    d = 42
    sz = f"{f(d/DW*100)}% {f(d/DH*100)}%"
    ys = f"{f((DREELS[0][1]-21)/(DH-d)*100)}%"
    xl = f"{f((DREELS[0][0]-21)/(DW-d)*100)}%"
    xr = f"{f((DREELS[1][0]-21)/(DW-d)*100)}%"
    oy = (DWS + 9) / DWS * 100
    layers = [data_uri(dock_plate()) + " 0 0/100% 100% no-repeat"]
    for i, (x, y) in enumerate(DWINS):
        layers.append(needle(f"--vu{i+1}", oy, 3.2, 1.2) + f" {f(x/(DW-DWS)*100)}% {f(y/(DH-DWS)*100)}%/{f(DWS/DW*100)}% {f(DWS/DH*100)}% no-repeat")
    layers += [spoke_conic("var(--ra)") + f" {xl} {ys}/{sz} no-repeat",
               spoke_conic(RB) + f" {xr} {ys}/{sz} no-repeat",
               data_uri(dock_wells()) + " 0 0/100% 100% no-repeat"]
    return ",".join(layers)


# ------------------------------------------------------------------ motion data
def kf(name, prop, pts, loop_ease=True):
    """pts: list of (pct, angle). Needle ballistics: quick up, slower down. First and last point are the rest pose."""
    s = ""
    for i, (t, a) in enumerate(pts):
        nxt = pts[i + 1][1] if i + 1 < len(pts) else a
        e = "cubic-bezier(.16,.9,.3,1)" if nxt > a else "cubic-bezier(.5,0,.6,1)"
        s += f"{f(t)}%{{{prop}:{f(a)}deg;animation-timing-function:{e}}}"
    return f"@keyframes {name}{{{s}}}"


def kf_lvl(name, pts, steps):
    s = ""
    for t, a in pts:
        s += f"{f(t)}%{{--lvl:{f(max(6.25,min(100,(a-REST)/98*100)))}%;animation-timing-function:steps({steps})}}"
    return f"@keyframes {name}{{{s}}}"


# burst = lively 7s start; low = calm loop for long turns (rare peak); bg = a background thread stirs the right meter
BURST1 = [(0, -49), (7, 10), (14, -28), (21, 22), (28, -18), (36, 31), (44, -12), (52, 6), (60, -30), (68, -6), (77, -32), (87, -41), (100, -49)]
BURST2 = [(0, -49), (9, -4), (17, 25), (25, -24), (34, 14), (42, -20), (51, 34), (59, -10), (67, -26), (76, 2), (85, -36), (100, -49)]
LOW1 = [(0, -49), (9, -37), (20, -30), (31, -42), (42, -28), (53, -45), (62, -34), (70, -9), (76, -38), (86, -43), (100, -49)]
LOW2 = [(0, -49), (14, -38), (28, -31), (43, -42), (57, -27), (71, -41), (85, -34), (100, -49)]
BGL = [(0, -49), (18, -40), (36, -46), (52, -37), (70, -45), (100, -49)]

# ------------------------------------------------------------------ theme colours
colors = {
    "canvas": "#1b1511", "chrome": "#2a231e", "toolbar": "#3a3631", "toolbarForeground": "#f6ecd8",
    "toolbarBorder": "#15110d", "toolbarControl": "#4a463f", "toolbarControlForeground": "#f6ecd8",
    "toolbarControlHover": "#5b564d", "surface": "#241d18", "surfaceRaised": "#322921",
    "surfaceOverlay": "#2c241e", "text": "#f3e7cf", "textMuted": "#cdbb98", "border": "#4f4032",
    "input": "#6a5a49", "focus": AMB, "accent": AMB, "accentForeground": "#1b1206",
    "secondary": "#d4cfc4", "secondaryForeground": "#1f1b16", "muted": "#2e2620",
    "mutedForeground": "#c6b490", "placeholder": "#a2917a", "secondaryLabel": "#c2b08c",
    "iconMuted": "#bba988", "error": "#ff8f7d", "errorForeground": "#ffb8aa", "errorSurface": "#41201a",
    "warning": "#f2c14e", "warningForeground": "#ffd98a", "warningSurface": "#3d2d12",
    "update": "#8ed8a4", "updateForeground": "#b9edc7", "updateSurface": "#1c3526",
    "accentSurface": "#40290c", "accentSurfaceForeground": "#ffd488", "messageSurface": "#3d2517",
    "messageForeground": "#f8eedb", "messageAction": AMB, "messageActionForeground": "#1b1206",
    "messageActionHover": "#ffc85c", "codeBackground": "#14100c", "codeForeground": "#efe2c6",
    "searchMatchBackground": "#6e4c10", "searchMatchForeground": "#fff3d6",
    "searchMatchActiveBackground": AMB, "searchMatchActiveForeground": "#1b1206",
    "sidebar": "#2e1c10", "sidebarForeground": "#f6e9d0", "sidebarMutedForeground": "#d6bd93",
    "sidebarControlSurface": "#432818", "sidebarRowHover": "#4a2e1d", "sidebarRowActive": "#573520",
    "sidebarRowSelected": "#613c23", "sidebarBorder": "#1a0e07", "terminalBackground": "#110d0a",
    "terminalForeground": "#eddcbb", "terminalCursor": AMB, "terminalSelection": "#6b4a1a",
    "terminalScrollbar": "#5a4632", "terminalScrollbarHover": "#8a6a44",
}

BUSY = ('body:has([data-timeline-row-kind="working"])',
        'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')
NOTBUSY = ":not(:has([data-timeline-row-kind=\"working\"])):not(:has([data-thread-item] [aria-busy=\"true\"][aria-current]:not([aria-current=\"false\"])))"
ANYBG = 'has([data-thread-item] [aria-busy="true"])'


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


def bgonly(sel):
    return f"body:{ANYBG}{NOTBUSY} {sel}"


CONV = '[data-workspace-area="conversation"]'
SIDE = '[data-slot="sidebar-inner"]'
CW = "var(--chat-content-max-width,46rem)"

walnut = data_uri(walnut_svg())
walnut_s = data_uri(walnut_svg(260, 180, seed=5))
brush = data_uri(brush_svg())
brush_dark = data_uri(brush_svg(seed=8, hi=False))
vinyl = data_uri(vinyl_svg())

meter_layers = meter_bg()
deck_layers_css = deck_layers()
dock_layers_css = dock_bg()

# ---- state bundles: idle declarations, working declarations, background-thread declarations
EASE = "linear(0,.3 11%,.66 22%,.92 32%,1 40%,.9 46%,.74 53%,.7 55%,.78 60%,.92 66%,1 70%,.96 76%,.9 80%,.94 86%,1 92%,1)"   # falls to the stop, rebounds up off it, never goes below it
# Idle: needles rest on the 20 tick. --h1/--h2 are "held" levels (1 while a turn runs); when the turn ends they
# spring back to 0 through a registered-property transition, so the needle falls from where it was, with overshoot,
# and nothing replays on mount or thread switch.
MET_IDLE = (f"--h1:0;--h2:0;--vu1:calc({REST}deg + var(--h1)*{KICK}deg);--vu2:calc({REST}deg + var(--h2)*{KICK}deg);"
            f"transition:--h1 1.9s {EASE},--h2 2.3s {EASE};")
A_MET = "vu-b1 7s 1,vu-l1 12s linear 7s infinite,vu-b2 7s 1,vu-l2 8s linear 7s infinite"
A_BG = "vu-bg 8s linear infinite"
A_REEL = lambda st: f"reel-a 8s linear infinite {st},tape-run .8s steps(4) infinite {st}"
MET_WORK = f"--h1:1;--h2:1;transition:none;animation:{A_MET};"
MET_BG = f"--h2:1;transition:none;animation:{A_BG};"
REEL_IDLE = f"--tp:0px;animation:{A_REEL('paused')};"
REEL_WORK = f"animation:{A_REEL('running')};"
DOCK_WORK = f"--h1:1;--h2:1;transition:none;animation:{A_MET},{A_REEL('running')};"
DOCK_BG = f"--h2:1;transition:none;animation:{A_BG},{A_REEL('paused')};"
LED_IDLE = "--hh:0;--lvl:calc(6.25% + var(--hh)*36%);transition:--hh 1.1s steps(8);"
LED_WORK = "--hh:1;transition:none;animation:lvl-b 7s 1,lvl-l 8s linear 7s infinite;"

props = (
    '@property --vu1{syntax:"<angle>";inherits:false;initial-value:-49deg}'
    '@property --vu2{syntax:"<angle>";inherits:false;initial-value:-49deg}'
    '@property --h1{syntax:"<number>";inherits:false;initial-value:0}'
    '@property --h2{syntax:"<number>";inherits:false;initial-value:0}'
    '@property --hh{syntax:"<number>";inherits:false;initial-value:0}'
    '@property --ra{syntax:"<angle>";inherits:false;initial-value:0deg}'
    '@property --tp{syntax:"<length>";inherits:false;initial-value:0px}'
    '@property --lvl{syntax:"<percentage>";inherits:false;initial-value:6.25%}'
)

keyframes = (
    kf("vu-b1", "--vu1", BURST1) + kf("vu-b2", "--vu2", BURST2)
    + kf("vu-l1", "--vu1", LOW1) + kf("vu-l2", "--vu2", LOW2) + kf("vu-bg", "--vu2", BGL)
    + kf_lvl("lvl-b", BURST1, 6) + kf_lvl("lvl-l", LOW2, 4)
    + "@keyframes reel-a{to{--ra:-360deg}}"
    + "@keyframes tape-run{to{--tp:12px}}"
    + "@keyframes perf{to{background-position:12px 100%}}"
    + "@keyframes tape{to{background-position:5px 8px}}"
)

css = props + keyframes

# ---- sidebar: walnut cheek, silkscreen type (no forced position/overflow/isolation) --------
css += (
    f"{SIDE}{{background:linear-gradient(90deg,rgba(0,0,0,.34),transparent 9%,transparent 88%,rgba(0,0,0,.4)),"
    f"linear-gradient(180deg,rgba(255,196,120,.07),transparent 30%,rgba(0,0,0,.28)),{walnut} 0 0/360px 720px,#6a3f22!important;"
    f"font-family:{DISPLAY};letter-spacing:.025em}}"
    "[data-slot=\"sidebar\"]{border-right:1px solid #120905!important;box-shadow:inset -1px 0 0 rgba(255,214,160,.14)}"
    "[data-slot=\"project-monogram\"]{background:linear-gradient(145deg,#ece9e0,#9a968b)!important;color:#2a2418!important;"
    f"border:1px solid #1c1208;border-radius:4px!important;font-family:{DISPLAY};font-weight:700;box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 1px 0 rgba(0,0,0,.5)}}"
)

# ---- conversation panel: dark vinyl + gutter instruments ------------------
# position:relative on the conversation area is forced on purpose: the two gutter instruments are absolutely placed
# pseudo-elements so their animated custom properties repaint ~300px boxes, never the whole conversation background.
css += (
    f"{CONV}{{position:relative;"
    f"--g:calc((100% - {CW})/2);"
    "--pw:clamp(0px,calc((var(--g) - 232px)*1000),min(320px,calc(var(--g) - 64px)));"
    "--mw:clamp(0px,calc((var(--g) - 232px)*1000),min(300px,calc(var(--g) - 56px)));"
    f"background:radial-gradient(ellipse at 50% 30%,transparent 35%,rgba(0,0,0,.4)),{vinyl} 0 0/200px 200px,#1b1511!important}}"
    f"{CONV}::before{{content:\"\";position:absolute;pointer-events:none;left:calc((var(--g) - var(--pw))/2);top:50%;transform:translateY(-50%);"
    f"width:var(--pw);aspect-ratio:{PW}/{PH};border-radius:2.9%/4.8%;"
    f"background:{deck_layers_css};{REEL_IDLE}}}"
    f"{CONV}::after{{content:\"\";position:absolute;pointer-events:none;right:calc((var(--g) - var(--mw))/2);top:50%;transform:translateY(-50%);"
    f"width:var(--mw);aspect-ratio:{SW}/{SH};border-radius:4.7%/3.5%;"
    f"background:{meter_layers};{MET_IDLE}}}"
    + bgonly(f"{CONV}::after") + f"{{{MET_BG}}}"
    + busy(f"{CONV}::before") + f"{{{REEL_WORK}}}"
    + busy(f"{CONV}::after") + f"{{{MET_WORK}}}"
    # reading-column scrim so no art or texture ever sits behind text
    + f"{CONV} .messages-timeline-scroll{{background:linear-gradient(90deg,transparent calc(50% - {CW}/2 - 96px),rgba(24,18,14,.93) calc(50% - {CW}/2 - 14px),"
    f"rgba(24,18,14,.93) calc(50% + {CW}/2 + 14px),transparent calc(50% + {CW}/2 + 96px))!important}}"
)

# ---- narrow: gutters give way to a small in-flow dock under the sidebar's Settings row ---------
# In flow means nothing can ever sit behind thread text, however long the list is.
css += (
    "@media (max-width:1459px){"
    f"{CONV}::before,{CONV}::after{{display:none!important}}"
    f"{SIDE}::after{{content:\"\";display:block;flex:none;width:min(100%,224px);aspect-ratio:{DW}/{DH};margin:6px auto 0;border-radius:4px;"
    f"background:{dock_layers_css};{MET_IDLE}{REEL_IDLE}}}"
    + bgonly(f"{SIDE}::after") + f"{{{DOCK_BG}}}"
    + busy(f"{SIDE}::after") + f"{{{DOCK_WORK}}}"
    + "}"
)

# ---- header: brushed aluminium faceplate with a 16-segment LED ladder at the right ----------
LEDW = 128
SEG = f"repeating-linear-gradient(90deg,transparent 0 6px,#150f0a 6px 8px) right 150px center/{LEDW}px 6px no-repeat"
LIT = f"linear-gradient(90deg,{AMB} var(--lvl),#3b2a12 var(--lvl)) right 150px center/{LEDW}px 6px no-repeat"
css += (
    "[data-chat-header]{"
    f"background:{SEG},{LIT},{brush} 0 0/320px 80px,linear-gradient(180deg,#4c4842,#3a3631 55%,#302d29)!important;"
    "border-bottom:1px solid #120d09!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.14);"
    f"font-family:{DISPLAY};letter-spacing:.05em;{LED_IDLE}}}"
    + busy("[data-chat-header]") + f"{{{LED_WORK}}}"
)

# ---- thread rows ----------------------------------------------------------
css += (
    "[data-thread-item]{border-radius:8px;transition:box-shadow .2s}"
    "[data-thread-item]:hover{box-shadow:inset 3px 0 0 rgba(212,207,196,.6)}"
    f"[data-thread-item] [aria-current]:not([aria-current=\"false\"]){{box-shadow:inset 3px 0 0 {AMB}}}"
    f"[data-thread-item] [aria-busy=\"true\"]{{background-image:linear-gradient(180deg,{AMB} 50%,transparent 0);background-size:3px 8px;"
    "background-repeat:repeat-y;background-position:5px 0;animation:tape 1s steps(4) infinite}"
    "[data-timeline-row-kind=\"working\"]{color:#ffc65c;background-image:radial-gradient(circle at 50% 50%,#ffb52e 1.3px,transparent 1.8px);"
    "background-size:12px 5px;background-repeat:repeat-x;background-position:0 100%;animation:perf 1.2s steps(6) infinite;padding-bottom:6px}"
    # work rows read like lines on a tape log
    f"[data-timeline-row-kind=\"work\"]{{font-family:{DISPLAY};font-size:12.5px;letter-spacing:.03em;border-left:2px solid rgba(255,181,46,.32);padding-left:12px}}"
)

# ---- messages -------------------------------------------------------------
css += (
    f"[data-user-message-bubble]{{background:linear-gradient(180deg,rgba(255,200,140,.08),transparent 50%),{walnut_s} 0 0/260px 180px,#3d2517!important;"
    "border:1px solid #6f4a2e!important;border-radius:10px!important;box-shadow:inset 0 1px 0 rgba(255,225,180,.16),0 1px 0 rgba(0,0,0,.5)}"
    f".chat-markdown :is(h1,h2,h3,h4){{font-family:{DISPLAY};letter-spacing:.04em;text-transform:uppercase;font-weight:600}}"
    ".chat-markdown :is(h1,h2,h3) code{text-transform:none}"
    ".chat-markdown :is(h1,h2){border-bottom:1px solid rgba(205,187,152,.28);padding-bottom:.25em;box-shadow:0 2px 0 -1px rgba(0,0,0,.6)}"
    ".chat-markdown a{color:#ffc65c!important;text-decoration-style:dotted;text-underline-offset:3px}"
    f".chat-markdown :not(pre)>code{{font-family:{MONO};color:#ffd68a;background:rgba(255,181,46,.1);border:1px solid rgba(255,181,46,.18);padding:.05em .32em;border-radius:4px}}"
    f".chat-markdown-codeblock{{font-family:{MONO};background-color:#14100c!important;"
    f"background-image:radial-gradient(circle at 50% 50%,#ffb52e 1px,transparent 1.5px),{brush},linear-gradient(180deg,#a8a398,#7d786f)!important;"
    "background-size:12px 6px,320px 6px,100% 6px!important;background-repeat:repeat-x,repeat-x,no-repeat!important;background-position:0 0!important;background-origin:border-box!important;"
    "border:1px solid #3e3226!important;border-top:6px solid #7d786f!important;"
    "border-radius:6px!important;box-shadow:inset 0 10px 14px -12px rgba(0,0,0,.8)}"
    ".chat-markdown blockquote{border-left:3px solid #ffb52e;background:rgba(255,181,46,.07);padding:.4em 1em;margin-left:0;border-radius:0 6px 6px 0;color:#e8d8b8}"
    f".chat-markdown table{{border-collapse:collapse;border:1px solid #4f4032}}"
    f".chat-markdown th{{background:#3a3631;color:#f6ecd8;font-family:{DISPLAY};text-transform:uppercase;letter-spacing:.1em;font-size:.82em;border:1px solid #14100c;padding:.4em .8em}}"
    ".chat-markdown td{border:1px solid #4f4032;padding:.4em .8em}.chat-markdown tr:nth-child(even) td{background:rgba(255,200,140,.04)}"
    ".chat-markdown hr{border:0;height:6px;background:radial-gradient(circle at 50% 50%,#ffb52e 1.3px,transparent 1.8px) 0 0/12px 6px repeat-x;opacity:.55;margin:1.4em 0}"
    ".chat-markdown li::marker{color:#ffb52e}"
)

# ---- composer: recessed deck slot with aluminium bezel ---------------------
css += (
    "[data-slot=\"composer-host\"]{background:linear-gradient(#201914,#201914) padding-box,linear-gradient(180deg,#c4bfb3,#8a857b 45%,#5d584f) border-box!important;"
    "border:2px solid transparent!important;border-radius:10px!important;"
    "box-shadow:inset 0 2px 5px rgba(0,0,0,.6),0 1px 0 rgba(255,255,255,.08);transition:box-shadow .3s}"
    f"[data-slot=\"composer-host\"]:focus-within{{background:linear-gradient(#201914,#201914) padding-box,linear-gradient(180deg,#ffd27a,{AMB} 50%,#c98512) border-box!important;"
    "box-shadow:inset 0 2px 5px rgba(0,0,0,.6),0 0 0 3px rgba(255,181,46,.16)}"
    "[data-slot=\"composer-host\"] :focus-visible,.composer-tiptap:focus-visible{outline:none!important}"
)

# ---- controls: deck keys, switches, inputs ---------------------------------
KEY = "[data-slot=\"button\"]:not(:disabled)"
css += (
    "[data-slot=\"button\"],[data-slot=\"input\"],[data-slot=\"select-trigger\"]{border-radius:8px!important}"
    "[data-slot=\"button\"]{box-shadow:0 1px 0 rgba(0,0,0,.35);transition:box-shadow .12s,background-color .15s}"
    f"{KEY}:active{{box-shadow:inset 0 1px 3px rgba(0,0,0,.5)}}"
    "[data-slot=\"input\"],[data-slot=\"select-trigger\"]{box-shadow:inset 0 2px 4px rgba(0,0,0,.45),0 1px 0 rgba(255,255,255,.08)}"
    "[data-slot=\"switch\"]{border-radius:6px!important;background:#2a231e!important;box-shadow:inset 0 2px 4px rgba(0,0,0,.6),0 1px 0 rgba(255,255,255,.1);border:1px solid #6d655a}"
    f"[data-slot=\"switch\"][aria-checked=\"true\"]{{background:{AMB}!important;border-color:#8a5a0c}}"
    "[data-slot=\"switch\"]>*{background:linear-gradient(180deg,#f2efe6,#9c988d)!important;border-radius:4px!important;box-shadow:0 1px 2px rgba(0,0,0,.6)}"
    f"[data-slot=\"button\"]:focus-visible,[data-slot=\"input\"]:focus-visible,[data-slot=\"select-trigger\"]:focus-visible,[data-slot=\"switch\"]:focus-visible{{outline:2px solid {AMB};outline-offset:2px}}"
    "svg.lucide{stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}"
    "::selection{background:rgba(255,181,46,.34)}"
)

# ---- popups: aluminium faceplate edge on walnut-dark bodies ----------------
css += (
    "[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{border:1px solid #6d655a!important;border-top:5px solid #a8a398!important;"
    "border-radius:10px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 12px 30px rgba(0,0,0,.5)!important;"
    f"background-image:linear-gradient(180deg,rgba(255,200,140,.05),transparent 40%),{walnut_s}!important;background-size:auto,260px 180px!important}}"
    f"[data-slot=\"dialog-popup\"] :is(h1,h2,h3){{font-family:{DISPLAY};text-transform:uppercase;letter-spacing:.1em}}"
    "[data-slot=\"tooltip-popup\"]{background:#d9d4c8!important;color:#1d1710!important;border:1px solid #8f8a80!important;border-radius:6px!important;"
    f"font-family:{DISPLAY};letter-spacing:.04em}}"
)

# ---- panels: details card, terminal drawer, settings ---------------------
css += (
    "[data-thread-details-card]{border:1px solid #6d655a!important;border-top:4px solid #a8a398!important;border-radius:10px!important;"
    "box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 10px 24px rgba(0,0,0,.45)}"
    "[data-thread-terminal-drawer]{border-top:4px solid #8f8a80!important;box-shadow:0 -10px 24px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.14)}"
    f"[data-settings-page-scroll]{{background:{vinyl} 0 0/200px 200px,#1b1511}}"
    f"[data-settings-page-scroll] :is(h1,h2,h3){{font-family:{DISPLAY};text-transform:uppercase;letter-spacing:.1em}}"
)

# ---- scrollbars: aluminium thumb in a recessed track ------------------------
css += (
    "::-webkit-scrollbar-track,[data-slot=\"scroll-area-scrollbar\"]{background:rgba(0,0,0,.32)!important;box-shadow:inset 1px 0 0 rgba(0,0,0,.5)}"
    "::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{background:linear-gradient(90deg,#8b8579,#5f5a50)!important;border-radius:4px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.3)}"
    "::-webkit-scrollbar-thumb:hover{background:linear-gradient(90deg,#ffc65c,#d99620)!important}"
)

# ---- reduced motion: freeze to a still that still shows state -------------------
# idle = the true rest pose (needles on the stop, lamps out); working / background-only get their own held poses
css += (
    "@media (prefers-reduced-motion:reduce){"
    f"{CONV}::before,{CONV}::after,{SIDE}::after,[data-chat-header],[data-timeline-row-kind],[data-thread-item] [aria-busy]{{animation:none!important;transition:none!important}}"
    f"{CONV}::before,{SIDE}::after{{--ra:20deg!important;--tp:0px!important}}"
    + ",".join(busy(x) for x in (f"{CONV}::after", f"{SIDE}::after")) + "{--vu1:-30deg!important;--vu2:-37deg!important;--h1:1!important;--h2:1!important}"
    + ",".join(bgonly(x) for x in (f"{CONV}::after", f"{SIDE}::after")) + "{--vu2:-40deg!important;--h2:1!important}"
    + busy("[data-chat-header]") + "{--lvl:38%!important}"
    + "}"
)

theme = {"version": 1, "id": "reel-to-reel", "name": "Reel to Reel", "appearance": "dark",
         "accent": AMB, "canvas": "#1b1511", "colors": colors, "css": css}

# ------------------------------------------------------------------ landing page
SITE = "https://joshsaintjacque.github.io/t3code-theme-reel-to-reel/"
REPO = "https://github.com/joshsaintjacque/t3code-theme-reel-to-reel"
SLUG = "reel-to-reel"

PALETTE = [  # (role, label, note)
    ("canvas", "Canvas", "chat panel"), ("sidebar", "Sidebar", "walnut cheek"), ("toolbar", "Toolbar", "brushed faceplate"),
    ("messageSurface", "Message", "your bubble"), ("codeBackground", "Code", "slab"), ("surface", "Composer", "recessed slot"),
    ("text", "Text", "cream"), ("textMuted", "Muted", "aged cream"), ("accent", "Accent", "amber, for things that need you"),
    ("secondary", "Aluminium", "bezels and keys"), ("update", "Update", "VU green"), ("warning", "Warning", "lamp yellow"),
    ("error", "Error", "peak red"), ("border", "Border", "walnut line"),
]


def palette_rows():
    out = []
    for role, label, note in PALETTE:
        h = colors[role]
        out.append(f'    <button type="button" data-hex="{h}" aria-label="Copy {label} {h}"><span class="sw" style="background:{h}"></span>'
                   f'<span class="nm">{label}<small>{note}</small></span><span class="hx">{h}</span></button>')
    return "\n".join(out)


def deck_css():
    return (props + keyframes
            + f".deck-reels{{aspect-ratio:{PW}/{PH};border-radius:2.9%/4.8%;background:{deck_layers_css};{REEL_IDLE}}}"
            + f".deck.on .deck-reels{{{REEL_WORK}}}"
            + f".deck-meters{{aspect-ratio:{SW}/{SH};border-radius:4.7%/3.5%;background:{meter_layers};{MET_IDLE}}}"
            + f".deck.on .deck-meters{{{MET_WORK}}}"
            + f".deck-led{{width:128px;max-width:100%;height:6px;background:{SEG.replace('right 150px center/'+str(LEDW)+'px 6px','0 0/100% 6px')},{LIT.replace('right 150px center/'+str(LEDW)+'px 6px','0 0/100% 6px')};{LED_IDLE}}}"
            + f".deck.on .deck-led{{{LED_WORK}}}")


def render_index():
    t = open(os.path.join(HERE, "index.template.html")).read()
    rep = {"{{DECK_CSS}}": deck_css(), "{{PALETTE_ROWS}}": palette_rows(), "{{SITE}}": SITE, "{{REPO}}": REPO, "{{SLUG}}": SLUG,
           "{{WALNUT}}": walnut, "{{BRUSH}}": brush, "{{BRUSH_DK}}": data_uri(brush_svg(hi=True, seed=9)), "{{VINYL}}": vinyl}
    for k, v in rep.items():
        t = t.replace(k, v)
    return t


def render_og():
    return ("<!doctype html><meta charset='utf-8'><style>*{box-sizing:border-box}html,body{margin:0}"
            f"body{{width:1200px;height:630px;overflow:hidden;position:relative;font-family:{DISPLAY};color:#f3e7cf;background:#1b1511}}"
            f".cheek{{position:absolute;top:0;bottom:0;width:56px;background:linear-gradient(90deg,rgba(0,0,0,.4),transparent 50%),{walnut} 0 0/360px 720px,#6a3f22;z-index:3}}"
            ".cheek.l{left:0;box-shadow:2px 0 14px rgba(0,0,0,.6)}.cheek.r{right:0;transform:scaleX(-1);box-shadow:2px 0 14px rgba(0,0,0,.6)}"
            f".panel{{position:absolute;left:0;right:0;top:0;bottom:0;background:radial-gradient(ellipse at 40% 40%,transparent 30%,rgba(0,0,0,.5)),{vinyl} 0 0/200px 200px,#1b1511}}"
            f".bar{{position:absolute;left:56px;right:56px;top:0;height:46px;border-bottom:1px solid #120d09;"
            f"background:{SEG.replace('right 150px center/'+str(LEDW)+'px 6px','right 40px center/'+str(LEDW)+'px 6px')},{LIT.replace('right 150px center/'+str(LEDW)+'px 6px','right 40px center/'+str(LEDW)+'px 6px').replace('var(--lvl)','56%')},{brush} 0 0/320px 80px,linear-gradient(180deg,#4c4842,#3a3631 55%,#302d29)}}"
            ".t{position:absolute;left:112px;top:132px}.k{font:600 18px/1 "+DISPLAY+";letter-spacing:.32em;color:#cdbb98;text-transform:uppercase}"
            ".h{font:700 112px/.92 "+DISPLAY+";letter-spacing:.04em;text-transform:uppercase;margin:22px 0 0}.h i{display:block;font:italic 400 50px/1 Georgia,serif;color:#ffb52e;text-transform:none;letter-spacing:0;margin:8px 0 8px 10px}"
            ".s{font:400 25px/1.4 "+DISPLAY+";color:#cdbb98;margin-top:24px;max-width:440px}"
            f".reels{{position:absolute;left:585px;top:336px;width:300px;aspect-ratio:{PW}/{PH};border-radius:2.9%/4.8%;--ra:25deg;--tp:0px;background:{deck_layers_css}}}"
            f".meters{{position:absolute;left:930px;top:104px;width:190px;aspect-ratio:{SW}/{SH};border-radius:4.7%/3.5%;--vu1:-42deg;--vu2:40deg;--h1:1;--h2:1;background:{meter_layers}}}"
            f"{props}</style>"
            "<div class=panel></div><div class='cheek l'></div><div class='cheek r'></div><div class=bar></div>"
            "<div class=t><div class=k>A theme for T3 Code</div><div class=h>Reel<i>to</i>Reel</div><div class=s>Your agent runs the tape. The meters tell you how hard.</div></div>"
            "<div class=meters></div><div class=reels></div>")


if __name__ == "__main__":
    with open(os.path.join(ROOT, "reel-to-reel.json"), "w") as fh:
        json.dump(theme, fh, ensure_ascii=False)
    print("css chars:", len(css))
    os.makedirs(os.path.join(ROOT, "assets", "svg"), exist_ok=True)
    face, bezel, cover = meter_svgs()
    for n, s in (("meters-face", face), ("meters-bezel", bezel), ("deck-plate", deck_plate()), ("deck-wells", reel_wells()), ("dock-plate", dock_plate())):
        with open(os.path.join(ROOT, "assets", "svg", n + ".svg"), "w") as fh:
            fh.write(s)
    with open(os.path.join(ROOT, "index.html"), "w") as fh:
        fh.write(render_index())
    with open(os.path.join(HERE, "..", "..", "work", "og.reel.html"), "w") as fh:
        fh.write(render_og())
