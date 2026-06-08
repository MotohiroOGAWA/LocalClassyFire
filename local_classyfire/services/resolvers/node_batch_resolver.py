from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from local_classyfire.models import (
    AlternativeParent,
    Ancestor,
    IntermediateNode,
)
from local_classyfire.services.classyfire_result import (
    AlternativeParentData,
    IntermediateNodeData,
)

from .batch_base import get_ids_by_name, get_or_create_ids_by_name


def _node_create_fields(
    data: IntermediateNodeData | AlternativeParentData,
) -> dict[str, str | None]:
    return {
        "name": data.name.strip(),
        "description": data.description,
        "chemont_id": data.chemont_id,
        "url": data.url,
    }


def get_intermediate_node_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=IntermediateNode,
        id_attr_name="intermediate_node_id",
        names=names,
    )


def get_or_create_intermediate_node_ids(
    session: Session,
    records: Iterable[IntermediateNodeData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=IntermediateNode,
        id_attr_name="intermediate_node_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_node_create_fields,
    )


def get_alternative_parent_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=AlternativeParent,
        id_attr_name="alternative_parent_id",
        names=names,
    )


def get_or_create_alternative_parent_ids(
    session: Session,
    records: Iterable[AlternativeParentData | None],
) -> dict[str, int]:
    valid_records = [
        record
        for record in records
        if record is not None
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=AlternativeParent,
        id_attr_name="alternative_parent_id",
        records=valid_records,
        name_getter=lambda record: record.name,
        create_fields_getter=_node_create_fields,
    )


def get_ancestor_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=Ancestor,
        id_attr_name="ancestor_id",
        names=names,
    )


def get_or_create_ancestor_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    valid_names = [
        name
        for name in names
        if name
    ]

    return get_or_create_ids_by_name(
        session=session,
        model=Ancestor,
        id_attr_name="ancestor_id",
        records=valid_names,
        name_getter=lambda name: name,
        create_fields_getter=lambda name: {
            "name": name.strip(),
        },
    )