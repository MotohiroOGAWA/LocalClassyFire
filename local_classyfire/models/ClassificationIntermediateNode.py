from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassificationIntermediateNode(Base):
    """Association table between Classification and IntermediateNode."""

    __tablename__ = "ClassificationIntermediateNode"

    classification_id: Mapped[int] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey("Classification.ClassificationID", ondelete="CASCADE"),
        primary_key=True,
    )

    intermediate_node_id: Mapped[int] = mapped_column(
        "IntermediateNodeID",
        Integer,
        ForeignKey("IntermediateNode.IntermediateNodeID", ondelete="CASCADE"),
        primary_key=True,
    )

    classification = relationship(
        "Classification",
        back_populates="intermediate_node_links",
    )

    intermediate_node = relationship(
        "IntermediateNode",
        back_populates="classification_links",
    )

    __table_args__ = (
        UniqueConstraint(
            "ClassificationID",
            "IntermediateNodeID",
            name="uq_classification_intermediate_node",
        ),
    )