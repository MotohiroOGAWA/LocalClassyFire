from __future__ import annotations

from sqlalchemy.orm import Session

from ..classyfire_result import (
    AlternativeParentData,
    IntermediateNodeData,
)

from .base import normalize_text
from .node_batch_resolver import (
    get_alternative_parent_ids,
    get_ancestor_ids,
    get_intermediate_node_ids,
    get_or_create_alternative_parent_ids,
    get_or_create_ancestor_ids,
    get_or_create_intermediate_node_ids,
)


def get_intermediate_node_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_intermediate_node_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_intermediate_node_id(
    session: Session,
    data: IntermediateNodeData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_intermediate_node_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_alternative_parent_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_alternative_parent_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_alternative_parent_id(
    session: Session,
    data: AlternativeParentData | None,
) -> int | None:
    if data is None:
        return None

    name = normalize_text(data.name)

    if name is None:
        return None

    id_by_name = get_or_create_alternative_parent_ids(
        session=session,
        records=[data],
    )

    return id_by_name.get(name)


def get_ancestor_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_ancestor_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)


def get_or_create_ancestor_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    id_by_name = get_or_create_ancestor_ids(
        session=session,
        names=[name],
    )

    return id_by_name.get(name)