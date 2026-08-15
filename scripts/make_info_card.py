#!/usr/bin/env python3
"""
Neofetch-style info card. Lines fade + slide in once, then freeze.

    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
"""
from __future__ import annotations

import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import (
    ACCENT,
    BG,
    BG2,
    FRAME,
    INK,
    KEY,
    MUTED,
    PROMPT_HOST,
    TITLE_TEXT,
)

OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

# Display size 1:1 with the README <img width="490"> so glyphs stay crisp.
CANVAS_W = 490
CANVAS_H = 400
PAD = 22
TITLEBAR_H = 30
LINE_H = 22
BODY_X = PAD + 4
BODY_TOP = TITLEBAR_H + 28

ROWS = [
    ("title", "esquire@github", None),
    ("rule", "----------------------------", None),
    ("kv", "Name / Имя", "Dmitrij Nikitin"),
    ("kv", "Role / Роль", "Web & motion"),
    ("kv", "Now / Сейчас", "Premium landings · e-com · UI"),
    ("kv", "Stack", "TypeScript · Next.js · GSAP"),
    ("kv", "Highlights", "Motion.lab · 680+ UI patterns"),
    ("indent", None, "EasySite · Star Carpet · GIGANT"),
    ("indent", None, "In Her Light · Гостиная Бочуля"),
    ("kv", "Lang", "RU · EN"),
    ("kv", "GitHub", "github.com/Esquire0169"),
    ("blank", None, None),
    ("swatch", None, None),
]


def emit() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient></defs>",
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#ibg)"/>',
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
        f'text-anchor="middle">{PROMPT_HOST}: ~$ neofetch</text>'
    )

    y = BODY_TOP
    line_i = 0
    key_w = 132
    for kind, a, b in ROWS:
        delay = 0.18 + line_i * 0.11
        inner = []
        if kind == "title":
            inner.append(
                f'<text x="{BODY_X}" y="{y}" fill="{ACCENT}" font-size="16" font-weight="700">'
                f"{html.escape(a)}</text>"
            )
        elif kind == "rule":
            inner.append(
                f'<text x="{BODY_X}" y="{y}" fill="{FRAME}" font-size="13">{a}</text>'
            )
        elif kind == "kv":
            inner.append(
                f'<text x="{BODY_X}" y="{y}" fill="{KEY}" font-size="13">{html.escape(a)}</text>'
            )
            inner.append(
                f'<text x="{BODY_X + key_w}" y="{y}" fill="{INK}" font-size="13">'
                f"{html.escape(b)}</text>"
            )
        elif kind == "indent":
            inner.append(
                f'<text x="{BODY_X + key_w}" y="{y}" fill="{INK}" font-size="13">'
                f"{html.escape(b)}</text>"
            )
        elif kind == "swatch":
            colors = ["#ff5f56", "#ffbd2e", "#27c93f", KEY, ACCENT, "#a371f7", INK]
            x = BODY_X
            for c in colors:
                inner.append(
                    f'<rect x="{x}" y="{y - 12}" width="18" height="14" rx="2" fill="{c}"/>'
                )
                x += 22
        elif kind == "blank":
            y += LINE_H * 0.45
            continue

        body = "".join(inner)
        if STATIC:
            parts.append(f"<g>{body}</g>")
        else:
            parts.append(
                f'<g opacity="1">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.32s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-10 0" to="0 0" begin="{delay:.2f}s" dur="0.32s" fill="freeze"/>'
                f"{body}</g>"
            )
        y += LINE_H
        line_i += 1

    # status
    status_y = CANVAS_H - 18
    parts.append(
        f'<line x1="0" y1="{CANVAS_H - 30}" x2="{CANVAS_W}" y2="{CANVAS_H - 30}" stroke="{FRAME}"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{status_y}" fill="{MUTED}" font-size="11">'
        f'{PROMPT_HOST}:~$ echo $STATUS  <tspan fill="{ACCENT}">shipping</tspan></text>'
    )
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = emit()
    with open(OUT, "w") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
