from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationExternalDescriptor(Base):
    """Association table between Classification and ExternalDescriptor."""

    __tablename__ = "ClassificationExternalDescriptor"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    external_descriptor_id: Mapped[int] = mapped_column(
        "ExternalDescriptorID",
        Integer,
        ForeignKey("ExternalDescriptor.ExternalDescriptorID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="external_descriptor_links",
    )

    external_descriptor = relationship(
        "ExternalDescriptor",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "ExternalDescriptorID",
            name="uq_classification_external_descriptor",
        ),
    )