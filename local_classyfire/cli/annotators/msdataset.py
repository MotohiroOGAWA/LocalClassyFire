from __future__ import annotations

from pathlib import Path
from typing import Any
from collections import defaultdict
import pandas as pd

from msentity import MSDataset

from ..annotators.classification import (
    ClassificationValues,
)
from ..lookup_runner import run_lookup
from ..progress import progress_iter


CLASSIFICATION_COLUMNS = [
    "Kingdom",
    "Superclass",
    "Class",
    "Subclass",
    "DirectParent",
]


def annotate_msdataset(
    *,
    dataset: MSDataset,
    db_path: str | Path,
    identifier_column: str,
    identifier_type: str,
    batch_size: int = 100,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
    overwrite: bool = True,
    show_progress: bool = True,
):
    """Add ClassyFire classification columns to an msentity.MSDataset."""

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    if identifier_type not in {"smiles", "inchikey"}:
        raise ValueError(
            "identifier_type must be either 'smiles' or 'inchikey'."
        )

    if identifier_column not in dataset.columns:
         raise KeyError(
            f"identifier_column does not exist in dataset metadata: "
            f"{identifier_column}"
        )

    indices_by_identifier: dict[str, list[int]] = defaultdict(list)

    for index, record in enumerate(dataset):
        identifier = _to_optional_text(record[identifier_column])

        if identifier is None:
            continue

        indices_by_identifier[identifier].append(index)

    unique_identifiers = list(indices_by_identifier.keys())

    batch_starts = list(range(0, len(unique_identifiers), batch_size))

    for start in progress_iter(
        batch_starts,
        total=len(batch_starts),
        desc="Annotating unique identifiers",
        unit="batch",
        enabled=show_progress,
    ):
        end = start + batch_size
        batch_identifiers = unique_identifiers[start:end]

        batch_classifications = lookup_classification_batch(
            db_path=db_path,
            identifier_type=identifier_type,
            identifiers=batch_identifiers,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            include_ids=include_ids,
        )

        for identifier, classification in zip(
            batch_identifiers,
            batch_classifications,
            strict=True,
        ):
            indices = indices_by_identifier[identifier]
            batch_dataset = dataset[indices]

            set_classification_columns_for_view(
                dataset=batch_dataset,
                classification=classification,
                overwrite=overwrite,
            )

    new_columns = [col for col in dataset.columns if col not in CLASSIFICATION_COLUMNS]

    identifier_column_idx = -1
    for idx, column in enumerate(new_columns):
        if column == identifier_column:
            identifier_column_idx = idx
            break
    else:
        raise KeyError(
            f"identifier_column does not exist in new dataset metadata: "
            f"{identifier_column}"
        )
    for column in reversed(CLASSIFICATION_COLUMNS):
        new_columns.insert(identifier_column_idx + 1, column)
    dataset.columns = new_columns

    return dataset

def set_classification_columns_for_view(
    *,
    dataset: MSDataset,
    classification: ClassificationValues,
    overwrite: bool,
) -> None:
    values_by_column = {
        "Kingdom": classification.kingdom,
        "Superclass": classification.superclass,
        "Class": classification.class_name,
        "Subclass": classification.subclass,
        "DirectParent": classification.direct_parent,
    }

    for column, value in values_by_column.items():
        if not overwrite and column in dataset.columns:
            continue

        dataset[column] = [value] * len(dataset)
        
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