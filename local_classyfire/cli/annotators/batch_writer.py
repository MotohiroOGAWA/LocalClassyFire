from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, TextIO

from .classification import (
    ClassificationValues,
    is_classification_line,
    make_classification_lines,
)
from .text_records import (
    IdentifierHit,
    find_identifier_in_line,
)
from local_classyfire.cli.lookup_runner import run_lookup


@dataclass
class PendingRecord:
    """One MSP/MGF record waiting for annotation and writing."""

    lines: list[str]
    hit: IdentifierHit | None = None


@dataclass
class PendingAnnotationBatch:
    """Records and identifier positions waiting for batch lookup."""

    records: list[PendingRecord] = field(default_factory=list)
    hit_count: int = 0

    def add_record(self, record: PendingRecord) -> None:
        self.records.append(record)

        if record.hit is not None:
            self.hit_count += 1

    def should_flush(self, batch_size: int) -> bool:
        return self.hit_count >= batch_size

    def clear(self) -> None:
        self.records.clear()
        self.hit_count = 0


def annotate_records_streaming(
    *,
    records: Iterable[list[str]],
    output_stream: TextIO,
    db_path: str | Path,
    preferred_identifier: str,
    batch_size: int = 100,
    delimiter: str,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
) -> None:
    """Annotate records in batches and write them incrementally.

    This function does not look up classification for each record immediately.
    It keeps records until the number of found identifiers reaches batch_size.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    batch = PendingAnnotationBatch()

    for record_lines in records:
        pending_record = PendingRecord(
            lines=record_lines,
            hit=find_identifier_hit_in_record(
                lines=record_lines,
                identifier=preferred_identifier,
            ),
        )

        batch.add_record(pending_record)

        if batch.should_flush(batch_size):
            flush_annotation_batch(
                batch=batch,
                output_stream=output_stream,
                db_path=db_path,
                delimiter=delimiter,
                timeout=timeout,
                request_interval_seconds=request_interval_seconds,
                retry_missing=retry_missing,
                include_ids=include_ids,
            )

    if batch.records:
        flush_annotation_batch(
            batch=batch,
            output_stream=output_stream,
            db_path=db_path,
            delimiter=delimiter,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            include_ids=include_ids,
        )


def find_identifier_hit_in_record(
    *,
    lines: list[str],
    identifier: str,
) -> IdentifierHit | None:
    """Find the requested InChIKey or SMILES line in one record."""

    for line_index, line in enumerate(lines):
        found = find_identifier_in_line(
            line,
            identifier=identifier,
        )

        if found is None:
            continue

        identifier_type, identifier_value = found

        return IdentifierHit(
            line_index=line_index,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
        )

    return None


def flush_annotation_batch(
    *,
    batch: PendingAnnotationBatch,
    output_stream: TextIO,
    db_path: str | Path,
    delimiter: str,
    timeout: int,
    request_interval_seconds: float,
    retry_missing: bool,
    include_ids: bool,
) -> None:
    """Lookup classification for pending records and write them."""

    classification_by_record_index = build_classification_by_record_index(
        records=batch.records,
        db_path=db_path,
        timeout=timeout,
        request_interval_seconds=request_interval_seconds,
        retry_missing=retry_missing,
        include_ids=include_ids,
    )

    for record_index, record in enumerate(batch.records):
        classification = classification_by_record_index.get(
            record_index,
            ClassificationValues.empty(),
        )

        annotated_lines = annotate_record_lines(
            lines=record.lines,
            hit=record.hit,
            classification=classification,
            delimiter=delimiter,
        )

        for line in annotated_lines:
            output_stream.write(line)
            output_stream.write("\n")

    batch.clear()


def build_classification_by_record_index(
    *,
    records: list[PendingRecord],
    db_path: str | Path,
    timeout: int,
    request_interval_seconds: float,
    retry_missing: bool,
    include_ids: bool,
) -> dict[int, ClassificationValues]:
    """Build record index -> classification values."""

    values_by_type: dict[str, list[str]] = {
        "inchikey": [],
        "smiles": [],
    }

    record_indices_by_type: dict[str, list[int]] = {
        "inchikey": [],
        "smiles": [],
    }

    for record_index, record in enumerate(records):
        if record.hit is None:
            continue

        values_by_type[record.hit.identifier_type].append(
            record.hit.identifier_value
        )
        record_indices_by_type[record.hit.identifier_type].append(record_index)

    classification_by_record_index: dict[int, ClassificationValues] = {}

    for identifier_type in ["inchikey", "smiles"]:
        values = values_by_type[identifier_type]

        if not values:
            continue

        dataframe = run_lookup(
            db_path=db_path,
            input_type=identifier_type,
            values=values,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            include_ids=include_ids,
            create_missing_tables=True,
        )

        for local_index, (_, row) in enumerate(dataframe.iterrows()):
            record_index = record_indices_by_type[identifier_type][local_index]
            classification_by_record_index[record_index] = (
                ClassificationValues.from_row(row)
            )

    return classification_by_record_index


def annotate_record_lines(
    *,
    lines: list[str],
    hit: IdentifierHit | None,
    classification: ClassificationValues,
    delimiter: str,
) -> list[str]:
    """Insert classification lines after the identifier line."""

    if hit is None:
        return lines

    output_lines: list[str] = []

    index = 0

    while index < len(lines):
        output_lines.append(lines[index])

        if index == hit.line_index:
            output_lines.extend(
                make_classification_lines(
                    classification,
                    delimiter=delimiter,
                )
            )

            index += 1

            while index < len(lines) and is_classification_line(lines[index]):
                index += 1

            continue

        index += 1

    return output_lines