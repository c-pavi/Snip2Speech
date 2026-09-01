"""Wraps macOS `screencapture` to let the user select an on-screen region."""

import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from typing import Iterator, Optional


@contextmanager
def capture_region() -> Iterator[Optional[str]]:
    """Yield the path to a temp PNG of the user's selection, or None if the
    selection was cancelled or `screencapture` is unavailable.

    The temp directory (and the PNG in it) is removed automatically when
    the `with` block exits, so do any reading of the file inside the block.
    """
    with tempfile.TemporaryDirectory(prefix="snip2speech_") as tmpdir:
        out_path = os.path.join(tmpdir, "capture.png")
        # -i: interactive (drag to select, spans all monitors)
        # -o: do not capture the cursor
        # -x: do not play sounds
        # -r: do not add screen-resolution metadata (no scaling surprises)
        cmd = ["screencapture", "-i", "-o", "-x", "-r", out_path]
        try:
            subprocess.run(cmd, check=False)
        except FileNotFoundError:
            print("Error: 'screencapture' not found (should exist on macOS).", file=sys.stderr)
            yield None
            return

        # screencapture exits 0 even when the user presses Esc; the only
        # reliable "cancelled" signal is that no file was written.
        yield out_path if os.path.exists(out_path) else None
