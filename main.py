#!/usr/bin/env python3
# "The World in One Day" - Friday 20 November 2026.
# A one-page broadsheet: 48 stories, drawn from scratch with PIL.
# Layout: two-line masthead, numbers strip, UTC timeline, region strip,
# three stacked heroes down the left, map + briefs rail on the right,
# pictured grid in rows of 4 / 5 / 4, date check, footer.
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W = 1600
H = 1600
M = 56
CW = W - 2 * M

PAPER = (247, 243, 233)
INK = (26, 24, 20)
NAVY = (18, 42, 84)
NAVY_DK = (12, 30, 62)
RED = (168, 32, 40)
TEAL = (18, 110, 110)
OCHRE = (176, 120, 30)
GREEN = (46, 110, 60)
GREY = (96, 92, 84)
LIGHT = (232, 226, 212)
RULE = (26, 24, 20)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def _load_font(candidates, size):
    for cand in candidates:
        try:
            return ImageFont.truetype(cand, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def F(name, size):
    return _load_font([FD + name, name], size)


def FLF(name, size):
    return _load_font([FL + name, FD + name, name], size)


SANS = "DejaVuSans.ttf"
BOLD = "DejaVuSans-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SERIFB = "LiberationSerif-Bold.ttf"
SERIFI = "LiberationSerif-Italic.ttf"


def wrap(d, text, font, width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, width, leading, fill, max_lines=None,
               align="left"):
    lines = wrap(d, text, font, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        if align == "center":
            lx = x + (width - d.textlength(line, font=font)) / 2
        elif align == "right":
            lx = x + width - d.textlength(line, font=font)
        else:
            lx = x
        d.text((lx, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_text(d, text, font_names, sizes, width, max_lines, fill, x, y,
             leading_ratio=1.12):
    for size in sizes:
        font = FLF(font_names, size)
        lines = wrap(d, text, font, width)
        if len(lines) <= max_lines:
            return text_block(d, x, y, text, font, width,
                              size * leading_ratio, fill,
                              max_lines=max_lines)
    font = FLF(font_names, sizes[-1])
    return text_block(d, x, y, text, font, width, sizes[-1] * leading_ratio,
                      fill, max_lines=max_lines)


# ---------------------------------------------------------------- scenes
# Each motif draws a small flat illustration inside (x, y, w, h).
def skyline(d, x, y, w, h, base, tops, fill):
    for i, t in enumerate(tops):
        bw = w / len(tops)
        bx = x + i * bw + 2
        bh = h * t
        d.rectangle([bx, y + h - bh, bx + bw - 4, y + h], fill=fill)
        if i % 3 == 0:
            d.rectangle([bx + bw / 2 - 2, y + h - bh - 8, bx + bw / 2 + 2,
                         y + h - bh], fill=fill)


def sun_disc(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    for k in range(8):
        a = math.pi * k / 4
        x0 = cx + math.cos(a) * (r + 4)
        y0 = cy + math.sin(a) * (r + 4)
        x1 = cx + math.cos(a) * (r + 12)
        y1 = cy + math.sin(a) * (r + 12)
        d.line([x0, y0, x1, y1], fill=fill, width=3)


def draw_scene(d, x, y, w, h, motif):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 96))
    if motif == "storm":
        for i in range(6):
            yy = y + i * (h / 6)
            d.rectangle([x, yy, x + w, yy + h / 12], fill=(44, 84, 110))
        d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(16, 44, 60))
        cx, cy, r = x + w * 0.62, y + h * 0.42, min(w, h) * 0.26
        for k in range(3):
            d.arc([cx - r + k * 6, cy - r + k * 6, cx + r - k * 6,
                   cy + r - k * 6], 20, 300, fill=(240, 244, 248), width=4)
        for i in range(14):
            rx = x + (i * 37) % w
            ry = y + (i * 23) % int(h * 0.7)
            d.line([rx, ry, rx - 6, ry + 12], fill=(180, 210, 225), width=2)
        for i in range(5):
            wx = x + i * (w / 5) + 8
            d.arc([wx, y + h - 16, wx + 26, y + h + 6], 180, 360,
                  fill=(150, 190, 205), width=3)
    elif motif == "missile":
        for i in range(5):
            d.rectangle([x, y + i * (h / 5), x + w, y + (i + 1) * (h / 5)],
                        fill=(16 + i * 6, 22 + i * 5, 46 + i * 4))
        rnd = random.Random(11)
        for _ in range(22):
            sx = x + rnd.random() * w
            sy = y + rnd.random() * h * 0.5
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(230, 230, 240))
        skyline(d, x, y + h * 0.45, w, h * 0.55,
                (0, 0, 0), [0.5, 0.8, 0.4, 0.9, 0.6, 0.35, 0.75],
                (10, 14, 30))
        mx, my = x + w * 0.72, y + h * 0.42
        d.line([x + w * 0.1, y + h * 0.9, mx, my], fill=(255, 150, 40),
               width=4)
        sun_disc(d, mx, my, 11, (255, 120, 30))
        d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(8, 10, 22))
    elif motif == "flags":
        d.rectangle([x, y, x + w, y + h], fill=(52, 84, 140))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(24, 32, 54))
        skyline(d, x, y + h * 0.5, w, h * 0.5,
                (0, 0, 0), [0.6, 0.9, 0.5, 0.75, 0.95, 0.45],
                (16, 22, 40))
        poles = [0.18, 0.5, 0.82]
        flagcols = [[(200, 40, 40), (240, 240, 240)],
                    [(210, 30, 30), (255, 220, 0)],
                    [(240, 240, 240), (30, 80, 200), (210, 30, 30)]]
        for pi, px in enumerate(poles):
            fx = x + w * px
            d.line([fx, y + h * 0.12, fx, y + h * 0.62], fill=(220, 220, 220),
                   width=3)
            fw, fh = w * 0.13, h * 0.11
            for fi, col in enumerate(flagcols[pi]):
                d.rectangle([fx, y + h * 0.12 + fi * fh,
                             fx + fw, y + h * 0.12 + (fi + 1) * fh], fill=col)
    elif motif == "bridge":
        d.rectangle([x, y, x + w, y + h * 0.6], fill=(70, 110, 150))
        d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(24, 68, 96))
        d.line([x, y + h * 0.62, x + w, y + h * 0.62], fill=(240, 240, 235),
               width=4)
        d.arc([x + w * 0.15, y + h * 0.18, x + w * 0.85, y + h * 0.95],
              180, 360, fill=(240, 240, 235), width=4)
        for i in range(5):
            px = x + w * (0.2 + i * 0.15)
            d.line([px, y + h * 0.32 + i * 2, px, y + h * 0.62],
                   fill=(240, 240, 235), width=2)
        d.polygon([(x + w * 0.42, y + h * 0.72), (x + w * 0.58, y + h * 0.72),
                   (x + w * 0.54, y + h * 0.82), (x + w * 0.46, y + h * 0.82)],
                  fill=(180, 60, 40))
    elif motif == "globe":
        d.rectangle([x, y, x + w, y + h], fill=(32, 96, 110))
        cx, cy, r = x + w / 2, y + h / 2, min(w, h) * 0.36
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 130, 170))
        d.ellipse([cx - r * 0.45, cy - r * 0.7, cx + r * 0.15, cy - r * 0.1],
                  fill=(90, 170, 90))
        d.ellipse([cx - r * 0.1, cy + r * 0.15, cx + r * 0.6, cy + r * 0.75],
                  fill=(90, 170, 90))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 240, 240),
                  width=2)
    elif motif == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
        for i in range(5):
            gy = y + 8 + i * (h - 16) / 4
            d.line([x + 6, gy, x + w - 6, gy], fill=(200, 196, 184), width=1)
        pts = [(0.05, 0.3), (0.25, 0.42), (0.45, 0.38), (0.65, 0.62),
               (0.85, 0.72), (0.97, 0.85)]
        prev = None
        for fx, fy in pts:
            px, py = x + w * fx, y + h * fy
            if prev:
                d.line([prev, (px, py)], fill=RED, width=4)
            prev = (px, py)
        for fx, fy in pts:
            d.ellipse([x + w * fx - 4, y + h * fy - 4, x + w * fx + 4,
                       y + h * fy + 4], fill=RED)
        d.rectangle([x + w * 0.86, y + h * 0.72, x + w - 8, y + h - 8],
                    fill=(18, 42, 84))
    elif motif == "game":
        d.rectangle([x, y, x + w, y + h * 0.55], fill=(58, 32, 96))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(22, 16, 40))
        sun_disc(d, x + w * 0.7, y + h * 0.4, min(w, h) * 0.2,
                 (255, 170, 60))
        skyline(d, x, y + h * 0.5, w, h * 0.5,
                (0, 0, 0), [0.5, 0.9, 0.65, 0.4, 0.8, 0.55],
                (14, 10, 32))
        d.rectangle([x + w * 0.08, y + h * 0.62, x + w * 0.3, y + h * 0.78],
                    outline=(120, 220, 200), width=3)
        d.text((x + w * 0.12, y + h * 0.66), "VI", font=F(BOLD, 16),
               fill=(120, 220, 200))
    elif motif == "space":
        d.rectangle([x, y, x + w, y + h], fill=(6, 8, 20))
        rnd = random.Random(23)
        for _ in range(30):
            sx = x + rnd.random() * w
            sy = y + rnd.random() * h
            r = 1 + rnd.random() * 2
            d.ellipse([sx, sy, sx + r, sy + r], fill=(235, 235, 245))
        cx, cy = x + w * 0.62, y + h * 0.5
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(220, 170, 90))
        d.ellipse([cx - 40, cy - 8, cx + 40, cy + 8], outline=(200, 200, 220),
                  width=2)
        d.ellipse([x + w * 0.18 - 5, y + h * 0.3 - 5, x + w * 0.18 + 5,
                   y + h * 0.3 + 5], fill=(150, 200, 235))
        d.line([x + w * 0.18, y + h * 0.3, cx - 20, cy - 10],
               fill=(150, 200, 235), width=2)
    elif motif == "court":
        d.rectangle([x, y, x + w, y + h], fill=(44, 58, 84))
        d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(30, 40, 60))
        for i in range(4):
            cx = x + w * (0.16 + i * 0.23)
            d.rectangle([cx - 7, y + h * 0.3, cx + 7, y + h * 0.78],
                        fill=(225, 220, 205))
            d.rectangle([cx - 14, y + h * 0.24, cx + 14, y + h * 0.3],
                        fill=(225, 220, 205))
        d.rectangle([x + w * 0.06, y + h * 0.16, x + w * 0.94, y + h * 0.24],
                    fill=(225, 220, 205))
    elif motif == "drought":
        d.rectangle([x, y, x + w, y + h * 0.6], fill=(240, 200, 110))
        d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(196, 150, 80))
        sun_disc(d, x + w * 0.72, y + h * 0.28, min(w, h) * 0.2,
                 (255, 140, 40))
        for i in range(4):
            bx = x + w * (0.1 + i * 0.24)
            d.line([bx, y + h * 0.62, bx + 12, y + h * 0.8, bx - 8,
                    y + h * 0.98], fill=(140, 96, 46), width=2)
        d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(150, 104, 52))
    elif motif == "dome":
        d.rectangle([x, y, x + w, y + h], fill=(120, 130, 140))
        d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(70, 78, 84))
        cx, cy, r = x + w / 2, y + h * 0.72, min(w, h) * 0.3
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360,
                   fill=(200, 205, 210))
        d.rectangle([cx - 4, y + h * 0.3, cx + 4, y + h * 0.72],
                    fill=(200, 205, 210))
        for i in range(6):
            fx = x + 8 + i * (w - 16) / 5
            d.line([fx, y + h * 0.72, fx, y + h * 0.95], fill=(40, 44, 48),
                   width=2)
    elif motif == "handshake":
        d.rectangle([x, y, x + w, y + h], fill=(52, 84, 140))
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(30, 48, 84))
        cx, cy = x + w / 2, y + h * 0.45
        d.rectangle([cx - 52, cy - 18, cx - 2, cy + 18], fill=(240, 235, 220))
        d.rectangle([cx + 2, cy - 18, cx + 52, cy + 18], fill=(200, 60, 50))
        for k in range(3):
            ly = cy - 10 + k * 8
            d.line([cx - 46, ly, cx - 10, ly], fill=(120, 116, 108), width=2)
            d.line([cx + 8, ly, cx + 44, ly], fill=(255, 255, 255), width=2)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 210, 60),
                  outline=(120, 90, 20), width=2)
    elif motif == "ship":
        d.rectangle([x, y, x + w, y + h * 0.55], fill=(110, 150, 180))
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(24, 68, 110))
        d.polygon([(x + w * 0.12, y + h * 0.6), (x + w * 0.88, y + h * 0.6),
                   (x + w * 0.78, y + h * 0.82), (x + w * 0.22, y + h * 0.82)],
                  fill=(60, 60, 66))
        d.rectangle([x + w * 0.4, y + h * 0.42, x + w * 0.6, y + h * 0.6],
                    fill=(200, 60, 40))
        for i in range(3):
            wx = x + w * (0.15 + i * 0.3)
            d.arc([wx, y + h * 0.86, wx + 40, y + h + 8], 180, 360,
                  fill=(190, 220, 235), width=3)
        sun_disc(d, x + w * 0.8, y + h * 0.22, 12, (255, 220, 120))
    elif motif == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(70, 140, 70))
        d.rectangle([x + w * 0.36, y, x + w * 0.64, y + h],
                    fill=(210, 190, 140))
        d.line([x + w * 0.5, y, x + w * 0.5, y + h], fill=(255, 255, 255),
               width=2)
        d.ellipse([x + w * 0.72 - 8, y + h * 0.3 - 8, x + w * 0.72 + 8,
                   y + h * 0.3 + 8], fill=(200, 40, 40))
        d.rectangle([x + w * 0.14, y + h * 0.6, x + w * 0.2, y + h * 0.85],
                    fill=(150, 110, 60))
    else:  # generic skyline
        d.rectangle([x, y, x + w, y + h], fill=(70, 96, 130))
        skyline(d, x, y + h * 0.4, w, h * 0.6,
                (0, 0, 0), [0.5, 0.8, 0.6, 0.9, 0.45, 0.7],
                (24, 32, 52))


