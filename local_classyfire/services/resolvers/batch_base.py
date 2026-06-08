from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")
RecordT = TypeVar("RecordT")
KeyT = TypeVar("KeyT")


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    text = value.strip()

    if not text:
        return None

    return text


def get_ids_by_single_unique_key(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    key_attr_name: str,
    keys: Iterable[Any],
) -> dict[Any, int]:
    """Get IDs for many records by one unique column."""

    unique_keys = sorted(
        {
            key
            for key in keys
            if key is not None
        }
    )

    if not unique_keys:
        return {}

    key_column = getattr(model, key_attr_name)

    stmt = select(model).where(key_column.in_(unique_keys))
    rows = session.execute(stmt).scalars().all()

    return {
        getattr(row, key_attr_name): getattr(row, id_attr_name)
        for row in rows
    }


def get_or_create_ids_by_single_unique_key(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    key_attr_name: str,
    records: Iterable[RecordT],
    key_getter: Callable[[RecordT], Any | None],
    create_fields_getter: Callable[[RecordT], dict[str, Any]],
) -> dict[Any, int]:
    """Get or create IDs for many records by one unique column.

    Returns
    -------
    dict[Any, int]
        Mapping from unique key to row ID.
    """

    record_by_key: dict[Any, RecordT] = {}

    for record in records:
        key = key_getter(record)

        if key is None:
            continue

        record_by_key.setdefault(key, record)

    if not record_by_key:
        return {}

    existing_id_by_key = get_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name=key_attr_name,
        keys=record_by_key.keys(),
    )

    missing_keys = [
        key
        for key in record_by_key
        if key not in existing_id_by_key
    ]

    if missing_keys:
        new_rows = [
            model(**create_fields_getter(record_by_key[key]))
            for key in missing_keys
        ]

        session.add_all(new_rows)
        session.flush()

    return get_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name=key_attr_name,
        keys=record_by_key.keys(),
    )

def get_ids_by_name(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    names: Iterable[str | None],
) -> dict[str, int]:
    normalized_names = [
        normalize_text(name)
        for name in names
    ]

    return get_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name="name",
        keys=normalized_names,
    )


def get_or_create_ids_by_name(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    records: Iterable[RecordT],
    name_getter: Callable[[RecordT], str | None],
    create_fields_getter: Callable[[RecordT], dict[str, Any]],
) -> dict[str, int]:
    return get_or_create_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name="name",
        records=records,
        key_getter=lambda record: normalize_text(name_getter(record)),
        create_fields_getter=create_fields_getter,
    )