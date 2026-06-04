from __future__ import annotations

from typing import Any, Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


def get_or_create(
    session: Session,
    model: type[T],
    lookup: dict[str, Any],
    defaults: dict[str, Any] | None = None,
) -> T:
    statement = select(model)

    for key, value in lookup.items():
        statement = statement.where(getattr(model, key) == value)

    instance = session.execute(statement).scalar_one_or_none()

    if instance is not None:
        return instance

    values = dict(lookup)

    if defaults is not None:
        values.update(defaults)

    instance = model(**values)
    session.add(instance)
    session.flush()

    return instance


def update_existing_columns(
    instance: Any,
    values: dict[str, Any],
    *,
    skip_none: bool = True,
) -> None:
    for key, value in values.items():
        if skip_none and value is None:
            continue

        if hasattr(instance, key):
            setattr(instance, key, value)


def replace_relationship_items(
    session: Session,
    parent: Any,
    relationship_name: str,
    new_items: Iterable[Any],
) -> None:
    old_items = list(getattr(parent, relationship_name))

    for item in old_items:
        session.delete(item)

    session.flush()

    setattr(parent, relationship_name, list(new_items))