from __future__ import annotations

from sqlalchemy.orm import Session

from .external_descriptor_batch_resolver import (
    ExternalDescriptorKey,
    get_external_descriptor_annotation_ids,
    get_external_descriptor_ids,
    get_or_create_external_descriptor_annotation_ids,
    get_or_create_external_descriptor_ids,
    make_external_descriptor_key,
)


def get_external_descriptor_id(
    session: Session,
    *,
    source: str | None,
    source_id: str | None,
    annotation_hash: str | None,
) -> int | None:
    key = make_external_descriptor_key(
        source=source,
        source_id=source_id,
        annotation_hash=annotation_hash,
    )

    if key is None:
        return None

    return get_external_descriptor_ids(
        session=session,
        keys=[key],
    ).get(key)


def get_or_create_external_descriptor_id(
    session: Session,
    *,
    source: str | None,
    source_id: str | None,
    annotation_hash: str | None,
) -> int | None:
    key = make_external_descriptor_key(
        source=source,
        source_id=source_id,
        annotation_hash=annotation_hash,
    )

    if key is None:
        return None

    return get_or_create_external_descriptor_ids(
        session=session,
        keys=[key],
    ).get(key)


def get_external_descriptor_annotation_id(
    session: Session,
    annotation: str | None,
) -> int | None:
    id_by_annotation = get_external_descriptor_annotation_ids(
        session=session,
        annotations=[annotation],
    )

    if annotation is None:
        return None

    return id_by_annotation.get(annotation.strip())


def get_or_create_external_descriptor_annotation_id(
    session: Session,
    annotation: str | None,
) -> int | None:
    id_by_annotation = get_or_create_external_descriptor_annotation_ids(
        session=session,
        annotations=[annotation],
    )

    if annotation is None:
        return None

    return id_by_annotation.get(annotation.strip())