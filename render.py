#!/usr/bin/env python3
"""Render the front page for 26 November 2026 as a 1024x1024 PNG.

Deterministic by construction: fixed geometry, no randomness, no clocks,
no network. Every text block is measured before it is drawn and the build
fails (assert) rather than silently shrinking or clipping text.

Layout (1024x1024, 24px margins, 16px gutters):
  masthead + folio line | LEAD: Hormuz supertanker | second row:
  US tariffs bar chart + Kyiv strike scene | ALSO strip (3 one-line
  heads) | bottom rail (3 short briefs).
"""

import hashlib
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
GUTTER = 16
INNER = W - 2 * MARGIN  # 976

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 32, 32)
GREY = (88, 88, 88)
RULE = (70, 70, 70)
SKY_TOP = (38, 48, 74)
SKY_BOT = (214, 122, 54)
SEA = (16, 42, 66)
SEA_DARK = (10, 30, 50)
FLAME = (255, 140, 0)
FLAME_HOT = (255, 210, 60)
SMOKE = (90, 90, 96)
BAR = (34, 84, 140)
BAR_HI = (176, 32, 32)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns lines that all fit max_w (asserted)."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        assert draw.textlength(line, font=fnt) <= max_w, (
            "wrapped line too wide: %r" % line)
    return lines


