from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def write_dataframe(
    dataframe: pd.DataFrame,
    *,
    output_path: str | Path | None = None,
    output_format: str = "tsv",
) -> None:
    """Write DataFrame to stdout or file.

    If output_path is None, the result is printed to stdout.
    Otherwise, the result is saved to the specified file.
    """

    separator = _get_separator(output_format)

    if output_path is None:
        dataframe.to_csv(
            sys.stdout,
            sep=separator,
            index=False,
            lineterminator="\n",
        )
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        path,
        sep=separator,
        index=False,
        lineterminator="\n",
        encoding="utf-8",
    )


def _get_separator(output_format: str) -> str:
    if output_format == "tsv":
        return "\t"

    if output_format == "csv":
        return ","

    raise ValueError(f"Unsupported output format: {output_format}")