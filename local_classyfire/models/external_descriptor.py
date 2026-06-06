from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ExternalDescriptor(Base):
    """External descriptor from an external database.

    The descriptor identity includes source, source_id, and annotations.
    """

    __tablename__ = "ExternalDescriptor"

    __table_args__ = (
        UniqueConstraint(
            "Source",
            "SourceID",
            "AnnotationHash",
            name="UQ_ExternalDescriptor_Source_SourceID_AnnotationHash",
        ),
    )

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

    annotation_hash: Mapped[str] = mapped_column(
        "AnnotationHash",
        String(64),
        nullable=False,
        index=True,
    )

    annotation_links = relationship(
        "ExternalDescriptorAnnotationLink",
        back_populates="external_descriptor",
        cascade="all, delete-orphan",
    )

    set_items = relationship(
        "ExternalDescriptorSetItem",
        back_populates="external_descriptor",
        cascade="all, delete-orphan",
    )


class ExternalDescriptorAnnotation(Base):
    """Annotation text attached to an external descriptor."""

    __tablename__ = "ExternalDescriptorAnnotation"

    __table_args__ = (
        UniqueConstraint(
            "Annotation",
            name="UQ_ExternalDescriptorAnnotation_Annotation",
        ),
    )

    external_descriptor_annotation_id: Mapped[int] = mapped_column(
        "ExternalDescriptorAnnotationID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    annotation: Mapped[str] = mapped_column(
        "Annotation",
        String(255),
        nullable=False,
    )

    descriptor_links = relationship(
        "ExternalDescriptorAnnotationLink",
        back_populates="annotation",
        cascade="all, delete-orphan",
    )


class ExternalDescriptorAnnotationLink(Base):
    """Link table between ExternalDescriptor and ExternalDescriptorAnnotation."""

    __tablename__ = "ExternalDescriptorAnnotationLink"

    external_descriptor_id: Mapped[int] = mapped_column(
        "ExternalDescriptorID",
        Integer,
        ForeignKey(
            "ExternalDescriptor.ExternalDescriptorID",
            ondelete="CASCADE",
        ),
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


class ExternalDescriptorSet(Base):
    """A reusable set of external descriptors."""

    __tablename__ = "ExternalDescriptorSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_ExternalDescriptorSet_SetHash",
        ),
    )

    external_descriptor_set_id: Mapped[int] = mapped_column(
        "ExternalDescriptorSetID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    set_hash: Mapped[str] = mapped_column(
        "SetHash",
        String(64),
        nullable=False,
        index=True,
    )

    items = relationship(
        "ExternalDescriptorSetItem",
        back_populates="external_descriptor_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="external_descriptor_set",
    )


class ExternalDescriptorSetItem(Base):
    """Link table between ExternalDescriptorSet and ExternalDescriptor."""

    __tablename__ = "ExternalDescriptorSetItem"

    external_descriptor_set_id: Mapped[int] = mapped_column(
        "ExternalDescriptorSetID",
        Integer,
        ForeignKey(
            "ExternalDescriptorSet.ExternalDescriptorSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    external_descriptor_id: Mapped[int] = mapped_column(
        "ExternalDescriptorID",
        Integer,
        ForeignKey(
            "ExternalDescriptor.ExternalDescriptorID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    external_descriptor_set = relationship(
        "ExternalDescriptorSet",
        back_populates="items",
    )

    external_descriptor = relationship(
        "ExternalDescriptor",
        back_populates="set_items",
    )