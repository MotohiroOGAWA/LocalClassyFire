from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .ExternalDescriptorAnnotation import ExternalDescriptorAnnotation


class ExternalDescriptor(Base):
    """External descriptor from an external database.

    Examples
    --------
    Source:
        CHEBI

    SourceID:
        CHEBI:10002
    """

    __tablename__ = "ExternalDescriptor"

    external_descriptor_id: Mapped[int] = mapped_column(
        "ExternalDescriptorID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        "Source",
        String(255),
        nullable=False,
    )

    source_id: Mapped[str] = mapped_column(
        "SourceID",
        String(255),
        nullable=False,
    )

    annotation_links = relationship(
        "ExternalDescriptorAnnotationLink",
        back_populates="external_descriptor",
        cascade="all, delete-orphan",
    )

    classification_links = relationship(
        "ClassificationExternalDescriptor",
        back_populates="external_descriptor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "Source",
            "SourceID",
            name="uq_external_descriptors_source_source_id",
        ),
    )