# ---------------------------------------------------------------- data
TIMELINE = [
    ("Overnight", "Crimean Bridge hit a third time"),
    ("~06:00 UTC", "APEC leaders meet in Shenzhen"),
    ("~10:00 UTC", "Trilateral declaration issued"),
    ("~12:00 UTC", "Akvan makes landfall in Odisha"),
    ("~14:00 UTC", "Houthi missile hits Riyadh KAFD"),
    ("Late", "Wall Street slides; Dow -1,084"),
]

REGIONS = [
    ("EUROPE", 11, (18, 42, 84)),
    ("THE AMERICAS", 7, (168, 32, 40)),
    ("ASIA-PACIFIC", 19, (18, 110, 110)),
    ("MIDEAST", 4, (176, 120, 30)),
    ("AFRICA", 2, (46, 110, 60)),
    ("OCEANIA", 1, (120, 80, 140)),
    ("WORLD", 4, (90, 86, 78)),
]

NUMBERS = [
    ("300,000", "people moved out of Akvan's path"),
    ("423", "rescue teams deployed in Odisha"),
    ("90-100", "km/h winds, gusting to 110"),
    ("-1,084", "Dow points on the day"),
    ("$1.84bn", "GTA VI launch-day sales"),
    ("16bn", "miles out: Voyager 1, one light-day"),
]

