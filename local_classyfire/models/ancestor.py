from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Ancestor(Base):
    """ClassyFire ancestor name."""

    __tablename__ = "Ancestor"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_Ancestor_Name",
        ),
    )

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

    set_items = relationship(
        "AncestorSetItem",
        back_populates="ancestor",
        cascade="all, delete-orphan",
    )


class AncestorSet(Base):
    """A reusable set of ClassyFire ancestors."""

    __tablename__ = "AncestorSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_AncestorSet_SetHash",
        ),
    )

    ancestor_set_id: Mapped[int] = mapped_column(
        "AncestorSetID",
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
        "AncestorSetItem",
        back_populates="ancestor_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="ancestor_set",
    )


class AncestorSetItem(Base):
    """Link table between AncestorSet and Ancestor."""

    __tablename__ = "AncestorSetItem"

    ancestor_set_id: Mapped[int] = mapped_column(
        "AncestorSetID",
        Integer,
        ForeignKey(
            "AncestorSet.AncestorSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    ancestor_id: Mapped[int] = mapped_column(
        "AncestorID",
        Integer,
        ForeignKey(
            "Ancestor.AncestorID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    ancestor_set = relationship(
        "AncestorSet",
        back_populates="items",
    )

    ancestor = relationship(
        "Ancestor",
        back_populates="set_items",
    )