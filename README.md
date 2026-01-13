# Snip2Speech

A macOS tool that lets you select any screen region (works across multiple monitors), extracts text using OCR, and reads it aloud using macOS's built-in text-to-speech.

## Features

- 🖥️ **Multi-monitor support**: Select regions from any connected monitor
- 📸 **Interactive selection**: Uses macOS's native screen capture UI
- 🔍 **OCR powered by Tesseract**: Extracts text from images
- 🔊 **Text-to-speech**: Reads extracted text aloud using macOS `say` command
- 📋 **Auto-copy**: Automatically copies extracted text to clipboard

## Requirements

- macOS (uses native `screencapture` and `say` commands)
- Python 3.6+
- Tesseract OCR
- Python dependencies (see Installation)

## Installation

1. **Install Tesseract OCR:**
   ```bash
   brew install tesseract
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or manually:
   ```bash
   pip install pillow pytesseract
   ```

3. **Configure Tesseract path (if needed):**
   
   If you encounter issues finding Tesseract, uncomment the appropriate line in `speak_selection_mac_mm.py`:
   - For Apple Silicon Macs: `/opt/homebrew/bin/tesseract`
   - For Intel Macs: `/usr/local/bin/tesseract`

## Usage

Run the script:
```bash
python3 speak_selection_mac_mm.py
```

1. The script will prompt you to select a region on your screen
2. Drag to select the area containing text you want to read
3. Press `Esc` to cancel
4. The text will be:
   - Extracted via OCR
   - Displayed in the terminal
   - Copied to your clipboard
   - Read aloud using macOS text-to-speech

## Configuration

You can customize the following in `speak_selection_mac_mm.py`:

- `TESS_LANG`: OCR language (default: `"eng"`). Install additional languages via Homebrew if needed
- `SAY_RATE_WPM`: Speech rate in words per minute (default: `190`, natural range: 150-220)
- Voice: Currently set to `"Samantha"`. Change in the `main()` function or pass `None` to use system default

## Troubleshooting

**"Tesseract not found" error:**
- Make sure Tesseract is installed: `brew install tesseract`
- If installed but not found, uncomment the appropriate `pytesseract.tesseract_cmd` line in the script

**"screencapture not found" error:**
- This should not happen on macOS. If it does, your system may be misconfigured

## License

This project is open source and available for use and modification.
