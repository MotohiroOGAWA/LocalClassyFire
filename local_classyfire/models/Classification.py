from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Classification(Base):
    """ClassyFire classification result.

    This table stores the main classification result returned by ClassyFire.

    One row corresponds to one successful ClassyFire classification result.
    The InChIKey itself is managed by ClassyFireRecord.
    """

    __tablename__ = "Classification"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    kingdom: Mapped[str | None] = mapped_column(
        "Kingdom",
        Text,
        nullable=True,
    )

    superclass: Mapped[str | None] = mapped_column(
        "Superclass",
        Text,
        nullable=True,
    )

    class_name: Mapped[str | None] = mapped_column(
        "Class",
        Text,
        nullable=True,
    )

    subclass: Mapped[str | None] = mapped_column(
        "Subclass",
        Text,
        nullable=True,
    )

    direct_parent: Mapped[str | None] = mapped_column(
        "DirectParent",
        Text,
        nullable=True,
    )

    molecular_framework_id: Mapped[int | None] = mapped_column(
        "MolecularFrameworkID",
        Integer,
        ForeignKey(
            "MolecularFramework.MolecularFrameworkID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        "Description",
        Text,
        nullable=True,
    )

    classification_version: Mapped[str | None] = mapped_column(
        "ClassificationVersion",
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    molecular_framework = relationship(
        "MolecularFramework",
        back_populates="classification",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="classification",
    )

    intermediate_node_links = relationship(
        "ClassificationIntermediateNode",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    alternative_parent_links = relationship(
        "ClassificationAlternativeParent",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    external_descriptor_links = relationship(
        "ClassificationExternalDescriptor",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    substituent_links = relationship(
        "ClassificationSubstituent",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    predicted_chebi_term_links = relationship(
        "ClassificationPredictedChebiTerm",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    predicted_lipidmaps_term_links = relationship(
        "ClassificationPredictedLipidmapsTerm",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    ancestor_links = relationship(
        "ClassificationAncestor",
        back_populates="classification",
        cascade="all, delete-orphan",
    )