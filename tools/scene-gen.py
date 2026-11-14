"""Clean ASCII-art night scene: a moonlit rolling hill under a starry sky.

Original art (not traced from any photo). Static, pure ASCII SVG, kept well
under the app's 131,072-byte limit. Rules learned in this app: no CSS, no
<use>, xml:space="preserve" on each <text>, no non-ASCII characters.
usage: python scene-gen.py <out.svg>
"""
import math, random, sys

random.seed(5)
W, H = 1680, 1050
COLS, ROWS = 336, 140
CW, LH = W / COLS, H / ROWS
FS = 8.4
FONT = 'Consolas,Menlo,monospace'

PAL = {
    'crest': '#a9d3b4', 'h3': '#7fb08e', 'h2': '#5a8a6b', 'h1': '#3d6650',
    'f2': '#4f7d5f', 'f1': '#36584a', 'tuft': '#6d9c7c', 'fly': '#e4f59a',
    'moon': '#efeacf', 'moond': '#bdb79c', 'moone': '#d9d4b8',
    'cloud': '#53648f', 'cloudl': '#9aaad3',
    'far': '#34477a', 'farl': '#5a6fa6',
}

# ---------- shapes ----------
def hill_top(x):
    return 700 - 185 * math.exp(-((x - 520) / 720) ** 2)

def field_top(x):
    return 905 + 16 * math.sin(x / 260 + 0.5) - 0.025 * x

def far_top(x):
    return 668 - 36 * math.exp(-((x - 1560) / 115) ** 2) - 24 * math.exp(-((x - 1395) / 95) ** 2)

MOON = (1290, 235, 112)

# ---------- character grid ----------
grid = [[None] * COLS for _ in range(ROWS)]

def put(c, r, ch, key, force=False):
    if 0 <= c < COLS and 0 <= r < ROWS and (force or grid[r][c] is None):
        grid[r][c] = (ch, key)

def line_glyph(y, slope):
    """Cell row and glyph for a curve passing at pixel height y with slope dy/dx."""
    m = slope * CW / LH  # slope in cell units
    rr = y / LH
    r = int(rr)
    frac = rr - r
    if abs(m) < 0.28:
        if frac >= 0.55:
            return r, '_'
        if frac >= 0.2:
            return r, '-'
        return r - 1, '_'
    if abs(m) < 1.8:
        return r, '/' if m < 0 else '\\'
    return r, '|'

def draw_curve(f, x0, x1, key_of, force=False):
    for c in range(int(x0 / CW), int(x1 / CW) + 1):
        px = (c + 0.5) * CW
        y = f(px)
        s = (f(px + CW / 2) - f(px - CW / 2)) / CW
        r, ch = line_glyph(y, s)
        put(c, r, ch, key_of(px, s), force)

# hill crest: one crisp moonlit line
draw_curve(hill_top, 0, W, lambda px, s: 'crest', force=True)

# Shading: a density ramp whose neighbouring glyphs look alike, mixed by a fixed
# 4x4 Bayer pattern so a gradient never shows a hard staircase edge (and no noise).
RAMP_G = " .:;+*"
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def dither(v, c, r, n):
    x = max(0.0, min(0.9999, v)) * (n - 1)
    base = int(x)
    return min(n - 1, base + (1 if x - base > (BAYER[r % 4][c % 4] + 0.5) / 16 else 0))

def hill_light(px, py):
    yt, yf = hill_top(px), field_top(px)
    slope = (hill_top(px + 8) - hill_top(px - 8)) / 16      # >0 where the hill falls to the right
    depth = min(1.0, (py - yt) / max(1.0, yf - yt))
    v = 0.48 + 2.2 * slope - 0.40 * depth + 0.30 * math.exp(-(py - yt) / 26)
    return max(0.22 + 0.06 * (1 - depth), v)                 # the shadowed slope keeps a quiet dot texture

def shade_key(v):
    # colour follows the smooth light, not the dithered glyph, so runs stay long
    x = v * (len(RAMP_G) - 1)
    return 'h3' if x >= 3.5 else 'h2' if x >= 1.6 else 'h1'

