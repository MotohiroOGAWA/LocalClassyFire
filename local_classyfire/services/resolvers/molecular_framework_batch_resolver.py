from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from local_classyfire.models import MolecularFramework

from .batch_base import get_ids_by_name, get_or_create_ids_by_name


def get_molecular_framework_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=MolecularFramework,
        id_attr_name="molecular_framework_id",
        names=names,
    )


def get_or_create_molecular_framework_ids(
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
        model=MolecularFramework,
        id_attr_name="molecular_framework_id",
        records=valid_names,
        name_getter=lambda name: name,
        create_fields_getter=lambda name: {
            "name": name.strip(),
        },
    )