from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from sqlalchemy.orm import Session

from ...models import (
    AlternativeParentSet,
    AncestorSet,
    ExternalDescriptorSet,
    IntermediateNodeSet,
    PredictedChebiTermSet,
    PredictedLipidmapsTermSet,
    SubstituentSet,
)
from .batch_base import (
    get_ids_by_single_unique_key,
    get_or_create_ids_by_single_unique_key,
)
from .base import normalize_text

ModelT = TypeVar("ModelT")


def get_set_ids_by_hash(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    normalized_hashes = [
        normalize_text(set_hash)
        for set_hash in set_hashes
    ]

    return get_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name="set_hash",
        keys=normalized_hashes,
    )


def get_or_create_set_ids_by_hash(
    session: Session,
    *,
    model: type[ModelT],
    id_attr_name: str,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    valid_hashes = [
        set_hash
        for set_hash in (
            normalize_text(set_hash)
            for set_hash in set_hashes
        )
        if set_hash is not None
    ]

    return get_or_create_ids_by_single_unique_key(
        session=session,
        model=model,
        id_attr_name=id_attr_name,
        key_attr_name="set_hash",
        records=valid_hashes,
        key_getter=lambda set_hash: set_hash,
        create_fields_getter=lambda set_hash: {
            "set_hash": set_hash,
        },
    )


def get_intermediate_node_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=IntermediateNodeSet,
        id_attr_name="intermediate_node_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_intermediate_node_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=IntermediateNodeSet,
        id_attr_name="intermediate_node_set_id",
        set_hashes=set_hashes,
    )


def get_alternative_parent_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=AlternativeParentSet,
        id_attr_name="alternative_parent_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_alternative_parent_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=AlternativeParentSet,
        id_attr_name="alternative_parent_set_id",
        set_hashes=set_hashes,
    )


def get_ancestor_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=AncestorSet,
        id_attr_name="ancestor_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_ancestor_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=AncestorSet,
        id_attr_name="ancestor_set_id",
        set_hashes=set_hashes,
    )


def get_substituent_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=SubstituentSet,
        id_attr_name="substituent_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_substituent_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=SubstituentSet,
        id_attr_name="substituent_set_id",
        set_hashes=set_hashes,
    )


def get_external_descriptor_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=ExternalDescriptorSet,
        id_attr_name="external_descriptor_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_external_descriptor_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=ExternalDescriptorSet,
        id_attr_name="external_descriptor_set_id",
        set_hashes=set_hashes,
    )


def get_predicted_chebi_term_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=PredictedChebiTermSet,
        id_attr_name="predicted_chebi_term_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_predicted_chebi_term_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=PredictedChebiTermSet,
        id_attr_name="predicted_chebi_term_set_id",
        set_hashes=set_hashes,
    )


def get_predicted_lipidmaps_term_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_set_ids_by_hash(
        session=session,
        model=PredictedLipidmapsTermSet,
        id_attr_name="predicted_lipidmaps_term_set_id",
        set_hashes=set_hashes,
    )


def get_or_create_predicted_lipidmaps_term_set_ids(
    session: Session,
    set_hashes: Iterable[str | None],
) -> dict[str, int]:
    return get_or_create_set_ids_by_hash(
        session=session,
        model=PredictedLipidmapsTermSet,
        id_attr_name="predicted_lipidmaps_term_set_id",
        set_hashes=set_hashes,
    )