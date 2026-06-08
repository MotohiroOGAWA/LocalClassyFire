from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ClassyFireMissingQuery(Base):
    """Missing or failed ClassyFire query record.

    This table stores InChIKeys that could not be converted into a
    successful ClassyFireQuery record.

    Examples
    --------
    - ClassyFire returned no result.
    - The API request failed.
    - The response could not be parsed.
    """

    __tablename__ = "ClassyFireMissingQuery"

    __table_args__ = (
        UniqueConstraint(
            "InChIKey",
            name="UQ_ClassyFireMissingQuery_InChIKey",
        ),
    )

    classyfire_missing_query_id: Mapped[int] = mapped_column(
        "ClassyFireMissingQueryID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    inchikey: Mapped[str] = mapped_column(
        "InChIKey",
        String(27),
        nullable=False,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(
        "Reason",
        String(255),
        nullable=True,
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
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )