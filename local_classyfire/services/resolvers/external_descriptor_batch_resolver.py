from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from ...models import (
    ExternalDescriptor,
    ExternalDescriptorAnnotation,
)
from .base import normalize_text
from .batch_base import get_ids_by_single_unique_key


@dataclass(frozen=True)
class ExternalDescriptorKey:
    source: str
    source_id: str
    annotation_hash: str


def make_external_descriptor_key(
    *,
    source: str | None,
    source_id: str | None,
    annotation_hash: str | None,
) -> ExternalDescriptorKey | None:
    source = normalize_text(source)
    source_id = normalize_text(source_id)
    annotation_hash = normalize_text(annotation_hash)

    if source is None or source_id is None or annotation_hash is None:
        return None

    return ExternalDescriptorKey(
        source=source,
        source_id=source_id,
        annotation_hash=annotation_hash,
    )


def get_external_descriptor_ids(
    session: Session,
    keys: Iterable[ExternalDescriptorKey],
) -> dict[ExternalDescriptorKey, int]:
    unique_keys = sorted(
        set(keys),
        key=lambda key: (
            key.source,
            key.source_id,
            key.annotation_hash,
        ),
    )

    if not unique_keys:
        return {}

    stmt = (
        select(ExternalDescriptor)
        .where(
            tuple_(
                ExternalDescriptor.source,
                ExternalDescriptor.source_id,
                ExternalDescriptor.annotation_hash,
            ).in_(
                [
                    (
                        key.source,
                        key.source_id,
                        key.annotation_hash,
                    )
                    for key in unique_keys
                ]
            )
        )
    )

    rows = session.execute(stmt).scalars().all()

    return {
        ExternalDescriptorKey(
            source=row.source,
            source_id=row.source_id,
            annotation_hash=row.annotation_hash,
        ): row.external_descriptor_id
        for row in rows
    }


def get_or_create_external_descriptor_ids(
    session: Session,
    keys: Iterable[ExternalDescriptorKey],
) -> dict[ExternalDescriptorKey, int]:
    unique_keys = sorted(
        set(keys),
        key=lambda key: (
            key.source,
            key.source_id,
            key.annotation_hash,
        ),
    )

    if not unique_keys:
        return {}

    existing_id_by_key = get_external_descriptor_ids(
        session=session,
        keys=unique_keys,
    )

    missing_keys = [
        key
        for key in unique_keys
        if key not in existing_id_by_key
    ]

    if missing_keys:
        rows = [
            ExternalDescriptor(
                source=key.source,
                source_id=key.source_id,
                annotation_hash=key.annotation_hash,
            )
            for key in missing_keys
        ]

        session.add_all(rows)
        session.flush()

    return get_external_descriptor_ids(
        session=session,
        keys=unique_keys,
    )


def get_external_descriptor_annotation_ids(
    session: Session,
    annotations: Iterable[str | None],
) -> dict[str, int]:
    normalized_annotations = [
        normalize_text(annotation)
        for annotation in annotations
    ]

    return get_ids_by_single_unique_key(
        session=session,
        model=ExternalDescriptorAnnotation,
        id_attr_name="external_descriptor_annotation_id",
        key_attr_name="annotation",
        keys=normalized_annotations,
    )


def get_or_create_external_descriptor_annotation_ids(
    session: Session,
    annotations: Iterable[str | None],
) -> dict[str, int]:
    valid_annotations = sorted(
        {
            annotation
            for annotation in (
                normalize_text(annotation)
                for annotation in annotations
            )
            if annotation is not None
        }
    )

    if not valid_annotations:
        return {}

    existing_id_by_annotation = get_external_descriptor_annotation_ids(
        session=session,
        annotations=valid_annotations,
    )

    missing_annotations = [
        annotation
        for annotation in valid_annotations
        if annotation not in existing_id_by_annotation
    ]

    if missing_annotations:
        rows = [
            ExternalDescriptorAnnotation(
                annotation=annotation,
            )
            for annotation in missing_annotations
        ]

        session.add_all(rows)
        session.flush()

    return get_external_descriptor_annotation_ids(
        session=session,
        annotations=valid_annotations,
    )