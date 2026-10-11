"""Turn raw OCR text into text that `say` reads with natural pauses.

`say` only pauses at punctuation. OCR output of bullet lists, headings and
UI labels has line breaks but no punctuation, so it gets read as one long
run-on sentence -- and Tesseract usually renders bullet glyphs as a stray
"e" or "o", which `say` then speaks aloud.

This module (1) strips bullet markers, (2) rejoins lines that were only
wrapped by the screen width, and (3) ends every other line with a period so
`say` pauses there. It is applied to the spoken text only; the clipboard
keeps the raw OCR output.
"""

import re
from typing import List

# Real bullet glyphs, plus the characters Tesseract commonly produces for them.
_GLYPH_BULLET = re.compile(r"^\s*[•●○▪▫◦‣⁃·*«©®]+\s*")
_DASH_BULLET = re.compile(r"^\s*[-–—]\s+")
# A lone "e"/"o" misread from a bullet. Only when followed by a capital letter,
# so ordinary words are left alone.
_LETTER_BULLET = re.compile(r"^\s*[eo]\s+(?=[A-Z0-9])")

_TERMINAL = (".", "!", "?", ":", ";")


def _strip_bullet(line: str):
    """Return (text, was_bullet)."""
    for pattern in (_GLYPH_BULLET, _DASH_BULLET, _LETTER_BULLET):
        stripped = pattern.sub("", line, count=1)
        if stripped != line:
            return stripped.strip(), True
    return line.strip(), False


def _end_with_pause(text: str) -> str:
    if text.endswith(_TERMINAL) or text.endswith(","):
        return text
    return text + "."


def prepare_for_speech(text: str) -> str:
    """Return `text` with bullets removed and a pause added at each hard line break."""
    paragraphs: List[str] = []

    for block in re.split(r"\n\s*\n", text.strip()):
        parsed = []
        for raw in block.splitlines():
            if not raw.strip():
                continue
            line, is_bullet = _strip_bullet(raw)
            if line:
                parsed.append((line, is_bullet))
        if not parsed:
            continue

        pieces: List[str] = []
        current, _ = parsed[0]
        for (nxt, nxt_is_bullet) in parsed[1:]:
            soft_wrap = (
                not nxt_is_bullet
                and not current.endswith(_TERMINAL)
                and (nxt[0].islower() or current.endswith(","))
            )
            if soft_wrap:
                # Line was only wrapped by the screen width: keep it one sentence.
                joiner = "" if current.endswith("-") else " "
                current = current + joiner + nxt
            else:
                pieces.append(_end_with_pause(current))
                current = nxt
        pieces.append(_end_with_pause(current))
        paragraphs.append(" ".join(pieces))

    # A blank line between paragraphs gives say a slightly longer pause.
    return "\n\n".join(paragraphs)
