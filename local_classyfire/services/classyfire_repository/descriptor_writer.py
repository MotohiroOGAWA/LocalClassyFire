from __future__ import annotations

from sqlalchemy.orm import Session

from local_classyfire.models import (
    Classification,
    ClassificationExternalDescriptor,
    ExternalDescriptor,
    ExternalDescriptorAnnotation,
    ExternalDescriptorAnnotationLink,
)
from local_classyfire.services.classyfire_result import ExternalDescriptorData

from .utils import get_or_create, replace_relationship_items


class DescriptorWriter:
    @classmethod
    def replace_external_descriptors(
        cls,
        session: Session,
        classification: Classification,
        descriptors: list[ExternalDescriptorData],
    ) -> None:
        links: list[ClassificationExternalDescriptor] = []

        for descriptor in descriptors:
            stored_descriptor = cls._get_or_create_external_descriptor(
                session=session,
                descriptor=descriptor,
            )

            cls._replace_annotations(
                session=session,
                external_descriptor=stored_descriptor,
                annotations=descriptor.annotations,
            )

            link = ClassificationExternalDescriptor(
                classification_id=classification.classification_id,
                external_descriptor_id=stored_descriptor.external_descriptor_id,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="external_descriptor_links",
            new_items=links,
        )

    @classmethod
    def _get_or_create_external_descriptor(
        cls,
        session: Session,
        descriptor: ExternalDescriptorData,
    ) -> ExternalDescriptor:
        return get_or_create(
            session=session,
            model=ExternalDescriptor,
            lookup={
                "source": descriptor.source,
                "source_id": descriptor.source_id,
            },
        )

    @classmethod
    def _replace_annotations(
        cls,
        session: Session,
        external_descriptor: ExternalDescriptor,
        annotations: list[str],
    ) -> None:
        links: list[ExternalDescriptorAnnotationLink] = []

        for annotation in annotations:
            stored_annotation = get_or_create(
                session=session,
                model=ExternalDescriptorAnnotation,
                lookup={"annotation": annotation},
            )

            link = ExternalDescriptorAnnotationLink(
                external_descriptor_id=external_descriptor.external_descriptor_id,
                external_descriptor_annotation_id=(
                    stored_annotation.external_descriptor_annotation_id
                ),
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=external_descriptor,
            relationship_name="annotation_links",
            new_items=links,
        )