#!/usr/bin/env python3
"""
macOS multi-monitor screen read-aloud:
1) Uses macOS 'screencapture -i' to let you select any on-screen region (any monitor)
2) OCRs it with Tesseract
3) Speaks it with macOS 'say'
Requires: brew install tesseract; pip install pillow pytesseract
"""

import os
import subprocess
import sys
import tempfile
from PIL import Image
import pytesseract

# ---- CONFIG ----
TESS_LANG = "eng"       # Install extra languages via Homebrew if needed
SAY_RATE_WPM = 190      # 150–220 is a natural range
# If pytesseract can't find tesseract, uncomment the correct path:
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"   # Apple Silicon
# pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"      # Intel
# ----------------

def speak(text: str, rate=SAY_RATE_WPM, voice=None):
    if not text.strip():
        subprocess.run(["say", "No readable text found."])
        return
    cmd = ["say", "-r", str(rate)]
    if voice:
        cmd += ["-v", voice]
    cmd.append(text)
    subprocess.run(cmd)

from typing import Optional
def select_region_to_tempfile() -> Optional[str]:
    """
    Opens macOS's native selection UI (spans all monitors).
    Returns the path to a temporary PNG containing the selected region,
    or None if cancelled.
    """
    tmpdir = tempfile.mkdtemp(prefix="speak_sel_")
    out_path = os.path.join(tmpdir, "capture.png")

    # -i: interactive (drag to select)
    # -o: do not capture the cursor
    # -x: do not play sounds
    # -r: force screen resolution (no scaling)
    # NOTE: screencapture returns nonzero on cancel
    cmd = ["screencapture", "-i", "-o", "-x", "-r", out_path]
    try:
        res = subprocess.run(cmd)
        if res.returncode != 0 or not os.path.exists(out_path):
            return None
        return out_path
    except FileNotFoundError:
        print("Error: 'screencapture' not found (should exist on macOS).", file=sys.stderr)
        return None

def ocr_image(path: str) -> str:
    # You can tune OCR with psm/oem if needed; 6 is good for uniform text blocks
    # config = r'--oem 3 --psm 6'
    # return pytesseract.image_to_string(Image.open(path), lang=TESS_LANG, config=config)
    return pytesseract.image_to_string(Image.open(path), lang=TESS_LANG)

def copy_to_clipboard(text: str):
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
    except Exception:
        pass

def main():
    print("Select a region (drag) on ANY monitor. Press Esc to cancel.")
    png_path = select_region_to_tempfile()
    if not png_path:
        print("Selection cancelled.")
        return

    try:
        text = ocr_image(png_path)
    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found. Install with: brew install tesseract", file=sys.stderr)
        speak("Tesseract not found. Please install Tesseract.")
        return

    text = text.strip()
    print("\n--- OCR TEXT ---\n", text, "\n----------------")
    copy_to_clipboard(text)
    speak(text, rate=SAY_RATE_WPM, voice="Samantha")

if __name__ == "__main__":
    main()
