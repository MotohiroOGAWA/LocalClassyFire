from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class IntermediateNode(Base):
    """ClassyFire intermediate node."""

    __tablename__ = "IntermediateNode"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_IntermediateNode_Name",
        ),
    )

    intermediate_node_id: Mapped[int] = mapped_column(
        "IntermediateNodeID",
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
        "IntermediateNodeSetItem",
        back_populates="intermediate_node",
        cascade="all, delete-orphan",
    )


class IntermediateNodeSet(Base):
    """A reusable set of intermediate nodes."""

    __tablename__ = "IntermediateNodeSet"

    __table_args__ = (
        UniqueConstraint(
            "SetHash",
            name="UQ_IntermediateNodeSet_SetHash",
        ),
    )

    intermediate_node_set_id: Mapped[int] = mapped_column(
        "IntermediateNodeSetID",
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
        "IntermediateNodeSetItem",
        back_populates="intermediate_node_set",
        cascade="all, delete-orphan",
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="intermediate_node_set",
    )


class IntermediateNodeSetItem(Base):
    """Link table between IntermediateNodeSet and IntermediateNode."""

    __tablename__ = "IntermediateNodeSetItem"

    intermediate_node_set_id: Mapped[int] = mapped_column(
        "IntermediateNodeSetID",
        Integer,
        ForeignKey(
            "IntermediateNodeSet.IntermediateNodeSetID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    intermediate_node_id: Mapped[int] = mapped_column(
        "IntermediateNodeID",
        Integer,
        ForeignKey(
            "IntermediateNode.IntermediateNodeID",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    intermediate_node_set = relationship(
        "IntermediateNodeSet",
        back_populates="items",
    )

    intermediate_node = relationship(
        "IntermediateNode",
        back_populates="set_items",
    )