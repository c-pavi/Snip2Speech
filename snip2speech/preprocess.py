"""Image preprocessing to improve Tesseract OCR accuracy on screenshots.

Tesseract's accuracy drops noticeably on small selections and low-contrast
UI text. This upscales small captures, converts to grayscale, and boosts
contrast before OCR. See benchmarks/ for a measured before/after comparison.
"""

from PIL import Image, ImageEnhance, ImageOps

MIN_WIDTH_PX = 1000
CONTRAST_FACTOR = 1.5


def preprocess_for_ocr(img: Image.Image) -> Image.Image:
    """Return a copy of `img` prepared for OCR. Does not mutate `img`."""
    if img.width < MIN_WIDTH_PX:
        scale = MIN_WIDTH_PX / img.width
        new_size = (round(img.width * scale), round(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)

    img = ImageOps.grayscale(img)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST_FACTOR)
    img = ImageOps.autocontrast(img)
    return img
