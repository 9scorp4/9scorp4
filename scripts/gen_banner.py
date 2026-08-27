"""Garden banner v4 — designed, not scribbled.

Above the soil line: fern fronds (curved rachis + tapering pinnae), grass
blades, gold seed stalks. Below: roots as circuit traces with pads and a
data bus carrying a moving pulse. Palette from the profile stats card.
"""
import math
import sys

W, H = 900, 230
SOIL = 180
DARK = len(sys.argv) > 1 and sys.argv[1] == "dark"
if DARK:
    CREAM = "#151b14"        # background (green-tinted near-black); also pad fill
    MOSS = "#7aa886"
    MOSS_LIGHT = "#5f8a6b"
    BROWN = "#d9c9a0"        # soil line + title, warm cream on dark
    GOLD = "#d9a441"
else:
    CREAM = "#efe2c2"
    MOSS = "#2d5a3d"
    MOSS_LIGHT = "#4a7a58"
    BROWN = "#3d2f1a"
    GOLD = "#c08820"

elems = []  # svg element strings, painted in order


def qpoint(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def qtangent(p0, p1, p2, t):
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    n = math.hypot(dx, dy) or 1
    return (dx / n, dy / n)


def qlength(p0, p1, p2, n=24):
    pts = [qpoint(p0, p1, p2, i / n) for i in range(n + 1)]
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(n))


def stroke(d, color, width, length, delay, dur, opacity=1.0, cap="round"):
    elems.append(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="{cap}" stroke-linejoin="round" opacity="{opacity}" '
        f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}" '
        f'style="animation:draw {dur:.2f}s ease-out {delay:.2f}s both"/>'
    )


