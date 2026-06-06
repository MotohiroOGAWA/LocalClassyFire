from __future__ import annotations

from pathlib import Path

import pandas as pd

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
    timeout: int = 30,
    request_interval_seconds: float = 5.0,
    retry_missing: bool = False,
    include_ids: bool = False,
    create_missing_tables: bool = True,
) -> pd.DataFrame:
    """Run ClassyFire lookup and return classification table."""

    engine = create_sqlite_engine(db_path)

    if create_missing_tables:
        create_tables(engine)

    session_factory = create_session_factory(engine)

    with session_factory() as session:
        if input_type == "inchikey":
            return (
                ClassyFireLookupService
                .get_classification_dataframe_by_inchikey_list(
                    session=session,
                    inchikey_list=values,
                    timeout=timeout,
                    request_interval_seconds=request_interval_seconds,
                    retry_missing=retry_missing,
                    include_input_columns=True,
                    include_ids=include_ids,
                )
            )

        if input_type == "smiles":
            return (
                ClassyFireLookupService
                .get_classification_dataframe_by_smiles_list(
                    session=session,
                    smiles_list=values,
                    timeout=timeout,
                    request_interval_seconds=request_interval_seconds,
                    retry_missing=retry_missing,
                    include_input_columns=True,
                    include_ids=include_ids,
                )
            )

    raise ValueError(f"Unsupported input_type: {input_type}")