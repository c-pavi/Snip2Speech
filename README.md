# Snip2Speech

A macOS tool that lets you select any screen region (works across multiple
monitors), extracts text using OCR, and reads it aloud using macOS's
built-in text-to-speech.

## Features

- 🖥️ **Multi-monitor support**: select regions from any connected monitor
- 📸 **Interactive selection**: uses macOS's native screen capture UI
- 🔍 **OCR powered by Tesseract**, with grayscale/contrast/upscale
  preprocessing for small or low-contrast screenshots
- 🔊 **Text-to-speech**: reads extracted text aloud using macOS `say`
- 📋 **Auto-copy**: copies extracted text to the clipboard
- 📊 **Table detection**: detects tabular data (tabs or aligned columns),
  parses it with pandas, and copies it as TSV instead of reading it word
  by word

## Requirements

- macOS (uses native `screencapture` and `say` commands)
- Python 3.8+
- Tesseract OCR

## Installation

1. **Install Tesseract OCR:**
   ```bash
   brew install tesseract
   ```

2. **Install Snip2Speech:**
   ```bash
   pip install -e .
   ```
   This gives you the `snip2speech` command. If you'd rather not install
   the package, `pip install -r requirements.txt` plus
   `python3 speak_selection_mac_mm.py` still works.

3. **Point at Tesseract, if needed**, with `--tesseract-cmd`:
   ```bash
   snip2speech --tesseract-cmd /opt/homebrew/bin/tesseract  # Apple Silicon
   snip2speech --tesseract-cmd /usr/local/bin/tesseract     # Intel
   ```

## Usage

```bash
snip2speech
```

1. Drag to select the region containing the text you want to read.
2. Press `Esc` to cancel.
3. The text is extracted via OCR, then:
   - **If it looks like a table** (tabs or aligned columns, 3+ rows,
     consistent column count): parsed into a pandas DataFrame, printed,
     copied as TSV, and a brief spoken summary ("Table with N rows and
     M columns").
   - **Otherwise**: printed, copied as plain text, and read aloud in full.

### Options

```
--lang LANG              Tesseract language (default: eng)
--rate RATE               Speech rate in WPM (default: 190)
--voice VOICE              macOS 'say' voice, e.g. Alex (default: Samantha)
--psm PSM                 Tesseract page segmentation mode (default: 6)
--oem OEM                 Tesseract OCR engine mode (default: 3)
--tesseract-cmd PATH      Explicit path to the tesseract binary
--no-preprocess           Skip grayscale/contrast/upscale preprocessing
--no-speak                Extract and copy text, but don't read it aloud
--no-clipboard            Don't copy the extracted text to the clipboard
```

Run `snip2speech --help` for the full list.

## Project layout

```
snip2speech/
├── snip2speech/
│   ├── capture.py      # wraps `screencapture`
│   ├── preprocess.py   # grayscale/contrast/upscale before OCR
│   ├── ocr.py           # wraps Tesseract
│   ├── table.py         # tabular-data detection
│   ├── output.py        # clipboard + speech
│   ├── config.py        # defaults, overridden by CLI flags
│   └── cli.py           # argparse + orchestration
├── tests/                # pytest, covers preprocess.py and table.py
├── benchmarks/           # measures preprocessing's effect on OCR accuracy
└── speak_selection_mac_mm.py  # deprecated entry point, kept for old hotkeys/workflows
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

See [benchmarks/README.md](benchmarks/README.md) to measure OCR accuracy
before/after preprocessing on your own screenshots.

## Troubleshooting

**"Tesseract not found" error:**
- Make sure Tesseract is installed: `brew install tesseract`
- If installed but not found, pass `--tesseract-cmd` (see above)

**"screencapture not found" error:**
- This should not happen on macOS. If it does, your system may be misconfigured.

## License

This project is open source and available for use and modification.
