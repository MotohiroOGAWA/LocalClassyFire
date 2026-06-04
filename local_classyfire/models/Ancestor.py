from __future__ import annotations

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Ancestor(Base):
    """Dictionary table for ClassyFire ancestor nodes."""

    __tablename__ = "Ancestor"

    ancestor_id: Mapped[int] = mapped_column(
        "AncestorID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        "Name",
        String(255),
        nullable=False,
    )

    classification_links = relationship(
        "ClassificationAncestor",
        back_populates="ancestor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="uq_ancestor_name",
        ),
    )