from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationAncestor(Base):
    """Association table between Classification and Ancestor."""

    __tablename__ = "ClassificationAncestor"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    ancestor_id: Mapped[int] = mapped_column(
        "AncestorID",
        Integer,
        ForeignKey("Ancestor.AncestorID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="ancestor_links",
    )

    ancestor = relationship(
        "Ancestor",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "AncestorID",
            name="uq_classification_ancestor",
        ),
    )