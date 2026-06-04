from __future__ import annotations

from sqlalchemy import Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ExternalDescriptorAnnotation(Base):
    """Dictionary table for external descriptor annotation terms."""

    __tablename__ = "ExternalDescriptorAnnotation"

    external_descriptor_annotation_id: Mapped[int] = mapped_column(
        "ExternalDescriptorAnnotationID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    annotation: Mapped[str] = mapped_column(
        "Annotation",
        Text,
        nullable=False,
    )

    descriptor_links = relationship(
        "ExternalDescriptorAnnotationLink",
        back_populates="annotation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "Annotation",
            name="uq_external_descriptor_annotations_annotation",
        ),
    )