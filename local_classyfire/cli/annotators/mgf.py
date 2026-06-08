from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .batch_writer import (
    annotate_records_streaming,
)


def annotate_mgf_file(
    *,
    input_path: str | Path,
    output_path: str | Path,
    db_path: str | Path,
    identifier: str = "inchikey",
    batch_size: int = 100,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
    delimiter: str = "=",
    show_progress: bool = True,
) -> None:
    """Annotate MGF file with ClassyFire classification metadata."""

    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", encoding="utf-8") as reader:
        with output_file.open("w", encoding="utf-8", newline="") as writer:
            annotate_records_streaming(
                records=iter_mgf_records(reader),
                output_stream=writer,
                db_path=db_path,
                preferred_identifier=identifier,
                batch_size=batch_size,
                delimiter=delimiter,
                timeout=timeout,
                request_interval_seconds=request_interval_seconds,
                retry_missing=retry_missing,
                include_ids=include_ids,
                show_progress=show_progress,
            )


def iter_mgf_records(reader) -> Iterator[list[str]]:
    """Yield MGF records.

    MGF records are separated by END IONS.
    Lines outside BEGIN IONS / END IONS are also preserved.
    """

    record_lines: list[str] = []

    for raw_line in reader:
        line = raw_line.rstrip("\n\r")
        record_lines.append(line)

        if line.strip().upper() == "END IONS":
            yield record_lines
            record_lines = []

    if record_lines:
        yield record_lines