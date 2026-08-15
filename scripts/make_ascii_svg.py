#!/usr/bin/env python3
"""
ASCII mark from the Plix lockup. A looping ASCII "PLIX GROUP"
ticker sits under the art, painted with the same plix glyphs.

    python scripts/make_ascii_svg.py
    python scripts/make_ascii_svg.py path/to/photo.png ascii-portrait.svg
"""
from __future__ import annotations

import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import BG, BG2, DISPLAY_NAME, FRAME, INK, PROMPT_HOST, TITLE_TEXT

PHOTO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "ascii-portrait.svg")

HANDLE = "plix"
BANNER = "PLIX GROUP"
COLS = 102
CELL_W = 8
CELL_H = 15
PAD = 20
TITLEBAR_H = 30
STATUS_H = 34

# 5-row block font. On-pixels become "plix" glyphs so the ticker
# matches the lockup above it.
GLYPHS = {
    "P": ["#####", "#   #", "#####", "#    ", "#    "],
    "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
    "I": ["###", " # ", " # ", " # ", "###"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "G": [" ####", "#    ", "#  ##", "#   #", " ### "],
    "R": ["#####", "#   #", "#####", "#  # ", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    " ": ["  ", "  ", "  ", "  ", "  "],
}
GLYPH_H = 5
BANNER_GAP = "    "

# Thin → dense, only letters from the mark.
RAMP = " ilxpg"
BG_CUT = 0.28
GAMMA = 0.78


def load_photo(path: str) -> Image.Image:
    im = Image.open(path).convert("L")
    w, h = im.size
    # Wordmark only — drop the tiny header/footer lines.
    im = im.crop((int(w * 0.04), int(h * 0.20), int(w * 0.96), int(h * 0.62)))
    w, h = im.size
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=3)
    im = ImageEnhance.Contrast(im).enhance(1.85)
    im = ImageEnhance.Brightness(im).enhance(1.04)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=170, threshold=1))
    return im


def row_count(im: Image.Image) -> int:
    aspect = im.width / max(1, im.height)
    visual = aspect * CELL_H / CELL_W
    rows = int(round(COLS / visual))
    return max(22, min(40, rows))


def to_rows(im: Image.Image) -> list[str]:
    rows_n = row_count(im)
    im = im.resize((COLS, rows_n), Image.LANCZOS)
    px = im.load()
    rows = []
    n_ramp = len(RAMP) - 1
    for y in range(rows_n):
        chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            if lum <= BG_CUT:
                chars.append(" ")
                continue
            t = (lum - BG_CUT) / (1.0 - BG_CUT)
            t = pow(max(0.0, min(1.0, t)), GAMMA)
            idx = int(t * n_ramp + 0.5)
            idx = max(1, min(n_ramp, idx))
            handle_ch = HANDLE[x % len(HANDLE)]
            handle_w = RAMP.find(handle_ch)
            if handle_w < 0:
                handle_w = idx
            if idx >= max(2, handle_w):
                chars.append(handle_ch)
            else:
                chars.append(RAMP[idx])
        rows.append("".join(chars))
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    while rows and len(rows[-1].replace(" ", "")) < 8:
        rows.pop()
    while rows and len(rows[0].replace(" ", "")) < 8:
        rows.pop(0)
    pad = " " * COLS
    return [pad, *rows, pad]


def banner_rows() -> list[str]:
    glyphs = [GLYPHS[ch] for ch in BANNER]
    lines = []
    for y in range(GLYPH_H):
        raw = "  ".join(g[y] for g in glyphs) + BANNER_GAP
        painted = []
        for x, ch in enumerate(raw):
            painted.append(HANDLE[x % len(HANDLE)] if ch == "#" else " ")
        lines.append("".join(painted))
    return lines


