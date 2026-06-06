from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from local_classyfire.cli.annotators.classification import (
    ClassificationValues,
)
from local_classyfire.cli.lookup_runner import run_lookup


CLASSIFICATION_COLUMNS = [
    "Kingdom",
    "Superclass",
    "Class",
    "Subclass",
    "DirectParent",
]


def annotate_msdataset(
    *,
    dataset,
    db_path: str | Path,
    identifier_column: str,
    identifier_type: str,
    batch_size: int = 100,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
    overwrite: bool = True,
):
    """Add ClassyFire classification columns to an msentity.MSDataset.

    Parameters
    ----------
    dataset:
        msentity.MSDataset object.

    db_path:
        Path to LocalClassyFire SQLite database.

    identifier_column:
        Metadata column name containing SMILES or InChIKey.

    identifier_type:
        Either "smiles" or "inchikey".

    batch_size:
        Number of identifiers passed to lookup at once.

    overwrite:
        If False, existing classification columns are not overwritten.

    Returns
    -------
    dataset
        The same MSDataset object with classification columns added.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    if identifier_type not in {"smiles", "inchikey"}:
        raise ValueError(
            "identifier_type must be either 'smiles' or 'inchikey'."
        )

    metadata = dataset.metadata

    if identifier_column not in metadata.columns:
        raise KeyError(
            f"identifier_column does not exist in dataset metadata: "
            f"{identifier_column}"
        )

    identifiers = [
        _to_optional_text(value)
        for value in metadata[identifier_column].tolist()
    ]

    output_columns: dict[str, list[str]] = {
        column: []
        for column in CLASSIFICATION_COLUMNS
    }

    for start in range(0, len(identifiers), batch_size):
        end = start + batch_size
        batch_identifiers = identifiers[start:end]

        batch_classifications = lookup_classification_batch(
            db_path=db_path,
            identifier_type=identifier_type,
            identifiers=batch_identifiers,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            include_ids=include_ids,
        )

        for classification in batch_classifications:
            output_columns["Kingdom"].append(classification.kingdom)
            output_columns["Superclass"].append(classification.superclass)
            output_columns["Class"].append(classification.class_name)
            output_columns["Subclass"].append(classification.subclass)
            output_columns["DirectParent"].append(classification.direct_parent)

    for column, values in output_columns.items():
        if not overwrite and column in dataset.columns:
            continue

        dataset[column] = values

    return dataset


def lookup_classification_batch(
    *,
    db_path: str | Path,
    identifier_type: str,
    identifiers: list[str | None],
    timeout: int,
    request_interval_seconds: float,
    retry_missing: bool,
    include_ids: bool,
) -> list[ClassificationValues]:
    """Lookup one batch and return results aligned to input order."""

    normalized_identifiers = [
        identifier
        for identifier in identifiers
        if identifier is not None
    ]

    if not normalized_identifiers:
        return [
            ClassificationValues.empty()
            for _ in identifiers
        ]

    dataframe = run_lookup(
        db_path=db_path,
        input_type=identifier_type,
        values=normalized_identifiers,
        batch_size=len(normalized_identifiers),
        timeout=timeout,
        request_interval_seconds=request_interval_seconds,
        retry_missing=retry_missing,
        include_ids=include_ids,
        create_missing_tables=True,
        show_progress=False,
    )

    lookup_column = "SMILES" if identifier_type == "smiles" else "InChIKey"

    classification_by_identifier = make_classification_by_identifier(
        dataframe=dataframe,
        identifier_column=lookup_column,
    )

    results: list[ClassificationValues] = []

    for identifier in identifiers:
        if identifier is None:
            results.append(ClassificationValues.empty())
            continue

        results.append(
            classification_by_identifier.get(
                identifier,
                ClassificationValues.empty(),
            )
        )

    return results


def make_classification_by_identifier(
    *,
    dataframe: pd.DataFrame,
    identifier_column: str,
) -> dict[str, ClassificationValues]:
    """Create identifier -> ClassificationValues mapping."""

    if dataframe.empty:
        return {}

    if identifier_column not in dataframe.columns:
        return {}

    classification_by_identifier: dict[str, ClassificationValues] = {}

    for _, row in dataframe.iterrows():
        identifier = _to_optional_text(row.get(identifier_column))

        if identifier is None:
            continue

        classification_by_identifier[identifier] = (
            ClassificationValues.from_row(row)
        )

    return classification_by_identifier


def _to_optional_text(value: Any) -> str | None:
    if value is None:
        return None

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    return text