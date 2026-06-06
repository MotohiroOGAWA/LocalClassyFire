from __future__ import annotations

from sqlalchemy.orm import Session

from .base import normalize_text
from .term_batch_resolver import (
    get_or_create_predicted_chebi_term_ids,
    get_or_create_predicted_lipidmaps_term_ids,
    get_or_create_substituent_ids,
    get_predicted_chebi_term_ids,
    get_predicted_lipidmaps_term_ids,
    get_substituent_ids,
)


def get_substituent_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_substituent_ids(
        session=session,
        names=[name],
    ).get(name)


def get_or_create_substituent_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_or_create_substituent_ids(
        session=session,
        names=[name],
    ).get(name)


def get_predicted_chebi_term_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_predicted_chebi_term_ids(
        session=session,
        names=[name],
    ).get(name)


def get_or_create_predicted_chebi_term_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_or_create_predicted_chebi_term_ids(
        session=session,
        names=[name],
    ).get(name)


def get_predicted_lipidmaps_term_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_predicted_lipidmaps_term_ids(
        session=session,
        names=[name],
    ).get(name)


def get_or_create_predicted_lipidmaps_term_id(
    session: Session,
    name: str | None,
) -> int | None:
    name = normalize_text(name)

    if name is None:
        return None

    return get_or_create_predicted_lipidmaps_term_ids(
        session=session,
        names=[name],
    ).get(name)