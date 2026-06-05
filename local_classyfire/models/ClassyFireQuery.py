from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Boolean, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .Classification import Classification


class ClassyFireQuery(Base):
    """Cache table for ClassyFire query results by InChIKey.

    This table stores both successful and failed ClassyFire queries.
    """

    __tablename__ = "ClassyFireQuery"

    classyfire_query_id: Mapped[int] = mapped_column(
        "ClassyFireQueryID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    inchikey: Mapped[str] = mapped_column(
        "InChIKey",
        String(255),
        nullable=False,
    )

    smiles: Mapped[str | None] = mapped_column(
        "SMILES",
        Text,
        nullable=True,
    )

    classification_id: Mapped[int | None] = mapped_column(
        "ClassificationID",
        Integer,
        ForeignKey(
            "Classification.ClassificationID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    is_found: Mapped[bool] = mapped_column(
        "IsFound",
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    message: Mapped[str | None] = mapped_column(
        "Message",
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    classification: Mapped["Classification | None"] = relationship(
        "Classification",
        back_populates="queries",
    )

    __table_args__ = (
        UniqueConstraint(
            "InChIKey",
            name="uq_classyfire_query_inchikey",
        ),
    )