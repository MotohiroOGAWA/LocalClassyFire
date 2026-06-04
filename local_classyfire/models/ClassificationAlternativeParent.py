from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationAlternativeParent(Base):
    """Association table between Classification and AlternativeParent."""

    __tablename__ = "ClassificationAlternativeParent"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    alternative_parent_id: Mapped[int] = mapped_column(
        "AlternativeParentID",
        Integer,
        ForeignKey("AlternativeParent.AlternativeParentID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="alternative_parent_links",
    )

    alternative_parent = relationship(
        "AlternativeParent",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "AlternativeParentID",
            name="uq_classification_alternative_parent",
        ),
    )