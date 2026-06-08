from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from ...models import (
    PredictedChebiTerm,
    PredictedLipidmapsTerm,
    Substituent,
)
from .batch_base import get_ids_by_name, get_or_create_ids_by_name


def get_substituent_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=Substituent,
        id_attr_name="substituent_id",
        names=names,
    )


def get_or_create_substituent_ids(
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
        model=Substituent,
        id_attr_name="substituent_id",
        records=valid_names,
        name_getter=lambda name: name,
        create_fields_getter=lambda name: {
            "name": name.strip(),
        },
    )


def get_predicted_chebi_term_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=PredictedChebiTerm,
        id_attr_name="predicted_chebi_term_id",
        names=names,
    )


def get_or_create_predicted_chebi_term_ids(
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
        model=PredictedChebiTerm,
        id_attr_name="predicted_chebi_term_id",
        records=valid_names,
        name_getter=lambda name: name,
        create_fields_getter=lambda name: {
            "name": name.strip(),
        },
    )


def get_predicted_lipidmaps_term_ids(
    session: Session,
    names: Iterable[str | None],
) -> dict[str, int]:
    return get_ids_by_name(
        session=session,
        model=PredictedLipidmapsTerm,
        id_attr_name="predicted_lipidmaps_term_id",
        names=names,
    )


def get_or_create_predicted_lipidmaps_term_ids(
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
        model=PredictedLipidmapsTerm,
        id_attr_name="predicted_lipidmaps_term_id",
        records=valid_names,
        name_getter=lambda name: name,
        create_fields_getter=lambda name: {
            "name": name.strip(),
        },
    )