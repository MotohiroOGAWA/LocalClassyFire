from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationSubstituent(Base):
    """Association table between Classification and Substituent."""

    __tablename__ = "ClassificationSubstituent"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    substituent_id: Mapped[int] = mapped_column(
        "SubstituentID",
        Integer,
        ForeignKey("Substituent.SubstituentID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="substituent_links",
    )

    substituent = relationship(
        "Substituent",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "SubstituentID",
            name="uq_classification_substituent",
        ),
    )