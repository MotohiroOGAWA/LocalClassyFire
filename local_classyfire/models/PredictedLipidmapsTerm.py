from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PredictedLipidmapsTerm(Base):
    """Dictionary table for predicted LIPID MAPS terms."""

    __tablename__ = "PredictedLipidmapsTerm"

    predicted_lipidmaps_term_id: Mapped[int] = mapped_column(
        "PredictedLipidmapsTermID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    term_name: Mapped[str] = mapped_column(
        "TermName",
        String(255),
        nullable=False,
    )

    classification_links = relationship(
        "ClassificationPredictedLipidmapsTerm",
        back_populates="predicted_lipidmaps_term",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "TermName",
            name="uq_predicted_lipidmaps_terms_term_name",
        ),
    )