# OCR accuracy benchmark

Measures whether `preprocess_for_ocr` (grayscale + contrast + upscaling)
actually improves OCR accuracy, using word error rate (WER) via `jiwer`.

## Setup

1. Install the dev extras: `pip install -e ".[dev]"`
2. Add 5-10 screenshots to `benchmarks/data/images/` — a mix of clear
   text, small text, and low-contrast text is the most informative set.
3. Hand-transcribe each one exactly and add it to
   `benchmarks/data/ground_truth.json`:

   ```json
   {
     "clear_text.png": "The exact text that appears in that screenshot.",
     "small_text.png": "..."
   }
   ```

   Keys must match filenames in `benchmarks/data/images/`.

## Run

```bash
python3 benchmarks/run_benchmark.py
```

Prints per-image WER with and without preprocessing, plus the average
and relative improvement across all labeled images. That average is
the number to cite (e.g. "reduced OCR word error rate by N% across
K test screenshots") — only after you've actually run it.