HEROES = [
    dict(num=1, kicker="1 \u00b7 ODISHA \u00b7 STORM",
         head="Akvan comes ashore on the Odisha coast",
         dek=("Cyclone Akvan crossed the coast near Gopalpur at noon, winds "
              "90-100 km/h gusting to 110. Three hundred thousand people are "
              "out of harm's way, 423 rescue teams deployed, red alerts in "
              "11 districts."),
         src="IMD \u00b7 THE HINDU", motif="storm"),
    dict(num=2, kicker="2 \u00b7 RIYADH \u00b7 ATTACK",
         head="Houthi missile hits Riyadh's KAFD financial district",
         dek=("A Houthi missile damaged a wealth-fund tower in the financial "
              "district, one of Riyadh's tallest. No casualties are "
              "reported, as air defences answered the strike."),
         src="ARAB NEWS \u00b7 REUTERS", motif="missile"),
    dict(num=3, kicker="3 \u00b7 SHENZHEN \u00b7 DIPLOMACY",
         head="Trump, Xi and Putin issue a joint declaration",
         dek=("No big peace deal from the trilateral's second day. Trump "
              "says the Iran war call waits until 2027, rates the summit "
              "'12 out of 10', and Putin may attend December's G20 in "
              "Miami."),
         src="REUTERS \u00b7 AP", motif="flags"),
]

