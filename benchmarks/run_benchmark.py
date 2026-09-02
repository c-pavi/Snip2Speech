#!/usr/bin/env python3
"""Compare OCR word error rate with and without preprocessing.

For each entry in benchmarks/data/ground_truth.json, run Tesseract on the
matching image twice -- once on the raw image, once through
snip2speech.preprocess.preprocess_for_ocr -- and score both against the
ground truth with jiwer.

Methodology:
- OCR uses the same Tesseract config the app uses (--oem 3 --psm 6, lang
  eng); see snip2speech/ocr.py.
- Before scoring, reference and hypothesis are lightly normalized:
  lowercased, runs of whitespace collapsed, surrounding whitespace
  stripped. Punctuation is kept and counts as a real error.
- Two aggregates are reported: a macro average (mean of per-image WER)
  and a micro / corpus average (total word edits / total reference
  words). The micro average is the more representative single number
  because it weights images by length.
"""

import json
import sys
from pathlib import Path

import jiwer
import pytesseract
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from snip2speech.config import Config  # noqa: E402
from snip2speech.preprocess import preprocess_for_ocr  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = DATA_DIR / "images"
GROUND_TRUTH_PATH = DATA_DIR / "ground_truth.json"

_CFG = Config()
_TESS_CONFIG = f"--oem {_CFG.oem} --psm {_CFG.psm}"
_TESS_LANG = _CFG.lang

_NORMALIZE = jiwer.Compose(
    [
        jiwer.ToLowerCase(),
        jiwer.SubstituteRegexes({r"\s+": " "}),  # collapse newlines/tabs/runs to one space
        jiwer.Strip(),
        jiwer.ReduceToListOfListOfWords(),
    ]
)


def _ocr(img: Image.Image) -> str:
    return pytesseract.image_to_string(img, lang=_TESS_LANG, config=_TESS_CONFIG)


def _score(reference: str, hypothesis: str) -> jiwer.WordOutput:
    return jiwer.process_words(
        reference,
        hypothesis,
        reference_transform=_NORMALIZE,
        hypothesis_transform=_NORMALIZE,
    )


def _edits(out: jiwer.WordOutput) -> int:
    return out.substitutions + out.deletions + out.insertions


def _ref_words(out: jiwer.WordOutput) -> int:
    return out.hits + out.substitutions + out.deletions


def run() -> int:
    if not GROUND_TRUTH_PATH.exists():
        print(f"Missing {GROUND_TRUTH_PATH} -- see benchmarks/README.md", file=sys.stderr)
        return 1

    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text())
    if not ground_truth:
        print(
            "ground_truth.json is empty -- add labeled screenshots first (see benchmarks/README.md).",
            file=sys.stderr,
        )
        return 1

    rows = []
    raw_edits = raw_ref = pre_edits = pre_ref = 0

    for filename, truth in sorted(ground_truth.items()):
        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            print(f"Skipping {filename}: not found in {IMAGES_DIR}", file=sys.stderr)
            continue

        with Image.open(image_path) as img:
            raw_out = _score(truth, _ocr(img))
            pre_out = _score(truth, _ocr(preprocess_for_ocr(img)))

        rows.append((filename, _ref_words(raw_out), raw_out.wer, pre_out.wer))
        raw_edits += _edits(raw_out)
        raw_ref += _ref_words(raw_out)
        pre_edits += _edits(pre_out)
        pre_ref += _ref_words(pre_out)

    if not rows:
        print("No images matched ground_truth.json entries.", file=sys.stderr)
        return 1

    name_w = max(len(r[0]) for r in rows)
    print(f"{'image'.ljust(name_w)}  {'words':>5}  {'raw WER':>9}  {'pre WER':>9}  {'delta':>8}")
    for filename, ref_words, raw_wer, pre_wer in rows:
        print(
            f"{filename.ljust(name_w)}  {ref_words:>5}  {raw_wer:>9.2%}  {pre_wer:>9.2%}  {pre_wer - raw_wer:>+8.2%}"
        )

    macro_raw = sum(r[2] for r in rows) / len(rows)
    macro_pre = sum(r[3] for r in rows) / len(rows)
    micro_raw = raw_edits / raw_ref if raw_ref else 0.0
    micro_pre = pre_edits / pre_ref if pre_ref else 0.0

    print()
    print(f"Images:                     {len(rows)}")
    print(f"Macro-average raw WER:      {macro_raw:.2%}")
    print(f"Macro-average preproc WER:  {macro_pre:.2%}")
    if macro_raw > 0:
        print(f"  relative improvement:     {(macro_raw - macro_pre) / macro_raw:.1%}")
    print(f"Micro-average raw WER:      {micro_raw:.2%}")
    print(f"Micro-average preproc WER:  {micro_pre:.2%}")
    if micro_raw > 0:
        print(f"  relative improvement:     {(micro_raw - micro_pre) / micro_raw:.1%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
