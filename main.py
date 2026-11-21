#!/usr/bin/env python3
"""Sum up Saturday 21 November 2026 world news in one image.

Writes a single broadsheet-style PNG to /output/entry.png (or the
directory named by MAKEFUN_OUTPUT_DIR). Pure Python 3 standard library:
the program draws everything itself -- a small raster canvas, a stroke
font defined below, simple pictograms -- and encodes the PNG by hand
(zlib + struct). No network, no files read, no randomness, no clock:
two runs write byte-identical output.

Layout (1024 x 1024): navy masthead, giant date headline, three hero
panels with self-drawn scenes, then 37 numbered story cards in a
4-column grid (stories 4-39), one final card, and a DATE CHECK footer
that also carries the sources. 40 stories in total, every one reported
on Saturday 21 November 2026.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- PNG encode
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(rgb, w, h):
    """rgb: bytes, 3 bytes per pixel, row-major. Returns PNG bytes."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, paper):
        self.w, self.h = w, h
        self.px = bytearray(paper * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill(self, x0, y0, x1, y1, color):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = color * (x1 - x0)

    def rect(self, x0, y0, x1, y1, color, lw=1):
        for t in range(lw):
            self.hline(x0, y0 + t, x1, color)
            self.hline(x0, y1 - 1 - t, x1, color)
            self.vline(x0 + t, y0, y1, color)
            self.vline(x1 - 1 - t, y0, y1, color)

    def hline(self, x0, y, x1, color):
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(max(0, x0), min(self.w, x1)):
            self.set(x, y, color)

    def vline(self, x, y0, y1, color):
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(max(0, y0), min(self.h, y1)):
            self.set(x, y, color)

    def dot(self, x, y, color, r=1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r + r:
                    self.set(x + dx, y + dy, color)

    def line(self, x0, y0, x1, y1, color, lw=1):
        """Bresenham line; lw draws a square brush around each step."""
        dx = abs(x1 - x0); dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        half = lw // 2
        while True:
            for oy in range(-half, half + 1):
                for ox in range(-half, half + 1):
                    self.set(x + ox, y + oy, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x += sx
            if e2 < dx:
                err += dx; y += sy

    def polyline(self, pts, color, lw=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], color, lw)

    def circle(self, cx, cy, r, color, lw=1, fill=False):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d2 = x * x + y * y
                if fill:
                    if d2 <= r * r:
                        self.set(cx + x, cy + y, color)
                else:
                    if abs(d2 - r * r) <= r * max(1, lw):
                        self.set(cx + x, cy + y, color)

    def disc(self, cx, cy, r, color):
        self.circle(cx, cy, r, color, fill=True)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        # Filled triangle via scanlines.
        ys = sorted([(ay, ax), (by, bx), (cy, cx)])
        (y0, x0), (y1, x1), (y2, x2) = ys
        def interp(y, ya, xa, yb, xb):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(y, y0, x0, y1, x1)
            else:
                xa = interp(y, y1, x1, y2, x2)
            xb = interp(y, y0, x0, y2, x2)
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.hline(lo, y, hi + 1, color)


# ---------------------------------------------------------------- stroke font
# Each glyph: list of polylines on a 5 wide x 7 tall grid (x 0..4, y 0..6).
# Uppercase only; all text is uppercased before drawing.
FONT = {
    "A": [[(0, 6), (2, 0), (4, 6)], [(1, 4), (3, 4)]],
    "B": [[(0, 0), (0, 6)], [(0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)],
          [(0, 3), (3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]],
    "C": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5)]],
    "D": [[(0, 0), (0, 6)], [(0, 0), (3, 0), (4, 1), (4, 5), (3, 6), (0, 6)]],
    "E": [[(0, 0), (0, 6)], [(0, 0), (4, 0)], [(0, 3), (3, 3)], [(0, 6), (4, 6)]],
    "F": [[(0, 0), (0, 6)], [(0, 0), (4, 0)], [(0, 3), (3, 3)]],
    "G": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5),
           (4, 3), (2, 3)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(2, 0), (2, 6)], [(0, 0), (4, 0)], [(0, 6), (4, 6)]],
    "J": [[(2, 0), (4, 0)], [(4, 0), (4, 5), (3, 6), (1, 6), (0, 5), (0, 4)]],
    "K": [[(0, 0), (0, 6)], [(4, 0), (0, 3)], [(1, 3), (4, 6)]],
    "L": [[(0, 0), (0, 6)], [(0, 6), (4, 6)]],
    "M": [[(0, 6), (0, 0)], [(0, 0), (2, 3), (4, 0)], [(4, 0), (4, 6)]],
    "N": [[(0, 6), (0, 0)], [(0, 0), (4, 6)], [(4, 6), (4, 0)]],
    "O": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)]],
    "P": [[(0, 0), (0, 6)], [(0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)]],
    "Q": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)],
          [(3, 4), (4, 6)]],
    "R": [[(0, 0), (0, 6)], [(0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)],
          [(1, 3), (4, 6)]],
    "S": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 2), (1, 3), (3, 3), (4, 4),
           (4, 5), (3, 6), (1, 6), (0, 5)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "U": [[(0, 0), (0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]],
    "V": [[(0, 0), (2, 6), (4, 0)]],
    "W": [[(0, 0), (1, 6), (2, 3), (3, 6), (4, 0)]],
    "X": [[(0, 0), (4, 6)], [(4, 0), (0, 6)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
    "Z": [[(0, 0), (4, 0)], [(4, 0), (0, 6)], [(0, 6), (4, 6)]],
    "0": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)]],
    "1": [[(1, 1), (2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "2": [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (0, 6), (4, 6)]],
    "3": [[(0, 0), (4, 0)], [(4, 0), (4, 6)], [(0, 6), (4, 6)], [(1, 3), (4, 3)]],
    "4": [[(0, 0), (0, 3), (4, 3)], [(3, 0), (3, 6)]],
    "5": [[(4, 0), (0, 0), (0, 3), (3, 3), (4, 4), (4, 5), (3, 6), (1, 6), (0, 5)]],
    "6": [[(4, 1), (3, 0), (1, 0), (0, 2), (0, 5), (1, 6), (3, 6), (4, 5),
           (4, 3), (2, 3), (0, 3)]],
    "7": [[(0, 0), (4, 0)], [(4, 0), (1, 6)]],
    "8": [[(1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0)],
          [(1, 3), (3, 3), (4, 4), (4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3)]],
    "9": [[(0, 5), (0, 3), (1, 1), (2, 0), (3, 0), (4, 1), (4, 3), (4, 6),
           (3, 6), (1, 6)]],
    ".": [[(2, 6), (2, 6)]],
    ",": [[(2, 5), (2, 6)], [(2, 6), (1, 7)]],
    ":": [[(2, 1), (2, 1)], [(2, 5), (2, 5)]],
    ";": [[(2, 1), (2, 1)], [(2, 4), (2, 6)], [(2, 6), (1, 7)]],
    "-": [[(0, 3), (4, 3)]],
    "!": [[(2, 0), (2, 4)], [(2, 6), (2, 6)]],
    "?": [[(1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (2, 3)], [(2, 5), (2, 6)]],
    "(": [[(3, 0), (2, 1), (2, 5), (3, 6)]],
    ")": [[(1, 0), (2, 1), (2, 5), (1, 6)]],
    "/": [[(4, 0), (0, 6)]],
    "&": [[(3, 1), (2, 0), (1, 0), (0, 1), (0, 3), (2, 4), (4, 4), (4, 5),
           (3, 6), (1, 6), (0, 5)], [(4, 0), (0, 6)]],
    "%": [[(0, 0), (1, 0), (1, 2), (0, 2), (0, 0)], [(3, 4), (4, 4), (4, 6),
           (3, 6), (3, 4)], [(4, 0), (0, 6)]],
    "+": [[(2, 1), (2, 5)], [(0, 3), (4, 3)]],
    "=": [[(0, 2), (4, 2)], [(0, 4), (4, 4)]],
    '"': [[(1, 0), (1, 2)], [(3, 0), (3, 2)]],
    "'": [[(2, 0), (2, 2)]],
    "*": [[(2, 0), (2, 6)], [(0, 2), (4, 4)], [(4, 2), (0, 4)]],
    "$": [[(4, 1), (3, 0), (1, 0), (0, 1), (0, 2), (1, 3), (3, 3), (4, 4),
           (4, 5), (3, 6), (1, 6), (0, 5)], [(2, 0), (2, 6)]],
    " ": [],
}
ADV = 6  # grid units per character advance (5 + 1 gap)


def text_w(s, sc):
    return int(round(len(s) * ADV * sc))


def draw_text(cv, x, y, s, sc, color, align="l"):
    """Draw uppercased text; (x, y) is the top-left of the cap box
    (or centre/right anchor when align is c/r). Returns width drawn."""
    s = s.upper()
    w = text_w(s, sc)
    if align == "c":
        x = x - w // 2
    elif align == "r":
        x = x - w
    lw = 1 if sc < 1.6 else (2 if sc < 3.0 else 3)
    cx = x
    for ch in s:
        for stroke in FONT.get(ch, []):
            pts = [(cx + int(round(px * sc)), y + int(round(py * sc)))
                   for px, py in stroke]
            if len(pts) == 1:
                cv.dot(pts[0][0], pts[0][1], color, max(1, lw - 1))
            else:
                cv.polyline(pts, color, lw)
        cx += int(round(ADV * sc))
    return w


def wrap(s, sc, max_w):
    """Greedy word wrap; returns list of lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in s.upper().split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, sc) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- palette
PAPER = bytes((248, 244, 233))
INK = bytes((20, 20, 20))
NAVY = bytes((27, 42, 94))
RED = bytes((179, 32, 44))
TEAL = bytes((14, 107, 107))
GOLD = bytes((176, 128, 30))
GREY = bytes((110, 108, 100))
LIGHT = bytes((232, 226, 210))
SKY = bytes((146, 190, 220))
DARK = bytes((38, 48, 66))
GREEN = bytes((46, 125, 60))
WHITE = bytes((255, 255, 255))


# -------------------------------------------------------------------- icons
def icon(cv, x, y, kind, color, s=1.0):
    """Small pictogram in a ~16*s box at (x, y). Kinds are story tags."""
    u = s
    if kind == "missile":
        cv.line(x, y + 14, x + 14, y, color, 2)
        cv.triangle(x + 14, y, x + 10, y + 2, x + 12, y + 5, color)
        cv.line(x + 2, y + 12, x + 6, y + 14, color, 1)
        cv.line(x + 5, y + 10, x + 9, y + 12, color, 1)
    elif kind == "leaf":
        cv.circle(x + 8, y + 8, 7, color, 1)
        cv.line(x + 8, y + 15, x + 8, y + 2, color, 1)
        cv.line(x + 8, y + 8, x + 3, y + 4, color, 1)
        cv.line(x + 8, y + 8, x + 13, y + 4, color, 1)
    elif kind == "chart":
        cv.line(x + 1, y + 2, x + 6, y + 6, color, 2)
        cv.line(x + 6, y + 6, x + 10, y + 4, color, 2)
        cv.line(x + 10, y + 4, x + 15, y + 13, color, 2)
        cv.line(x + 12, y + 13, x + 15, y + 13, color, 2)
        cv.line(x + 15, y + 10, x + 15, y + 13, color, 2)
    elif kind == "quake":
        cv.line(x + 1, y + 2, x + 5, y + 6, color, 2)
        cv.line(x + 5, y + 6, x + 4, y + 10, color, 2)
        cv.line(x + 4, y + 10, x + 9, y + 12, color, 2)
        cv.line(x + 9, y + 12, x + 8, y + 15, color, 2)
        cv.line(x + 11, y + 1, x + 14, y + 4, color, 1)
    elif kind == "gavel":
        cv.line(x + 3, y + 3, x + 12, y + 8, color, 2)
        cv.line(x + 2, y + 1, x + 5, y + 6, color, 2)
        cv.line(x + 10, y + 5, x + 13, y + 10, color, 2)
        cv.line(x + 8, y + 9, x + 13, y + 14, color, 2)
        cv.line(x + 2, y + 14, x + 14, y + 14, color, 2)
    elif kind == "globe":
        cv.circle(x + 8, y + 8, 7, color, 1)
        cv.line(x + 1, y + 8, x + 15, y + 8, color, 1)
        cv.line(x + 4, y + 3, x + 12, y + 3, color, 1)
        cv.line(x + 4, y + 13, x + 12, y + 13, color, 1)
    elif kind == "ship":
        cv.line(x + 2, y + 10, x + 14, y + 10, color, 2)
        cv.line(x + 4, y + 10, x + 6, y + 13, color, 1)
        cv.line(x + 10, y + 10, x + 12, y + 13, color, 1)
        cv.line(x + 8, y + 2, x + 8, y + 10, color, 2)
        cv.triangle(x + 8, y + 3, x + 8, y + 9, x + 13, y + 9, color)
    elif kind == "flag":
        cv.line(x + 3, y + 1, x + 3, y + 15, color, 2)
        cv.triangle(x + 3, y + 2, x + 3, y + 8, x + 13, y + 5, color)
    elif kind == "chip":
        cv.rect(x + 4, y + 4, x + 12, y + 12, color, 1)
        cv.rect(x + 7, y + 7, x + 9, y + 9, color, 1)
        for dx in (5, 8, 11):
            cv.line(x + dx, y + 1, x + dx, y + 4, color, 1)
            cv.line(x + dx, y + 12, x + dx, y + 15, color, 1)
        for dy in (5, 8, 11):
            cv.line(x + 1, y + dy, x + 4, y + dy, color, 1)
            cv.line(x + 12, y + dy, x + 15, y + dy, color, 1)
    elif kind == "storm":
        cv.circle(x + 6, y + 9, 4, color, 1)
        cv.circle(x + 11, y + 9, 4, color, 1)
        cv.line(x + 3, y + 13, x + 5, y + 15, color, 1)
        cv.line(x + 8, y + 13, x + 10, y + 15, color, 1)
        cv.line(x + 12, y + 13, x + 14, y + 15, color, 1)
    elif kind == "aid":
        cv.line(x + 8, y + 2, x + 8, y + 14, color, 2)
        cv.line(x + 2, y + 8, x + 14, y + 8, color, 2)
        cv.circle(x + 8, y + 8, 7, color, 1)
    elif kind == "vote":
        cv.rect(x + 2, y + 3, x + 14, y + 13, color, 1)
        cv.line(x + 4, y + 8, x + 7, y + 11, color, 2)
        cv.line(x + 7, y + 11, x + 13, y + 4, color, 2)
    elif kind == "plane":
        cv.line(x + 1, y + 8, x + 15, y + 8, color, 2)
        cv.triangle(x + 8, y + 3, x + 10, y + 8, x + 8, y + 8, color)
        cv.line(x + 3, y + 8, x + 5, y + 11, color, 1)
        cv.line(x + 11, y + 8, x + 13, y + 11, color, 1)
    elif kind == "ball":
        cv.circle(x + 8, y + 8, 7, color, 1)
        cv.line(x + 8, y + 1, x + 8, y + 15, color, 1)
        cv.line(x + 2, y + 5, x + 14, y + 11, color, 1)
        cv.line(x + 14, y + 5, x + 2, y + 11, color, 1)
    elif kind == "bat":
        cv.line(x + 3, y + 13, x + 10, y + 3, color, 2)
        cv.line(x + 10, y + 3, x + 13, y + 1, color, 2)
        cv.line(x + 13, y + 1, x + 14, y + 4, color, 2)
        cv.circle(x + 12, y + 12, 2, color, 1)
    elif kind == "tv":
        cv.rect(x + 1, y + 3, x + 15, y + 12, color, 1)
        cv.line(x + 5, y + 1, x + 8, y + 3, color, 1)
        cv.line(x + 11, y + 1, x + 8, y + 3, color, 1)
        cv.line(x + 6, y + 12, x + 10, y + 12, color, 1)
    elif kind == "coin":
        cv.circle(x + 8, y + 8, 7, color, 1)
        cv.circle(x + 8, y + 8, 4, color, 1)
        cv.line(x + 8, y + 4, x + 8, y + 12, color, 1)
    elif kind == "court":
        cv.line(x + 2, y + 14, x + 14, y + 14, color, 2)
        cv.line(x + 3, y + 14, x + 3, y + 6, color, 1)
        cv.line(x + 13, y + 14, x + 13, y + 6, color, 1)
        cv.line(x + 1, y + 6, x + 15, y + 6, color, 2)
        cv.line(x + 3, y + 6, x + 8, y + 2, color, 1)
        cv.line(x + 13, y + 6, x + 8, y + 2, color, 1)
    elif kind == "fire":
        cv.line(x + 8, y + 1, x + 12, y + 7, color, 1)
        cv.line(x + 12, y + 7, x + 13, y + 11, color, 1)
        cv.line(x + 13, y + 11, x + 11, y + 14, color, 1)
        cv.line(x + 11, y + 14, x + 5, y + 14, color, 1)
        cv.line(x + 5, y + 14, x + 3, y + 11, color, 1)
        cv.line(x + 3, y + 11, x + 5, y + 7, color, 1)
        cv.line(x + 5, y + 7, x + 8, y + 1, color, 1)
    elif kind == "lock":
        cv.rect(x + 4, y + 8, x + 12, y + 14, color, 1)
        cv.line(x + 5, y + 8, x + 5, y + 5, color, 1)
        cv.line(x + 11, y + 8, x + 11, y + 5, color, 1)
        cv.line(x + 5, y + 5, x + 11, y + 5, color, 1)
        cv.dot(x + 8, y + 11, color, 1)
    elif kind == "star":
        cv.line(x + 8, y + 1, x + 10, y + 6, color, 1)
        cv.line(x + 10, y + 6, x + 15, y + 6, color, 1)
        cv.line(x + 15, y + 6, x + 11, y + 9, color, 1)
        cv.line(x + 11, y + 9, x + 13, y + 14, color, 1)
        cv.line(x + 13, y + 14, x + 8, y + 11, color, 1)
        cv.line(x + 8, y + 11, x + 3, y + 14, color, 1)
        cv.line(x + 3, y + 14, x + 5, y + 9, color, 1)
        cv.line(x + 5, y + 9, x + 1, y + 6, color, 1)
        cv.line(x + 1, y + 6, x + 6, y + 6, color, 1)
        cv.line(x + 6, y + 6, x + 8, y + 1, color, 1)
    else:  # "dot" fallback: simple square bullet
        cv.rect(x + 4, y + 4, x + 12, y + 12, color, 1)


# -------------------------------------------------------------- hero scenes
def hero_poland(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, DARK)
    # stars
    for sx, sy in [(18, 14), (52, 30), (96, 10), (150, 26), (210, 12),
                   (260, 34), (300, 16), (120, 44), (180, 8), (240, 48)]:
        cv.dot(x + sx, y + sy, WHITE, 1)
    # ground + border line
    cv.fill(x, y + h - 26, x + w, y + h, bytes((90, 60, 44)))
    cv.hline(x, y + h - 26, x + w, GOLD)
    # missile streak with fire trail
    cv.line(x + 30, y + h - 30, x + 190, y + 22, RED, 3)
    cv.line(x + 30, y + h - 30, x + 150, y + 34, GOLD, 2)
    cv.triangle(x + 190, y + 22, x + 176, y + 20, x + 182, y + 34, WHITE)
    cv.disc(x + 30, y + h - 30, 5, GOLD)
    # NATO jets
    for jx, jy in [(60, 60), (110, 84)]:
        cv.line(x + jx, y + jy, x + jx + 22, y + jy, WHITE, 2)
        cv.triangle(x + jx + 22, y + jy, x + jx + 16, y + jy - 5,
                    x + jx + 16, y + jy + 2, WHITE)
        cv.line(x + jx + 4, y + jy, x + jx + 8, y + jy + 6, WHITE, 1)
    # radar arcs
    cv.circle(x + w - 46, y + h - 46, 18, TEAL, 1)
    cv.circle(x + w - 46, y + h - 46, 10, TEAL, 1)
    cv.dot(x + w - 46, y + h - 46, RED, 2)


def hero_cop(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, bytes((214, 232, 226)))
    # sun behind clouds
    cv.disc(x + w - 52, y + 34, 20, GOLD)
    cv.circle(x + w - 52, y + 34, 20, INK, 1)
    # globe
    cv.circle(x + 62, y + 46, 30, TEAL, 2)
    cv.line(x + 32, y + 46, x + 92, y + 46, TEAL, 1)
    cv.line(x + 40, y + 26, x + 84, y + 26, TEAL, 1)
    cv.line(x + 40, y + 66, x + 84, y + 66, TEAL, 1)
    cv.line(x + 62, y + 16, x + 62, y + 76, TEAL, 1)
    # empty speech bubble where the words should be
    cv.rect(x + 120, y + 14, x + w - 16, y + 62, WHITE, 2)
    cv.triangle(x + 140, y + 62, x + 156, y + 62, x + 140, y + 76, WHITE)
    cv.line(x + 140, y + 62, x + 140, y + 76, INK, 1)
    cv.line(x + 156, y + 62, x + 140, y + 76, INK, 1)
    draw_text(cv, x + 130, y + 24, "FOSSIL", 1.6, RED)
    draw_text(cv, x + 130, y + 40, "FUELS ?", 1.6, RED)
    # delegates: rows of heads
    for i in range(7):
        hx = x + 30 + i * 40
        cv.disc(hx, y + h - 34, 9, NAVY)
        cv.fill(hx - 12, y + h - 24, hx + 12, y + h - 8, NAVY)
    cv.fill(x, y + h - 8, x + w, y + h, NAVY)


def hero_market(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, WHITE)
    # grid
    for gy in range(y + 12, y + h - 20, 18):
        cv.hline(x + 8, gy, x + w - 8, LIGHT)
    for gx in range(x + 12, x + w - 8, 24):
        cv.vline(gx, y + 8, y + h - 24, LIGHT)
    # plunging chart
    pts = [(x + 14, y + 22), (x + 70, y + 34), (x + 120, y + 30),
           (x + 170, y + 52), (x + 220, y + 58), (x + 270, y + 92),
           (x + w - 20, y + h - 12)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    # big red down arrow
    ax = x + w - 66
    cv.line(ax, y + 14, ax, y + 52, RED, 4)
    cv.triangle(ax, y + 62, ax - 12, y + 44, ax + 12, y + 44, RED)
    # tick labels: two at the top, one low-left where the chart is high
    draw_text(cv, x + 12, y + 6, "S&P -3.7%", 1.2, RED)
    draw_text(cv, x + 100, y + 6, "NASDAQ -5.3%", 1.2, RED)
    draw_text(cv, x + 12, y + h - 18, "DOW -1.9%", 1.2, RED)


# ------------------------------------------------------------------ the news
# Every story below was reported on Saturday 21 November 2026, as
# carried that day by the wire services and the day's digests
# (AP, Reuters, BBC, AFP, Xinhua). Heroes first, then numbered cards.
HEROES = [
    ("missile", "RUSSIAN MISSILE LANDS IN POLAND",
     "Two missiles and a suspected drone come down; Warsaw calls it a "
     "deliberate provocation and NATO jets scramble."),
    ("leaf", "COP31 PASSES DEADLINE WITH NO FOSSIL-FUEL DEAL",
     "The draft drops every mention of fossil fuels, so the climate talks "
     "in Antalya spill into Saturday."),
    ("chart", "WALL ST SLIDES INTO CORRECTION",
     "S&P 500 -3.7% and Nasdaq -5.3% as the AI sell-off deepens; "
     "Nvidia falls 13.8%."),
]

# (number, icon, headline, summary)
CARDS = [
    (4, "gavel", "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "Judges rule 9-6 on the Rohingya and order a probe and compensation."),
    (5, "globe", "TRUMP, XI AND PUTIN SUMMIT ENDS FLAT",
     "Few concrete results in Shenzhen; humans stay in charge of military AI."),
    (6, "ship", "IRAN TANKERS MASS TO TEST US BLOCKADE",
     "14+ tankers gather at Kharg Island; Trump defers a strike decision."),
    (7, "missile", "SAUDI-HOUTHI FIGHTING ESCALATES",
     "Strikes hit four Yemeni cities; Houthi missiles at Riyadh intercepted."),
    (8, "flag", "UK AND EU SEAL FOOD AND CARBON DEALS",
     "Farm checks scrapped from 2028; carbon markets link, youth mobility opens."),
    (9, "chip", "TRUMP THREATENS BAN ON AI CENTRES ABROAD",
     "US firms may be barred from building data centres abroad."),
    (10, "quake", "6.8 QUAKE SHAKES CENTRAL PERU",
     "Junin region hit; tremors felt in Lima, 320 km away."),
    (11, "storm", "CYCLONE AKVAN HITS ODISHA COAST",
     "Crosses near Gopalpur with heavy rain, then weakens fast."),
    (12, "aid", "FOUR NATIONS URGE AID INTO FLOODED GAZA",
     "Four nations call on Israel to open humanitarian access at once."),
    (13, "vote", "EISENKOT TAPPED TO FORM ISRAEL GOVERNMENT",
     "President Herzog picks the ex-army chief over Netanyahu."),
    (14, "flag", "FRANCE: FOURTH WEEKEND OF PROTESTS",
     "Cost-of-living marches sweep the country again."),
    (15, "plane", "RUSSIAN MILITARY PLANE CRASHES IN SIBERIA",
     "Transport aircraft goes down; 19 people killed."),
    (16, "lock", "AUSTRIA MINISTRY WEBSITE HACKED",
     "Foreign ministry confirms breach; staff contact details viewed."),
    (17, "coin", "US DETAILS $12BN VENEZUELA OIL REVENUE",
     "State Dept report, nearly a year after Maduro was captured by US forces."),
    (18, "chip", "NVIDIA PROBES CEO LINK TO CHINESE SPY",
     "Chipmaker hires a law firm as the SEC examines accounting issues."),
    (19, "chip", "US CLEARED 900,000 AI CHIPS FOR CHINA",
     "Nearly 900,000 AI chip exports approved over six months."),
    (20, "court", "MAMDANI SETS 2032 TO CLOSE RIKERS",
     "New York mayor unveils first full plan to shut the jail complex."),
    (21, "fire", "PALISADES FIRE: MAN CONVICTED",
     "LA jury finds Jonathan Rinderknecht started the blaze."),
    (22, "coin", "RECORD CASH POURS INTO INDIAN SHARES",
     "Foreign investors put a record Rs 1.22 lakh crore in, 2-20 Nov."),
    (23, "chart", "SENSEX RALLIES; NSE NOW WORLD NO. 5",
     "Sensex up 898 to 83,920; exchange passes Nasdaq in size."),
    (24, "flag", "NEPAL PM HEADS TO DELHI ON FIRST TRIP",
     "Balendra Shah begins a two-day state visit; meets Modi."),
    (25, "star", "MODI MARKS 75 YEARS OF IIT KHARAGPUR",
     "PM tours West Bengal, Bihar and UP for the platinum jubilee."),
    (26, "bat", "KL RAHUL COMPLETES THE SENA SET",
     "First Indian opener with Test tons in all four SENA countries."),
    (27, "bat", "INDIA FIGHT BACK IN WELLINGTON TEST",
     "Rahul's century leads the reply against New Zealand."),
    (28, "ball", "ATP FINALS SEMIS SET IN TURIN",
     "Alcaraz v Shelton and Zverev v Medvedev on Saturday."),
    (29, "ball", "RAIN HITS LAS VEGAS GRAND PRIX",
     "Wet opening practice; Russell fastest in second session."),
    (30, "ball", "INDIA WOMEN BEAT MALAYSIA 4-1",
     "Winning start in the Asian Champions Trophy in Bhopal."),
    (31, "bat", "CUMMINS KEEPS CAPTAINCY BACKING",
     "Cricket Australia gives unanimous support to its captain."),
    (32, "fire", "INDONESIA FIRE LOSSES MAY HIT $30BN",
     "Economic toll of the fires keeps climbing."),
    (33, "flag", "JAPAN TO DRILL LIVE FIRE IN INDIA",
     "Japanese forces to use Indian facilities for the first time."),
    (34, "star", "CHEETAH GIVES BIRTH TO FOUR CUBS",
     "Botswana-born cheetah delivers at Kuno."),
    (35, "court", "19 YEARS FOR SIKH LEADER PLOT",
     "Indian man sentenced in the US over an assassination plot."),
    (36, "lock", "RANSOMWARE FIRM CTO CHARGED",
     "Florida executive accused of secretly paying a $6,000 bitcoin ransom."),
    (37, "chip", "GTA 6 PC SCAM: $200 MALWARE KIT",
     "Fake downloads target gamers with crypto theft."),
    (38, "lock", "BANKS REPORT VENDOR CYBERATTACKS",
     "JPMorgan, Visa and Mastercard hit via third-party providers."),
    (39, "flag", "INDIA HOLDS LINE ON INDUS TREATY",
     "No change in position as Pakistan minister attends the SCO forum in Delhi."),
    (40, "coin", "GOLD SLIDES AS STOCKS RALLY",
     "Gold prices fall sharply in India while markets climb."),
]
HERO_SCENES = [hero_poland, hero_cop, hero_market]


# --------------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    mx = 24                      # side margin
    cw = W - 2 * mx              # content width: 976

    # --- masthead: red rule, navy band, gold rule
    cv.fill(0, 0, W, 6, RED)
    cv.fill(0, 6, W, 92, NAVY)
    draw_text(cv, mx, 22, "THE SATURDAY GLOBE", 3.2, WHITE)
    draw_text(cv, W - mx, 30, "ONE PAGE, EVERY DAY", 1.3, GOLD, align="r")
    draw_text(cv, W - mx, 52, "SATURDAY EDITION", 1.3, WHITE, align="r")
    cv.fill(0, 92, W, 96, GOLD)

    # --- giant date headline + standfirst
    draw_text(cv, W // 2, 108, "SATURDAY 21 NOVEMBER 2026", 5.5, NAVY, align="c")
    draw_text(cv, W // 2, 158,
              "THE WORLD TODAY IN 40 STORIES - REPORTED SATURDAY 21 NOVEMBER 2026",
              1.25, RED, align="c")
    cv.hline(mx, 180, W - mx, INK)
    cv.hline(mx, 183, W - mx, INK)

    # --- three hero panels
    hy, hh = 192, 196
    hw = (cw - 16) // 3
    for i, (kind, head, sub) in enumerate(HEROES):
        x = mx + i * (hw + 8)
        cv.rect(x, hy, x + hw, hy + hh, INK, 1)
        cv.fill(x + 1, hy + 1, x + hw - 1, hy + hh - 1, WHITE)
        HERO_SCENES[i](cv, x + 1, hy + 1, hw - 2, 108)
        cv.fill(x + 1, hy + 109, x + hw - 1, hy + 112, RED)
        draw_text(cv, x + 10, hy + 120, "%d." % (i + 1), 1.5, RED)
        hlines = wrap(head, 1.7, hw - 44)[:2]
        yy = hy + 120
        for ln in hlines:
            draw_text(cv, x + 34, yy, ln, 1.7, INK)
            yy += 15
        slines = wrap(sub, 1.15, hw - 20)[:3]
        yy = hy + 152
        for ln in slines:
            draw_text(cv, x + 10, yy, ln, 1.15, GREY)
            yy += 11

    # --- section label
    draw_text(cv, mx, 400, "THE DAY IN 40 STORIES", 1.7, RED)
    draw_text(cv, W - mx, 402, "40 STORIES - ONE PAGE", 1.2, GREY,
              align="r")
    cv.hline(mx, 420, W - mx, INK)

    # --- story card grid: 4 cols x 10 rows; last row holds card 40 + footer
    gx, gy = mx, 428
    colw = (cw - 24) // 4        # 238
    rowh = 57
    gap = 8
    for idx, (num, kind, head, sub) in enumerate(CARDS):
        row, col = divmod(idx, 4)
        x = gx + col * (colw + gap)
        y = gy + row * (rowh + 1)
        cv.fill(x, y, x + colw, y + rowh, WHITE)
        cv.rect(x, y, x + colw, y + rowh, bytes((200, 194, 178)), 1)
        # number box + icon
        cv.fill(x + 4, y + 4, x + 24, y + 24, RED)
        draw_text(cv, x + 14, y + 8, "%02d" % num, 1.15, WHITE, align="c")
        icon(cv, x + colw - 24, y + 5, kind, NAVY)
        # headline, up to 2 lines
        hlines = wrap(head, 1.4, colw - 52)[:2]
        yy = y + 5
        for ln in hlines:
            draw_text(cv, x + 28, yy, ln, 1.4, INK)
            yy += 12
        # summary, up to 2 lines
        slines = wrap(sub, 1.0, colw - 10)[:2]
        yy = y + 31
        for ln in slines:
            draw_text(cv, x + 5, yy, ln, 1.0, GREY)
            yy += 9

    # --- footer: DATE CHECK stamp + sources, spanning last row cols 2-4
    fx = gx + (colw + gap)
    fy = gy + 9 * (rowh + 1)
    fw = 3 * colw + 2 * gap
    cv.fill(fx, fy, fx + fw, fy + rowh, NAVY)
    cv.rect(fx, fy, fx + fw, fy + rowh, NAVY, 2)
    draw_text(cv, fx + 12, fy + 8, "DATE CHECK", 1.6, GOLD)
    draw_text(cv, fx + 12, fy + 26,
              "EVERY STORY ABOVE WAS REPORTED ON SATURDAY 21 NOVEMBER 2026.",
              1.15, WHITE)
    draw_text(cv, fx + 12, fy + 41,
              "SOURCES: AP, REUTERS, BBC, AFP, XINHUA. 21 NOV IS WORLD TELEVISION DAY.",
              1.0, bytes((200, 205, 225)))
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    png = encode_png(build().px, W, H)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