def draw_lines(draw, lines, fnt, x, y, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_hormuz(draw, x0, y0, x1, y1):
    """Burning supertanker at dusk in the Strait of Hormuz."""
    w, h = x1 - x0, y1 - y0
    horizon = y0 + int(h * 0.52)
    # Sky: dusk gradient in bands.
    bands = 24
    for i in range(bands):
        t = i / (bands - 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        yy0 = y0 + int(h * 0.52 * i / bands)
        yy1 = y0 + int(h * 0.52 * (i + 1) / bands) + 1
        draw.rectangle([x0, yy0, x1, yy1], fill=(r, g, b))
    # Low sun disc, half-sunk.
    cx, cy, r = x0 + int(w * 0.78), horizon - 6, 26
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 196, 90))
    # Sea.
    draw.rectangle([x0, horizon, x1, y1], fill=SEA)
    draw.rectangle([x0, horizon + 26, x1, y1], fill=SEA_DARK)
    # Sun glitter on the water.
    for i, gx in enumerate((0.72, 0.76, 0.80, 0.84)):
        gw = 34 - i * 6
        gy = horizon + 8 + i * 12
        draw.rectangle([x0 + int(w * gx) - gw // 2, gy,
                        x0 + int(w * gx) + gw // 2, gy + 3],
                       fill=(255, 196, 90))
    # Tanker hull (dark silhouette) with red waterline.
    hx0, hx1 = x0 + int(w * 0.10), x0 + int(w * 0.62)
    hy0, hy1 = horizon - 34, horizon + 16
    draw.rectangle([hx0, hy0, hx1, hy1], fill=(20, 20, 24))
    draw.rectangle([hx0, hy1 - 6, hx1, hy1], fill=(140, 30, 30))
    # Bow.
    draw.polygon([(hx1, hy0), (hx1 + 44, hy0 + 22),
                  (hx1, hy1)], fill=(20, 20, 24))
    # Superstructure + funnel.
    draw.rectangle([hx0 + 26, hy0 - 34, hx0 + 96, hy0], fill=(24, 24, 28))
    draw.rectangle([hx0 + 108, hy0 - 52, hx0 + 132, hy0], fill=(24, 24, 28))
    draw.rectangle([hx0 + 108, hy0 - 52, hx0 + 132, hy0 - 40],
                   fill=(176, 32, 32))
    # Deck containers.
    for i in range(4):
        cx0 = hx0 + 150 + i * 62
        draw.rectangle([cx0, hy0 - 16, cx0 + 52, hy0], fill=(52, 52, 58))
    # Smoke columns (drawn first, so the flames rise in front of them).
    for (sx, sy, sr) in ((0.30, 0.10, 22), (0.36, 0.05, 26),
                         (0.42, 0.09, 20), (0.33, 0.02, 15)):
        draw.ellipse([x0 + int(w * sx) - sr, y0 + int(h * sy) - sr,
                      x0 + int(w * sx) + sr, y0 + int(h * sy) + sr],
                     fill=SMOKE)
    # Flames: layered triangles + cores above the mid-deck. Heights are
    # capped so the tips stay inside the scene (deck top is ~y0+68).
    fx = x0 + int(w * 0.36)
    for (dx, fh, fw, col) in ((-46, 48, 54, FLAME), (0, 58, 66, FLAME_HOT),
                              (46, 52, 56, FLAME), (-18, 40, 34, FLAME_HOT)):
        draw.polygon([(fx + dx - fw // 2, hy0 - 8),
                      (fx + dx, hy0 - 8 - fh),
                      (fx + dx + fw // 2, hy0 - 8)], fill=col)
    # Sea mines: spiked circles in the foreground water.
    for (mx, my, mr) in ((0.70, 0.72, 10), (0.82, 0.80, 9), (0.58, 0.84, 8)):
        px, py = x0 + int(w * mx), y0 + int(h * my)
        for ang in range(0, 360, 45):
            import math
            dx = math.cos(math.radians(ang)) * (mr + 4)
            dy = math.sin(math.radians(ang)) * (mr + 4)
            draw.line([(px, py), (px + dx, py + dy)], fill=(8, 8, 10),
                      width=3)
        draw.ellipse([px - mr, py - mr, px + mr, py + mr], fill=(12, 12, 14))
    # Label plate, bottom-left of the scene.
    label = "STRAIT OF HORMUZ"
    lf = font(SANS_B, 17)
    lw = draw.textlength(label, font=lf)
    pad = 10
    draw.rectangle([x0 + 10, y1 - 40, x0 + 10 + lw + 2 * pad, y1 - 10],
                   fill=(17, 17, 17))
    draw.text((x0 + 10 + pad, y1 - 36), label, font=lf,
              fill=(255, 255, 255))


def draw_kyiv(draw, x0, y0, x1, y1):
    """Night skyline under a missile strike: dark sky, lit windows,
    one explosion burst."""
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(18, 22, 38))
    # Stars.
    for (sx, sy) in ((0.08, 0.12), (0.22, 0.06), (0.35, 0.16), (0.55, 0.08),
                     (0.72, 0.14), (0.88, 0.06), (0.94, 0.22), (0.45, 0.24)):
        draw.ellipse([x0 + int(w * sx) - 1, y0 + int(h * sy) - 1,
                      x0 + int(w * sx) + 1, y0 + int(h * sy) + 1],
                     fill=(220, 220, 235))
    # Explosion burst in the sky first, so the rooftops occlude its base
    # and it reads as a blast behind the skyline, not a sun on it.
    ex, ey = x0 + int(w * 0.62), y0 + int(h * 0.20)
    for (r, col) in ((26, FLAME), (17, FLAME_HOT), (9, (255, 240, 180))):
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    for ang in range(0, 360, 30):
        import math
        dx = math.cos(math.radians(ang)) * 34
        dy = math.sin(math.radians(ang)) * 34
        draw.line([(ex, ey), (ex + dx, ey + dy)], fill=FLAME, width=3)
    # Buildings.
    base = y1 - 8
    bx = x0 + 6
    heights = (0.42, 0.62, 0.50, 0.74, 0.56, 0.66, 0.46)
    widths = (0.13, 0.12, 0.14, 0.13, 0.12, 0.14, 0.12)
    for bh, bw in zip(heights, widths):
        bw_px = int(w * bw)
        bh_px = int(h * bh)
        draw.rectangle([bx, base - bh_px, bx + bw_px, base],
                       fill=(34, 36, 52))
        # Lit windows.
        for wy in range(base - bh_px + 10, base - 8, 18):
            for wx in range(bx + 8, bx + bw_px - 8, 16):
                if (wx + wy) % 3 == 0:
                    draw.rectangle([wx, wy, wx + 6, wy + 8],
                                   fill=(255, 200, 90))
        bx += bw_px + 4
    # Falling trail dots (drones).
    for (tx, ty) in ((0.78, 0.30), (0.84, 0.38), (0.70, 0.22)):
        draw.ellipse([x0 + int(w * tx) - 3, y0 + int(h * ty) - 3,
                      x0 + int(w * tx) + 3, y0 + int(h * ty) + 3],
                     fill=(255, 220, 120))


def draw_bars(draw, x0, y0, x1, y1, data):
    """Horizontal bars: (label, value, highlight). Values are percents."""
    maxv = max(v for _, v, _ in data)
    row_h = (y1 - y0) // len(data)
    lf = font(SANS_B, 17)
    vf = font(SANS_B, 17)
    for i, (label, value, hot) in enumerate(data):
        ry = y0 + i * row_h
        draw.text((x0, ry + 2), label, font=lf, fill=INK)
        bar_x0 = x0 + 108
        bar_w = int((x1 - 52 - bar_x0) * value / maxv)
        draw.rectangle([bar_x0, ry + 4, bar_x0 + bar_w, ry + 22],
                       fill=BAR_HI if hot else BAR)
        draw.text((bar_x0 + bar_w + 8, ry + 2), "%d%%" % value,
                  font=vf, fill=INK)
    return y1


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    y = MARGIN

    # ---- Masthead -----------------------------------------------------
    mast = font(SERIF_B, 76)
    title = "THE WORLD"
    tw = draw.textlength(title, font=mast)
    assert tw <= INNER, "masthead too wide"
    draw.text(((W - tw) / 2, y), title, font=mast, fill=INK)
    y += 92
    hline(draw, x0, x1, y, width=3)
    y += 8
    folio = font(SANS_B, 16)
    left = "THURSDAY, 26 NOVEMBER 2026"
    right = "ONE DAY — ONE PAGE"
    assert draw.textlength(left, font=folio) <= INNER // 2
    assert draw.textlength(right, font=folio) <= INNER // 2
    draw.text((x0, y), left, font=folio, fill=INK)
    rw = draw.textlength(right, font=folio)
    draw.text((x1 - rw, y), right, font=folio, fill=INK)
    y += 26
    hline(draw, x0, x1, y, width=2)
    y += 14

    # ---- LEAD: Hormuz -------------------------------------------------
    kick = font(SANS_B, 16)
    draw.text((x0, y), "THE STRAIT OF HORMUZ  •  OIL ON FIRE",
              font=kick, fill=RED)
    y += 26
    head = font(SERIF_B, 64)
    headline = ["TANKERS BURN", "IN HORMUZ"]
    for line in headline:
        hw = draw.textlength(line, font=head)
        assert hw <= INNER, "lead headline too wide: %d" % hw
    y = draw_lines(draw, headline, head, x0, y, INK, 74)
    scene_y0, scene_y1 = y, y + 196
    draw_hormuz(draw, x0, scene_y0, x1, scene_y1)
    y = scene_y1 + 12
    sub = font(SERIF, 21)
    sub_lines = wrap(
        draw,
        "Iran vows the strait stays shut as mines hit a supertanker "
        "carrying two million barrels of crude; a second tanker burns "
        "and a blast is reported west of Dubai.",
        sub, INNER)
    assert len(sub_lines) <= 2, "lead subhead wraps to %d lines" % len(sub_lines)
    y = draw_lines(draw, sub_lines, sub, x0, y, INK, 28)
    y += 6
    hline(draw, x0, x1, y, width=2)
    y += 14

    # ---- Second row: tariffs | Kyiv ------------------------------------
    col_w = (INNER - GUTTER) // 2
    c0, c1 = x0, x0 + col_w
    row_y = y
    # Left: tariffs.
    sec = font(SERIF_B, 30)
    t_lines = wrap(draw, "AMERICA'S TARIFF WALL", sec, col_w)
    assert len(t_lines) <= 2
    y2 = draw_lines(draw, t_lines, sec, c0, row_y, INK, 36)
    y2 += 4
    cap = font(SANS, 15)
    y2 = draw_lines(
        draw,
        wrap(draw, "Washington proposes duties on 14 nations",
             cap, col_w), cap, c0, y2, GREY, 19)
    y2 += 6
    draw_bars(draw, c0, y2, c0 + col_w, y2 + 96,
              [("China", 20, False), ("India", 25, False),
               ("Vietnam", 35, True), ("EU · Japan", 15, False)])
    # Right: Kyiv.
    k_lines = wrap(draw, "MISSILES HIT KYIV MALL", sec, col_w)
    assert len(k_lines) <= 2
    y3 = draw_lines(draw, k_lines, sec, c1, row_y, INK, 36)
    y3 += 4
    y3 = draw_lines(
        draw,
        wrap(draw, "Russia fires 113 drones at Ukraine's cities",
             cap, col_w), cap, c1, y3, GREY, 19)
    y3 += 6
    draw_kyiv(draw, c1, y3, c1 + col_w, y3 + 96)
    y3 += 96
    y3 = draw_lines(
        draw,
        wrap(draw, "7 hurt in Kyiv, 3 killed in Kharkiv",
             font(SANS_B, 15), col_w), font(SANS_B, 15), c1, y3 + 6,
        INK, 19)
    y = max(y2 + 96, y3) + 10
    hline(draw, x0, x1, y, width=2)
    y += 12

    # ---- ALSO strip ----------------------------------------------------
    also = font(SANS_B, 16)
    draw.text((x0, y), "ALSO TODAY", font=also, fill=RED)
    y += 26
    small = font(SERIF_B, 20)
    assert 20 >= 18, "small headline below Gate 1 minimum"
    items = [
        ("Cairo tanker blast kills 31", FLAME),
        ("Macy's parade delayed — first in 100 years", BAR),
        ("Gaza strikes kill 9 despite ceasefire", RED),
    ]
    third = INNER // 3
    for i, (text, dot) in enumerate(items):
        ix = x0 + i * third
        draw.ellipse([ix, y + 6, ix + 10, y + 16], fill=dot)
        lines = wrap(draw, text, small, third - 24)
        assert len(lines) <= 2, "also head wraps to %d" % len(lines)
        draw_lines(draw, lines, small, ix + 18, y, INK, 25)
    y += 52
    hline(draw, x0, x1, y, width=2)
    y += 10

    # ---- Bottom rail: briefs -------------------------------------------
    brief = font(SANS, 14)
    assert 14 >= 13, "brief below Gate 1 minimum"
    briefs = [
        "Netanyahu trial: judges urge bribery charge dropped",
        "Solomon Islands signs Australia security treaty",
        "UK migration lowest since 1997",
    ]
    for i, text in enumerate(briefs):
        bx = x0 + i * third
        lines = wrap(draw, text, brief, third - 16)
        assert len(lines) <= 2, "brief wraps to %d" % len(lines)
        draw_lines(draw, lines, brief, bx, y, GREY, 18)
    y += 40
    hline(draw, x0, x1, y, width=3)
    assert y <= H - MARGIN, "page overflow: y=%d" % y

    img.save("entry.png", optimize=True)
    data = open("entry.png", "rb").read()
    print("entry.png: %dx%d, %d bytes, sha256 %s"
          % (W, H, len(data), hashlib.sha256(data).hexdigest()))
    assert len(data) <= 1048576, "image over 1 MiB"
    return 0


if __name__ == "__main__":
    sys.exit(main())
