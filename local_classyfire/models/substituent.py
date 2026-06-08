from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Substituent(Base):
    """ClassyFire substituent name."""

    __tablename__ = "Substituent"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_Substituent_Name",
        ),
    )

    substituent_id: Mapped[int] = mapped_column(
        "SubstituentID",
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
        "SubstituentSetItem",
        back_populates="substituent",
        cascade="all, delete-orphan",
    )


class SubstituentSet(Base):
    """A reusable set of ClassyFire substituents."""

    __tablename__ = "SubstituentSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_SubstituentSet_SetHash",
        ),
    )

    substituent_set_id: Mapped[int] = mapped_column(
        "SubstituentSetID",
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
        "SubstituentSetItem",
        back_populates="substituent_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="substituent_set",
    )


class SubstituentSetItem(Base):
    """Link table between SubstituentSet and Substituent."""

    __tablename__ = "SubstituentSetItem"

    substituent_set_id: Mapped[int] = mapped_column(
        "SubstituentSetID",
        Integer,
        ForeignKey(
            "SubstituentSet.SubstituentSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    substituent_id: Mapped[int] = mapped_column(
        "SubstituentID",
        Integer,
        ForeignKey(
            "Substituent.SubstituentID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    substituent_set = relationship(
        "SubstituentSet",
        back_populates="items",
    )

    substituent = relationship(
        "Substituent",
        back_populates="set_items",
    )