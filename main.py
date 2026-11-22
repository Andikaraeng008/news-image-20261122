#!/usr/bin/env python3
"""The World Today - Sunday 22 November 2026, in one image.

Draws a 1024x1024 newspaper front page summarising the day's world news.
Pure Pillow drawing: no network, no external assets, fully deterministic.
Writes to $MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CONTENT_W = W - 2 * MARGIN

# --- palette: broadsheet newsprint, deep navy + signal red + gold ---
PAPER = (247, 244, 236)
INK = (18, 22, 30)
NAVY = (16, 35, 63)
NAVY_LIGHT = (31, 58, 95)
RED = (178, 34, 34)
GOLD = (198, 158, 74)
TEAL = (23, 84, 96)
TEAL_DARK = (14, 58, 68)
SEA = (27, 96, 110)
SEA_DARK = (16, 66, 80)
SKY = (214, 230, 232)
GREY = (92, 98, 108)
LIGHT_LINE = (205, 198, 184)
CARD_BG = (255, 255, 255)
FOOT = (84, 88, 96)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap by pixel width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def para(draw, xy, text, fnt, fill, width, leading=None):
    """Draw wrapped paragraph, return y after last line."""
    x, y = xy
    leading = leading or int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, color=RED):
    f = SANS_B(13)
    draw.text((x, y), text.upper(), font=f, fill=color)
    return y + 20


def rule(draw, x, y, w, color=INK, width=2):
    draw.line([(x, y), (x + w, y)], fill=color, width=width)


def draw_sea_scene(draw, box):
    """Stylised Gulf of Finland: dusk sea, cargo ship, two drones, blast."""
    x0, y0, x1, y1 = box
    # dusk sky
    draw.rectangle([x0, y0, x1, y0 + 118], fill=(58, 84, 110))
    draw.rectangle([x0, y0 + 118, x1, y1], fill=SEA_DARK)
    # low sun
    cx, cy = x0 + 96, y0 + 62
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(232, 176, 92))
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(240, 200, 120))
    # distant coastline
    draw.polygon([(x0, y0 + 118), (x0 + 150, y0 + 96), (x0 + 300, y0 + 112),
                  (x0 + 430, y0 + 92), (x1, y0 + 108), (x1, y0 + 118)],
                 fill=(38, 60, 78))
    # sea bands
    for i, yy in enumerate(range(y0 + 128, y1 - 8, 26)):
        shade = SEA if i % 2 == 0 else SEA_DARK
        draw.rectangle([x0, yy, x1, yy + 13], fill=shade)
    # wave strokes
    for yy in range(y0 + 150, y1 - 10, 34):
        for xx in range(x0 + 12, x1 - 60, 96):
            draw.arc([xx, yy, xx + 56, yy + 16], 200, 340, fill=(150, 200, 205), width=2)
    # cargo ship (centre-left)
    sx, sy = x0 + 150, y0 + 208
    draw.polygon([(sx, sy), (sx + 250, sy), (sx + 228, sy + 34),
                  (sx + 22, sy + 34)], fill=(52, 58, 66))          # hull
    draw.rectangle([sx + 8, sy - 6, sx + 242, sy], fill=(70, 76, 84))  # deck
    for i, col in enumerate([(178, 74, 52), (74, 110, 130), (198, 158, 74),
                             (120, 130, 110), (150, 60, 60)]):
        draw.rectangle([sx + 18 + i * 44, sy - 44, sx + 56 + i * 44, sy - 6],
                       fill=col, outline=(30, 34, 40))
    draw.rectangle([sx + 214, sy - 66, sx + 238, sy - 6], fill=(220, 222, 226),
                   outline=(30, 34, 40))                            # bridge
    draw.rectangle([sx + 60, sy - 58, sx + 74, sy - 44], fill=(200, 90, 60))  # funnel
    # blast above the stern
    bx, by = sx + 46, sy - 78
    star = []
    import math
    for k in range(16):
        ang = math.pi * k / 8
        r = 34 if k % 2 == 0 else 15
        star.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    draw.polygon(star, fill=(240, 140, 40))
    draw.polygon([(bx - 12, by - 6), (bx + 12, by - 6), (bx, by + 12)],
                 fill=(250, 210, 90))
    # smoke
    for dx, dy, r in [(-16, -96, 12), (2, -104, 15), (20, -94, 10)]:
        draw.ellipse([bx + dx - r, by + dy - r, bx + dx + r, by + dy + r],
                     fill=(90, 92, 96))
    # drones with dashed approach paths
    for dx, dy in [(x0 + 430, y0 + 96), (x0 + 478, y0 + 128)]:
        draw.ellipse([dx - 7, dy - 5, dx + 7, dy + 5], fill=(20, 24, 32))
        draw.line([(dx - 12, dy), (dx + 12, dy)], fill=(20, 24, 32), width=2)
        draw.line([(dx, dy - 9), (dx, dy + 9)], fill=(20, 24, 32), width=2)
    for x in range(x0 + 300, x0 + 424, 18):
        draw.line([(x, y0 + 132), (x + 8, y0 + 132)], fill=(220, 222, 226), width=2)
    # caption tag inside the picture
    tag = "GULF OF FINLAND  ·  21 NOV"
    tf = SANS_B(12)
    tw = draw.textlength(tag, font=tf)
    draw.rectangle([x0 + 10, y1 - 34, x0 + 22 + tw, y1 - 10], fill=(12, 18, 28))
    draw.text((x0 + 16, y1 - 31), tag, font=tf, fill=(240, 240, 238))


def card(draw, box, kick, head, deck, accent=RED, head_size=21, deck_size=15):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=LIGHT_LINE, width=1)
    draw.rectangle([x0, y0, x1, y0 + 5], fill=accent)
    x = x0 + 14
    y = y0 + 16
    y = kicker(draw, x, y, kick, color=accent)
    y = para(draw, (x, y + 2), head, SANS_B(head_size), INK, x1 - x - 14,
             leading=head_size + 7)
    para(draw, (x, y + 6), deck, SANS(deck_size), (52, 56, 64),
         x1 - x - 14, leading=deck_size + 6)


def mini(draw, box, kick, head, deck):
    x0, y0, x1, y1 = box
    x = x0 + 2
    y = y0
    f = SANS_B(11)
    draw.text((x, y), kick.upper(), font=f, fill=RED)
    y += 17
    y = para(draw, (x, y), head, SANS_B(14), INK, x1 - x - 2, leading=17)
    para(draw, (x, y + 3), deck, SANS(12), (52, 56, 64), x1 - x - 2, leading=15)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 112], fill=NAVY)
    d.rectangle([0, 112, W, 116], fill=GOLD)
    d.text((MARGIN, 18), "THE WORLD TODAY", font=SERIF_B(52), fill=(250, 248, 242))
    right = "SUNDAY 22 NOVEMBER 2026"
    d.text((W - MARGIN - d.textlength(right, font=SANS_B(21)), 30),
           right, font=SANS_B(21), fill=(240, 200, 120))
    sub = "ONE DAY  ·  ONE IMAGE  ·  THE WORLD IN BRIEF"
    d.text((W - MARGIN - d.textlength(sub, font=SANS(13)), 62),
           sub, font=SANS(13), fill=(190, 200, 214))
    d.text((MARGIN, 82), "A front page drawn from the day's news — 12 stories",
           font=SANS(13), fill=(170, 182, 198))

    # ---------- lead story ----------
    ly = 132
    pic = (MARGIN, ly, MARGIN + 560, ly + 318)
    draw_sea_scene(d, pic)
    lx = MARGIN + 584
    lw = W - MARGIN - lx
    y = ly + 2
    y = kicker(d, lx, y, "Lead  ·  The Baltic")
    y = para(d, (lx, y + 4),
             "Drones strike Russian cargo ship in the Gulf of Finland",
             SANS_B(31), INK, lw, leading=37)
    y = para(d, (lx, y + 8),
             "Two drones hit the Sparta II, a vessel linked to Russia's "
             "military, sailing from St Petersburg to Kaliningrad. Its crew "
             "was evacuated; the ship lies anchored off Loviisa.",
             SANS(16), (52, 56, 64), lw, leading=22)
    rule(d, lx, y + 10, lw, color=LIGHT_LINE, width=1)
    y = para(d, (lx, y + 20),
             "\u201cWar is spilling over into our immediate vicinity.\u201d",
             SERIF(16), NAVY, lw, leading=22)
    d.text((lx, y + 4), "— PETTERI ORPO, PRIME MINISTER OF FINLAND",
           font=SANS_B(11), fill=GREY)

    # ---------- row of three ----------
    ry = 466
    rh = 180
    cw = (CONTENT_W - 2 * 16) // 3
    cards = [
        ("Poland", "Missiles crash in Poland as Russia bombards Ukraine",
         "Warsaw calls it a likely \u201cintentional provocation\u201d; jets "
         "scrambled, NATO allies alerted.", RED),
        ("Ceasefire", "Zelensky offers local truces; Melania hopes for one by Christmas",
         "Kyiv proposes ceasefires to evacuate 15 Dnipro villages. The US "
         "first lady: \u201cI'm in talks already.\u201d", TEAL),
        ("APEC summit", "Trump calls Putin \u201cmy friend\u201d; Zelensky calls him a \u201ckiller\u201d",
         "The Shenzhen trilateral with Xi ends with no Ukraine plan; "
         "Trump: talks are \u201cstuck in the mud\u201d.", NAVY_LIGHT),
    ]
    for i, (kick, head, deck, acc) in enumerate(cards):
        x0 = MARGIN + i * (cw + 16)
        card(d, (x0, ry, x0 + cw, ry + rh), kick, head, deck, accent=acc,
             head_size=20, deck_size=14)

    # ---------- row of three ----------
    ry2 = 660
    cards2 = [
        ("Ukraine", "Double-tap strike kills boy, 7, and paramedic in Kryvyi Rih",
         "Two Russian missiles hit a crowded area on World Children's Day; "
         "52 people were wounded.", RED),
        ("The Gulf", "Tankers hit off Oman as Hormuz shipping war grinds on",
         "UKMTO confirms projectile strikes on two tankers near Khasab. "
         "Brent crude holds near $91.", TEAL),
        ("COP31", "Climate talks in overtime as fossil-fuel pledge is dropped",
         "The Antalya draft drops any phase-out language. Current plans "
         "still point to 2.6\u00b0C of warming.", NAVY_LIGHT),
    ]
    for i, (kick, head, deck, acc) in enumerate(cards2):
        x0 = MARGIN + i * (cw + 16)
        card(d, (x0, ry2, x0 + cw, ry2 + rh), kick, head, deck, accent=acc,
             head_size=20, deck_size=14)

    # ---------- bottom band: five briefs ----------
    by = 872
    rule(d, MARGIN, by - 12, CONTENT_W, color=INK, width=2)
    d.text((MARGIN, by - 2), "ALSO TODAY", font=SANS_B(13), fill=INK)
    mw = (CONTENT_W - 4 * 14) // 5
    minis = [
        ("Estonia", "Border with Russia to shut",
         "Tallinn closes road crossings for six months; Moscow cries "
         "\u201cIron Curtain\u201d."),
        ("Denmark", "Russian attach\u00e9 expelled",
         "Copenhagen acts over an alleged plot to kill a US-Ukrainian "
         "citizen."),
        ("United States", "Airlines warned before Thanksgiving",
         "FBI, DHS and TSA alert carriers to al-Qaeda hijacking calls; no "
         "specific threat."),
        ("Sport", "Australia edge England at the death",
         "Hosts chase 188 to win the T20 by three wickets; India A crush "
         "Nepal by 306."),
        ("India", "Modi opens Nitish Setu bridge",
         "The Patna\u2013Vaishali link opens as Cyclone Akvan cancels 14 "
         "flights at Ranchi."),
    ]
    for i, (kick, head, deck) in enumerate(minis):
        x0 = MARGIN + i * (mw + 14)
        if i:
            d.line([(x0 - 7, by + 18), (x0 - 7, by + 96)], fill=LIGHT_LINE, width=1)
        mini(d, (x0, by + 18, x0 + mw, by + 116), kick, head, deck)

    # ---------- footer ----------
    fy = 996
    rule(d, MARGIN, fy, CONTENT_W, color=LIGHT_LINE, width=1)
    foot = ("MARKETS (FRI)  ·  S&P 500 \u22123.7%   Nasdaq \u22125.3%   "
            "Brent \u2248 $91   ·   12 STORIES   ·   SOURCES: AP · REUTERS · ISW · UKMTO")
    d.text((MARGIN, fy + 8), foot, font=SANS(12), fill=FOOT)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img.save(path, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
