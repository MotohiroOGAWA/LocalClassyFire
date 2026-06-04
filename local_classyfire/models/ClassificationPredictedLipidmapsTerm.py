from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationPredictedLipidmapsTerm(Base):
    """Association table between Classification and PredictedLipidmapsTerm."""

    __tablename__ = "ClassificationPredictedLipidmapsTerm"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    predicted_lipidmaps_term_id: Mapped[int] = mapped_column(
        "PredictedLipidmapsTermID",
        Integer,
        ForeignKey(
            "PredictedLipidmapsTerm.PredictedLipidmapsTermID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="predicted_lipidmaps_term_links",
    )

    predicted_lipidmaps_term = relationship(
        "PredictedLipidmapsTerm",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "PredictedLipidmapsTermID",
            name="uq_classification_predicted_lipidmaps_term",
        ),
    )