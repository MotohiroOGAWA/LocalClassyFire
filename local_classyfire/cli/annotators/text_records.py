from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentifierHit:
    """Identifier found in a metadata line."""

    line_index: int
    identifier_type: str
    identifier_value: str


def parse_metadata_line(line: str) -> tuple[str, str] | None:
    """Parse 'KEY: value' or 'KEY=value' metadata line."""

    stripped = line.strip()

    if not stripped:
        return None

    colon_index = stripped.find(":")
    equal_index = stripped.find("=")

    indices = [
        index
        for index in [colon_index, equal_index]
        if index >= 0
    ]

    if not indices:
        return None

    separator_index = min(indices)

    key = stripped[:separator_index].strip()
    value = stripped[separator_index + 1:].strip()

    if not key:
        return None

    return key, value


def find_identifier_in_line(
    line: str,
    *,
    identifier: str,
    identifier_column: str | None = None,
) -> tuple[str, str] | None:
    """Find the selected column without changing identifier value case.

    Omitted column names default to SMILES or InChIKey for the requested type.
    There is no fallback to the other identifier type.
    """

    parsed = parse_metadata_line(line)

    if parsed is None:
        return None

    key, value = parsed

    if not value:
        return None

    if identifier not in {"smiles", "inchikey"}:
        raise ValueError("identifier must be either 'smiles' or 'inchikey'.")
    column = identifier_column if identifier_column is not None else (
        "SMILES" if identifier == "smiles" else "InChIKey"
    )
    if normalize_metadata_key(key) == normalize_metadata_key(column):
        return identifier, value

    return None


def normalize_metadata_key(key: str) -> str:
    """Normalize metadata key for robust matching."""

    return (
        key.strip()
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )