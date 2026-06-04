from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PredictedChebiTerm(Base):
    """Dictionary table for predicted ChEBI terms."""

    __tablename__ = "PredictedChebiTerm"

    predicted_chebi_term_id: Mapped[int] = mapped_column(
        "PredictedChebiTermID",
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
        "ClassificationPredictedChebiTerm",
        back_populates="predicted_chebi_term",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "TermName",
            name="uq_predicted_chebi_terms_term_name",
        ),
    )