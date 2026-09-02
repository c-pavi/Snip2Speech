# OCR accuracy benchmark

Measures whether `snip2speech.preprocess.preprocess_for_ocr` (upscale +
grayscale + contrast) actually improves OCR accuracy, using word error
rate (WER) via `jiwer`.

## Result

On the current 7-image test set, the preprocessing pass cut word error
rate from **7.2% to 1.1%** (micro-average, i.e. total word edits over
total reference words). It helped 5 of 7 images, was neutral on 2, and
hurt none.

```
image                       words    raw WER    pre WER     delta
clear_dialog.png               41      0.00%      0.00%    +0.00%
clear_paragraph.png            49      2.04%      0.00%    -2.04%
dense_or_dark.png             103      8.74%      3.88%    -4.85%
low_contrast_secondary.png     81      4.94%      0.00%    -4.94%
small_code.png                 27      3.70%      3.70%    +0.00%
small_footnote.png             82      7.32%      0.00%    -7.32%
small_ui_labels.png            76     15.79%      0.00%   -15.79%

Macro-average raw WER:  6.08%  ->  1.08%
Micro-average raw WER:  7.19%  ->  1.09%
```

### Caveats

- **n = 7.** Small sample; treat the number as indicative, not precise.
- **Every capture here is under 1000px wide**, so the upscale branch of
  `preprocess_for_ocr` fires on all of them — that is the main driver of
  the improvement. On a Retina display, `screencapture` produces 2x
  images and a normal selection often exceeds 1000px, so upscaling would
  not fire and the gain would be smaller. This number reflects
  standard-DPI displays and/or small selections.
- **4 of 7 images are HTML fixtures** rendered in a browser and
  screenshotted (`benchmarks/fixtures/`), which gives exact ground
  truth. The other 3 (`clear_paragraph`, `small_code`, `small_footnote`)
  are real application screenshots.
- `small_code.png` is unchanged because its only error (`0` read as
  `@`) survives preprocessing; grayscale does not help syntax-highlighted
  text much.

## Methodology

- OCR runs with the same Tesseract config the app uses: `--oem 3
  --psm 6`, language `eng` (see `snip2speech/ocr.py`). The benchmark
  imports these from `snip2speech.config.Config` so they stay in sync.
- Before scoring, reference and hypothesis are normalized: lowercased,
  all whitespace runs (including newlines) collapsed to single spaces,
  surrounding whitespace stripped. Punctuation is kept and counts as a
  real error.
- Two aggregates are reported. The **macro-average** is the mean of the
  per-image WER. The **micro-average** is total word edits divided by
  total reference words across all images, which weights images by
  length and is the more representative single number.

## Reproducing / extending the test set

The HTML fixtures live in `benchmarks/fixtures/`. To regenerate those
screenshots: open each file in a browser at 100% zoom, capture the area
inside the dashed guide (excluding the guide and the caption above it),
and save it into `benchmarks/data/images/` under the filename shown in
the caption.

To add real screenshots: capture tight selections of text (no icons or
images), save the PNGs into `benchmarks/data/images/`, and add a
`"filename.png": "exact transcription"` entry to
`benchmarks/data/ground_truth.json`. Keys must match filenames; the
transcription must match the image character-for-character (case and
whitespace are normalized away, punctuation is not).

## Run

```bash
pip install -e ".[dev]"      # jiwer + pytest
python3 benchmarks/run_benchmark.py
```
