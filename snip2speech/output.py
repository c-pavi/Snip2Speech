"""Clipboard and speech output."""

import subprocess
import sys
from typing import Optional


def copy_to_clipboard(text: str) -> None:
    try:
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        print(f"Warning: could not copy to clipboard ({exc}).", file=sys.stderr)


def speak(text: str, rate: int, voice: Optional[str] = None) -> None:
    if not text.strip():
        text = "No readable text found."
    cmd = ["say", "-r", str(rate)]
    if voice:
        cmd += ["-v", voice]
    # Pass text via stdin rather than argv: OCR output that happens to start
    # with '-' would otherwise be parsed as a 'say' flag, and very long
    # captures can exceed the OS argv length limit.
    try:
        subprocess.run(cmd, input=text, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        print(f"Warning: 'say' failed ({exc}).", file=sys.stderr)