PICTURED = [
    dict(num=4, kicker="4 \u00b7 KERCH STRAIT \u00b7 WAR",
         head="Crimean Bridge hit a third time this week; rail halted",
         dek=("A Ukrainian naval drone strike disrupted rail traffic on the "
              "bridge. Rail partly resumes; Putin vows retaliation, and "
              "Kyiv was hit by drones."),
         src="CLAIM \u00b7 KYIV", motif="bridge"),
    dict(num=5, kicker="5 \u00b7 SHENZHEN \u00b7 SUMMIT",
         head="APEC leaders meet in Shenzhen",
         dek=("Leaders gather in China for the APEC summit. Xi urges APEC "
              "economies to back open trade and new technology."),
         src="AP", motif="flags"),
    dict(num=6, kicker="6 \u00b7 ANTALYA \u00b7 CLIMATE",
         head="COP31's final day: fossil fuels cut from the text",
         dek=("A revised draft strips out every fossil-fuel phase-out "
              "pledge. Delegates push back as the final plenary meets "
              "today."),
         src="UNFCCC \u00b7 AFP", motif="globe"),
    dict(num=7, kicker="7 \u00b7 THE HAGUE \u00b7 LAW",
         head="The world answers the genocide verdict",
         dek=("Britain expels Myanmar's defence attache and seeks an urgent "
              "Security Council meeting. The Gambia hails a 'historic' "
              "verdict."),
         src="AP \u00b7 BBC", motif="court"),
    dict(num=8, kicker="8 \u00b7 NEW YORK \u00b7 MARKETS",
         head="Anthropic's debut can't stop the slide",
         dek=("The Dow fell 1,084 points, the S&P 2.02% and the Nasdaq "
              "2.25%, as the AI selloff bit a day after Anthropic's record "
              "debut."),
         src="BLOOMBERG", motif="chart"),
    dict(num=9, kicker="9 \u00b7 VICE CITY \u00b7 GAMES",
         head="GTA VI passes The Odyssey's $1.84bn",
         dek=("Launch-day sales top The Odyssey's $1.80bn global run, Sensor "
              "Tower estimates. Reviews land; Rockstar calls it the "
              "highest-rated game ever."),
         src="SENSOR TOWER", motif="game"),
    dict(num=10, kicker="10 \u00b7 SPACE \u00b7 SCIENCE",
         head="NASA confirms Voyager 1's light-day milestone",
         dek=("The probe is now a full light-day from Earth - 16 billion "
              "miles out, the farthest any human-made object has ever "
              "travelled."),
         src="NASA \u00b7 JPL", motif="space"),
    dict(num=11, kicker="11 \u00b7 SEOUL \u00b7 LAW",
         head="South Korea clears ex-PM Han",
         dek=("The Supreme Court overturns former prime minister Han "
              "Duck-soo's conviction, in the case tied to the 2024 "
              "martial-law declaration."),
         src="KOREA TIMES", motif="court"),
    dict(num=12, kicker="12 \u00b7 SUVA \u00b7 CLIMATE",
         head="Fiji declares a national disaster over drought",
         dek=("Fiji declares a national disaster over drought and water "
              "shortages. El Nino leaves water short across the islands."),
         src="AFP", motif="drought"),
    dict(num=13, kicker="13 \u00b7 VIENNA \u00b7 SECURITY",
         head="North Korea expands uranium enrichment at Yongbyon",
         dek=("The UN watchdog reports growth at the nuclear site, in its "
              "latest assessment of the Yongbyon complex."),
         src="IAEA", motif="dome"),
    dict(num=14, kicker="14 \u00b7 CARACAS \u00b7 DIPLOMACY",
         head="US and Venezuela restore military cooperation",
         dek=("The two countries sign an agreement to work together again, "
              "restoring a military channel closed for years."),
         src="REUTERS", motif="handshake"),
    dict(num=15, kicker="15 \u00b7 HORMUZ \u00b7 CONFLICT",
         head="ADNOC vessel attacked in the Strait of Hormuz",
         dek=("One crew member is missing after the strike on the ADNOC "
              "vessel in the strait."),
         src="REUTERS", motif="ship"),
    dict(num=16, kicker="16 \u00b7 WELLINGTON \u00b7 CRICKET",
         head="Day two at the Basin: Nicholls' 113 anchors New Zealand",
         dek=("New Zealand build on Henry Nicholls' unbeaten 113 as India "
              "hunt early wickets, in the first Test at the Basin Reserve."),
         src="AP", motif="cricket"),
]

