#!/usr/bin/env python3
"""World news of Saturday 21 November 2026, drawn as one newspaper image.

Pure Python 3.13 standard library. Draws a 1024x1024 front page with an
embedded 8x12 bitmap font (rasterised from DejaVu Sans) and writes a PNG
with a hand-rolled encoder (zlib). No network, no time, no randomness:
two runs write byte-identical files.
"""
import base64
import os
import struct
import zlib

# ---------------------------------------------------------------- font ----
# Bitmap font: chars 32..126, regular then bold. Each glyph is 13 bytes:
# one width byte (1..8) + 12 rows of 8 bits. Rasterised from DejaVu Sans.
FONT_B64 = (
'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',
'AAAAAABx/44AAA==',
)

_FONT_RAW = base64.b64decode("".join(FONT_B64))
# glyphs[weight][ord-32] = (width, rows tuple of 12 ints)
_GLYPHS = []
for _w in range(2):
    bank = []
    base = _w * 95 * 13
    for _i in range(95):
        off = base + _i * 13
        bank.append((_FONT_RAW[off], tuple(_FONT_RAW[off + 1:off + 13])))
    _GLYPHS.append(bank)

# glyph cache: (weight, ch, scale) -> (width_px, [row bytes]) row bytes are RGB
_GCACHE = {}


def glyph_rows(weight, ch, scale):
    key = (weight, ch, scale)
    hit = _GCACHE.get(key)
    if hit is not None:
        return hit
    width, rows = _GLYPHS[weight][ord(ch) - 32]
    out = []
    for bits in rows:
        line = bytearray()
        for x in range(width):
            on = (bits >> (7 - x)) & 1
            line += b"\x01" * scale if on else b"\x00" * scale
        out.extend([bytes(line)] * scale)
    res = (width * scale, out)
    _GCACHE[key] = res
    return res


def text_width(text, scale, bold=False):
    w = 0
    weight = 1 if bold else 0
    for ch in text:
        if ch == " ":
            w += 4 * scale
        else:
            gw, _ = glyph_rows(weight, ch, scale)
            w += gw + scale
    return w - scale if w else 0