def rot(vx, vy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (vx * c - vy * s, vx * s + vy * c)


def frond(bx, height, lean, delay, n_pinnae=16, color=MOSS):
    p0 = (bx, SOIL)
    p2 = (bx + lean, SOIL - height)
    p1 = (bx + lean * 0.15, SOIL - height * 0.55)
    rlen = qlength(p0, p1, p2)
    rdur = rlen / 90.0
    d = f"M{p0[0]:.1f},{p0[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    stroke(d, color, 1.8, rlen, delay, rdur)
    max_len = height * 0.30
    for i in range(n_pinnae):
        t = 0.16 + 0.80 * i / (n_pinnae - 1)
        px, py = qpoint(p0, p1, p2, t)
        tx, ty = qtangent(p0, p1, p2, t)
        side = 1 if i % 2 == 0 else -1
        taper = (1 - t) ** 0.9 * min(1.0, (t - 0.05) / 0.25)
        plen = max_len * taper
        if plen < 3:
            continue
        dx, dy = rot(tx, ty, side * math.radians(62))
        ex, ey = px + dx * plen, py + dy * plen
        cx_, cy_ = (px + dx * plen * 0.5 + tx * plen * 0.30,
                    py + dy * plen * 0.5 + ty * plen * 0.30)
        pd = f"M{px:.1f},{py:.1f} Q{cx_:.1f},{cy_:.1f} {ex:.1f},{ey:.1f}"
        plength = qlength((px, py), (cx_, cy_), (ex, ey))
        pdelay = delay + rdur * t + 0.05
        stroke(pd, color, 1.1, plength, pdelay, 0.4)


def grass(bx, height, lean, delay, color=MOSS_LIGHT):
    p0 = (bx, SOIL)
    p2 = (bx + lean, SOIL - height)
    p1 = (bx + lean * 0.1, SOIL - height * 0.6)
    L = qlength(p0, p1, p2)
    d = f"M{p0[0]:.1f},{p0[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    stroke(d, color, 1.4, L, delay, L / 80.0)


def seed_stalk(bx, height, lean, delay):
    p0 = (bx, SOIL)
    p2 = (bx + lean, SOIL - height)
    p1 = (bx + lean * 0.2, SOIL - height * 0.5)
    L = qlength(p0, p1, p2)
    dur = L / 90.0
    d = f"M{p0[0]:.1f},{p0[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    stroke(d, MOSS, 1.3, L, delay, dur)
    bloom_delay = delay + dur
    elems.append(
        f'<circle cx="{p2[0]:.1f}" cy="{p2[1]:.1f}" r="4.5" fill="{GOLD}" '
        f'style="animation:bloom .6s ease-out {bloom_delay:.2f}s both,'
        f'breathe 5s ease-in-out {bloom_delay + 1:.2f}s infinite"/>'
    )
    elems.append(
        f'<circle cx="{p2[0]:.1f}" cy="{p2[1]:.1f}" r="8" fill="none" '
        f'stroke="{GOLD}" stroke-width="0.8" '
        f'style="animation:halo .8s ease-out {bloom_delay + 0.2:.2f}s both,'
        f'breathe 5s ease-in-out {bloom_delay + 1.5:.2f}s infinite"/>'
    )


def root_trace(bx, delay, jog, run, pad=True):
    """Circuit-style root: down, 45° jog, horizontal run, end pad."""
    y1 = SOIL + 6 + jog * 0.4
    xj = bx + (8 if run > 0 else -8)
    y2 = y1 + 8
    xe = xj + run
    d = (f"M{bx:.1f},{SOIL + 1} L{bx:.1f},{y1:.1f} "
         f"L{xj:.1f},{y2:.1f} L{xe:.1f},{y2:.1f}")
    L = (y1 - SOIL - 1) + math.hypot(xj - bx, y2 - y1) + abs(xe - xj)
    stroke(d, GOLD, 1.0, L, delay, L / 120.0, opacity=0.55, cap="square")
    if pad:
        elems.append(
            f'<circle cx="{xe:.1f}" cy="{y2:.1f}" r="2.4" fill="{CREAM}" '
            f'stroke="{GOLD}" stroke-width="1" opacity="0" '
            f'style="animation:fadein .4s ease-out {delay + L / 120.0:.2f}s both"/>'
        )


# ---- composition ----------------------------------------------------------
# left-weighted plant cluster; right third stays open for the title

frond(80, 150, -22, 0.9)
frond(148, 175, 28, 0.5, n_pinnae=18)
frond(215, 115, 42, 1.4, n_pinnae=13, color=MOSS_LIGHT)
grass(115, 70, 14, 1.8)
grass(185, 55, -10, 2.1)

seed_stalk(300, 105, 18, 1.2)
frond(370, 160, -24, 0.7, n_pinnae=17)
grass(340, 60, -12, 2.3)

frond(475, 130, 30, 1.1, n_pinnae=14)
seed_stalk(560, 140, -14, 0.6)
frond(625, 95, 20, 1.6, n_pinnae=11, color=MOSS_LIGHT)
grass(600, 50, 10, 2.5)

grass(835, 45, -8, 2.7)   # small accent under the title, right edge
grass(858, 32, 6, 2.9)

# stubble: short arcs along the soil line
for sx, sh, sl in [(55, 12, 5), (250, 10, -4), (415, 13, 6), (520, 9, -5),
                   (665, 11, 4), (720, 8, -3), (770, 10, 5)]:
    grass(sx, sh, sl, 2.0 + sx / 900.0, color=MOSS_LIGHT)

# ---- soil line ------------------------------------------------------------
elems.append(
    f'<line x1="18" y1="{SOIL}" x2="{W - 18}" y2="{SOIL}" stroke="{BROWN}" '
    f'stroke-width="1.3" opacity="0.55"/>'
)

# ---- roots: circuit traces + bus ------------------------------------------
BUS_Y = 212
bus_d = f"M40,{BUS_Y} L{W - 40},{BUS_Y}"
elems.append(
    f'<path d="{bus_d}" fill="none" stroke="{GOLD}" stroke-width="0.9" '
    f'opacity="0.30" stroke-dasharray="{W - 80}" stroke-dashoffset="{W - 80}" '
    f'style="animation:draw 2.2s ease-out 0.3s both"/>'
)
# moving data pulse on the bus
elems.append(
    f'<path d="{bus_d}" fill="none" stroke="{GOLD}" stroke-width="1.6" '
    f'opacity="0.75" stroke-linecap="round" stroke-dasharray="5 200" '
    f'style="animation:flow 7s linear 3s infinite"/>'
)

for bx, jog, run in [(80, 4, 60), (148, 10, -45), (300, 2, 80), (370, 8, -60),
                     (475, 5, 55), (560, 12, 70), (625, 3, -50)]:
    root_trace(bx, 0.4 + bx / 900.0, jog, run)
# stubs dropping from pads to the bus
for sx in [148 + 8 - 45, 370 + 8 - 60, 560 + 8 + 70]:
    d = f"M{sx:.1f},{SOIL + 22} L{sx:.1f},{BUS_Y}"
    stroke(d, GOLD, 0.8, BUS_Y - SOIL - 22, 1.8, 0.4, opacity=0.4, cap="square")
# vias on the bus
for vx in [120, 340, 480, 640, 760]:
    elems.append(
        f'<circle cx="{vx}" cy="{BUS_Y}" r="1.8" fill="{GOLD}" opacity="0" '
        f'style="animation:fadein .5s ease-out {2.0 + vx / 900.0:.2f}s both;'
        f'opacity:0.5"/>'
    )

# ---- spores ---------------------------------------------------------------
for i, (sx, sy, dl) in enumerate([(240, 70, 4), (520, 55, 6), (690, 90, 8),
                                  (420, 45, 10)]):
    elems.append(
        f'<circle cx="{sx}" cy="{sy}" r="1.6" fill="{GOLD}" opacity="0" '
        f'style="animation:drift 11s ease-in-out {dl}s infinite"/>'
    )

# ---- title ----------------------------------------------------------------
elems.append(
    f'<text x="{W - 36}" y="86" text-anchor="end" font-size="17" '
    f'fill="{BROWN}" opacity="0" style="animation:fadein 1.2s ease-out 2.6s both;'
    f'opacity:0.9">un jardín cibernético</text>'
)
elems.append(
    f'<text x="{W - 36}" y="106" text-anchor="end" font-size="10.5" '
    f'fill="{MOSS}" opacity="0" style="animation:fadein 1.2s ease-out 3.1s both;'
    f'opacity:0.7">▲ growing · ◐ dormant · ○ wild</text>'
)

svg = f'''<svg viewBox="0 0 {W} {H}" width="{W}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="un jardín cibernético — ferns growing above a soil line, circuit-trace roots below">
<style>
@keyframes draw{{to{{stroke-dashoffset:0;}}}}
@keyframes fadein{{from{{opacity:0;}}}}
@keyframes bloom{{from{{opacity:0;transform:scale(0);}}to{{opacity:0.95;transform:scale(1);}}}}
@keyframes halo{{from{{opacity:0;}}to{{opacity:0.35;}}}}
@keyframes breathe{{0%,100%{{opacity:0.95;}}50%{{opacity:0.5;}}}}
@keyframes flow{{from{{stroke-dashoffset:820;}}to{{stroke-dashoffset:-205;}}}}
@keyframes drift{{0%,100%{{opacity:0;transform:translateY(0);}}20%{{opacity:0.5;}}50%{{opacity:0.6;transform:translateY(-16px);}}80%{{opacity:0.25;}}}}
circle,text{{transform-box:fill-box;transform-origin:center;}}
text{{font-family:'Courier New',monospace;}}
</style>
<rect width="{W}" height="{H}" fill="{CREAM}" rx="8"/>
{chr(10).join(elems)}
</svg>'''

name = "banner-dark.svg" if DARK else "banner.svg"
out = f"assets/{name}"
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}: {len(svg)} bytes, {len(elems)} elements")
