from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ExternalDescriptorAnnotationLink(Base):
    """Association table between ExternalDescriptor and ExternalDescriptorAnnotation."""

    __tablename__ = "ExternalDescriptorAnnotationLink"

    external_descriptor_id: Mapped[int] = mapped_column(
        "ExternalDescriptorID",
        Integer,
        ForeignKey("ExternalDescriptor.ExternalDescriptorID", ondelete="CASCADE"),
        primary_key=True,
    )

    external_descriptor_annotation_id: Mapped[int] = mapped_column(
        "ExternalDescriptorAnnotationID",
        Integer,
        ForeignKey(
            "ExternalDescriptorAnnotation.ExternalDescriptorAnnotationID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    external_descriptor = relationship(
        "ExternalDescriptor",
        back_populates="annotation_links",
    )

    annotation = relationship(
        "ExternalDescriptorAnnotation",
        back_populates="descriptor_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ExternalDescriptorID",
            "ExternalDescriptorAnnotationID",
            name="uq_external_descriptor_annotation_link",
        ),
    )