#!/usr/bin/env python3
"""
Terminal banner: esquire0169 runs forever through a cyan–violet–green gradient.

    python scripts/make_ascii_svg.py
"""
from __future__ import annotations

import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import BG, BG2, DISPLAY_NAME, FRAME, INK, PROMPT_HOST, TITLE_TEXT, USERNAME

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "ascii-portrait.svg")

HANDLE = USERNAME.lower()  # esquire0169
CANVAS_W = 860
TITLEBAR_H = 30
STATUS_H = 36
PAD = 20
STAGE_H = 120
CANVAS_H = TITLEBAR_H + STAGE_H + STATUS_H

# One marquee cell: the handle plus a gap, wide enough to read at a glance.
FONT_SIZE = 72
CELL_W = 560
GAP = 80
UNIT = CELL_W + GAP
SWEEP = CANVAS_W + 240


def emit() -> str:
    word = html.escape(HANDLE)
    y = TITLEBAR_H + STAGE_H * 0.68
    copies = 4

    texts = []
    for i in range(copies):
        texts.append(
            f'<text xml:space="preserve" x="{PAD + i * UNIT}" y="{y:.1f}" fill="url(#ink)" '
            f'font-size="{FONT_SIZE}" font-weight="700" letter-spacing="4" '
            f'textLength="{CELL_W}" lengthAdjust="spacing">{word}</text>'
        )

    return "".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
            f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
            f'Menlo, Consolas, monospace">',
            "<defs>",
            f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
            "</linearGradient>",
            f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{CANVAS_W}" y2="0">'
            '<stop offset="0%" stop-color="#22d3ee"/>'
            '<stop offset="25%" stop-color="#a371f7"/>'
            '<stop offset="50%" stop-color="#39d353"/>'
            '<stop offset="75%" stop-color="#22d3ee"/>'
            '<stop offset="100%" stop-color="#a371f7"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" '
            f'from="-{SWEEP} 0" to="{SWEEP} 0" dur="5s" repeatCount="indefinite"/>'
            "</linearGradient>",
            f'<clipPath id="stage"><rect x="0" y="{TITLEBAR_H}" width="{CANVAS_W}" height="{STAGE_H}"/></clipPath>',
            "</defs>",
            f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
            f'<rect x="0.5" y="0.5" width="{CANVAS_W - 1}" height="{CANVAS_H - 1}" rx="12" '
            f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
            f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
            *[
                f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{c}"/>'
                for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"])
            ],
            f'<text x="{CANVAS_W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
            f'text-anchor="middle">{PROMPT_HOST}: ~$ echo {word}</text>',
            '<g clip-path="url(#stage)">',
            '<g>',
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="-{UNIT} 0" dur="8s" repeatCount="indefinite"/>',
            *texts,
            "</g>",
            "</g>",
            f'<line x1="0" y1="{TITLEBAR_H + STAGE_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H + STAGE_H}" '
            f'stroke="{FRAME}"/>',
            f'<text x="{PAD}" y="{TITLEBAR_H + STAGE_H + 24}" fill="{TITLE_TEXT}" font-size="13">'
            f'{html.escape(PROMPT_HOST)}:~$ whoami '
            f'<tspan fill="{INK}">{html.escape(DISPLAY_NAME)}</tspan></text>',
            f'<rect x="{PAD + (len(PROMPT_HOST) + len(":~$ whoami ") + len(DISPLAY_NAME)) * 7.4:.1f}" '
            f'y="{TITLEBAR_H + STAGE_H + 12}" width="8" height="14" fill="{INK}">'
            '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
            'dur="1s" repeatCount="indefinite"/></rect>',
            "</svg>",
        ]
    )


if __name__ == "__main__":
    svg = emit()
    with open(OUT, "w") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes")
