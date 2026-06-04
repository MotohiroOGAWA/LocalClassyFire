from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import NotFoundCompound


class NotFoundWriter:
    """
    Store InChIKeys that failed to be fetched from ClassyFire.

    These records are used to avoid repeated API access.
    """

    @classmethod
    def upsert_not_found(
        cls,
        session: Session,
        inchikey: str,
        message: str,
    ) -> NotFoundCompound:
        record = session.execute(
            select(NotFoundCompound).where(
                NotFoundCompound.inchikey == inchikey,
            )
        ).scalar_one_or_none()

        if record is None:
            record = NotFoundCompound(
                inchikey=inchikey,
            )
            session.add(record)

        record.message = message

        if hasattr(record, "updated_at"):
            record.updated_at = datetime.now()

        session.flush()

        return record