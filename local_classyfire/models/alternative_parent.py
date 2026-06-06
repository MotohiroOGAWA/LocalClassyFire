from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AlternativeParent(Base):
    """ClassyFire alternative parent."""

    __tablename__ = "AlternativeParent"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_AlternativeParent_Name",
        ),
    )

    alternative_parent_id: Mapped[int] = mapped_column(
        "AlternativeParentID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        "Name",
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        "Description",
        Text,
        nullable=True,
    )

    chemont_id: Mapped[str | None] = mapped_column(
        "ChemOntID",
        String(255),
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        "URL",
        Text,
        nullable=True,
    )

    set_items = relationship(
        "AlternativeParentSetItem",
        back_populates="alternative_parent",
        cascade="all, delete-orphan",
    )


class AlternativeParentSet(Base):
    """A reusable set of alternative parents."""

    __tablename__ = "AlternativeParentSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_AlternativeParentSet_SetHash",
        ),
    )

    alternative_parent_set_id: Mapped[int] = mapped_column(
        "AlternativeParentSetID",
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
        "AlternativeParentSetItem",
        back_populates="alternative_parent_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="alternative_parent_set",
    )


class AlternativeParentSetItem(Base):
    """Link table between AlternativeParentSet and AlternativeParent."""

    __tablename__ = "AlternativeParentSetItem"

    alternative_parent_set_id: Mapped[int] = mapped_column(
        "AlternativeParentSetID",
        Integer,
        ForeignKey(
            "AlternativeParentSet.AlternativeParentSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    alternative_parent_id: Mapped[int] = mapped_column(
        "AlternativeParentID",
        Integer,
        ForeignKey(
            "AlternativeParent.AlternativeParentID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    alternative_parent_set = relationship(
        "AlternativeParentSet",
        back_populates="items",
    )

    alternative_parent = relationship(
        "AlternativeParent",
        back_populates="set_items",
    )