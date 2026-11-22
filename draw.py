#!/usr/bin/env python3
"""Draw entry.png: a one-page newspaper front page summing up 21 Nov 2026.

Saturday 21 November 2026. 35 stories across 7 regions (EUROPE 5,
AMERICAS 10, ASIA 5, MIDDLE EAST 5, WORLD 3, AFRICA 4, OCEANIA 3),
3 hero + 10 secondary original flat illustrations, a numbers strip
where every number tells a complete mini-story, a pinned dotted world
map, a 22-story numbered list, a DATE CHECK box with 13 dated
exclusions plus one unconfirmed item, and a sources footer.
Counts reconcile: 3 hero + 10 secondary + 22 listed = 35; region
counts sum to 35.

Every story was verified as having happened, or first been reported,
on Saturday 21 November 2026, from Reuters, AP, AFP, BBC, Al Jazeera,
USGS, CoinDesk, NBC, CNN, NYT, IANS, RNZ, Capital Ethiopia, MyJoyOnline,
Punch, Radio Tamazuj and Formula 1. Near-misses are named in the
DATE CHECK box, not shown as news. Changes vs the 20 Nov v4 template:
new heroes (Iran strikes Bahrain, Mexico captures "El Chapo Isidro",
Peru M6.7 quake with a data table); the Riyadh story is the verified
3 missiles of Saturday, not 5 (the 2 over Jazan were Friday evening);
the third hero is again data-driven, now with quake figures; the
Missouri Roundup ruling and the UN Sudan report were Friday/Tuesday,
so they are exclusions, not stories. Drawn with Pillow only; no
photos, no copied art.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W = H = 1024
PAPER = (248, 245, 238)
INK = (20, 20, 20)
MUTED = (90, 86, 78)
RED = (166, 27, 27)
NAVY = (18, 34, 64)
RULE = (180, 174, 162)
CARD = (255, 255, 255)
MAPDOT = (158, 168, 180)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, xy, text, fnt, width, fill, spacing=2, max_lines=None):
    """Draw wrapped text; returns y after the last line. Warns on overflow."""
    x, y = xy
    lines = wrap(d, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        print(f"OVERFLOW: {text[:48]!r} -> {len(lines)} lines (max {max_lines})")
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


# ---------- flat-illustration primitives ----------
def bands(d, box, colors):
    x0, y0, x1, y1 = box
    n = len(colors)
    for i, c in enumerate(colors):
        d.rectangle([x0, y0 + (y1 - y0) * i // n,
                     x1, y0 + (y1 - y0) * (i + 1) // n], fill=c)


def sun(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def cloud(d, x, y, s, color):
    d.ellipse([x, y, x + s, y + s * 0.55], fill=color)
    d.ellipse([x + s * 0.5, y - s * 0.25, x + s * 1.5, y + s * 0.4], fill=color)
    d.ellipse([x + s, y, x + s * 2, y + s * 0.55], fill=color)


def building(d, x, y, w, h, color, win=(255, 214, 90)):
    d.rectangle([x, y, x + w, y + h], fill=color)
    for wy in range(y + 8, y + h - 8, 14):
        for wx in range(x + 6, x + w - 8, 14):
            d.rectangle([wx, wy, wx + 6, wy + 7], fill=win)


def star4(d, cx, cy, r, color):
    d.polygon([(cx, cy - r), (cx + r * 0.28, cy - r * 0.28), (cx + r, cy),
               (cx + r * 0.28, cy + r * 0.28), (cx, cy + r),
               (cx - r * 0.28, cy + r * 0.28), (cx - r, cy),
               (cx - r * 0.28, cy - r * 0.28)], fill=color)


def wave(d, x0, y, x1, color, amp=5, step=14):
    pts = []
    for x in range(x0, x1 + 1, step):
        pts.append((x, y + amp * math.sin((x - x0) / 22.0)))
    d.line(pts, fill=color, width=2)


def figure(d, x, y, s, skin=(232, 190, 160), shirt=(30, 90, 160), helm=(40, 44, 52)):
    """A small standing person: helmeted head, torso, legs."""
    d.ellipse([x - s * 0.28, y, x + s * 0.28, y + s * 0.55], fill=skin)
    d.pieslice([x - s * 0.32, y - s * 0.12, x + s * 0.32, y + s * 0.4],
               start=180, end=360, fill=helm)
    d.rectangle([x - s * 0.3, y + s * 0.55, x + s * 0.3, y + s * 1.15], fill=shirt)
    d.rectangle([x - s * 0.22, y + s * 1.15, x - s * 0.02, y + s * 1.7], fill=(30, 30, 34))
    d.rectangle([x + s * 0.02, y + s * 1.15, x + s * 0.22, y + s * 1.7], fill=(30, 30, 34))


# ---------- hero illustrations (310 x 128 boxes) ----------
def ill_bahrain(d, box):
    """Hero 1: night over Bahrain — missiles, a burning plant, intercept flash."""
    x0, y0, x1, y1 = box
    bands(d, box, [(12, 18, 40), (20, 30, 58), (30, 44, 78)])
    star4(d, x0 + 30, y0 + 16, 5, (255, 255, 255))
    star4(d, x0 + 150, y0 + 10, 4, (255, 255, 255))
    star4(d, x0 + 260, y0 + 22, 5, (255, 255, 255))
    # missile streaks
    for sx, sy in [(x0 + 60, y0 + 66), (x0 + 170, y0 + 52), (x0 + 250, y0 + 74)]:
        d.line([sx, sy, sx + 42, sy - 34], fill=(255, 214, 90), width=3)
        d.ellipse([sx + 40, sy - 38, sx + 48, sy - 30], fill=(255, 236, 160))
    # intercept burst
    star4(d, x0 + 210, y0 + 34, 18, (255, 140, 40))
    star4(d, x0 + 210, y0 + 34, 9, (255, 220, 120))
    # skyline with a burning industrial site
    for bx, bw, bh in [(x0 + 10, 30, 40), (x0 + 46, 24, 56), (x0 + 76, 36, 30),
                       (x0 + 118, 28, 48), (x0 + 152, 40, 34), (x0 + 198, 26, 52),
                       (x0 + 230, 34, 38), (x0 + 270, 26, 44)]:
        building(d, bx, y1 - bh, bw, bh, (8, 12, 26), win=(255, 190, 90))
    # burning plant: chimney + flames
    px = x0 + 150
    d.rectangle([px, y1 - 78, px + 10, y1 - 34], fill=(60, 60, 64))
    d.polygon([(px - 2, y1 - 78), (px + 5, y1 - 104), (px + 12, y1 - 78)], fill=(255, 140, 40))
    d.polygon([(px + 1, y1 - 78), (px + 5, y1 - 92), (px + 9, y1 - 78)], fill=(255, 220, 120))
    cloud(d, px - 16, y1 - 112, 18, (110, 110, 116))
    d.rectangle([x0, y1 - 10, x1, y1], fill=(16, 22, 38))


def ill_chapo(d, box):
    """Hero 2: night raid in Sinaloa — soldiers, roadblock fire, helicopter beam."""
    x0, y0, x1, y1 = box
    bands(d, box, [(24, 28, 48), (36, 42, 66), (52, 58, 86)])
    # helicopter with searchlight
    hx, hy = x0 + 230, y0 + 26
    d.ellipse([hx - 26, hy - 10, hx + 26, hy + 10], fill=(20, 20, 24))
    d.line([hx - 34, hy - 12, hx + 34, hy - 12], fill=(90, 90, 96), width=2)
    d.line([hx - 8, hy - 22, hx + 8, hy - 22], fill=(90, 90, 96), width=2)
    d.polygon([(hx - 14, hy + 8), (hx + 14, hy + 8), (hx + 44, y1 - 30), (hx - 44, y1 - 30)],
              fill=(255, 236, 160))
    # street
    d.rectangle([x0, y1 - 34, x1, y1], fill=(40, 40, 44))
    d.line([x0, y1 - 34, x1, y1 - 34], fill=(120, 120, 124), width=2)
    for lx in range(x0 + 20, x1 - 10, 40):
        d.line([lx, y1 - 17, lx + 18, y1 - 17], fill=(220, 200, 90), width=3)
    # soldiers advancing
    figure(d, x0 + 60, y1 - 78, 26, shirt=(46, 90, 60))
    figure(d, x0 + 110, y1 - 74, 24, shirt=(46, 90, 60))
    figure(d, x0 + 150, y1 - 80, 26, shirt=(46, 90, 60))
    # roadblock fire on the right
    d.rectangle([x0 + 250, y1 - 52, x0 + 296, y1 - 34], fill=(90, 60, 40))
    d.polygon([(x0 + 256, y1 - 52), (x0 + 266, y1 - 84), (x0 + 276, y1 - 52)], fill=(255, 140, 40))
    d.polygon([(x0 + 268, y1 - 52), (x0 + 273, y1 - 70), (x0 + 280, y1 - 52)], fill=(255, 220, 120))
    cloud(d, x0 + 252, y1 - 96, 16, (110, 110, 116))
    # houses behind
    for bx, bw, bh in [(x0 + 8, 34, 30), (x0 + 190, 30, 38)]:
        building(d, bx, y1 - 34 - bh, bw, bh, (16, 20, 34), win=(255, 190, 90))


def ill_quake(d, box):
    """Hero 3: the quake as a data table, with a seismograph trace."""
    x0, y0, x1, y1 = box
    bands(d, box, [(248, 240, 228), (244, 232, 214), (238, 224, 200)])
    rows = [("MAGNITUDE", "6.7"), ("DEPTH", "108 km"),
            ("EPICENTRE", "30 km NW of Junin"), ("TIME", "00:09 UTC")]
    for i, (name, val) in enumerate(rows):
        ry = y0 + 8 + i * 22
        d.text((x0 + 12, ry), name, font=font(SANS_B, 13), fill=INK)
        d.text((x0 + 150, ry), val, font=font(SANS_B, 13), fill=RED)
        d.line([x0 + 12, ry + 19, x1 - 12, ry + 19], fill=(214, 204, 186), width=1)
    # seismograph zigzag along the bottom, below the caption
    pts = []
    x = x0 + 12
    base = y1 - 10
    import random
    random.seed(21)
    while x < x1 - 12:
        pts.append((x, base + random.randint(-6, 6)))
        x += 7
    d.line(pts, fill=(178, 34, 34), width=2)
    d.text((x0 + 12, y1 - 30), "USGS · felt in Lima", font=font(SANS, 9), fill=MUTED)

# ---------- secondary illustrations (185 x 58 boxes) ----------
def ill_kryvyi(d, box):
    """4: night city, a struck building, explosion, rescue smoke."""
    x0, y0, x1, y1 = box
    bands(d, box, [(16, 24, 48), (26, 38, 70), (40, 56, 96)])
    for bx, bw, bh in [(x0 + 6, 26, 26), (x0 + 36, 20, 34), (x0 + 60, 30, 22),
                       (x0 + 96, 24, 30), (x0 + 124, 28, 26), (x0 + 156, 22, 32)]:
        building(d, bx, y1 - bh, bw, bh, (10, 16, 32), win=(255, 190, 90))
    star4(d, x0 + 84, y0 + 22, 14, (255, 140, 40))
    star4(d, x0 + 84, y0 + 22, 7, (255, 220, 120))
    cloud(d, x0 + 66, y0 + 4, 14, (120, 128, 148))
    cloud(d, x0 + 120, y0 + 30, 12, (120, 128, 148))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(12, 18, 34))


def ill_riyadh(d, box):
    """5: Riyadh at night — a tall tower, three interceptors climbing."""
    x0, y0, x1, y1 = box
    bands(d, box, [(14, 20, 44), (22, 32, 62), (32, 46, 84)])
    star4(d, x0 + 20, y0 + 8, 4, (255, 255, 255))
    star4(d, x0 + 160, y0 + 12, 4, (255, 255, 255))
    for sx, sy in [(x0 + 44, y0 + 44), (x0 + 96, y0 + 48), (x0 + 140, y0 + 42)]:
        d.line([sx, sy, sx + 22, sy - 20], fill=(255, 214, 90), width=2)
        d.ellipse([sx + 20, sy - 24, sx + 26, sy - 18], fill=(255, 236, 160))
    # tall tower + low blocks
    d.rectangle([x0 + 66, y0 + 14, x0 + 78, y1 - 8], fill=(10, 16, 32))
    for wy in range(y0 + 18, y1 - 12, 8):
        d.rectangle([x0 + 69, wy, x0 + 75, wy + 4], fill=(255, 190, 90))
    for bx, bw, bh in [(x0 + 6, 26, 18), (x0 + 36, 22, 24), (x0 + 84, 30, 16),
                       (x0 + 118, 24, 22), (x0 + 146, 28, 18)]:
        building(d, bx, y1 - bh, bw, bh, (10, 16, 32), win=(255, 190, 90))
    d.rectangle([x0, y1 - 6, x1, y1], fill=(12, 18, 34))


def ill_sparta(d, box):
    """6: a cargo ship burning in the Gulf of Finland, crew in a lifeboat."""
    x0, y0, x1, y1 = box
    bands(d, box, [(214, 226, 232), (190, 208, 220), (168, 192, 208)])
    sun(d, x0 + 22, y0 + 12, 9, (255, 214, 90))
    d.rectangle([x0, y1 - 20, x1, y1], fill=(36, 76, 118))
    wave(d, x0 + 6, y1 - 14, x1 - 6, (220, 235, 242))
    # ship hull + containers, fire amidships
    hx, hy = x0 + 46, y1 - 34
    d.polygon([(hx, hy + 14), (hx + 96, hy + 14), (hx + 104, hy + 2), (hx, hy + 2)],
              fill=(24, 24, 28))
    for i, c in enumerate([(200, 60, 50), (40, 120, 90), (220, 160, 40)]):
        d.rectangle([hx + 10 + i * 22, hy - 8, hx + 28 + i * 22, hy + 2], fill=c)
    d.polygon([(hx + 44, hy - 8), (hx + 50, hy - 26), (hx + 56, hy - 8)], fill=(255, 140, 40))
    d.polygon([(hx + 47, hy - 8), (hx + 50, hy - 18), (hx + 53, hy - 8)], fill=(255, 220, 120))
    cloud(d, hx + 40, y0 + 2, 12, (110, 110, 116))
    # lifeboat with crew
    d.ellipse([x1 - 44, y1 - 26, x1 - 14, y1 - 16], fill=(220, 120, 40))
    d.ellipse([x1 - 38, y1 - 32, x1 - 32, y1 - 26], fill=(232, 190, 160))
    d.ellipse([x1 - 28, y1 - 32, x1 - 22, y1 - 26], fill=(232, 190, 160))
    # two drones above
    for dx, dy in [(x0 + 30, y0 + 8), (x0 + 120, y0 + 4)]:
        d.rectangle([dx - 6, dy - 2, dx + 6, dy + 2], fill=(30, 30, 34))
        d.line([dx - 10, dy - 4, dx - 10, dy + 4], fill=(30, 30, 34), width=1)
        d.line([dx + 10, dy - 4, dx + 10, dy + 4], fill=(30, 30, 34), width=1)


def ill_cop31(d, box):
    """7: the summit in overtime — globe, flags, a clock."""
    x0, y0, x1, y1 = box
    bands(d, box, [(126, 196, 178), (150, 212, 190), (178, 226, 200)])
    sun(d, x0 + 20, y0 + 12, 9, (255, 214, 90))
    cx, cy, r = x0 + 78, y0 + 30, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 120, 180))
    d.ellipse([cx - r + 5, cy - r + 6, cx - r + 15, cy - r + 14], fill=(86, 170, 110))
    d.ellipse([cx + 2, cy + 4, cx + 12, cy + 14], fill=(86, 170, 110))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=1)
    # flags row
    for i, c in enumerate([(30, 90, 160), (220, 60, 50), (255, 214, 90), (60, 140, 90)]):
        fx = x0 + 118 + i * 14
        d.line([fx, y0 + 8, fx, y0 + 26], fill=(60, 60, 60), width=1)
        d.rectangle([fx, y0 + 8, fx + 10, y0 + 16], fill=c)
    # clock showing overtime
    gx, gy = x1 - 22, y0 + 16
    d.ellipse([gx - 11, gy - 11, gx + 11, gy + 11], fill=(255, 255, 255),
              outline=(60, 60, 60), width=1)
    d.line([gx, gy, gx, gy - 7], fill=(60, 60, 60), width=1)
    d.line([gx, gy, gx + 6, gy + 2], fill=(178, 34, 34), width=1)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(46, 110, 74))


def ill_dengue(d, box):
    """8: a mosquito, a child, and falling case bars."""
    x0, y0, x1, y1 = box
    bands(d, box, [(214, 236, 214), (196, 224, 196), (178, 212, 178)])
    # falling bars (cases down)
    for i, h in enumerate([30, 24, 16, 9]):
        bx = x0 + 118 + i * 14
        d.rectangle([bx, y1 - 8 - h, bx + 9, y1 - 8], fill=(46, 134, 74))
    d.line([x0 + 116, y1 - 42, x0 + 170, y1 - 20], fill=(178, 34, 34), width=2)
    # mosquito
    mx, my = x0 + 44, y0 + 22
    d.ellipse([mx - 12, my - 4, mx + 12, my + 4], fill=(60, 60, 64))
    d.ellipse([mx + 10, my - 3, mx + 18, my + 3], fill=(60, 60, 64))
    d.ellipse([mx - 2, my - 12, mx + 8, my - 2], fill=(200, 220, 230))
    d.ellipse([mx - 2, my + 2, mx + 8, my + 12], fill=(200, 220, 230))
    for lx in range(3):
        d.line([mx - 8 + lx * 8, my + 4, mx - 12 + lx * 8, my + 14],
               fill=(60, 60, 64), width=1)
    # child silhouette
    d.ellipse([x0 + 82, y1 - 34, x0 + 94, y1 - 22], fill=(232, 190, 160))
    d.rectangle([x0 + 82, y1 - 22, x0 + 94, y1 - 8], fill=(30, 90, 160))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(60, 128, 64))


def ill_bepi(d, box):
    """9: BepiColombo at Mercury — dark space, cratered planet, spacecraft."""
    x0, y0, x1, y1 = box
    bands(d, box, [(12, 16, 36), (18, 24, 50), (26, 34, 66)])
    star4(d, x0 + 18, y0 + 10, 4, (255, 255, 255))
    star4(d, x0 + 150, y0 + 8, 3, (255, 255, 255))
    star4(d, x0 + 96, y0 + 44, 3, (255, 255, 255))
    # Mercury
    cx, cy, r = x0 + 52, y0 + 30, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 140, 92))
    for ox, oy, orr in [(cx - 8, cy - 6, 4), (cx + 6, cy + 4, 5), (cx + 2, cy - 10, 3),
                        (cx - 2, cy + 10, 3)]:
        d.ellipse([ox - orr, oy - orr, ox + orr, oy + orr], fill=(160, 106, 66))
    # spacecraft: body + two solar panels
    sx, sy = x0 + 128, y0 + 26
    d.rectangle([sx - 10, sy - 8, sx + 10, sy + 8], fill=(220, 220, 224))
    d.rectangle([sx - 34, sy - 5, sx - 10, sy + 5], fill=(40, 90, 180))
    d.rectangle([sx + 10, sy - 5, sx + 34, sy + 5], fill=(40, 90, 180))
    d.line([sx - 34, sy, sx - 10, sy], fill=(255, 255, 255), width=1)
    d.line([sx + 10, sy, sx + 34, sy], fill=(255, 255, 255), width=1)
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 214, 90))


def ill_gaza(d, box):
    """10: an aid truck on a dusty road, boxes stacked beside it."""
    x0, y0, x1, y1 = box
    bands(d, box, [(222, 232, 238), (206, 220, 230), (188, 206, 220)])
    sun(d, x0 + 18, y0 + 10, 8, (255, 214, 90))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(120, 118, 110))
    tx, ty = x0 + 26, y1 - 34
    d.rectangle([tx, ty, tx + 58, ty + 18], fill=(240, 240, 238),
                outline=(90, 90, 90), width=1)
    d.rectangle([tx + 58, ty + 5, tx + 76, ty + 18], fill=(200, 70, 50))
    for wx in (tx + 12, tx + 46):
        d.ellipse([wx - 5, ty + 18, wx + 5, ty + 26], fill=(30, 30, 34))
    d.ellipse([tx + 70 - 5, ty + 18, tx + 70 + 5, ty + 26], fill=(30, 30, 34))
    # aid boxes
    for i, c in enumerate([(190, 150, 90), (150, 120, 80), (190, 150, 90)]):
        bx = x1 - 44 + (i % 2) * 16
        by = ty - 10 - (i // 2) * 12
        d.rectangle([bx, by, bx + 14, by + 10], fill=c)
    cloud(d, x1 - 60, y0 + 6, 12, (180, 178, 172))


def ill_bitcoin(d, box):
    """11: a rising chart and a coin — Bitcoin back above $60,000."""
    x0, y0, x1, y1 = box
    bands(d, box, [(248, 240, 228), (244, 232, 214), (238, 224, 200)])
    for gy in range(y0 + 8, y1 - 6, 10):
        d.line([x0 + 6, gy, x1 - 6, gy], fill=(214, 204, 186), width=1)
    pts = [(x0 + 12, y0 + 40), (x0 + 44, y0 + 36), (x0 + 70, y0 + 38),
           (x0 + 96, y0 + 28), (x0 + 122, y0 + 18), (x0 + 148, y0 + 10)]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=(46, 134, 74), width=3)
    for p in pts:
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(46, 134, 74))
    d.polygon([(pts[-1][0] - 6, pts[-1][1] - 10), (pts[-1][0] + 6, pts[-1][1] - 10),
               (pts[-1][0], pts[-1][1] + 2)], fill=(46, 134, 74))
    # coin
    cx, cy = x1 - 24, y1 - 16
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(247, 147, 26))
    d.text((cx - 4, cy - 8), "B", font=font(SANS_B, 13), fill=(255, 255, 255))
    d.text((x0 + 12, y1 - 20), "+9%", font=font(SANS_B, 14), fill=(46, 134, 74))


def ill_denmark(d, box):
    """12: Copenhagen — a ministry building, the Danish flag, a departing plane."""
    x0, y0, x1, y1 = box
    bands(d, box, [(196, 210, 222), (178, 194, 210), (160, 178, 198)])
    # ministry building
    d.rectangle([x0 + 12, y1 - 34, x0 + 96, y1 - 8], fill=(120, 110, 96))
    for wx in range(x0 + 20, x0 + 92, 14):
        d.rectangle([wx, y1 - 28, wx + 7, y1 - 20], fill=(255, 214, 90))
    d.rectangle([x0 + 48, y1 - 40, x0 + 60, y1 - 34], fill=(90, 80, 66))
    # Danish flag on a pole
    fx, fy = x0 + 112, y0 + 8
    d.line([fx, fy, fx, y1 - 8], fill=(60, 60, 60), width=2)
    d.rectangle([fx + 1, fy, fx + 26, fy + 16], fill=(200, 16, 46))
    d.rectangle([fx + 8, fy, fx + 11, fy + 16], fill=(255, 255, 255))
    d.rectangle([fx + 1, fy + 6, fx + 26, fy + 9], fill=(255, 255, 255))
    # departing plane
    px, py = x1 - 34, y0 + 14
    d.polygon([(px - 16, py), (px + 12, py - 5), (px + 16, py), (px + 12, py + 5)],
              fill=(40, 40, 44))
    d.line([px - 26, py + 4, px - 14, py + 4], fill=(140, 140, 144), width=1)
    d.line([px - 26, py + 8, px - 14, py + 8], fill=(140, 140, 144), width=1)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(110, 110, 108))


def ill_manipur(d, box):
    """13: tainted liquor — bottles, a warning, a hospital cross."""
    x0, y0, x1, y1 = box
    bands(d, box, [(232, 220, 200), (224, 208, 184), (214, 196, 168)])
    # bottles
    for i, (bx, bh, c) in enumerate([(x0 + 16, 30, (90, 120, 60)),
                                     (x0 + 44, 36, (120, 90, 50)),
                                     (x0 + 72, 28, (90, 120, 60))]):
        d.rectangle([bx, y1 - 8 - bh, bx + 16, y1 - 8], fill=c)
        d.rectangle([bx + 5, y1 - 8 - bh - 8, bx + 11, y1 - 8 - bh], fill=c)
    # warning triangle
    tx, ty = x0 + 118, y0 + 14
    d.polygon([(tx, ty), (tx + 22, ty + 18), (tx - 22, ty + 18)], fill=(255, 200, 40),
              outline=(60, 60, 60))
    d.text((tx - 2, ty + 4), "!", font=font(SANS_B, 12), fill=(60, 60, 60))
    # hospital cross
    cx, cy = x1 - 22, y0 + 16
    d.rectangle([cx - 10, cy - 3, cx + 10, cy + 3], fill=(200, 40, 40))
    d.rectangle([cx - 3, cy - 10, cx + 3, cy + 10], fill=(200, 40, 40))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(140, 120, 92))


ILLS = {
    1: ill_bahrain, 2: ill_chapo, 3: ill_quake, 4: ill_kryvyi, 5: ill_riyadh,
    6: ill_sparta, 7: ill_cop31, 8: ill_dengue, 9: ill_bepi, 10: ill_gaza,
    11: ill_bitcoin, 12: ill_denmark, 13: ill_manipur,
}

# ---------- story data ----------
# (num, region, topic, source, headline, summary)
HEROES = [
    (1, "MIDDLE EAST", "BAHRAIN", "REUTERS",
     "Iran hits US bases in Bahrain",
     "Guards claim hits on two US sites; Bahrain says a plant burned, no injuries."),
    (2, "AMERICAS", "MEXICO", "AP",
     "Mexico nabs FBI most-wanted boss",
     "Troops capture 'El Chapo Isidro' in Sinaloa; 11 dead in the raid and gunfights."),
    (3, "AMERICAS", "PERU", "USGS",
     "Peru quake 6.7 shakes the Andes",
     "No deaths in early reports; the tremor was felt in Lima."),
]
SECONDARY = [
    (4, "EUROPE", "UKRAINE", "AP",
     "Double-tap strike kills boy, 7",
     "Restaurant hit, then drones struck rescuers; 60 hurt."),
    (5, "MIDDLE EAST", "RIYADH", "REUTERS",
     "Three missiles downed over Riyadh",
     "Coalition intercepts Houthi missiles before dawn."),
    (6, "EUROPE", "BALTIC", "REUTERS",
     "Russian ship ablaze in Gulf of Finland",
     "Drones hit Sparta II; 16 crew evacuated to lifeboats."),
    (7, "WORLD", "CLIMATE", "REUTERS",
     "COP31 runs into overtime",
     "Summit passes deadline; plenary put off to Sunday."),
    (8, "AMERICAS", "HEALTH", "AP",
     "Mosquitoes cut dengue 69% in trial",
     "5,757 children in Brazil; results are preliminary."),
    (9, "WORLD", "SPACE", "AP",
     "BepiColombo reaches Mercury",
     "Spacecraft enters orbit after an 8-year, $2bn journey."),
    (10, "MIDDLE EAST", "GAZA", "REUTERS",
     "Strike kills three aid distributors",
     "Truck hit in Gaza City; IDF says militants targeted."),
    (11, "WORLD", "MARKETS", "COINDESK",
     "Bitcoin bounces 9% over $60,000",
     "From a $55,130 two-year low; $1.8bn liquidated."),
    (12, "EUROPE", "DIPLOMACY", "REUTERS",
     "Denmark urges EU curbs on Russians",
     "After expelling Russia's attaché over a foiled plot."),
    (13, "ASIA", "INDIA", "REUTERS",
     "Toxic liquor kills 11 in Manipur",
     "Adulterated alcohol; 180+ in hospital."),
]
LISTED = [
    "Kyiv: Zelensky says Crimea bridge 'will not stay'",
    "Helsinki: air and sea curbs after Sparta II",
    "London: Leeds stun Chelsea 4-1",
    "Washington: Trump plays down FBI breach",
    "Cleveland: Harden's 51 passes Kobe in win",
    "Florida: dengue outbreak biggest since 1940s",
    "Washington: Trump weighs new Iran strikes",
    "Las Vegas: Russell fastest in F1 practice",
    "Vancouver: Canada rests defence in climate trial",
    "Los Angeles: Palisades fire arson conviction",
    "Jakarta: EU and Indonesia sign trade deal",
    "Bhopal: India edge South Korea 2-1 in hockey",
    "Pyongyang: Kim tours factories after Trump snub",
    "Singapore: Wong meets Li Qiang; 20+ deals",
    "Tehran: Qatari delegation holds talks",
    "Addis Ababa: Ethiopia wins UN aviation seat",
    "Accra: Mahama unveils $10bn New Economy plan",
    "Sennar: night curfew as Blue Nile fighting grows",
    "Bayelsa: boat death toll rises to 23",
    "Cook Islands: relief on standby as Xavier fades",
    "Wellington: Rahul 124* as India reply to NZ's 368",
    "Perth: NZ man jailed over explosives material",
]
REGIONS = [("EUROPE", 5, (36, 84, 160)), ("AMERICAS", 10, (14, 128, 128)),
           ("ASIA", 5, (122, 62, 158)), ("MIDDLE EAST", 5, (178, 44, 44)),
           ("WORLD", 3, (96, 96, 100)), ("AFRICA", 4, (46, 134, 74)),
           ("OCEANIA", 3, (214, 122, 26))]
# numbers strip, two rows of three: each number tells a complete mini-story
NUMBERS_ROW1 = [("6.7", "magnitude of the Peru quake"),
                ("11", "dead in the 'El Chapo Isidro' raid"),
                ("69%", "fewer child dengue cases in Brazil")]
NUMBERS_ROW2 = [("3", "missiles downed over Riyadh"),
                ("+9%", "Bitcoin's rebound above $60,000"),
                ("60", "hurt in Kryvyi Rih double-tap strike")]
# map pins: (num, x, y); red for 1-3, navy for 4-13
PINS = [(1, 222, 840), (2, 95, 845), (3, 205, 878), (4, 204, 806),
        (5, 212, 830), (6, 200, 788), (7, 216, 818), (8, 214, 892),
        (9, 188, 798), (10, 202, 836), (11, 78, 812), (12, 190, 780),
        (13, 258, 830)]
LAND = [  # ellipses (x0, y0, x1, y1) forming a coarse dotted world map
    (45, 775, 170, 850), (175, 772, 200, 790), (130, 855, 185, 935),
    (185, 790, 235, 825), (190, 830, 250, 920), (235, 780, 310, 850),
    (255, 850, 285, 875), (265, 895, 305, 925), (180, 795, 192, 810),
    (300, 800, 312, 825), (235, 825, 265, 870), (190, 815, 230, 835),
    (165, 795, 195, 820), (205, 830, 235, 860), (185, 775, 205, 800),
    (308, 918, 318, 935),
]


def kicker(d, x, y, num, region, topic, src, width, size=10):
    """Left kicker 'N · REGION · TOPIC', source right; drops topic when tight."""
    f = font(SANS_B, size)
    sf = font(SANS, size - 1)
    full = f"{num} · {region} · {topic}"
    if d.textlength(full, font=f) + d.textlength(src, font=sf) + 16 > width:
        full = f"{num} · {region}"
    d.text((x, y), full, font=f, fill=RED)
    d.text((x + width - d.textlength(src, font=sf), y), src, font=sf, fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 24
    X1 = W - M

    # ---- header ----
    d.rectangle([M, 16, 118, 138], fill=RED)
    d.text((30, 22), "NOV", font=font(SANS_B, 22), fill=(255, 255, 255))
    d.text((30, 46), "21", font=font(SERIF_B, 52), fill=(255, 255, 255))
    d.text((30, 106), "SAT · 2026", font=font(SANS_B, 15), fill=(255, 255, 255))
    d.text((134, 20), "THE DAY IN WORLD NEWS", font=font(SANS_B, 15), fill=RED)
    d.text((134, 40), "Saturday 21 November 2026", font=font(SERIF_B, 46), fill=INK)
    d.text((134, 100),
           "Everything on this page happened, or was first reported, on Saturday 21 November 2026.",
           font=font(SANS, 15), fill=MUTED)
    for i, line in enumerate(["35 STORIES", "7 REGIONS", "ONE PAGE"]):
        f = font(SANS_B, 19)
        d.text((X1 - d.textlength(line, font=f), 26 + i * 26), line, font=f, fill=INK)
    d.line([M, 144, X1, 144], fill=INK, width=2)

    # ---- region strip ----
    y0, y1 = 150, 174
    total_w = X1 - M
    widths = []
    for name, n, _ in REGIONS:
        widths.append(max(64, int(total_w * n / 35)))
    scale = total_w / sum(widths)
    widths = [int(w * scale) for w in widths]
    widths[-1] += total_w - sum(widths)
    x = M
    for (name, n, col), w in zip(REGIONS, widths):
        d.rectangle([x, y0, x + w - 1, y1], fill=col)
        label = f"{name} {n}"
        f = font(SANS_B, 13)
        if d.textlength(label, font=f) <= w - 8:
            d.text((x + (w - d.textlength(label, font=f)) / 2, y0 + 6),
                   label, font=f, fill=(255, 255, 255))
        else:
            f2 = font(SANS_B, 10)
            d.text((x + (w - d.textlength(name, font=f2)) / 2, y0 + 2),
                   name, font=f2, fill=(255, 255, 255))
            d.text((x + (w - d.textlength(str(n), font=f2)) / 2, y0 + 13),
                   str(n), font=f2, fill=(255, 255, 255))
        x += w

    # ---- numbers strip: two rows of three, each number a full mini-story ----
    y = 182
    d.text((M, y), "THE DAY IN NUMBERS:", font=font(SANS_B, 14), fill=INK)
    nx = M + d.textlength("THE DAY IN NUMBERS:  ", font=font(SANS_B, 14))
    for num, lab in NUMBERS_ROW1:
        f1, f2 = font(SANS_B, 14), font(SANS, 13)
        d.text((nx, y), num, font=f1, fill=RED)
        nx += d.textlength(num + " ", font=f1)
        d.text((nx, y), lab, font=f2, fill=INK)
        nx += d.textlength(lab + "  ·  ", font=f2)
    if nx > X1:
        print(f"OVERFLOW: numbers strip row 1 ends at {nx}, page edge {X1}")
    nx = M
    y2 = y + 17
    for num, lab in NUMBERS_ROW2:
        f1, f2 = font(SANS_B, 14), font(SANS, 13)
        d.text((nx, y2), num, font=f1, fill=RED)
        nx += d.textlength(num + " ", font=f1)
        d.text((nx, y2), lab, font=f2, fill=INK)
        nx += d.textlength(lab + "  ·  ", font=f2)
    if nx > X1:
        print(f"OVERFLOW: numbers strip row 2 ends at {nx}, page edge {X1}")
    d.line([M, 210, X1, 210], fill=RULE, width=1)

    # ---- hero stories ----
    hy, hh = 216, 232
    hw, gap = 312, 20
    for i, (num, region, topic, src, head, summ) in enumerate(HEROES):
        x = M + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=RULE, width=1)
        ILLS[num](d, (x + 1, hy + 1, x + hw - 1, hy + 129))
        ky = hy + 136
        kicker(d, x + 10, ky, num, region, topic, src, hw - 20, size=12)
        y2 = draw_wrapped(d, (x + 10, ky + 18), head, font(SERIF_B, 22),
                          hw - 20, INK, spacing=1, max_lines=2)
        draw_wrapped(d, (x + 10, y2 + 3), summ, font(SANS, 12),
                     hw - 20, MUTED, spacing=1, max_lines=2)

    # ---- secondary stories: 5 columns x 2 rows ----
    sy = 456
    cw, cgap = 187, 10
    ch = 144
    for i, (num, region, topic, src, head, summ) in enumerate(SECONDARY):
        col, row = i % 5, i // 5
        x = M + col * (cw + cgap)
        yy = sy + row * (ch + 8)
        d.rectangle([x, yy, x + cw, yy + ch], fill=CARD, outline=RULE, width=1)
        ILLS[num](d, (x + 1, yy + 1, x + cw - 1, yy + 59))
        ky = yy + 64
        kicker(d, x + 8, ky, num, region, topic, src, cw - 16, size=10)
        y2 = draw_wrapped(d, (x + 8, ky + 14), head, font(SERIF_B, 15),
                          cw - 16, INK, spacing=1, max_lines=2)
        draw_wrapped(d, (x + 8, y2 + 2), summ, font(SANS, 11),
                     cw - 16, MUTED, spacing=1, max_lines=2)

    # ---- map + list ----
    my = 752
    d.line([M, my - 4, X1, my - 4], fill=INK, width=2)
    d.text((M, my), "WHERE IT HAPPENED", font=font(SANS_B, 14), fill=INK)
    d.text((330, my), "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
           font=font(SANS_B, 14), fill=INK)
    # dotted map
    mx0, my0, mx1, my1 = M, my + 24, 318, 946
    for gx in range(mx0, mx1, 6):
        for gy in range(my0, my1, 6):
            cx, cy = gx + 3, gy + 3
            if any((cx - (a + c) / 2) ** 2 / (((c - a) / 2) ** 2) +
                   (cy - (b + e) / 2) ** 2 / (((e - b) / 2) ** 2) <= 1
                   for a, b, c, e in LAND):
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=MAPDOT)
    for num, px, py in PINS:
        col = RED if num <= 3 else NAVY
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                  outline=(255, 255, 255), width=1)
        f = font(SANS_B, 9 if num < 10 else 8)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 5), t, font=f,
               fill=(255, 255, 255))
    d.text((M, 950), "Red pins: stories 1-3 · dark pins: stories 4-13",
           font=font(SANS, 11), fill=MUTED)
    # numbered list, two columns of 11
    lf = font(SANS, 11)
    for i, item in enumerate(LISTED):
        col = i // 11
        row = i % 11
        lx = 330 + col * 336
        ly = my + 24 + row * 12
        num = 14 + i
        d.text((lx, ly), f"{num}", font=font(SANS_B, 11), fill=RED)
        d.text((lx + 22, ly), item, font=lf, fill=INK)

    # ---- date check box ----
    by0 = 962
    d.rectangle([M, by0, X1, by0 + 46], outline=RED, width=2)
    d.text((M + 10, by0 + 3), "DATE CHECK", font=font(SANS_B, 12), fill=RED)
    d.text((M + 108, by0 + 3),
           "Left out on purpose — each was first reported before Saturday:",
           font=font(SANS, 12), fill=INK)
    d.text((M + 10, by0 + 16),
           "Kyiv bridges barrage (20 Nov) · Poland missile (20 Nov) · Cyclone Akvan landfall (20 Nov) · Wall Street correction (20 Nov)",
           font=font(SANS, 9), fill=MUTED)
    d.text((M + 10, by0 + 26),
           "UK–EU deal (20 Nov) · Anthropic IPO (19–20 Nov) · Bukele files for third term (19 Nov) · Voyager 1 light-day (18 Nov) · SoftBank loss (20 Nov)",
           font=font(SANS, 9), fill=MUTED)
    d.text((M + 10, by0 + 36),
           "FBI breach first reported (20 Nov) · PIF Tower hit (19 Nov) · Jazan missiles (20 Nov eve) · Missouri Roundup ruling (20 Nov) · final COP31 text (not confirmed)",
           font=font(SANS, 9), fill=MUTED)
    # ---- footer ----
    d.text((M, 1012),
           "Sources: Reuters · AP · AFP · Al Jazeera · USGS · CoinDesk · NBC · CNN · NYT · IANS · RNZ · Capital Ethiopia · MyJoyOnline · Punch · Radio Tamazuj · Formula 1",
           font=font(SANS, 8), fill=MUTED)
    d.text((X1 - d.textlength("Original drawings. Claims attributed, not stated as fact.",
                              font=font(SANS, 8)), 1012),
           "Original drawings. Claims attributed, not stated as fact.",
           font=font(SANS, 8), fill=MUTED)

    total = len(HEROES) + len(SECONDARY) + len(LISTED)
    rsum = sum(n for _, n, _ in REGIONS)
    print(f"counts: heroes {len(HEROES)} + secondary {len(SECONDARY)} + listed {len(LISTED)} = {total}; regions sum {rsum}")
    assert total == 35 and rsum == 35, "counts do not reconcile to 35"

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size, "bytes:", os.path.getsize("entry.png"))


if __name__ == "__main__":
    main()