def gradient_def() -> str:
    return (
        '<linearGradient id="ink" x1="-100%" y1="0" x2="0%" y2="0">'
        '<stop offset="0%" stop-color="#22d3ee">'
        '<animate attributeName="stop-color" values="#22d3ee;#a371f7;#39d353;#22d3ee" dur="3s" repeatCount="indefinite"/>'
        "</stop>"
        '<stop offset="50%" stop-color="#a371f7">'
        '<animate attributeName="stop-color" values="#a371f7;#39d353;#22d3ee;#a371f7" dur="3s" repeatCount="indefinite"/>'
        "</stop>"
        '<stop offset="100%" stop-color="#39d353">'
        '<animate attributeName="stop-color" values="#39d353;#22d3ee;#a371f7;#39d353" dur="3s" repeatCount="indefinite"/>'
        "</stop>"
        '<animate attributeName="x1" values="-100%;100%" dur="5s" repeatCount="indefinite"/>'
        '<animate attributeName="x2" values="0%;200%" dur="5s" repeatCount="indefinite"/>'
        "</linearGradient>"
    )


def emit(rows_txt: list[str], ticker: list[str]) -> str:
    n = len(rows_txt)
    art_w = COLS * CELL_W
    art_h = n * CELL_H
    banner_h = GLYPH_H * CELL_H + 12
    canvas_w = art_w + PAD * 2
    canvas_h = TITLEBAR_H + art_h + banner_h + STATUS_H
    font_size = CELL_H * 0.86
    art_top = TITLEBAR_H + 4
    banner_y = TITLEBAR_H + art_h
    unit_cols = len(ticker[0])
    unit = unit_cols * CELL_W
    copies = 4

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient>",
        gradient_def(),
        f'<clipPath id="banner"><rect x="0" y="{banner_y}" width="{canvas_w}" height="{banner_h}"/></clipPath>',
        "</defs>",
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w - 1}" height="{canvas_h - 1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(
            f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dotcol}"/>'
        )
    parts.append(
        f'<text x="{canvas_w / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
        f'text-anchor="middle">{PROMPT_HOST}: ~$ ./plix.sh --loop</text>'
    )

    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        parts.append(
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="url(#ink)" '
            f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">'
            f"{html.escape(line)}</text>"
        )

    parts.append(
        f'<line x1="0" y1="{banner_y}" x2="{canvas_w}" y2="{banner_y}" stroke="{FRAME}"/>'
    )
    parts.append('<g clip-path="url(#banner)"><g>')
    parts.append(
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="-{unit} 0" dur="12s" repeatCount="indefinite"/>'
    )
    ticker_top = banner_y + 8
    for i in range(copies):
        x0 = PAD + i * unit
        for ry, line in enumerate(ticker):
            y = ticker_top + ry * CELL_H + CELL_H * 0.74
            parts.append(
                f'<text xml:space="preserve" x="{x0}" y="{y:.1f}" fill="url(#ink)" '
                f'font-size="{font_size:.1f}" textLength="{unit_cols * CELL_W}" '
                f'lengthAdjust="spacing">{html.escape(line)}</text>'
            )
    parts.append("</g></g>")

    status_y = banner_y + banner_h
    parts.append(
        f'<line x1="0" y1="{status_y}" x2="{canvas_w}" y2="{status_y}" stroke="{FRAME}"/>'
    )
    prefix = f"{PROMPT_HOST}:~$ whoami "
    parts.append(
        f'<text x="{PAD}" y="{status_y + 22}" fill="{TITLE_TEXT}" font-size="13">'
        f'{html.escape(prefix)}<tspan fill="{INK}">{html.escape(DISPLAY_NAME)}</tspan></text>'
    )
    cursor_x = PAD + len(prefix + DISPLAY_NAME) * 7.4
    parts.append(
        f'<rect x="{cursor_x:.1f}" y="{status_y + 10}" width="8" height="14" fill="{INK}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
        'dur="1s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    if not os.path.isfile(PHOTO):
        sys.exit(f"missing photo: {PHOTO}")
    rows = to_rows(load_photo(PHOTO))
    ticker = banner_rows()
    svg = emit(rows, ticker)
    with open(OUT, "w") as f:
        f.write(svg)
    preview = os.path.join(HERE, "..", "ascii-preview.txt")
    with open(preview, "w") as f:
        f.write("\n".join(rows) + "\n\n--- ticker ---\n" + "\n".join(ticker) + "\n")
    print("wrote", OUT, len(svg), "bytes;", COLS, "x", len(rows))
