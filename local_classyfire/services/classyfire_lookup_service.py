from __future__ import annotations

from typing import Any
import pandas as pd
from rdkit import Chem
from rdkit.Chem import inchi
from sqlalchemy.orm import Session

from ..models import ClassyFireMissingQuery, ClassyFireQuery
from .classyfire_query_repository import (
    ClassyFireCachedQuery,
    ClassyFireQueryRepository,
)


class ClassyFireLookupService:
    """User-facing ClassyFire lookup service.

    This service accepts SMILES or InChIKey lists and returns query records
    as dictionaries keyed by the original normalized input strings.
    """

    @classmethod
    def get_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str | None],
        *,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        retry_missing: bool = False,
        flush: bool = True,
    ) -> dict[str, ClassyFireCachedQuery | None]:
        """Get ClassyFire queries from InChIKey list.

        Returns
        -------
        dict[str, ClassyFireCachedQuery | None]
            Mapping from normalized input InChIKey to cached query.
        """
        unique_inchikeys = cls._unique_normalized_strings(inchikey_list)

        if not unique_inchikeys:
            return {}

        query_by_inchikey = (
            ClassyFireQueryRepository.get_or_create_queries_by_inchikey_list(
                session=session,
                inchikey_list=unique_inchikeys,
                timeout=timeout,
                request_interval_seconds=request_interval_seconds,
                retry_missing=retry_missing,
                flush=flush,
            )
        )

        return {
            inchikey: query_by_inchikey.get(inchikey)
            for inchikey in unique_inchikeys
        }

    @classmethod
    def get_queries_by_smiles_list(
        cls,
        session: Session,
        smiles_list: list[str | None],
        *,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        retry_missing: bool = False,
        flush: bool = True,
    ) -> dict[str, ClassyFireCachedQuery | None]:
        """Get ClassyFire queries from SMILES list.

        SMILES are deduplicated before RDKit conversion to reduce
        conversion cost.

        Returns
        -------
        dict[str, ClassyFireCachedQuery | None]
            Mapping from normalized input SMILES to cached query.
            Invalid SMILES are mapped to None.
        """
        unique_smiles = cls._unique_normalized_strings(smiles_list)

        if not unique_smiles:
            return {}

        inchikey_by_smiles: dict[str, str | None] = {}

        for smiles in unique_smiles:
            inchikey_by_smiles[smiles] = cls._smiles_to_inchikey(smiles)

        unique_inchikeys = sorted(
            {
                inchikey
                for inchikey in inchikey_by_smiles.values()
                if inchikey is not None
            }
        )

        query_by_inchikey: dict[str, ClassyFireCachedQuery | None] = {}

        if unique_inchikeys:
            query_by_inchikey = (
                ClassyFireQueryRepository.get_or_create_queries_by_inchikey_list(
                    session=session,
                    inchikey_list=unique_inchikeys,
                    timeout=timeout,
                    request_interval_seconds=request_interval_seconds,
                    retry_missing=retry_missing,
                    flush=flush,
                )
            )

        return {
            smiles: (
                query_by_inchikey.get(inchikey)
                if inchikey is not None
                else None
            )
            for smiles, inchikey in inchikey_by_smiles.items()
        }

    @classmethod
    def get_classification_dataframe_by_inchikey_list(
        cls,
        session,
        inchikey_list: list[str | None],
        *,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        retry_missing: bool = False,
        flush: bool = True,
        include_input_columns: bool = True,
        include_ids: bool = False,
    ) -> pd.DataFrame:
        """Return kingdom-superclass-class-subclass-direct_parent by InChIKey.

        The output rows are aligned to the original input list.
        Internally, duplicate InChIKeys are queried only once.
        """
        query_by_inchikey = cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=inchikey_list,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            flush=flush,
        )

        rows: list[dict[str, Any]] = []

        for inchikey in inchikey_list:
            normalized_inchikey = cls._normalize_text(inchikey)

            query = (
                query_by_inchikey.get(normalized_inchikey)
                if normalized_inchikey is not None
                else None
            )

            row = cls._make_classification_row(
                input_value=normalized_inchikey,
                input_type="InChIKey",
                inchikey=None,
                query=query,
                include_input_columns=include_input_columns,
                include_ids=include_ids,
            )

            rows.append(row)

        return pd.DataFrame(rows)

    @classmethod
    def get_classification_dataframe_by_smiles_list(
        cls,
        session,
        smiles_list: list[str | None],
        *,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        retry_missing: bool = False,
        flush: bool = True,
        include_input_columns: bool = True,
        include_ids: bool = False,
    ) -> pd.DataFrame:
        """Return kingdom-superclass-class-subclass-direct_parent by SMILES.

        The output rows are aligned to the original input list.
        Internally, duplicate SMILES are converted only once, and duplicate
        InChIKeys are queried only once.
        """
        query_by_smiles = cls.get_queries_by_smiles_list(
            session=session,
            smiles_list=smiles_list,
            timeout=timeout,
            request_interval_seconds=request_interval_seconds,
            retry_missing=retry_missing,
            flush=flush,
        )

        rows: list[dict[str, Any]] = []

        for smiles in smiles_list:
            normalized_smiles = cls._normalize_text(smiles)

            query = (
                query_by_smiles.get(normalized_smiles)
                if normalized_smiles is not None
                else None
            )

            inchikey = (
                query.inchikey
                if isinstance(query, (ClassyFireQuery, ClassyFireMissingQuery))
                else None
            )

            row = cls._make_classification_row(
                input_value=normalized_smiles,
                input_type="SMILES",
                inchikey=inchikey,
                query=query,
                include_input_columns=include_input_columns,
                include_ids=include_ids,
            )

            rows.append(row)

        return pd.DataFrame(rows)

    @staticmethod
    def _unique_normalized_strings(
        values: list[str | None],
    ) -> list[str]:
        """Normalize, remove empty values, and deduplicate strings."""
        return sorted(
            {
                value.strip()
                for value in values
                if value is not None and value.strip()
            }
        )

    @staticmethod
    def _smiles_to_inchikey(
        smiles: str,
    ) -> str | None:
        """Convert SMILES to InChIKey using RDKit.

        Returns None if SMILES is invalid or conversion fails.
        """
        mol = Chem.MolFromSmiles(smiles)

        if mol is None:
            return None

        try:
            inchikey = inchi.MolToInchiKey(mol)
        except Exception:
            return None

        if not inchikey:
            return None

        return inchikey

    @classmethod
    def _make_classification_row(
        cls,
        *,
        input_value: str | None,
        input_type: str,
        inchikey: str | None,
        query: ClassyFireCachedQuery | None,
        include_input_columns: bool,
        include_ids: bool,
    ) -> dict[str, Any]:
        row: dict[str, Any] = {}

        if include_input_columns:
            row.update(
                {
                    input_type: input_value,
                }
            )
            if inchikey is not None:
                 row["InChIKey"] = inchikey

        row.update(
            {
                "Kingdom": None,
                "Superclass": None,
                "Class": None,
                "Subclass": None,
                "DirectParent": None,
            }
        )

        if include_ids:
            row.update(
                {
                    "KingdomID": None,
                    "SuperclassID": None,
                    "ClassID": None,
                    "SubclassID": None,
                    "DirectParentID": None,
                }
            )

        if not isinstance(query, ClassyFireQuery):
            return row

        row.update(
            {
                "Kingdom": cls._get_name(query.kingdom),
                "Superclass": cls._get_name(query.superclass),
                "Class": cls._get_name(query.classyfire_class),
                "Subclass": cls._get_name(query.subclass),
                "DirectParent": cls._get_name(query.direct_parent),
            }
        )

        if include_ids:
            row.update(
                {
                    "KingdomID": query.kingdom_id,
                    "SuperclassID": query.superclass_id,
                    "ClassID": query.class_id,
                    "SubclassID": query.subclass_id,
                    "DirectParentID": query.direct_parent_id,
                }
            )

        return row

    @staticmethod
    def _get_classification_status(
        query: ClassyFireCachedQuery | None,
    ) -> str:
        if isinstance(query, ClassyFireQuery):
            return "found"

        if isinstance(query, ClassyFireMissingQuery):
            return "missing"

        return "none"

    @staticmethod
    def _get_name(value: object | None) -> str | None:
        if value is None:
            return None

        name = getattr(value, "name", None)

        if name is None:
            return None

        return str(name)

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        text = value.strip()

        if not text:
            return None

        return text