# hill body down to the field, then the field continues the same light, fading
for r in range(ROWS):
    for c in range(COLS):
        px, py = (c + 0.5) * CW, (r + 0.5) * LH
        yt, yf = hill_top(px), field_top(px)
        if py < yt + LH * 0.6:
            continue
        if py < yf:
            v = hill_light(px, py)
        else:
            # pick up exactly where the hill's foot left off, then fade toward the bottom
            v = hill_light(px, yf - 0.01) * (1 - 0.35 * (py - yf) / (H - yf))
            v = max(0.22, v)
        lvl = dither(v, c, r, len(RAMP_G))
        if lvl:
            put(c, r, RAMP_G[lvl], shade_key(v))

# fireflies over the field
for i in range(18):
    px = random.uniform(60, W - 60)
    py = random.uniform(field_top(px) - 40, field_top(px) + 120)
    put(int(px / CW), int(py / LH), random.choice('.*'), 'fly', force=True)

# far range on the right: outline only, behind the hill
for c in range(int(1180 / CW), COLS):
    px = (c + 0.5) * CW
    y = far_top(px)
    if y > hill_top(px) - LH:
        continue
    s = (far_top(px + CW / 2) - far_top(px - CW / 2)) / CW
    r, ch = line_glyph(y, s)
    put(c, r, ch, 'farl')

# moon: smooth limb-darkened disc with soft maria, crisp edge glyphs
mx, my, mr = MOON
RAMP = ".:-=+*#%@"
for r in range(int((my - mr) / LH) - 1, int((my + mr) / LH) + 2):
    for c in range(int((mx - mr) / CW) - 1, int((mx + mr) / CW) + 2):
        sub = [((c + (i + 0.5) / 3) * CW, (r + (j + 0.5) / 3) * LH) for j in range(3) for i in range(3)]
        cov = [math.hypot(x - mx, y - my) < mr for x, y in sub]
        n = sum(cov)
        if n == 0:
            continue
        if n < 9:
            # outline: pick by which side of the cell the disc is on
            ax = sum(x for (x, y), k in zip(sub, cov) if k) / n - (c + 0.5) * CW
            ay = sum(y for (x, y), k in zip(sub, cov) if k) / n - (r + 0.5) * LH
            a = math.degrees(math.atan2(ay, ax)) % 360
            if 60 <= a < 120: ch = '_' if n < 5 else '.'
            elif 240 <= a < 300: ch = "'" if n < 5 else '-'
            elif a < 30 or a >= 330 or 150 <= a < 210: ch = '|' if n > 3 else ':'
            elif 30 <= a < 60 or 210 <= a < 240: ch = '/'   # disc lies down-right or up-left: the edge runs /
            else: ch = '\\'
            put(c, r, ch, 'moone', force=True)
            continue
        px, py = (c + 0.5) * CW, (r + 0.5) * LH
        d = math.hypot(px - mx, py - my) / mr
        v = 0.45 + 0.55 * math.sqrt(max(0.0, 1 - d * d))
        for ox, oy, rr, depth in ((-32, -26, 42, 0.30), (26, 20, 34, 0.26), (-8, 48, 22, 0.22), (42, -42, 17, 0.18)):
            q = math.hypot(px - mx - ox, py - my - oy) / rr
            if q < 1:
                v -= depth * (1 - q * q)
        v = max(0.05, min(0.99, v))
        put(c, r, RAMP[dither(v, c, r, len(RAMP))], 'moon' if v > 0.55 else 'moond', force=True)

# moonlit cloud banks: smooth elongated density, lit along the top edge
CLOUD_RAMP = " .-~=+"
CLOUDS = [(1110, 392, 300, 26), (1470, 430, 210, 20), (360, 360, 260, 22), (720, 455, 170, 15)]
for r in range(ROWS):
    for c in range(COLS):
        px, py = (c + 0.5) * CW, (r + 0.5) * LH
        best, top = 0.0, 0.0
        for cx, cy, rx, ry in CLOUDS:
            q = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            # three soft lobes along each bank
            for k in (-0.45, 0.0, 0.5):
                q2 = ((px - cx - k * rx) / (rx * 0.55)) ** 2 + ((py - cy + ry * 0.35) / (ry * 0.9)) ** 2
                q = min(q, q2)
            d = 1 - q
            if d > best:
                best, top = d, (cy - py) / ry
        if best <= 0.04:
            continue
        v = min(0.999, best * 1.3)
        ch = CLOUD_RAMP[dither(v, c, r, len(CLOUD_RAMP))]
        if ch != ' ':
            put(c, r, ch, 'cloudl' if top > 0.25 and v > 0.3 else 'cloud')