BRIEFS = [
    (17, "BRUSSELS", "EU-UK summit opens"),
    (18, "NEW DELHI", "Modi meets William and Kate"),
    (19, "DHAKA", "Fire at the Yunus home; arson feared"),
    (20, "MUMBAI", "Sensex +1.21%, Nifty +1.14% on the day"),
    (21, "TOKYO", "Hayabusa2 gives up landing; mission rewritten"),
    (22, "BERLIN", "Coalition of the Willing meets in Berlin"),
    (23, "BERLIN", "Merz hosts Qatar's emir in Berlin"),
    (24, "NEW DELHI", "Pakistan minister leads delegation to Delhi for SCO"),
    (25, "MANILA", "Philippines-Chile trade deal signed"),
    (26, "MANILA", "Musk plans Philippines projects"),
    (27, "HONG KONG", "India beats Malaysia, Asian Hockey Trophy opens"),
    (28, "IPOH", "Harimau Shakti exercise opens in Ipoh"),
    (29, "NEW DELHI", "India's electronics exports jump 44%"),
    (30, "NEW DELHI", "ICMR completes 100 tech transfers"),
    (31, "NEW DELHI", "India unveils its first bird-flu vaccine"),
    (32, "GENEVA", "World Children's Day marked worldwide"),
    (33, "EUROPE", "Youth anti-war protests across Europe"),
    (34, "BRUSSELS", "EU delays its methane rules by 24 months"),
    (35, "COLOGNE", "Bayern Munich beat Koln 3-0"),
    (36, "U17 CUP", "Argentina 0-2 Australia at the U17 Cup"),
    (37, "WASHINGTON", "Jobless claims come in at 203,000"),
    (38, "STRASBOURG", "NATO's assembly opens its 72nd session"),
    (39, "HANOI", "Azerbaijan's Aliyev visits Vietnam"),
    (40, "MARKETS", "Crude futures fall over 3%"),
    (41, "KHARTOUM", "Sudan army: two-year El Obeid siege broken"),
    (42, "MOGADISHU", "Somalia gives UAE ambassador 72 hours to leave"),
    (43, "SAN SALVADOR", "Migrant boat capsizes off El Salvador; dozens missing"),
    (44, "PORT-AU-PRINCE", "Haiti approves Salvadoran troop deal vs gangs"),
    (45, "ARABIAN SEA", "Amur falcons cross the Arabian Sea"),
    (46, "NEW YORK", "Al-Saadi appears in a New York court over a UK plot"),
    (47, "KYIV", "Witkoff and Kushner brief Zelenskyy"),
    (48, "BEIJING", "Xi urges APEC to back open trade, new tech"),
]

