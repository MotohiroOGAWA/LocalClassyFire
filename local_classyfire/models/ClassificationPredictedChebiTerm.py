from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationPredictedChebiTerm(Base):
    """Association table between Classification and PredictedChebiTerm."""

    __tablename__ = "ClassificationPredictedChebiTerm"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    predicted_chebi_term_id: Mapped[int] = mapped_column(
        "PredictedChebiTermID",
        Integer,
        ForeignKey("PredictedChebiTerm.PredictedChebiTermID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="predicted_chebi_term_links",
    )

    predicted_chebi_term = relationship(
        "PredictedChebiTerm",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "PredictedChebiTermID",
            name="uq_classification_predicted_chebi_term",
        ),
    )