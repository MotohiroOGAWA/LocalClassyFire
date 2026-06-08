from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PredictedChebiTerm(Base):
    """Predicted ChEBI term returned by ClassyFire.

    Examples
    --------
    ketal (CHEBI:59777)
    oxanes (CHEBI:46942)
    monosaccharide (CHEBI:35381)
    """

    __tablename__ = "PredictedChebiTerm"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_PredictedChebiTerm_Name",
        ),
    )

    predicted_chebi_term_id: Mapped[int] = mapped_column(
        "PredictedChebiTermID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        "Name",
        String(255),
        nullable=False,
    )

    set_items = relationship(
        "PredictedChebiTermSetItem",
        back_populates="predicted_chebi_term",
        cascade="all, delete-orphan",
    )


class PredictedChebiTermSet(Base):
    """A reusable set of predicted ChEBI terms."""

    __tablename__ = "PredictedChebiTermSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_PredictedChebiTermSet_SetHash",
        ),
    )

    predicted_chebi_term_set_id: Mapped[int] = mapped_column(
        "PredictedChebiTermSetID",
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
        "PredictedChebiTermSetItem",
        back_populates="predicted_chebi_term_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="predicted_chebi_term_set",
    )


class PredictedChebiTermSetItem(Base):
    """Link table between PredictedChebiTermSet and PredictedChebiTerm."""

    __tablename__ = "PredictedChebiTermSetItem"

    predicted_chebi_term_set_id: Mapped[int] = mapped_column(
        "PredictedChebiTermSetID",
        Integer,
        ForeignKey(
            "PredictedChebiTermSet.PredictedChebiTermSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    predicted_chebi_term_id: Mapped[int] = mapped_column(
        "PredictedChebiTermID",
        Integer,
        ForeignKey(
            "PredictedChebiTerm.PredictedChebiTermID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    predicted_chebi_term_set = relationship(
        "PredictedChebiTermSet",
        back_populates="items",
    )

    predicted_chebi_term = relationship(
        "PredictedChebiTerm",
        back_populates="set_items",
    )