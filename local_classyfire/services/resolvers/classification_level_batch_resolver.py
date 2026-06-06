from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from ...models import (
    ClassyFireClass,
    ClassyFireDirectParent,
    ClassyFireKingdom,
    ClassyFireSubclass,
    ClassyFireSuperclass,
)
from ..classyfire_result import ClassyFireLevelData

from .batch_base import get_ids_by_name, get_or_create_ids_by_name


def _level_create_fields(
    data: ClassyFireLevelData,
) -> dict[str, str | None]:
    return {
        "name": data.name.strip(),
        "description": data.description,
        "chemont_id": data.chemont_id,
        "url": data.url,
    }


def get_kingdom_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=ClassyFireKingdom,
        id_attr_name="classyfire_kingdom_id",
        names=names,
    )


def get_or_create_kingdom_ids(
    session: Session,
    records: Iterable[ClassyFireLevelData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=ClassyFireKingdom,
        id_attr_name="classyfire_kingdom_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_level_create_fields,
    )


def get_superclass_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=ClassyFireSuperclass,
        id_attr_name="classyfire_superclass_id",
        names=names,
    )


def get_or_create_superclass_ids(
    session: Session,
    records: Iterable[ClassyFireLevelData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=ClassyFireSuperclass,
        id_attr_name="classyfire_superclass_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_level_create_fields,
    )


def get_class_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=ClassyFireClass,
        id_attr_name="classyfire_class_id",
        names=names,
    )


def get_or_create_class_ids(
    session: Session,
    records: Iterable[ClassyFireLevelData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=ClassyFireClass,
        id_attr_name="classyfire_class_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_level_create_fields,
    )


def get_subclass_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=ClassyFireSubclass,
        id_attr_name="classyfire_subclass_id",
        names=names,
    )


def get_or_create_subclass_ids(
    session: Session,
    records: Iterable[ClassyFireLevelData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=ClassyFireSubclass,
        id_attr_name="classyfire_subclass_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_level_create_fields,
    )


def get_direct_parent_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=ClassyFireDirectParent,
        id_attr_name="classyfire_direct_parent_id",
        names=names,
    )


def get_or_create_direct_parent_ids(
    session: Session,
    records: Iterable[ClassyFireLevelData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=ClassyFireDirectParent,
        id_attr_name="classyfire_direct_parent_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_level_create_fields,
    )