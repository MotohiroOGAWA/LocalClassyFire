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
) -> tuple[str, str] | None:
    """Find the requested identifier in one metadata line.

    This function does not fall back to another identifier type.
    If identifier='inchikey', only InChIKey lines are accepted.
    If identifier='smiles', only SMILES lines are accepted.
    """

    parsed = parse_metadata_line(line)

    if parsed is None:
        return None

    key, value = parsed

    if not value:
        return None

    normalized_key = normalize_metadata_key(key)

    if identifier == "inchikey" and normalized_key == "inchikey":
        return "inchikey", value

    if identifier == "smiles" and normalized_key == "smiles":
        return "smiles", value

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