#!/usr/bin/env python3
"""Deprecated entry point, kept only for backward compatibility.

If you have a global hotkey, Automator Quick Action, or Alfred/Raycast
workflow that calls this file directly, it still works. New setups should
use the `snip2speech` command (installed via `pip install -e .`) or
`python3 -m snip2speech` — see README.md.
"""

import sys

from snip2speech.cli import main

if __name__ == "__main__":
    sys.exit(main())
