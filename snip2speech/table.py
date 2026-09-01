"""Heuristic detection of tabular data in OCR output."""

import io
import re
from collections import Counter
from typing import List, Optional, Tuple

import pandas as pd

MIN_TABLE_ROWS = 3
MIN_CONSISTENT_FRACTION = 0.8
_SEPARATORS = ("\t", r"\s{2,}")


def _column_consistency(lines: List[str], pattern: "re.Pattern[str]") -> Tuple[int, float]:
    """Return (most common field count, fraction of lines with that count)."""
    counts = [len(pattern.split(ln)) for ln in lines]
    if not counts:
        return 0, 0.0
    common_count, occurrences = Counter(counts).most_common(1)[0]
    return common_count, occurrences / len(counts)


def try_parse_as_table(text: str) -> Optional[pd.DataFrame]:
    """Return a DataFrame if `text` looks like a table, else None.

    Requires at least MIN_TABLE_ROWS non-blank lines where most of them
    (>= MIN_CONSISTENT_FRACTION) split into the same number of 2+ fields
    on either tabs or runs of 2+ spaces. Ordinary prose that happens to
    contain a stray double space won't have that column-count consistency,
    so it's correctly left undetected.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < MIN_TABLE_ROWS:
        return None

    for sep in _SEPARATORS:
        pattern = re.compile(sep)
        n_cols, consistency = _column_consistency(lines, pattern)
        if n_cols < 2 or consistency < MIN_CONSISTENT_FRACTION:
            continue
        try:
            df = pd.read_csv(
                io.StringIO("\n".join(lines)),
                sep=sep,
                engine="python",
                header=None,
                on_bad_lines="skip",
            )
        except Exception:
            continue
        if df.shape[1] == n_cols and df.shape[0] >= 1:
            return df

    return None
