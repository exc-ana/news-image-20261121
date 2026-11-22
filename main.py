#!/usr/bin/env python3
"""Sum up 21 November 2026's world news in one image (v2 refresh).

Draws a 1024x1024 broadsheet, "THE SATURDAY GLOBE", with three hero
stories and 40 numbered stories in total, all reported on Saturday
21 November 2026. Python 3 standard library only; everything is drawn
by hand (raster canvas, bitmap font, pictograms, hand-written PNG
encoder). Deterministic: two runs write byte-identical output.

Writes only to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (18, 34, 66)
NAVY2 = (26, 48, 92)
PAPER = (247, 242, 231)
PAPER2 = (238, 231, 214)
INK = (22, 22, 22)
RED = (176, 42, 42)
RED2 = (204, 64, 48)
GOLD = (198, 158, 74)
SKY = (52, 96, 140)
SKY2 = (120, 165, 205)
GREEN = (46, 110, 66)
WHITE = (255, 255, 255)
GREY = (110, 110, 110)
LIGHT = (214, 222, 232)
ORANGE = (224, 122, 40)
YELLOW = (240, 200, 60)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits, written as strings. Text is rendered
# in capitals; lowercase input is upper-cased before drawing.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                half = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
                self.rect(cx - half, yy, 2 * half + 1, 1, c)
        else:
            x, y, d = 0, r, 3 - 2 * r
            while x <= y:
                for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                               (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                               (cx + y, cy - x), (cx - y, cy - x)):
                    self.set(px, py, c)
                if d < 0:
                    d += 4 * x + 6
                else:
                    d += 4 * (x - y) + 10
                    y -= 1
                x += 1

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle via scanlines
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
                xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            else:
                xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
                xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            self.rect(int(min(xa, xb)), y, int(abs(xb - xa)) + 1, 1, c)

    # ------------------------------------------------------------ text
    def text_width(self, s, scale):
        return int(len(s) * 6 * scale)

    def draw_text(self, s, x, y, scale, c, bold=False):
        """Draw upper-cased text; (x, y) is the top-left of the first glyph."""
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == '1':
                        px = int(cx + col * scale)
                        py = int(y + row * scale)
                        wpx = max(1, int(scale + 0.5))
                        hpx = max(1, int(scale + 0.5))
                        self.rect(px, py, wpx, hpx, c)
                        if bold:
                            self.rect(px + 1, py, max(1, wpx - 1), hpx, c)
            cx += 6 * scale
        return cx

    def text_centred(self, s, cx, y, scale, c, bold=False):
        w = self.text_width(s, scale)
        return self.draw_text(s, int(cx - w / 2), y, scale, c, bold)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines (upper-cased)."""
        words = s.upper().split()
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- the news
# Every story was reported on Saturday 21 November 2026 (afternoon
# check, ~15:30 WIB). Friday-evening events are included only as
# reported in Saturday's news; the footer says so.
HEROES = [
    {
        "cat": "POLAND",
        "head": "RUSSIAN MISSILES LAND IN POLAND",
        "body": ("Two Kh-101 missiles and a drone crash in south-east "
                 "Poland in a huge strike on Ukraine. Tusk calls it a "
                 "deliberate provocation; NATO chief Rutte, due in "
                 "Warsaw today, calls it a grave violation. No one hurt."),
        "scene": "poland",
    },
    {
        "cat": "CLIMATE",
        "head": "COP31 RUNS INTO OVERTIME WITH NO DEAL",
        "body": ("The Antalya talks pass their Friday deadline. The "
                 "latest draft drops every mention of fossil fuels "
                 "and the $120bn adaptation target; a third draft is "
                 "due today. COP32 goes to Addis Ababa in 2027."),
        "scene": "cop31",
    },
    {
        "cat": "MARKETS",
        "head": "WALL STREET ROUT: S&P 500 IN CORRECTION",
        "body": ("The S&P 500 falls 3.7% on Friday, its seventh "
                 "straight loss, and the Nasdaq wipes out all its "
                 "2026 gains as the AI trade unwinds. Nvidia sinks "
                 "14% on an SEC probe; Anthropic slides 8.5%."),
        "scene": "markets",
    },
]

