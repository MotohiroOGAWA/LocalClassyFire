from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MolecularFramework(Base):
    """Dictionary table for molecular framework names."""

    __tablename__ = "MolecularFramework"

    molecular_framework_id: Mapped[int] = mapped_column(
        "MolecularFrameworkID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    framework_name: Mapped[str] = mapped_column(
        "FrameworkName",
        String(255),
        nullable=False,
    )

    classifications = relationship(
        "Classification",
        back_populates="molecular_framework",
    )

    __table_args__ = (
        UniqueConstraint(
            "FrameworkName",
            name="uq_molecular_framework_framework_name",
        ),
    )