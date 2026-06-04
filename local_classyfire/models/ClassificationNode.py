from __future__ import annotations

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ClassificationNode(Base):
    """Dictionary table for ClassyFire classification nodes.

    This table is not directly linked by foreign keys from Classification.
    Classification rows can refer to this table logically by:
        ClassificationType + Name
    """

    __tablename__ = "ClassificationNode"

    classification_node_id: Mapped[int] = mapped_column(
        "ClassificationNodeID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    classification_type: Mapped[str] = mapped_column(
        "ClassificationType",
        String(50),
        nullable=False,
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

    __table_args__ = (
        UniqueConstraint(
            "ClassificationType",
            "Name",
            name="uq_classification_node_type_name",
        ),
    )