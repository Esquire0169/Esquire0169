#!/usr/bin/env python3
"""Wide neofetch card (860px) — premium whoami, no portrait."""
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

CANVAS_W = 860
CANVAS_H = 280
PAD = 28
TITLEBAR_H = 30
COL2_X = 430
LINE_H = 24
BODY_TOP = TITLEBAR_H + 36


def line_group(inner: str, delay: float) -> str:
    if STATIC:
        return f"<g>{inner}</g>"
    return (
        f'<g opacity="1">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
        f'dur="0.28s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="-8 0" to="0 0" begin="{delay:.2f}s" dur="0.28s" fill="freeze"/>'
        f"{inner}</g>"
    )


def render_col(rows, x, start_delay):
    parts = []
    y = BODY_TOP
    key_w = 78
    for i, row in enumerate(rows):
        kind, a = row[0], row[1]
        b = row[2] if len(row) > 2 else None
        delay = start_delay + i * 0.08
        if kind == "title":
            inner = (
                f'<text x="{x}" y="{y}" fill="{ACCENT}" font-size="18" font-weight="700">'
                f"{html.escape(a)}</text>"
            )
        elif kind == "rule":
            inner = f'<text x="{x}" y="{y}" fill="{FRAME}" font-size="13">{a}</text>'
        elif kind == "kv":
            inner = (
                f'<text x="{x}" y="{y}" fill="{KEY}" font-size="13">{html.escape(a)}</text>'
                f'<text x="{x + key_w}" y="{y}" fill="{INK}" font-size="13">'
                f"{html.escape(b)}</text>"
            )
        else:
            inner = (
                f'<text x="{x + key_w}" y="{y}" fill="{INK}" font-size="13">'
                f"{html.escape(a)}</text>"
            )
        parts.append(line_group(inner, delay))
        y += LINE_H
    return parts


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
        f'text-anchor="middle">{PROMPT_HOST}: ~$ whoami</text>'
    )

    left_kv = [
        ("title", "esquire@github"),
        ("rule", "─────────────────────────"),
        ("kv", "Name", "Dmitrij Nikitin"),
        ("kv", "Role", "Web & motion"),
        ("kv", "Now", "Premium landings · e-com · UI"),
        ("kv", "Lang", "RU · EN"),
    ]
    right_kv = [
        ("kv", "Stack", "TypeScript · Next.js · GSAP"),
        ("kv", "Focus", "Design systems that ship"),
        ("kv", "Work", "Motion.lab · 680+ UI patterns"),
        ("plain", "EasySite · Star Carpet · GIGANT"),
        ("plain", "In Her Light · Гостиная Бочуля"),
        ("kv", "Status", "shipping"),
    ]
    parts.extend(render_col(left_kv, PAD, 0.12))
    parts.extend(render_col(right_kv, COL2_X, 0.18))

    parts.append(
        f'<line x1="0" y1="{CANVAS_H - 28}" x2="{CANVAS_W}" y2="{CANVAS_H - 28}" stroke="{FRAME}"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{CANVAS_H - 11}" fill="{MUTED}" font-size="11">'
        f'{PROMPT_HOST}:~$ echo $STATUS  <tspan fill="{ACCENT}">available for work</tspan></text>'
    )
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = emit()
    with open(OUT, "w") as f:
        f.write(svg)
    print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
