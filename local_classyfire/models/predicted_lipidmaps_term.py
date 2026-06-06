from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PredictedLipidmapsTerm(Base):
    """Predicted LIPID MAPS term returned by ClassyFire.

    Examples
    --------
    Benzopyranoids (PK1311)
    """

    __tablename__ = "PredictedLipidmapsTerm"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_PredictedLipidmapsTerm_Name",
        ),
    )

    predicted_lipidmaps_term_id: Mapped[int] = mapped_column(
        "PredictedLipidmapsTermID",
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
        "PredictedLipidmapsTermSetItem",
        back_populates="predicted_lipidmaps_term",
        cascade="all, delete-orphan",
    )


class PredictedLipidmapsTermSet(Base):
    """A reusable set of predicted LIPID MAPS terms."""

    __tablename__ = "PredictedLipidmapsTermSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_PredictedLipidmapsTermSet_SetHash",
        ),
    )

    predicted_lipidmaps_term_set_id: Mapped[int] = mapped_column(
        "PredictedLipidmapsTermSetID",
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
        "PredictedLipidmapsTermSetItem",
        back_populates="predicted_lipidmaps_term_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="predicted_lipidmaps_term_set",
    )


class PredictedLipidmapsTermSetItem(Base):
    """Link table between PredictedLipidmapsTermSet and PredictedLipidmapsTerm."""

    __tablename__ = "PredictedLipidmapsTermSetItem"

    predicted_lipidmaps_term_set_id: Mapped[int] = mapped_column(
        "PredictedLipidmapsTermSetID",
        Integer,
        ForeignKey(
            "PredictedLipidmapsTermSet.PredictedLipidmapsTermSetID",
            ondelete="CASCADE",
        ),
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

    predicted_lipidmaps_term_set = relationship(
        "PredictedLipidmapsTermSet",
        back_populates="items",
    )

    predicted_lipidmaps_term = relationship(
        "PredictedLipidmapsTerm",
        back_populates="set_items",
    )