# Dot-matrix world map: row -> list of (col0, col1) land spans.
# Grid is 60 cols (lon -180..180) by 24 rows (lat 84..-60).
MAP_ROWS = {
    1: [(6, 12), (30, 34)],
    2: [(3, 14), (28, 36), (38, 50)],
    3: [(2, 15), (27, 35), (37, 52)],
    4: [(2, 14), (28, 34), (38, 51)],
    5: [(3, 13), (29, 33), (40, 50)],
    6: [(4, 12), (30, 33), (41, 49)],
    7: [(5, 11), (29, 36), (43, 48)],
    8: [(6, 10), (30, 36), (44, 47)],
    9: [(7, 10), (30, 35)],
    10: [(9, 12), (31, 34)],
    11: [(11, 15), (31, 34)],
    12: [(12, 16), (32, 34)],
    13: [(12, 16), (33, 35)],
    14: [(13, 16), (47, 52)],
    15: [(13, 15), (48, 53)],
    16: [(14, 15), (49, 52)],
    17: [(14, 15)],
}

PINS = [
    (1, 85, 20), (2, 47, 25), (3, 114, 22), (4, 37, 45),
    (5, 114, 22), (6, 30, 37), (7, 4, 52), (8, -74, 41),
    (9, -80, 26), (10, -118, 34), (11, 127, 37), (12, 178, -18),
    (13, 16, 48), (14, -67, 10), (15, 56, 26), (16, 175, -41),
]

DATE_CHECK = (
    "Left out - they broke before Friday: the ICJ genocide ruling on Myanmar "
    "itself (Thursday 19 Nov) - Friday's news is the world's answer to it - "
    "Denmark's Greenland-US pact (19 Nov) - Anthropic's $81.34bn IPO (19 Nov); "
    "its first trading day was Thursday - Germany's electricity-tax cut "
    "(18 Nov) - the Crimean Bridge span collapse (17-18 Nov). Not yet: the "
    "trilateral's first meeting was 19 Nov; the joint declaration is Friday's."
)


# ---------------------------------------------------------------- layout
def draw_topbar(d):
    d.line([M, 30, M + CW, 30], fill=RULE, width=3)
    d.text((M, 36), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=F(BOLD, 19), fill=NAVY)
    right = "48 STORIES - 7 REGIONS"
    d.text((M + CW - d.textlength(right, font=F(BOLD, 19)), 36), right,
           font=F(BOLD, 19), fill=INK)
    d.line([M, 62, M + CW, 62], fill=RULE, width=3)


