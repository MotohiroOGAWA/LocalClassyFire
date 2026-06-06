from __future__ import annotations

from pathlib import Path

import pandas as pd

from local_classyfire.cli.progress import progress_iter
from local_classyfire.services.classyfire_lookup_service import (
    ClassyFireLookupService,
)
from local_classyfire.services.session import (
    create_session_factory,
    create_sqlite_engine,
    create_tables,
)


def run_lookup(
    *,
    db_path: str | Path,
    input_type: str,
    values: list[str],
    batch_size: int = 100,
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
    create_missing_tables: bool = True,
    show_progress: bool = True,
) -> pd.DataFrame:
    """Run ClassyFire lookup and return classification table."""

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    engine = create_sqlite_engine(db_path)

    if create_missing_tables:
        create_tables(engine)

    session_factory = create_session_factory(engine)

    dataframes: list[pd.DataFrame] = []

    batches = list(iter_batches(values, batch_size))

    with session_factory() as session:
        for batch_values in progress_iter(
            batches,
            total=len(batches),
            desc=f"Classifying {input_type}",
            unit="batch",
            enabled=show_progress,
        ):
            if input_type == "inchikey":
                dataframe = (
                    ClassyFireLookupService
                    .get_classification_dataframe_by_inchikey_list(
                        session=session,
                        inchikey_list=batch_values,
                        timeout=timeout,
                        request_interval_seconds=request_interval_seconds,
                        retry_missing=retry_missing,
                        include_input_columns=True,
                        include_ids=include_ids,
                    )
                )
            elif input_type == "smiles":
                dataframe = (
                    ClassyFireLookupService
                    .get_classification_dataframe_by_smiles_list(
                        session=session,
                        smiles_list=batch_values,
                        timeout=timeout,
                        request_interval_seconds=request_interval_seconds,
                        retry_missing=retry_missing,
                        include_input_columns=True,
                        include_ids=include_ids,
                    )
                )
            else:
                raise ValueError(f"Unsupported input_type: {input_type}")

            dataframes.append(dataframe)

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)


def iter_batches(
    values: list[str],
    batch_size: int,
):
    for start in range(0, len(values), batch_size):
        yield values[start:start + batch_size]