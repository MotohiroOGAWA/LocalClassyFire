from __future__ import annotations

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AlternativeParent(Base):
    """Dictionary table for ClassyFire alternative parents."""

    __tablename__ = "AlternativeParent"

    alternative_parent_id: Mapped[int] = mapped_column(
        "AlternativeParentID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    parent_name: Mapped[str] = mapped_column(
        "ParentName",
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        "Description",
        Text,
        nullable=True,
    )

    chemont_id: Mapped[str | None] = mapped_column(
        "ChemOntID",
        String(255),
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        "URL",
        Text,
        nullable=True,
    )

    classification_links = relationship(
        "ClassificationAlternativeParent",
        back_populates="alternative_parent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "ParentName",
            name="uq_alternative_parents_parent_name",
        ),
    )