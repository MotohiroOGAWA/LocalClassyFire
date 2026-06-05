from __future__ import annotations

from typing import Any, Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

T = TypeVar("T")


def get_or_create(
    session: Session,
    model: type[T],
    lookup: dict[str, Any],
    create_values: dict[str, Any],
) -> T:
    """Get an existing record or insert a fully populated new record.

    Rules
    -----
    - Do not create empty records.
    - If the record already exists, return it without overwriting.
    - If another process creates the record first, do not overwrite it.
    - Always re-fetch the record after the insert attempt.
    """

    instance = _get_one_by_lookup(
        session=session,
        model=model,
        lookup=lookup,
    )

    if instance is not None:
        return instance

    values = dict(create_values)

    missing_lookup_keys = [
        key for key in lookup
        if key not in values
    ]

    if missing_lookup_keys:
        raise ValueError(
            "create_values must include all lookup keys: "
            f"{missing_lookup_keys}"
        )

    try:
        with session.begin_nested():
            instance = model(**values)
            session.add(instance)
            session.flush()

    except IntegrityError:
        # Another process inserted the same unique record first.
        # Do not overwrite it. Re-fetch below.
        pass

    instance = _get_one_by_lookup(
        session=session,
        model=model,
        lookup=lookup,
    )

    if instance is None:
        raise RuntimeError(
            f"Failed to get or create {model.__name__} with lookup={lookup}"
        )

    return instance


def _get_one_by_lookup(
    session: Session,
    model: type[T],
    lookup: dict[str, Any],
) -> T | None:
    statement = select(model)

    for key, value in lookup.items():
        statement = statement.where(getattr(model, key) == value)

    return session.execute(statement).scalar_one_or_none()


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