# 37 more stories, numbered 4-40. (cat, headline)
CARDS = [
    ("UKRAINE", "RUSSIA HITS UKRAINE WITH 400 DRONES, 110 MISSILES; 8 KILLED IN KYIV"),
    ("JUSTICE", "ICJ: MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA - FIRST STATE EVER GUILTY, 9-6"),
    ("SCIENCE", "ANTHROPIC MATHEMATICIAN CLAIMS CLAUDE SOLVED THE RIEMANN HYPOTHESIS"),
    ("MARKETS", "ANTHROPIC SHARES SLIDE 8.5% TO $88.91, WIPING $109BN OFF ITS VALUE IN A DAY"),
    ("MARKETS", "NVIDIA SINKS 14% AS SEC OPENS ACCOUNTING PROBE AFTER HUANG RESIGNS"),
    ("WEATHER", "CYCLONE AKVAN FADES TO A LOW OVER ODISHA AFTER LANDFALL; 300,000 HAD BEEN EVACUATED"),
    ("QUAKE", "6.8 QUAKE SHAKES PERU AND LIMA; NO DEATHS REPORTED, ROCKFALLS BLOCK ROADS"),
    ("EUROPE", "UK AND EU SIGN BIGGEST POST-BREXIT DEALS: FOOD TRADE, CARBON, YOUTH MOBILITY"),
    ("MIDEAST", "SAUDI COALITION INTERCEPTS THREE HOUTHI MISSILES AIMED AT RIYADH"),
    ("HEALTH", "PANCREATIC CANCER PILL MAKES TUMOURS UNDETECTABLE IN 1 IN 12 PATIENTS IN TRIAL"),
    ("EUROPE", "GEN Z PROTESTS SPREAD ACROSS 25 EUROPEAN COUNTRIES"),
    ("USA", "FBI CRIMINAL DATABASE REPORTEDLY HACKED AS US OUTAGES CONTINUE"),
    ("USA", "MAN CONVICTED OF STARTING DEADLY PALISADES FIRE IN LOS ANGELES"),
    ("AMERICAS", "TWO SALVADORAN SOLDIERS KILLED BY EXPLOSIVES ON HAITI MISSION"),
    ("MIDEAST", "ISRAELI STRIKES KILL PALESTINIANS IN GAZA; WEST BANK VIOLENCE CONTINUES"),
    ("EUROPE", "SPAIN HEADS TO 29 NOVEMBER ELECTION AS CONSERVATIVES GAIN GROUND"),
    ("SPACE", "NASA HALTS PERSEVERANCE AND MARS ODYSSEY SCIENCE AMID HARDWARE TROUBLE"),
    ("CRYPTO", "BITCOIN SLIDES TOWARD $62,000 AS CRYPTO LIQUIDATIONS TOP $2 BILLION"),
    ("GAMING", "GTA VI SETS RECORD WITH $3.8 BILLION IN FIRST-DAY SALES"),
    ("USA", "MAMDANI PLANS TO CLOSE NEW YORK'S RIKERS ISLAND JAIL BY 2032"),
    ("EUROPE", "DENMARK EXPELS RUSSIAN DIPLOMAT OVER PLOT TO KILL UKRAINIAN RAPPER"),
    ("AFRICA", "NEARLY 600 WOMEN KILLED IN SOUTH AFRICA IN THREE MONTHS"),
    ("USA", "US DECLASSIFIES MORE UFO FOOTAGE FILMED IN THE MIDDLE EAST"),
    ("AMERICAS", "FORMER BRAZIL PRESIDENT BOLSONARO HOSPITALISED WITH INTESTINAL ISSUES"),
    ("SPORT", "NFL SUSPENDS PUKA NACUA AMID ONGOING ANTISEMITISM LAWSUIT"),
    ("USA", "TRUMP CALLS PUTIN 'MY FRIEND'; ZELENSKYY REPLIES: PUTIN IS A 'KILLER'"),
    ("USA", "TRUMP THREATENS 'TREMENDOUS' TAX ON DATA CENTRES BUILT OUTSIDE THE US"),
    ("CRICKET", "KL RAHUL MAKES HISTORY: TEST TONS IN ALL FOUR SENA COUNTRIES"),
    ("FOOTBALL", "HARRY KANE TEARS ANKLE LIGAMENT, OUT FOR MONTHS AFTER BAYERN DRAW"),
    ("RUGBY", "WALES BEAT THE ALL BLACKS FOR THE FIRST TIME IN 73 YEARS"),
    ("CRICKET", "PAKISTAN BEAT SRI LANKA FOR FIRST TEST SERIES WIN IN TWO YEARS"),
    ("NBA", "HARDEN SCORES 51; CUNNINGHAM DROPS 50 IN HISTORIC NBA NIGHT"),
    ("NFL", "DRAKE MAYE OUT FOR THE SEASON WITH FRACTURED FIBULA"),
    ("TENNIS", "ANDREEVA WINS WTA FINALS; ATP FINALS REACH SEMIS IN TURIN"),
    ("ASIA", "BANGLADESH PM BLAMES INDIA AND AWAMI LEAGUE FOR WAVE OF VIOLENCE"),
    ("MIDEAST", "IRAQ ARRESTS EIGHT OIL OFFICIALS; TROOPS RETAKE JURF AL-SAKHAR"),
    ("AFRICA", "ANC FIGHTS TO HOLD SOUTH AFRICA'S KEY CITIES AFTER ELECTION SETBACK"),
]

