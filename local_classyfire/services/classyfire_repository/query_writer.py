from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import ClassyFireQuery, Classification

from .utils import update_existing_columns


class ClassyFireQueryWriter:
    """
    Write query history/status into ClassyFireQuery.

    This replaces the need for a separate NotFoundCompound table.
    """

    @classmethod
    def get_or_create_query(
        cls,
        session: Session,
        inchikey: str,
    ) -> ClassyFireQuery:
        query = session.execute(
            select(ClassyFireQuery).where(
                ClassyFireQuery.inchikey == inchikey,
            )
        ).scalar_one_or_none()

        if query is not None:
            return query

        query = ClassyFireQuery(
            inchikey=inchikey,
        )

        session.add(query)
        session.flush()

        return query

    @classmethod
    def mark_success(
        cls,
        session: Session,
        *,
        inchikey: str,
        classification: Classification,
        smiles: str | None = None,
        inchi: str | None = None,
    ) -> ClassyFireQuery:
        query = cls.get_or_create_query(
            session=session,
            inchikey=inchikey,
        )

        update_existing_columns(
            query,
            {
                "inchikey": inchikey,
                "smiles": smiles,
                "inchi": inchi,
                "classification_id": classification.classification_id,
                "query_status": "success",
                "message": None,
                "updated_at": datetime.now(),
            },
            skip_none=False,
        )

        session.flush()

        return query

    @classmethod
    def mark_not_found(
        cls,
        session: Session,
        *,
        inchikey: str,
        message: str,
    ) -> ClassyFireQuery:
        query = cls.get_or_create_query(
            session=session,
            inchikey=inchikey,
        )

        update_existing_columns(
            query,
            {
                "inchikey": inchikey,
                "classification_id": None,
                "query_status": "not_found",
                "message": message,
                "updated_at": datetime.now(),
            },
            skip_none=False,
        )

        session.flush()

        return query

    @classmethod
    def mark_error(
        cls,
        session: Session,
        *,
        inchikey: str,
        message: str,
    ) -> ClassyFireQuery:
        query = cls.get_or_create_query(
            session=session,
            inchikey=inchikey,
        )

        update_existing_columns(
            query,
            {
                "inchikey": inchikey,
                "classification_id": None,
                "query_status": "error",
                "message": message,
                "updated_at": datetime.now(),
            },
            skip_none=False,
        )

        session.flush()

        return query