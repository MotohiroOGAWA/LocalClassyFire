from __future__ import annotations

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class IntermediateNode(Base):
    """Dictionary table for ClassyFire intermediate nodes."""

    __tablename__ = "IntermediateNode"

    intermediate_node_id: Mapped[int] = mapped_column(
        "IntermediateNodeID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    node_name: Mapped[str] = mapped_column(
        "NodeName",
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

    classification_links = relationship(
        "ClassificationIntermediateNode",
        back_populates="intermediate_node",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "NodeName",
            name="uq_intermediate_nodes_node_name",
        ),
    )