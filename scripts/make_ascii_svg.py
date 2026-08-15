#!/usr/bin/env python3
"""
ASCII portrait that types itself in, then freezes.

Default: Lambert-shaded 3D bust (head / neck / shoulders) — the look from
Avi's terminal profile, without needing a photo.
Optional: pass a prepped grayscale image as argv[1] for a real portrait later.

    python scripts/make_ascii_svg.py
    python scripts/make_ascii_svg.py source-prepped.png ascii-portrait.svg
    STATIC=1 python scripts/make_ascii_svg.py
"""
from __future__ import annotations

import html
import math
import os
import sys

from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import BG, BG2, CURSOR, DISPLAY_NAME, FRAME, INK, PROMPT_HOST, TITLE_TEXT

OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "ascii-portrait.svg")
PHOTO = sys.argv[1] if len(sys.argv) > 1 else None

COLS = 92
ROWS = 52
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"
WHITE_FLOOR = 0.88
GAMMA = 1.05
CONTRAST = 1.12

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

ROW_DUR = 0.09
STAGGER = 0.09
STATIC = bool(os.environ.get("STATIC"))

# (cx, cy, cz, rx, ry, rz) — y up, z toward camera
SOLIDS = [
    (0.00, 0.28, 0.00, 0.44, 0.54, 0.46),   # head
    (-0.43, 0.26, 0.02, 0.09, 0.16, 0.11),  # ear L
    (0.43, 0.26, 0.02, 0.09, 0.16, 0.11),   # ear R
    (0.00, -0.22, 0.06, 0.17, 0.24, 0.16),  # neck
    (0.00, -0.58, 0.10, 0.84, 0.28, 0.34),  # shoulders
]


def draw_bust(width: int, height: int) -> Image.Image:
    """Orthographic ellipsoid bust, white bg → ASCII spaces."""
    img = Image.new("L", (width, height), 255)
    px = img.load()
    lx, ly, lz = -0.35, 0.50, 0.79
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln

    for j in range(height):
        for i in range(width):
            x = (i / (width - 1) - 0.5) * 2.05
            y = -((j / (height - 1) - 0.48) * 2.15)
            best_z = None
            best_n = None
            for cx, cy, cz, rx, ry, rz in SOLIDS:
                a = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if a >= 1.0:
                    continue
                dz = rz * math.sqrt(1.0 - a)
                z_front = cz + dz
                if best_z is None or z_front > best_z:
                    best_z = z_front
                    nx = (x - cx) / (rx * rx)
                    ny = (y - cy) / (ry * ry)
                    nz = (z_front - cz) / (rz * rz)
                    nn = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                    best_n = (nx / nn, ny / nn, nz / nn)
            if best_n is None:
                continue
            shade = max(0.0, best_n[0] * lx + best_n[1] * ly + best_n[2] * lz)
            shade = 0.12 + 0.88 * shade
            lum = int(255 * (1.0 - shade * 0.94))
            px[i, j] = lum
    return img


def load_source() -> Image.Image:
    if PHOTO:
        im = Image.open(PHOTO).convert("L")
        return ImageEnhance.Contrast(im).enhance(CONTRAST)
    return draw_bust(736, 416)


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
    return rows


def emit(rows_txt: list[str]) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient></defs>",
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W - 1}" height="{CANVAS_H - 1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(
            f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dotcol}"/>'
        )
    parts.append(
        f'<text x="{CANVAS_W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
        f'text-anchor="middle">{PROMPT_HOST}: ~$ ./portrait.sh</text>'
    )

    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">'
            f"{safe}</text>"
        )
        if STATIC:
            parts.append(text)
            continue
        parts.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y + 1:.1f}" width="{CELL_W}" height="{CELL_H - 2}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + ROW_DUR:.3f}s"/></rect>'
        )

    status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(
        f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" '
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
    print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