# ---------------------------------------------------------- hero scenes
def burst(cv, cx, cy, r, c):
    """Starburst: 12 spikes from a centre."""
    for k in range(12):
        import math
        a = k * math.pi / 6
        x1 = int(cx + r * 0.35 * math.cos(a))
        y1 = int(cy + r * 0.35 * math.sin(a))
        x2 = int(cx + r * math.cos(a))
        y2 = int(cy + r * math.sin(a))
        cv.line(x1, y1, x2, y2, c, 3)
    cv.circle(cx, cy, int(r * 0.35), c, fill=True)


def scene_poland(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 34, w, 34, GREEN)
    cv.rect(x, y + h - 34, w, 4, (30, 80, 44))
    # sun and clouds
    cv.circle(x + w - 42, y + 26, 14, YELLOW, fill=True)
    cv.circle(x + 40, y + 22, 10, WHITE, fill=True)
    cv.circle(x + 56, y + 18, 12, WHITE, fill=True)
    # missile streaking down, left to right
    cv.line(x + 30, y + 18, x + 150, y + 78, ORANGE, 3)
    cv.line(x + 30, y + 24, x + 150, y + 84, YELLOW, 2)
    cv.line(x + 150, y + 78, x + 176, y + 92, WHITE, 6)
    cv.triangle(x + 176, y + 92, x + 168, y + 84, x + 186, y + 88, RED2)
    # explosion where it lands
    burst(cv, x + 208, y + h - 46, 26, ORANGE)
    burst(cv, x + 208, y + h - 46, 15, YELLOW)
    cv.circle(x + 208, y + h - 46, 8, RED2, fill=True)
    # Polish flag on a pole
    cv.vline(x + w - 62, y + h - 78, 44, INK)
    cv.rect(x + w - 61, y + h - 78, 34, 9, WHITE)
    cv.rect(x + w - 61, y + h - 69, 34, 9, RED2)
    # small NATO-style shield
    cv.rect(x + 12, y + h - 30, 30, 18, NAVY2)
    cv.draw_text("NATO", x + 16, y + h - 27, 0.9, WHITE, bold=True)


