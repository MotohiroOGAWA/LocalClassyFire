from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from local_classyfire.models import ClassyFireQuery, Classification
from .utils import update_existing_columns


class ClassyFireQueryWriter:
    """Write query result into ClassyFireQuery."""

    @classmethod
    def get_query(
        cls,
        session: Session,
        inchikey: str,
    ) -> ClassyFireQuery | None:
        return session.execute(
            select(ClassyFireQuery).where(
                ClassyFireQuery.inchikey == inchikey,
            )
        ).scalar_one_or_none()

    @classmethod
    def mark_success(
        cls,
        session: Session,
        *,
        inchikey: str,
        classification: Classification,
        smiles: str | None = None,
    ) -> ClassyFireQuery:
        values = {
            "inchikey": inchikey,
            "smiles": smiles,
            "classification_id": classification.classification_id,
            "is_found": True,
            "message": None,
            "updated_at": datetime.now(),
        }

        return cls._insert_or_update_own_query(
            session=session,
            inchikey=inchikey,
            values=values,
        )

    @classmethod
    def mark_not_found(
        cls,
        session: Session,
        *,
        inchikey: str,
        message: str,
    ) -> ClassyFireQuery:
        values = {
            "inchikey": inchikey,
            "classification_id": None,
            "is_found": False,
            "message": message,
            "updated_at": datetime.now(),
        }

        return cls._insert_or_update_own_query(
            session=session,
            inchikey=inchikey,
            values=values,
        )

    @classmethod
    def mark_error(
        cls,
        session: Session,
        *,
        inchikey: str,
        message: str,
    ) -> ClassyFireQuery:
        values = {
            "inchikey": inchikey,
            "classification_id": None,
            "is_found": False,
            "message": message,
            "updated_at": datetime.now(),
        }

        return cls._insert_or_update_own_query(
            session=session,
            inchikey=inchikey,
            values=values,
        )

    @classmethod
    def _insert_or_update_own_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        values: dict,
    ) -> ClassyFireQuery:
        """Insert a complete query record or update an existing one.

        This method does not create an empty ClassyFireQuery.
        If another process inserts the same InChIKey first, this method does
        not overwrite it in the insert path. It re-fetches the row afterward.
        """

        query = cls.get_query(
            session=session,
            inchikey=inchikey,
        )

        if query is not None:
            update_existing_columns(
                query,
                values,
                skip_none=False,
            )
            session.flush()

            return query

        try:
            with session.begin_nested():
                query = ClassyFireQuery(**values)
                session.add(query)
                session.flush()

        except IntegrityError:
            # Another process created the record first.
            # Do not overwrite it here.
            pass

        query = cls.get_query(
            session=session,
            inchikey=inchikey,
        )

        if query is None:
            raise RuntimeError(
                f"Failed to insert or fetch ClassyFireQuery: {inchikey}"
            )

        return query