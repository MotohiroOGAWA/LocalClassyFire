from __future__ import annotations

from sqlalchemy.orm import Session

from ..classyfire_result import ClassyFireLevelData

from .base import normalize_text
from .classification_level_batch_resolver import (
    get_class_ids,
    get_direct_parent_ids,
    get_kingdom_ids,
    get_or_create_class_ids,
    get_or_create_direct_parent_ids,
    get_or_create_kingdom_ids,
    get_or_create_subclass_ids,
    get_or_create_superclass_ids,
    get_subclass_ids,
    get_superclass_ids,
)


def get_kingdom_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_kingdom_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_kingdom_id(
    session: Session,
    data: ClassyFireLevelData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_kingdom_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_superclass_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_superclass_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_superclass_id(
    session: Session,
    data: ClassyFireLevelData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_superclass_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_class_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_class_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_class_id(
    session: Session,
    data: ClassyFireLevelData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_class_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_subclass_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_subclass_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_subclass_id(
    session: Session,
    data: ClassyFireLevelData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_subclass_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_direct_parent_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_direct_parent_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_direct_parent_id(
    session: Session,
    data: ClassyFireLevelData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_direct_parent_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)