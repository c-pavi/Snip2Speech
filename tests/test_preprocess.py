from PIL import Image

from snip2speech.preprocess import MIN_WIDTH_PX, preprocess_for_ocr


def _solid_image(width: int, height: int, color) -> Image.Image:
    return Image.new("RGB", (width, height), color)


def test_small_image_is_upscaled():
    img = _solid_image(200, 100, (255, 0, 0))
    out = preprocess_for_ocr(img)
    assert out.width >= MIN_WIDTH_PX
    expected_height = round(out.width * 100 / 200)
    assert abs(out.height - expected_height) <= 1


def test_large_image_is_not_downscaled():
    img = _solid_image(1600, 800, (0, 255, 0))
    out = preprocess_for_ocr(img)
    assert out.width == 1600
    assert out.height == 800


def test_output_is_grayscale():
    img = _solid_image(1200, 600, (10, 200, 30))
    out = preprocess_for_ocr(img)
    assert out.mode == "L"


def test_does_not_mutate_input():
    img = _solid_image(200, 100, (255, 0, 0))
    original_mode = img.mode
    original_size = img.size
    preprocess_for_ocr(img)
    assert img.mode == original_mode
    assert img.size == original_size