def wrap_text(text, width, scale, bold=False):
    """Greedy word wrap; returns list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, bold) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def _row(self, y):
        return y * self.w * 3

    def fill_rect(self, x, y, w, h, color):
        x = max(0, x)
        y = max(0, y)
        w = min(w, self.w - x)
        h = min(h, self.h - y)
        if w <= 0 or h <= 0:
            return
        row = bytes(color) * w
        for yy in range(y, y + h):
            off = self._row(yy) + x * 3
            self.px[off:off + w * 3] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            inner = int(((r - thick) ** 2 - dy * dy) ** 0.5) if abs(dy) < r - thick else -1
            if inner >= 0:
                self.fill_rect(cx - dx, cy + dy, dx - inner, 1, color)
                self.fill_rect(cx + inner + 1, cy + dy, dx - inner, 1, color)
            else:
                self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def star(self, cx, cy, r, color):
        """8-point starburst."""
        for k in range(8):
            import math
            a = math.pi * k / 4.0
            x1 = cx + int(r * math.cos(a))
            y1 = cy + int(r * math.sin(a))
            self.line(cx, cy, x1, y1, color, 3)
        self.disc(cx, cy, max(2, r // 3), color)

    def draw_text(self, x, y, text, scale, color, bold=False):
        weight = 1 if bold else 0
        cx = x
        for ch in text:
            if ch == " ":
                cx += 4 * scale
                continue
            gw, rows = glyph_rows(weight, ch, scale)
            rgb = bytes(color)
            for i, row in enumerate(rows):
                yy = y + i
                if yy < 0 or yy >= self.h:
                    continue
                off = self._row(yy) + cx * 3
                pos = 0
                for v in row:
                    if v:
                        self.px[off + pos * 3:off + pos * 3 + 3] = rgb
                    pos += 1
            cx += gw + scale
        return cx

    def draw_text_block(self, x, y, text, width, scale, color, bold=False,
                        leading=None):
        """Draw wrapped text; returns y just below the block."""
        lh = 12 * scale + (leading if leading is not None else 4 * scale // 2)
        for line in wrap_text(text, width, scale, bold):
            self.draw_text(x, y, line, scale, color, bold)
            y += lh
        return y


# ------------------------------------------------------------------ png ----
def write_png(canvas, path):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ----------------------------------------------------------------- page ----
W = H = 1024
M = 36
CW = W - 2 * M

PAPER = (250, 246, 238)
INK = (22, 21, 19)
RED = (179, 38, 30)
NAVY = (31, 58, 95)
NAVY_DARK = (18, 36, 62)
SEA = (46, 92, 138)
GOLD = (201, 162, 39)
GREY = (110, 106, 98)
LIGHT = (233, 226, 210)
ORANGE = (214, 106, 32)
WHITE = (250, 248, 244)

LEAD = ("GULF CRISIS",
        "IRAN STRIKES U.S. BASES IN BAHRAIN",
        "Tehran says its Guards hit two U.S. positions. Bahrain reports a "
        "fire, no injuries. Tanker strikes near Hormuz hit a wartime high.")

UKRAINE = ("WAR IN UKRAINE",
           "RUSSIAN MISSILE HITS ZELENSKY HOMETOWN",
           "A Russian missile hit Kryvyi Rih, killing two, wounding "
           "dozens. Missiles also landed in Poland.")

SHENZHEN = ("DIPLOMACY: SHENZHEN",
            "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
            "Trump defends Putin ties; Zelensky calls Putin a 'killer'.")

MEXICO = ("MEXICO",
          "FBI MOST-WANTED CARTEL BOSS SEIZED",
          "Meza Flores seized in Sinaloa; 11 die in the backlash.")

MARKETS = ("MARKETS",
           "U.S. STOCKS SLIDE INTO CORRECTION",
           "AI sell-off deepens; Nasdaq erases its 2026 gains.")

CLIMATE = ("CLIMATE: COP31, ANTALYA",
           "CLIMATE TALKS MISS DEADLINE",
           "Antalya summit in overtime; the draft leaves out fossil fuels.")

SPACE = ("SPACE",
         "BEPICOLOMBO REACHES MERCURY",
         "Two craft enter orbit after an eight-year voyage.")


def story_height(kicker, headline, summary, width, hscale):
    """Height of a story block: kicker + headline + summary."""
    hh = 12 * 2 + 4
    hl = len(wrap_text(headline, width, hscale, True))
    hh += hl * (12 * hscale + 2 * hscale) + 8
    sl = len(wrap_text(summary, width, 2, False))
    hh += sl * (12 * 2 + 4) + 4
    return hh


def draw_story(cv, x, y, width, kicker, headline, summary, hscale, icon=None):
    """Draw a story block at (x, y); returns y below the block."""
    if icon:
        icon(x + width - 48, y - 2)
    cv.draw_text(x, y, kicker, 2, RED, True)
    y += 12 * 2 + 6
    y = cv.draw_text_block(x, y, headline, width, hscale, INK, True,
                           leading=2 * hscale)
    y += 6
    y = cv.draw_text_block(x, y, summary, width, 2, INK, False, leading=4)
    return y


def icon_blast(cv, x, y):
    cv.star(x + 22, y + 22, 16, RED)
    cv.star(x + 30, y + 12, 8, ORANGE)


def icon_flags(cv, x, y):
    # US: stripes + blue corner; China: red + stars; Russia: tricolour
    fx, fy = x, y + 6
    for i in range(4):
        cv.fill_rect(fx, fy + i * 5, 14, 3, RED if i % 2 == 0 else WHITE)
    cv.fill_rect(fx, fy, 7, 10, NAVY)
    cv.fill_rect(fx + 17, fy, 14, 20, RED)
    cv.disc(fx + 21, fy + 5, 2, GOLD)
    cv.disc(fx + 26, fy + 9, 1, GOLD)
    cv.fill_rect(fx + 34, fy, 14, 7, WHITE)
    cv.fill_rect(fx + 34, fy + 7, 14, 6, (46, 92, 180))
    cv.fill_rect(fx + 34, fy + 13, 14, 7, RED)


def icon_badge(cv, x, y):
    cv.disc(x + 22, y + 22, 20, NAVY)
    cv.star(x + 22, y + 22, 12, GOLD)


def icon_chart(cv, x, y):
    cv.line(x + 4, y + 8, x + 16, y + 16, RED, 3)
    cv.line(x + 16, y + 16, x + 26, y + 14, RED, 3)
    cv.line(x + 26, y + 14, x + 44, y + 38, RED, 3)
    cv.line(x + 44, y + 38, x + 38, y + 38, RED, 3)
    cv.line(x + 44, y + 38, x + 44, y + 32, RED, 3)


def icon_globe(cv, x, y):
    cv.disc(x + 22, y + 22, 19, SEA)
    cv.ring(x + 22, y + 22, 19, WHITE, 2)
    cv.line(x + 22, y + 3, x + 22, y + 41, WHITE, 2)
    cv.line(x + 4, y + 22, x + 40, y + 22, WHITE, 2)


def icon_planet(cv, x, y):
    cv.disc(x + 22, y + 20, 13, GOLD)
    cv.line(x + 2, y + 28, x + 42, y + 12, WHITE, 3)
    cv.disc(x + 40, y + 34, 3, GREY)


def draw_lead_panel(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, NAVY_DARK)
    cv.fill_rect(x, y + int(h * 0.42), w, h - int(h * 0.42), NAVY)
    # land mass, top right
    cv.fill_rect(x + int(w * 0.45), y, w - int(w * 0.45), int(h * 0.42),
                 (94, 116, 84))
    cv.hline(x, y + int(h * 0.42), w, GOLD, 3)
    # missile arc from the sea to the coast
    cv.line(x + 30, y + h - 30, x + int(w * 0.55), y + int(h * 0.45),
            WHITE, 2)
    cv.line(x + int(w * 0.55), y + int(h * 0.45),
            x + int(w * 0.62), y + int(h * 0.38), WHITE, 2)
    # blasts on the coast
    cv.star(x + int(w * 0.62), y + int(h * 0.38), 15, ORANGE)
    cv.star(x + int(w * 0.80), y + int(h * 0.30), 11, RED)
    cv.star(x + int(w * 0.30), y + int(h * 0.62), 9, GOLD)
    cv.draw_text(x + 12, y + 10, "THE GULF", 2, WHITE, True)
    cv.draw_text(x + 12, y + h - 30, "HORMUZ STRAIT", 2, WHITE, True)


def build():
    cv = Canvas(W, H, PAPER)
    y = 16
    # masthead
    title = "WORLD NEWS"
    tw = text_width(title, 8, True)
    cv.draw_text((W - tw) // 2, y, title, 8, INK, True)
    y += 96 + 8
    cv.hline(M, y, CW, RED, 6)
    y += 6 + 10
    # dateline
    date = "SATURDAY, 21 NOVEMBER 2026"
    dw = text_width(date, 3, True)
    cv.draw_text((W - dw) // 2, y, date, 3, INK, True)
    y += 36 + 8
    cv.hline(M, y, CW, INK, 2)
    y += 2 + 12
    # lead story + panel
    lead_y = y
    lw = 668
    lh = story_height(LEAD[0], LEAD[1], LEAD[2], lw, 4)
    lead_h = max(lh, 220)
    draw_story(cv, M, lead_y, lw, LEAD[0], LEAD[1], LEAD[2], 4)
    draw_lead_panel(cv, M + lw + 24, lead_y, W - M - (M + lw + 24), lead_h)
    y = lead_y + lead_h + 12
    cv.hline(M, y, CW, INK, 2)
    y += 2 + 12
    # middle row: two stories side by side
    col_w = (CW - 24) // 2
    h1 = story_height(UKRAINE[0], UKRAINE[1], UKRAINE[2], col_w, 3)
    h2 = story_height(SHENZHEN[0], SHENZHEN[1], SHENZHEN[2], col_w, 3)
    row_h = max(h1, h2)
    draw_story(cv, M, y, col_w, UKRAINE[0], UKRAINE[1], UKRAINE[2], 3,
               icon=lambda a, b: icon_blast(cv, a, b))
    draw_story(cv, M + col_w + 24, y, col_w, SHENZHEN[0], SHENZHEN[1],
               SHENZHEN[2], 3,
               icon=lambda a, b: icon_flags(cv, a, b))
    y += row_h + 12
    cv.hline(M, y, CW, INK, 2)
    y += 2 + 12
    # bottom grid: 2 x 2
    cells = [(MEXICO, icon_badge), (MARKETS, icon_chart),
             (CLIMATE, icon_globe), (SPACE, icon_planet)]
    for row in range(2):
        a = cells[row * 2]
        b = cells[row * 2 + 1]
        ha = story_height(a[0][0], a[0][1], a[0][2], col_w, 2)
        hb = story_height(b[0][0], b[0][1], b[0][2], col_w, 2)
        rh = max(ha, hb)
        draw_story(cv, M, y, col_w, a[0][0], a[0][1], a[0][2], 2,
                   icon=lambda p, q, f=a[1]: f(cv, p, q))
        draw_story(cv, M + col_w + 24, y, col_w, b[0][0], b[0][1], b[0][2],
                   2, icon=lambda p, q, f=b[1]: f(cv, p, q))
        y += rh + 8
        if row == 0:
            cv.hline(M, y - 4, CW, LIGHT, 2)
    # footer
    cv.hline(M, y, CW, INK, 2)
    y += 2 + 8
    foot = "ALL EVENTS REPORTED ON 21 NOVEMBER 2026"
    fw = text_width(foot, 2, False)
    cv.draw_text((W - fw) // 2, y, foot, 2, GREY, False)
    y += 24
    print("layout bottom y =", y, "of", H)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
