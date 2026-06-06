from __future__ import annotations

from sqlalchemy.orm import Session

from .base import normalize_text
from .set_batch_resolver import (
    get_alternative_parent_set_ids,
    get_ancestor_set_ids,
    get_external_descriptor_set_ids,
    get_intermediate_node_set_ids,
    get_or_create_alternative_parent_set_ids,
    get_or_create_ancestor_set_ids,
    get_or_create_external_descriptor_set_ids,
    get_or_create_intermediate_node_set_ids,
    get_or_create_predicted_chebi_term_set_ids,
    get_or_create_predicted_lipidmaps_term_set_ids,
    get_or_create_substituent_set_ids,
    get_predicted_chebi_term_set_ids,
    get_predicted_lipidmaps_term_set_ids,
    get_substituent_set_ids,
)


def _get_single_id(
    id_by_hash: dict[str, int],
    set_hash: str | None,
) -> int | None:
    set_hash = normalize_text(set_hash)

    if set_hash is None:
        return None

    return id_by_hash.get(set_hash)


def get_intermediate_node_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_intermediate_node_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_intermediate_node_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_intermediate_node_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_alternative_parent_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_alternative_parent_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_alternative_parent_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_alternative_parent_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_ancestor_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_ancestor_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_ancestor_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_ancestor_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_substituent_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_substituent_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_substituent_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_substituent_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_external_descriptor_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_external_descriptor_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_external_descriptor_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_external_descriptor_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_predicted_chebi_term_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_predicted_chebi_term_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_predicted_chebi_term_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_predicted_chebi_term_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_predicted_lipidmaps_term_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_predicted_lipidmaps_term_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )


def get_or_create_predicted_lipidmaps_term_set_id(
    session: Session,
    set_hash: str | None,
) -> int | None:
    return _get_single_id(
        get_or_create_predicted_lipidmaps_term_set_ids(
            session=session,
            set_hashes=[set_hash],
        ),
        set_hash,
    )