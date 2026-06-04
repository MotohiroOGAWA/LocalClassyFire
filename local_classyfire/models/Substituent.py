from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Substituent(Base):
    """Dictionary table for substituent names."""

    __tablename__ = "Substituent"

    substituent_id: Mapped[int] = mapped_column(
        "SubstituentID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    substituent_name: Mapped[str] = mapped_column(
        "SubstituentName",
        String(255),
        nullable=False,
    )

    classification_links = relationship(
        "ClassificationSubstituent",
        back_populates="substituent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "SubstituentName",
            name="uq_substituents_substituent_name",
        ),
    )