def draw_masthead(d):
    d.text((M, 70), "Friday 20", font=FLF(SERIFB, 112), fill=INK)
    d.text((M, 178), "November 2026", font=FLF(SERIFB, 112), fill=NAVY)
    d.line([M, 292, M + CW, 292], fill=RULE, width=2)


def draw_numbers(d, y):
    d.text((M, y), "FRIDAY BY THE NUMBERS", font=F(BOLD, 16), fill=RED)
    y += 30
    colw = CW / 6
    for i, (num, label) in enumerate(NUMBERS):
        x = M + i * colw
        d.text((x, y), num, font=F(BOLD, 30), fill=NAVY)
        text_block(d, x, y + 40, label, F(SANS, 13), colw - 14, 17, INK,
                   max_lines=2)
        if i:
            d.line([x - 8, y, x - 8, y + 62], fill=(200, 194, 178), width=1)
    return y + 78


def draw_timeline(d, y):
    d.rectangle([M, y, M + 132, y + 62], fill=NAVY)
    d.text((M + 12, y + 8), "THE DAY", font=F(BOLD, 17), fill=(255, 255, 255))
    d.text((M + 12, y + 32), "IN UTC", font=F(BOLD, 17), fill=(255, 255, 255))
    colw = (CW - 148) / 6
    for i, (when, what) in enumerate(TIMELINE):
        x = M + 148 + i * colw
        d.text((x, y), when, font=F(BOLD, 15), fill=RED)
        text_block(d, x, y + 22, what, F(SANS, 14), colw - 12, 18, INK,
                   max_lines=3)
        if i:
            d.line([x - 8, y + 2, x - 8, y + 60], fill=(200, 194, 178),
                   width=1)
    return y + 72


def draw_regions(d, y):
    widths = [300, 200, 480, 140, 120, 100, 148]
    x = M
    for (name, count, color), w in zip(REGIONS, widths):
        d.rectangle([x, y, x + w, y + 36], fill=color)
        label = "%s %d" % (name, count)
        font = F(BOLD, 15)
        tw = d.textlength(label, font=font)
        d.text((x + (w - tw) / 2, y + 9), label, font=font,
               fill=(255, 255, 255))
        x += w
    return y + 46


def draw_hero(d, hero, x, y, w, h):
    draw_scene(d, x, y, w, 76, hero["motif"])
    ty = y + 84
    d.text((x, ty), hero["kicker"], font=F(BOLD, 13), fill=NAVY)
    sw = d.textlength(hero["src"], font=F(SANS, 11))
    d.text((x + w - sw, ty), hero["src"], font=F(SANS, 11), fill=GREY)
    hy = fit_text(d, hero["head"], SERIFB, [26, 24, 22], w, 2, INK, x,
                  ty + 20, leading_ratio=1.08)
    text_block(d, x, hy + 4, hero["dek"], F(SANS, 14), w, 18, (52, 48, 42),
               max_lines=2)
    d.line([x, y + h - 2, x + w, y + h - 2], fill=(200, 194, 178), width=1)


def draw_map_panel(d, x, y, w, h):
    d.text((x, y), "WHERE IT HAPPENED", font=F(BOLD, 20), fill=NAVY)
    my = y + 32
    mh = 220
    d.rectangle([x, my, x + w, my + mh], fill=NAVY_DK)
    cols, rows = 60, 24
    cell = min((w - 16) / cols, (mh - 16) / rows)
    ox = x + (w - cell * cols) / 2
    oy = my + (mh - cell * rows) / 2
    for row, spans in MAP_ROWS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = ox + c * cell + cell / 2
                cy = oy + row * cell + cell / 2
                d.ellipse([cx - 2.4, cy - 2.4, cx + 2.4, cy + 2.4],
                          fill=(190, 200, 215))
    for num, lon, lat in PINS:
        px = ox + (lon + 180) / 360 * cell * cols
        py = oy + (90 - lat) / 180 * cell * rows
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(num)
        tw = d.textlength(label, font=F(BOLD, 10))
        d.text((px - tw / 2, py - 7), label, font=F(BOLD, 10),
               fill=(255, 255, 255))
    return my + mh


