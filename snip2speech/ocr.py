"""Wraps pytesseract for OCR, with optional preprocessing."""

import pytesseract
from PIL import Image

from .config import Config
from .preprocess import preprocess_for_ocr


def ocr_image(path: str, config: Config) -> str:
    if config.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd

    with Image.open(path) as img:
        if config.preprocess:
            img = preprocess_for_ocr(img)
        tess_config = f"--oem {config.oem} --psm {config.psm}"
        return pytesseract.image_to_string(img, lang=config.lang, config=tess_config)
