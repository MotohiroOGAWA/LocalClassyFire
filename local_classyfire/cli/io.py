from __future__ import annotations

from pathlib import Path


def read_line_separated_values(path: str | Path) -> list[str]:
    """Read newline-separated identifiers from a text file.

    Empty lines and comment lines starting with '#' are ignored.
    """

    input_path = Path(path)

    values: list[str] = []

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            value = line.strip()

            if not value:
                continue

            if value.startswith("#"):
                continue

            values.append(value)

    return values


def collect_input_values(
    *,
    value: str | None,
    input_path: str | Path | None,
) -> list[str]:
    """Collect identifiers from a single terminal value or a file."""

    if value is not None and input_path is not None:
        raise ValueError("Specify either VALUE or --input, not both.")

    if value is None and input_path is None:
        raise ValueError("Specify VALUE or --input.")

    if value is not None:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("VALUE is empty.")

        return [normalized_value]

    if input_path is None:
        raise ValueError("input_path is required.")

    values = read_line_separated_values(input_path)

    if not values:
        raise ValueError(f"No input values found in file: {input_path}")

    return values