def draw_briefs(d, x, y, w):
    d.text((x, y), "ALSO ON FRIDAY 20 NOVEMBER \u2014 32 MORE STORIES",
           font=F(BOLD, 15), fill=NAVY)
    y += 24
    colw = w / 2
    font = F(SANS, 11)
    for i, (num, place, text) in enumerate(BRIEFS):
        col = i // 16
        row = i % 16
        bx = x + col * colw
        by = y + row * 13
        d.ellipse([bx, by + 2, bx + 6, by + 6], fill=RED)
        line = "%d %s \u2014 %s" % (num, place, text)
        while d.textlength(line, font=font) > colw - 14 and len(line) > 20:
            line = line[:-1]
        if d.textlength(line, font=font) > colw - 14:
            line = line[:-1] + "\u2026"
        d.text((bx + 10, by), line, font=font, fill=INK)
    return y + 16 * 13


def draw_panel(d, item, x, y, w, h):
    draw_scene(d, x, y, w, 40, item["motif"])
    ty = y + 44
    d.text((x, ty), item["kicker"], font=F(BOLD, 10), fill=NAVY)
    sw = d.textlength(item["src"], font=F(SANS, 9))
    d.text((x + w - sw, ty + 1), item["src"], font=F(SANS, 9), fill=GREY)
    hy = fit_text(d, item["head"], SERIFB, [15, 14, 13], w, 2, INK, x,
                  ty + 13, leading_ratio=1.05)
    text_block(d, x, hy + 2, item["dek"], F(SANS, 11), w, 13, (52, 48, 42),
               max_lines=2)


def draw_pictured(d, y):
    rows = [PICTURED[0:4], PICTURED[4:9], PICTURED[9:13]]
    row_h = 124
    gap = 8
    for group in rows:
        n = len(group)
        pw = (CW - (n - 1) * 16) / n
        for i, item in enumerate(group):
            draw_panel(d, item, M + i * (pw + 16), y, pw, row_h)
        y += row_h + gap
    return y - gap


def draw_datecheck(d, y):
    d.rectangle([M, y, M + 150, y + 56], fill=RED)
    d.text((M + 14, y + 8), "DATE", font=F(BOLD, 18), fill=(255, 255, 255))
    d.text((M + 14, y + 30), "CHECK", font=F(BOLD, 18), fill=(255, 255, 255))
    d.rectangle([M + 150, y, M + CW, y + 56], outline=RED, width=2)
    text_block(d, M + 164, y + 5, DATE_CHECK, F(SANS, 11.5), CW - 180, 14,
               INK, max_lines=4)
    return y + 64


def draw_footer(d, y):
    d.line([M, y, M + CW, y], fill=RULE, width=2)
    text_block(d, M, y + 8,
               "Every story here happened, or was first reported, on Friday "
               "20 November 2026, in some time zone. Disputed claims are "
               "attributed, not stated as fact.",
               FLF(SERIFI, 13), CW, 17, INK, max_lines=1)
    text_block(d, M, y + 28,
               "Sources: Reuters - AP - AFP - BBC - Bloomberg - IMD - NASA - "
               "IAEA - The Hindu - Arab News - Sensor Tower. Original "
               "drawings, drawn for this page.",
               F(SANS, 12), CW, 16, GREY, max_lines=1)


def main():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    draw_topbar(d)
    draw_masthead(d)
    y = draw_numbers(d, 304)
    y = draw_timeline(d, y + 6)
    y = draw_regions(d, y + 8)
    # Left: three stacked heroes. Right: map + briefs rail.
    hero_x, hero_w = M, 740
    rail_x, rail_w = M + 756, CW - 756
    hy = y + 6
    card_h = 168
    for i, hero in enumerate(HEROES):
        draw_hero(d, hero, hero_x, hy + i * (card_h + 8), hero_w, card_h)
    rail_bottom = draw_map_panel(d, rail_x, hy, rail_w, 0)
    draw_briefs(d, rail_x, rail_bottom + 12, rail_w)
    py = hy + 3 * card_h + 2 * 8 + 12
    py = draw_pictured(d, py)
    dy = draw_datecheck(d, py + 12)
    draw_footer(d, dy + 4)
    im = im.resize((1024, 1024), Image.LANCZOS)
    out_dirs = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        out_dirs.append(env_dir)
    out_dirs.append(".")
    out_dirs.append(os.path.dirname(os.path.abspath(__file__)))
    last_err = None
    for out_dir in out_dirs:
        try:
            im.save(os.path.join(out_dir, "entry.png"))
            last_err = None
            break
        except OSError as err:
            last_err = err
    if last_err is not None:
        raise last_err


if __name__ == "__main__":
    main()
