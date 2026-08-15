#!/usr/bin/env python3
"""
ASCII cube mark that stays on screen, with an infinite cyan–violet–green
gradient running through the glyphs.

    python scripts/make_ascii_svg.py
    python scripts/make_ascii_svg.py source-prepped.png ascii-portrait.svg
"""
from __future__ import annotations

import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import BG, BG2, DISPLAY_NAME, FRAME, INK, PROMPT_HOST, TITLE_TEXT

OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "ascii-portrait.svg")
PHOTO = sys.argv[1] if len(sys.argv) > 1 else None

COLS = 92
ROWS = 36
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"
WHITE_FLOOR = 0.90
GAMMA = 1.05
CONTRAST = 1.12

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30

# Same 5×5 as the avatar mark.
PATTERN = [
    [1, 0, 0, 0, 1],
    [0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1],
]


def _iso_pt(i: float, j: float, k: float, origin, cw: float, ch: float):
    x = (i - j) * cw / 2.0 + origin[0]
    y = (i + j) * ch / 4.0 - k * ch / 2.0 + origin[1]
    return (x, y)


def draw_cubes(width: int, height: int) -> Image.Image:
    img = Image.new("L", (width, height), 255)
    d = ImageDraw.Draw(img)
    n = 5
    cw, ch = 168.0, 96.0
    origin = (width / 2.0, height * 0.42)

    def cube(i, j, k=0.0, h=1.15):
        t = _iso_pt(i, j, k + h, origin, cw, ch)
        r = _iso_pt(i + 1, j, k + h, origin, cw, ch)
        b = _iso_pt(i + 1, j + 1, k + h, origin, cw, ch)
        l = _iso_pt(i, j + 1, k + h, origin, cw, ch)
        br = _iso_pt(i + 1, j, k, origin, cw, ch)
        bb = _iso_pt(i + 1, j + 1, k, origin, cw, ch)
        bl = _iso_pt(i, j + 1, k, origin, cw, ch)
        d.polygon([r, b, bb, br], fill=92)
        d.polygon([l, b, bb, bl], fill=36)
        d.polygon([t, r, b, l], fill=150)
        d.line([t, r, b, l, t], fill=18, width=2)
        d.line([r, br], fill=18, width=2)
        d.line([b, bb], fill=18, width=2)
        d.line([l, bl], fill=18, width=2)

    for s in range(2 * n):
        for i in range(n):
            j = s - i
            if 0 <= j < n and PATTERN[j][i]:
                cube(i - 2.0, j - 2.0)
    return img.filter(ImageFilter.GaussianBlur(radius=0.35))


def load_source() -> Image.Image:
    if PHOTO:
        im = Image.open(PHOTO).convert("L")
        return ImageEnhance.Contrast(im).enhance(CONTRAST)
    return draw_cubes(1100, 620)


def to_rows(im: Image.Image) -> list[str]:
    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            lum = pow(lum, GAMMA)
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    # Keep a single blank breathing row above/below the mark.
    rows = [" " * COLS, *rows, " " * COLS]
    return rows


def emit(rows_txt: list[str]) -> str:
    n = len(rows_txt)
    art_w = COLS * CELL_W
    art_h = n * CELL_H
    canvas_w = art_w + PAD * 2
    canvas_h = TITLEBAR_H + art_h + STATUS_H + PAD
    sweep = art_w + 320

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient>"
        # Wide repeating band so the run never stops.
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{art_w}" y2="0">'
        '<stop offset="0%" stop-color="#22d3ee"/>'
        '<stop offset="25%" stop-color="#a371f7"/>'
        '<stop offset="50%" stop-color="#39d353"/>'
        '<stop offset="75%" stop-color="#22d3ee"/>'
        '<stop offset="100%" stop-color="#a371f7"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" '
        f'values="-{sweep} 0; {sweep} 0; -{sweep} 0" '
        f'dur="6s" repeatCount="indefinite"/>'
        "</linearGradient>"
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
        f'text-anchor="middle">{PROMPT_HOST}: ~$ ./portrait.sh --loop</text>'
    )

    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86
    # Always visible — the gradient is what runs, not a typewriter wipe.
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        safe = html.escape(line)
        parts.append(
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="url(#ink)" '
            f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">'
            f"{safe}</text>"
        )

    status_line_y = TITLEBAR_H + art_h + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(
        f'<line x1="0" y1="{status_line_y:.1f}" x2="{canvas_w}" y2="{status_line_y:.1f}" '
        f'stroke="{FRAME}"/>'
    )
    prefix = f"{PROMPT_HOST}:~$ whoami "
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
        f'{html.escape(prefix)}<tspan fill="{INK}">{html.escape(DISPLAY_NAME)}</tspan></text>'
    )
    cursor_x = PAD + len(prefix + DISPLAY_NAME) * 7.4
    parts.append(
        f'<rect x="{cursor_x:.1f}" y="{status_y - 12:.1f}" width="8" height="14" fill="{INK}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    rows = to_rows(load_source())
    svg = emit(rows)
    with open(OUT, "w") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes")