if __name__ == "__main__":
    from pathlib import Path

    from local_classyfire.services.classyfire_query_repository import (
        ClassyFireQueryRepository,
    )
    from local_classyfire.services.session import (
        create_session_factory,
        create_sqlite_engine,
        create_tables,
    )

    database_path = Path("db/classyfire_cache.sqlite")
    results_dir = Path("db/trash/results")

    batch_size = 100

    engine = create_sqlite_engine(
        str(database_path),
        echo=False,
    )
    create_tables(engine)

    SessionFactory = create_session_factory(engine)

    smiles_list = [
        "c1ccccc1",          # benzene
        "Cc1ccccc1",         # toluene
        "c1ccc2ccccc2c1",    # naphthalene
        # "c1ccc(cc1)c2ccccc2", # biphenyl
        # "C(C1C(C(C(C(O1)O)O)O)O)O",   # glucose-like
        # "C(C(C(C(C=O)O)O)O)O",        # open-chain hexose-like
        # "C(C(C(CO)O)O)O",             # tetrose-like polyol
        # "OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@H]1O",
        # "O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",       # flavone-like
        # "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12", # quercetin-like
        # "Oc1cc(O)c2c(c1)OC(c1ccc(O)c(O)c1)CC2O",      # catechin-like
        # "O=C1C=CC(=O)C=C1",            # benzoquinone
        # "O=C1C=CC2=CC=CC=C2C1=O",      # naphthoquinone-like
        # "COC1=C(OC)C(=O)C=CC1=O",
        # "invalid_smiles",
    ]

    inchikey_list = [Chem.MolToInchiKey(Chem.MolFromSmiles(smiles)) for smiles in smiles_list]

    with SessionFactory() as session:
        result = ClassyFireLookupService.get_queries_by_smiles_list(
            session=session,
            smiles_list=smiles_list,
        )
        classification_df = ClassyFireLookupService.get_classification_dataframe_by_smiles_list(
            session=session,
            smiles_list=smiles_list,
            include_input_columns=True,
        )

        classification_df2 = ClassyFireLookupService.get_classification_dataframe_by_inchikey_list(
            session=session,
            inchikey_list=inchikey_list,
            include_input_columns=True,
        )

        queries = result