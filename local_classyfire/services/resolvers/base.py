from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def get_id_by_unique_fields(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    unique_fields: dict[str, Any],
) -> int | None:
    """Get an ID by unique fields.

    Returns None if the row does not exist.
    """
    stmt = select(model)

    for field_name, value in unique_fields.items():
        stmt = stmt.where(getattr(model, field_name) == value)

    row = session.execute(stmt).scalar_one_or_none()

    if row is None:
        return None

    return getattr(row, id_attr_name)


def get_or_create_id_by_unique_fields(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    unique_fields: dict[str, Any],
    create_fields: dict[str, Any] | None = None,
) -> int:
    """Get an ID by unique fields.

    If the row does not exist, create it and return its ID.
    """
    existing_id = get_id_by_unique_fields(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        unique_fields=unique_fields,
    )

    if existing_id is not None:
        return existing_id

    fields: dict[str, Any] = {}
    fields.update(unique_fields)

    if create_fields:
        fields.update(create_fields)

    row = model(**fields)

    session.add(row)
    session.flush()

    return getattr(row, id_attr_name)


def normalize_text(value: str | None) -> str | None:
    """Normalize text used as a unique key."""
    if value is None:
        return None

    text = value.strip()

    if not text:
        return None

    return text


def get_id_by_name(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    name: str | None,
) -> int | None:
    """Get an ID by unique name."""
    normalized_name = normalize_text(name)

    if normalized_name is None:
        return None

    return get_id_by_unique_fields(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        unique_fields={"name": normalized_name},
    )


def get_or_create_id_by_name(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    name: str | None,
    create_fields: dict[str, Any] | None = None,
) -> int | None:
    """Get or create an ID by unique name."""
    normalized_name = normalize_text(name)

    if normalized_name is None:
        return None

    return get_or_create_id_by_unique_fields(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        unique_fields={"name": normalized_name},
        create_fields=create_fields,
    )