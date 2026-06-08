from __future__ import annotations

from sqlalchemy.orm import Session

from .base import normalize_text
from .molecular_framework_batch_resolver import (
    get_molecular_framework_ids,
    get_or_create_molecular_framework_ids,
)


def get_molecular_framework_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_molecular_framework_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_molecular_framework_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_or_create_molecular_framework_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)