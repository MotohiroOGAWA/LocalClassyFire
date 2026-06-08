from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


CLASSIFICATION_FIELDS = [
    "Kingdom",
    "Superclass",
    "Class",
    "Subclass",
    "DirectParent",
]


@dataclass(frozen=True)
class ClassificationValues:
    """Classification values inserted into MSP/MGF metadata."""

    kingdom: str = ""
    superclass: str = ""
    class_name: str = ""
    subclass: str = ""
    direct_parent: str = ""

    @classmethod
    def empty(cls) -> ClassificationValues:
        return cls()

    @classmethod
    def from_row(cls, row: pd.Series | dict[str, Any] | None) -> ClassificationValues:
        if row is None:
            return cls.empty()

        return cls(
            kingdom=_to_text(_get_value(row, "Kingdom")),
            superclass=_to_text(_get_value(row, "Superclass")),
            class_name=_to_text(_get_value(row, "Class")),
            subclass=_to_text(_get_value(row, "Subclass")),
            direct_parent=_to_text(_get_value(row, "DirectParent")),
        )

    def to_pairs(self) -> list[tuple[str, str]]:
        return [
            ("Kingdom", self.kingdom),
            ("Superclass", self.superclass),
            ("Class", self.class_name),
            ("Subclass", self.subclass),
            ("DirectParent", self.direct_parent),
        ]


def make_classification_lookup(
    dataframe: pd.DataFrame,
    *,
    identifier_column: str,
) -> dict[str, ClassificationValues]:
    """Create identifier -> classification mapping from lookup DataFrame."""

    if dataframe.empty:
        return {}

    if identifier_column not in dataframe.columns:
        return {}

    lookup: dict[str, ClassificationValues] = {}

    for _, row in dataframe.iterrows():
        identifier = _to_identifier(row.get(identifier_column))

        if identifier is None:
            continue

        lookup[identifier] = ClassificationValues.from_row(row)

    return lookup


def make_classification_lines(
    classification: ClassificationValues,
    *,
    delimiter: str,
) -> list[str]:
    """Create metadata lines for MSP or MGF."""

    lines: list[str] = []

    for key, value in classification.to_pairs():
        if delimiter == ":":
            lines.append(f"{key}: {value}")
        elif delimiter == "=":
            lines.append(f"{key}={value}")
        else:
            raise ValueError(f"Unsupported delimiter: {delimiter}")

    return lines


def is_classification_line(line: str) -> bool:
    """Return True if a line is one of the inserted classification fields."""

    key = get_metadata_key(line)

    if key is None:
        return False

    return key.lower() in {
        field.lower()
        for field in CLASSIFICATION_FIELDS
    }


def get_metadata_key(line: str) -> str | None:
    """Get metadata key from 'KEY: value' or 'KEY=value' line."""

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

    if not key:
        return None

    return key


def _get_value(row: pd.Series | dict[str, Any], key: str) -> Any:
    if isinstance(row, pd.Series):
        return row.get(key)

    return row.get(key)


def _to_identifier(value: Any) -> str | None:
    if value is None:
        return None

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def _to_text(value: Any) -> str:
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value)