def scene_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, (222, 232, 214))
    # globe
    gx, gy, gr = x + 78, y + 62, 48
    cv.circle(gx, gy, gr, SKY, fill=True)
    cv.circle(gx, gy, gr, NAVY2)
    cv.circle(gx - 16, gy - 12, 12, GREEN, fill=True)
    cv.circle(gx + 14, gy + 8, 14, GREEN, fill=True)
    cv.circle(gx + 4, gy - 22, 8, GREEN, fill=True)
    # thermometer, mercury near the top (kept clear of the banner below)
    tx = x + w - 74
    cv.rect(tx, y + 12, 16, 58, WHITE)
    cv.rect(tx, y + 12, 16, 58, INK)
    cv.rect(tx + 2, y + 14, 12, 54, WHITE)
    cv.rect(tx + 4, y + 24, 8, 42, RED2)
    cv.circle(tx + 8, y + 76, 9, RED2, fill=True)
    # oil pumpjack with a red cross over it
    bx, by = x + 150, y + 96
    cv.line(bx, by, bx + 26, by - 34, INK, 3)
    cv.line(bx + 26, by - 34, bx + 44, by - 30, INK, 3)
    cv.line(bx + 10, by, bx + 18, by - 20, INK, 2)
    cv.line(bx + 2, by, bx + 46, by, INK, 3)
    cv.line(bx + 30, y + 52, bx + 58, y + 80, RED, 4)
    cv.line(bx + 58, y + 52, bx + 30, y + 80, RED, 4)
    # gavel line: "NO DEAL" banner
    cv.rect(x + 8, y + h - 26, w - 16, 20, RED)
    cv.text_centred("NO DEAL - TALKS RUN ON", x + w // 2, y + h - 22, 1.1, WHITE, bold=True)


def scene_markets(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    # skyline silhouettes
    for bx, bw, bh in ((8, 34, 44), (48, 26, 62), (80, 40, 36), (126, 24, 54),
                       (156, 34, 40), (196, 26, 66), (228, 40, 30), (274, 30, 48)):
        cv.rect(x + bx, y + h - bh, bw, bh, NAVY2)
    # falling chart, kept below the top labels
    pts = [(x + 16, y + 34), (x + 60, y + 44), (x + 104, y + 40),
           (x + 150, y + 62), (x + 196, y + 58), (x + 244, y + 86),
           (x + 288, y + 96)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED2, 4)
    # down arrow at the end
    ex, ey = pts[-1]
    cv.line(ex, ey, ex - 14, ey - 4, RED2, 4)
    cv.line(ex, ey, ex - 4, ey - 14, RED2, 4)
    # red bars
    for i, bh in enumerate((18, 26, 22, 34, 30, 44)):
        cv.rect(x + 20 + i * 46, y + h - 8 - bh, 22, bh, RED2)
    cv.draw_text("-3.7%", x + 14, y + 8, 1.6, WHITE, bold=True)
    cv.draw_text("S&P 500", x + 96, y + 10, 1.2, LIGHT, bold=True)


SCENES = {"poland": scene_poland, "cop31": scene_cop31, "markets": scene_markets}

# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.rect(0, 0, W, 58, NAVY)
    cv.rect(0, 58, W, 4, GOLD)
    cv.text_centred("THE SATURDAY GLOBE", W // 2, 10, 3.4, WHITE, bold=True)
    cv.draw_text("EST. 2026", 18, 22, 1.1, GOLD, bold=True)
    cv.draw_text("NO. 325", W - 18 - cv.text_width("NO. 325", 1.1), 22, 1.1, GOLD, bold=True)
    # giant date headline
    cv.rect(0, 62, W, 58, PAPER)
    cv.text_centred("SATURDAY 21 NOVEMBER 2026", W // 2, 74, 2.9, NAVY, bold=True)
    cv.rect(0, 120, W, 3, RED)
    cv.rect(0, 123, W, 26, NAVY2)
    cv.text_centred("MISSILES OVER POLAND  -  COP31 IN OVERTIME  -  WALL STREET IN CORRECTION",
                    W // 2, 130, 1.15, WHITE, bold=True)


def draw_heroes(cv):
    y0, hh = 152, 258
    gap, mx = 8, 12
    pw = (W - 2 * mx - 2 * gap) // 3
    for i, hero in enumerate(HEROES):
        x = mx + i * (pw + gap)
        cv.rect(x, y0, pw, hh, WHITE)
        cv.rect(x, y0, pw, 2, RED)
        # scene panel
        SCENES[hero["scene"]](cv, x + 6, y0 + 26, pw - 12, 118)
        # category + number
        cv.draw_text("1  " + hero["cat"], x + 8, y0 + 6, 1.15, RED, bold=True)
        cv.draw_text("HERO " + str(i + 1), x + pw - 8 - cv.text_width("HERO " + str(i + 1), 1.0),
                     y0 + 7, 1.0, GREY, bold=True)
        # headline
        lines = cv.wrap(hero["head"], pw - 16, 1.9)
        yy = y0 + 152
        for ln in lines[:2]:
            cv.draw_text(ln, x + 8, yy, 1.9, NAVY, bold=True)
            yy += 16
        # body
        blines = cv.wrap(hero["body"], pw - 16, 1.1)
        yy += 2
        for ln in blines[:5]:
            cv.draw_text(ln, x + 8, yy, 1.1, INK)
            yy += 10
        # thin frame
        cv.rect(x, y0, pw, 1, INK)
        cv.rect(x, y0 + hh - 1, pw, 1, INK)
        cv.rect(x, y0, 1, hh, INK)
        cv.rect(x + pw - 1, y0, 1, hh, INK)


def draw_grid(cv):
    y0 = 418
    cols, rows = 4, 10
    mx, gap = 12, 8
    cw = (W - 2 * mx - (cols - 1) * gap) // cols
    rh = 52
    for idx, (cat, head) in enumerate(CARDS):
        r, c = divmod(idx, cols)
        x = mx + c * (cw + gap)
        y = y0 + r * (rh + 2)
        n = idx + 4
        cv.rect(x, y, cw, rh, WHITE)
        cv.rect(x, y, cw, 2, GOLD)
        cv.draw_text("%02d" % n, x + 6, y + 6, 1.25, RED, bold=True)
        cv.draw_text(cat, x + 34, y + 7, 1.0, NAVY2, bold=True)
        lines = cv.wrap(head, cw - 12, 1.25)
        yy = y + 19
        for ln in lines[:3]:
            cv.draw_text(ln, x + 6, yy, 1.25, INK, bold=True)
            yy += 10
        cv.rect(x, y, cw, 1, INK)
        cv.rect(x, y + rh - 1, cw, 1, INK)
        cv.rect(x, y, 1, rh, INK)
        cv.rect(x + cw - 1, y, 1, rh, INK)


def draw_footer(cv):
    y0 = 962
    cv.rect(0, y0, W, H - y0, NAVY)
    cv.rect(0, y0, W, 3, GOLD)
    cv.draw_text("DATE CHECK", 14, y0 + 8, 1.5, GOLD, bold=True)
    cv.draw_text("EVERY STORY ABOVE WAS REPORTED ON SATURDAY 21 NOVEMBER 2026.",
                 14, y0 + 22, 1.1, WHITE, bold=True)
    cv.draw_text("FRIDAY-EVENING EVENTS (PERU QUAKE, WALL STREET CLOSE, ICJ REACTION)",
                 14, y0 + 33, 1.0, LIGHT)
    cv.draw_text("ARE INCLUDED ONLY AS REPORTED IN SATURDAY'S NEWS.",
                 14, y0 + 43, 1.0, LIGHT)
    cv.draw_text("SOURCES: AP - REUTERS - BBC - AFP - UN NEWS - IMD - IANS - WSJ - CNN - INVESTOPEDIA",
                 14, y0 + 53, 0.9, GOLD)
    # right-hand index note
    cv.draw_text("40 STORIES", W - 14 - cv.text_width("40 STORIES", 1.3), y0 + 8, 1.3, WHITE, bold=True)
    cv.draw_text("ONE DAY", W - 14 - cv.text_width("ONE DAY", 1.3), y0 + 24, 1.3, WHITE, bold=True)
    cv.draw_text("ONE PAGE", W - 14 - cv.text_width("ONE PAGE", 1.3), y0 + 40, 1.3, WHITE, bold=True)


def main():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_heroes(cv)
    draw_grid(cv)
    draw_footer(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
