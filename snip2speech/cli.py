"""Command-line entry point: capture -> OCR -> (table detection) -> output."""

import argparse
import sys
from typing import Optional, Sequence

import pytesseract

from .capture import capture_region
from .config import Config
from .ocr import ocr_image
from .output import copy_to_clipboard, speak
from .table import try_parse_as_table


def build_parser() -> argparse.ArgumentParser:
    defaults = Config()
    parser = argparse.ArgumentParser(
        prog="snip2speech",
        description="Select a screen region on macOS, OCR it, and read it aloud.",
    )
    parser.add_argument("--lang", default=defaults.lang, help="Tesseract language (default: %(default)s)")
    parser.add_argument("--rate", type=int, default=defaults.rate, help="Speech rate in WPM (default: %(default)s)")
    parser.add_argument("--voice", default=defaults.voice, help="macOS 'say' voice, e.g. Alex (default: %(default)s)")
    parser.add_argument("--psm", type=int, default=defaults.psm, help="Tesseract page segmentation mode (default: %(default)s)")
    parser.add_argument("--oem", type=int, default=defaults.oem, help="Tesseract OCR engine mode (default: %(default)s)")
    parser.add_argument("--tesseract-cmd", default=None, help="Explicit path to the tesseract binary")
    parser.add_argument("--no-preprocess", action="store_true", help="Skip grayscale/contrast/upscale preprocessing")
    parser.add_argument("--no-speak", action="store_true", help="Extract and copy text, but don't read it aloud")
    parser.add_argument("--no-clipboard", action="store_true", help="Don't copy the extracted text to the clipboard")
    return parser


def _config_from_args(args: argparse.Namespace) -> Config:
    return Config(
        lang=args.lang,
        rate=args.rate,
        voice=args.voice,
        psm=args.psm,
        oem=args.oem,
        tesseract_cmd=args.tesseract_cmd,
        preprocess=not args.no_preprocess,
        speak_output=not args.no_speak,
        copy_clipboard=not args.no_clipboard,
    )


def _run(config: Config) -> int:
    print("Select a region (drag) on ANY monitor. Press Esc to cancel.")
    with capture_region() as png_path:
        if not png_path:
            print("Selection cancelled.")
            return 0

        try:
            text = ocr_image(png_path, config).strip()
        except pytesseract.TesseractNotFoundError:
            print("Tesseract not found. Install with: brew install tesseract", file=sys.stderr)
            if config.speak_output:
                speak("Tesseract not found. Please install Tesseract.", config.rate)
            return 1
        except Exception as exc:  # OCR can fail in ways pytesseract doesn't type
            print(f"OCR failed: {exc}", file=sys.stderr)
            return 1

    df = try_parse_as_table(text)

    if df is not None:
        print("\n--- PARSED TABLE ---\n")
        print(df.to_string())
        print("\n-------------------")
        if config.copy_clipboard:
            copy_to_clipboard(df.to_csv(index=False, sep="\t"))
        if config.speak_output:
            speak(f"Table with {len(df)} rows and {len(df.columns)} columns.", config.rate, config.voice)
    else:
        print("\n--- OCR TEXT ---\n", text, "\n----------------")
        if config.copy_clipboard:
            copy_to_clipboard(text)
        if config.speak_output:
            speak(text, config.rate, config.voice)

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    config = _config_from_args(args)
    try:
        return _run(config)
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