# ---------- svg ----------
def esc(ch):
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}.get(ch, ch)

o = []
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
o.append('<defs>'
         '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#03060f"/><stop offset="0.6" stop-color="#0a1530"/>'
         '<stop offset="1" stop-color="#16264d"/></linearGradient>'
         '<radialGradient id="glow"><stop offset="0" stop-color="#b9c8f0" stop-opacity="0.28"/>'
         '<stop offset="0.45" stop-color="#8ea4dc" stop-opacity="0.08"/>'
         '<stop offset="1" stop-color="#8ea4dc" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="hill" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#0f2a1c"/><stop offset="1" stop-color="#071710"/></linearGradient>'
         '</defs>')
o.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
o.append(f'<circle cx="{mx}" cy="{my}" r="{mr * 3.4:.0f}" fill="url(#glow)"/>')

# stars: blue-noise placement, brightness by glyph, none in the moon's glow
stars = []
tries = 0
while len(stars) < 230 and tries < 20000:
    tries += 1
    x, y = random.uniform(10, W - 10), random.uniform(8, 640)
    if y > hill_top(x) - 30 or math.hypot(x - mx, y - my) < mr * 1.9:
        continue
    if any((x - a) ** 2 + (y - b) ** 2 < 46 ** 2 for a, b, _ in stars):
        continue
    t = random.random()
    stars.append((x, y, '*' if t < 0.07 else '+' if t < 0.25 else '.'))
groups = {'.': ('#7d8cb8', []), '+': ('#b9c6ea', []), '*': ('#f3f6ff', [])}
for x, y, ch in stars:
    groups[ch][1].append(f'<text x="{x:.0f}" y="{y:.0f}">{ch}</text>')
for ch, (col, items) in groups.items():
    size = FS * (1.5 if ch == '*' else 1.15 if ch == '+' else 1)
    o.append(f'<g font-family="{FONT}" font-size="{size:.1f}" fill="{col}">{"".join(items)}</g>')

# silhouettes under the line art
fpts = ' '.join(f'L{x} {far_top(x):.0f}' for x in range(1180, W + 1, 20))
o.append(f'<path d="M1180 720 {fpts} L{W} 720 Z" fill="#111d3b"/>')
hpts = ' '.join(f'L{x} {hill_top(x):.0f}' for x in range(0, W + 1, 20))
o.append(f'<path d="M0 {H} {hpts} L{W} {H} Z" fill="url(#hill)"/>')
# (no separate field shape: the hill's gradient runs to the bottom, so there is no seam)

# the grid, one text per row, colour runs as tspans
o.append(f'<g font-family="{FONT}" font-size="{FS}">')
for r in range(ROWS):
    row = grid[r]
    idx = [c for c in range(COLS) if row[c] is not None]
    if not idx:
        continue
    first, last = idx[0], idx[-1]
    parts, cur = [], None
    for c in range(first, last + 1):
        cell = row[c]
        ch, key = cell if cell else (' ', cur)
        if key != cur:
            if cur is not None:
                parts.append('</tspan>')
            parts.append(f'<tspan fill="{PAL[key]}">')
            cur = key
        parts.append(esc(ch))
    parts.append('</tspan>')
    y = (r + 1) * LH - (LH - FS * 0.72) / 2
    n = last - first + 1
    o.append(f'<text xml:space="preserve" x="{first * CW:.1f}" y="{y:.1f}" textLength="{n * CW:.1f}" lengthAdjust="spacing">{"".join(parts)}</text>')
o.append('</g></svg>')

svg = ''.join(o)
assert all(ord(ch) < 128 for ch in svg), 'scene must stay pure ASCII'
with open(sys.argv[1], 'w', encoding='utf-8', newline='') as fh:
    fh.write(svg)
print('bytes', len(svg.encode()))
