"""Default configuration values, overridable via CLI flags (see cli.py)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    lang: str = "eng"                     # Tesseract language; install more via Homebrew
    rate: int = 190                       # 'say' rate in words/minute; 150-220 is natural
    voice: Optional[str] = "Samantha"     # 'say' voice; None uses the system default
    psm: int = 6                          # Tesseract page segmentation mode (6 = uniform block)
    oem: int = 3                          # Tesseract OCR engine mode (3 = default LSTM+legacy)
    tesseract_cmd: Optional[str] = None   # override if pytesseract can't find the binary
    preprocess: bool = True               # grayscale/contrast/upscale before OCR
    speak_output: bool = True             # read the result aloud
    copy_clipboard: bool = True           # copy the result to the clipboard
    speech_cleanup: bool = True           # strip bullets / add pauses before speaking
