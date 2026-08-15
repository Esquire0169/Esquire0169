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
import os
import sys

from PIL import Image, ImageEnhance, ImageOps

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


# Horizontally symmetric 5x5 — same mark as the avatar.
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
    from PIL import ImageDraw, ImageFilter

    img = Image.new("L", (width, height), 255)
    d = ImageDraw.Draw(img)
    n = 5
    cw, ch = 128.0, 74.0
    origin = (width / 2.0, height * 0.36)

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
    return img.filter(ImageFilter.GaussianBlur(radius=0.4))


def load_source() -> Image.Image:
    if PHOTO:
        im = Image.open(PHOTO).convert("L")
        return ImageEnhance.Contrast(im).enhance(CONTRAST)
    return draw_cubes(920, 520)


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
    n = len(rows_txt)
    type_span = (n - 1) * STAGGER + ROW_DUR
    cycle = type_span + 2.8  # hold, then loop forever
    sweep = ART_W + 240

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient>"
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{PAD}" y1="0" x2="{PAD + 280}" y2="0">'
        '<stop offset="0%" stop-color="#22d3ee"/>'
        '<stop offset="35%" stop-color="#a371f7"/>'
        '<stop offset="70%" stop-color="#39d353"/>'
        '<stop offset="100%" stop-color="#22d3ee"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" '
        f'from="-{sweep} 0" to="{sweep} 0" dur="4.5s" repeatCount="indefinite"/>'
        "</linearGradient>"
        "</defs>",
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
        f'text-anchor="middle">{PROMPT_HOST}: ~$ ./portrait.sh --loop</text>'
    )

    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86
    fill = "url(#ink)"
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        t0 = max(0.002, delay / cycle)
        t1 = min(0.84, max(t0 + 0.004, (delay + ROW_DUR) / cycle))
        t_hold = 0.88
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{fill}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">'
            f"{safe}</text>"
        )
        if STATIC:
            parts.append(text)
            continue
        parts.append(
            f'<clipPath id="r{ry}">'
            f'<rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" values="0;0;{ART_W};{ART_W};0" '
            f'keyTimes="0;{t0:.4f};{t1:.4f};{t_hold:.2f};1" '
            f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y + 1:.1f}" width="{CELL_W}" height="{CELL_H - 2}" fill="#22d3ee" opacity="0">'
            f'<animate attributeName="x" values="{PAD};{PAD};{PAD + ART_W};{PAD + ART_W};{PAD}" '
            f'keyTimes="0;{t0:.4f};{t1:.4f};{t_hold:.2f};1" '
            f'dur="{cycle:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;0.9;0;0" '
            f'keyTimes="0;{t0:.4f};{t1:.4f};{t_hold:.2f};1" '
            f'dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>'
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
