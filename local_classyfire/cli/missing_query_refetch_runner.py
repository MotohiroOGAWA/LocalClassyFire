from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import pandas as pd

from .progress import progress_iter
from ..services.classyfire_lookup_service import (
    ClassyFireLookupService,
)
from ..services.classyfire_query_repository import (
    ClassyFireQueryRepository,
)
from ..services.session import (
    create_session_factory,
    create_sqlite_engine,
    create_tables,
)


@dataclass(frozen=True)
class MissingQueryRefetchSummary:
    selected_count: int
    processed_count: int
    succeeded_count: int
    missing_count: int


def run_missing_query_refetch(
    *,
    db_path: str | Path,
    limit: int | None = None,
    max_seconds: float | None = None,
    batch_size: int = 100,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    ascending: bool = True,
    include_ids: bool = False,
    create_missing_tables: bool = True,
    show_progress: bool = True,
    dry_run: bool = False,
) -> pd.DataFrame:
    """Refetch ClassyFire missing queries.

    Missing queries are selected by UpdatedAt order.
    By default, older records are retried first.
    """

    if limit is not None and limit <= 0:
        raise ValueError("limit must be greater than 0.")

    if max_seconds is not None and max_seconds <= 0:
        raise ValueError("max_seconds must be greater than 0.")

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    engine = create_sqlite_engine(db_path)

    if create_missing_tables:
        create_tables(engine)

    session_factory = create_session_factory(engine)

    with session_factory() as session:
        missing_queries = (
            ClassyFireQueryRepository
            .get_missing_queries_ordered_by_updated_at(
                session=session,
                limit=limit,
                ascending=ascending,
            )
        )

        inchikeys = [
            query.inchikey
            for query in missing_queries
        ]

        if dry_run:
            return pd.DataFrame(
                {
                    "InChIKey": inchikeys,
                }
            )

        started_at = time.monotonic()
        dataframes: list[pd.DataFrame] = []
        processed_count = 0

        batches = list(iter_batches(inchikeys, batch_size))

        for batch_values in progress_iter(
            batches,
            total=len(batches),
            desc="Refetching missing ClassyFire queries",
            unit="batch",
            enabled=show_progress,
        ):
            if is_time_limit_exceeded(
                started_at=started_at,
                max_seconds=max_seconds,
            ):
                break

            dataframe = (
                ClassyFireLookupService
                .get_classification_dataframe_by_inchikey_list(
                    session=session,
                    inchikey_list=batch_values,
                    timeout=timeout,
                    request_interval_seconds=request_interval_seconds,
                    retry_missing=True,
                    include_input_columns=True,
                    include_ids=include_ids,
                )
            )

            dataframes.append(dataframe)
            processed_count += len(batch_values)

        if not dataframes:
            return pd.DataFrame(
                columns=[
                    "InChIKey",
                    "Kingdom",
                    "Superclass",
                    "Class",
                    "Subclass",
                    "DirectParent",
                ]
            )

        return pd.concat(dataframes, ignore_index=True)


def iter_batches(
    values: list[str],
    batch_size: int,
):
    for start in range(0, len(values), batch_size):
        yield values[start:start + batch_size]


def is_time_limit_exceeded(
    *,
    started_at: float,
    max_seconds: float | None,
) -> bool:
    if max_seconds is None:
        return False

    elapsed_seconds = time.monotonic() - started_at
    return elapsed_seconds >= max_seconds