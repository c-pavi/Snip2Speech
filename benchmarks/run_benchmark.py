#!/usr/bin/env python3
"""Compares OCR word error rate with and without preprocessing.

Needs benchmarks/data/images/*.png and a matching
benchmarks/data/ground_truth.json — see benchmarks/README.md.
"""

import json
import sys
from pathlib import Path

import pytesseract
from jiwer import wer
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from snip2speech.preprocess import preprocess_for_ocr  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = DATA_DIR / "images"
GROUND_TRUTH_PATH = DATA_DIR / "ground_truth.json"


def run() -> int:
    if not GROUND_TRUTH_PATH.exists():
        print(f"Missing {GROUND_TRUTH_PATH} -- see benchmarks/README.md", file=sys.stderr)
        return 1

    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text())
    if not ground_truth:
        print("ground_truth.json is empty -- add labeled screenshots first (see benchmarks/README.md).", file=sys.stderr)
        return 1

    raw_scores = []
    preprocessed_scores = []

    for filename, truth in ground_truth.items():
        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            print(f"Skipping {filename}: not found in {IMAGES_DIR}", file=sys.stderr)
            continue

        with Image.open(image_path) as img:
            raw_text = pytesseract.image_to_string(img)
            preprocessed_text = pytesseract.image_to_string(preprocess_for_ocr(img))

        raw_score = wer(truth, raw_text)
        preprocessed_score = wer(truth, preprocessed_text)
        raw_scores.append(raw_score)
        preprocessed_scores.append(preprocessed_score)

        print(f"{filename}: raw WER={raw_score:.2%}  preprocessed WER={preprocessed_score:.2%}")

    if not raw_scores:
        print("No images matched ground_truth.json entries.", file=sys.stderr)
        return 1

    avg_raw = sum(raw_scores) / len(raw_scores)
    avg_pre = sum(preprocessed_scores) / len(preprocessed_scores)
    print(f"\nAverage raw WER:          {avg_raw:.2%}")
    print(f"Average preprocessed WER: {avg_pre:.2%}")
    if avg_raw > 0:
        print(f"Relative improvement:    {(avg_raw - avg_pre) / avg_raw:.1%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
