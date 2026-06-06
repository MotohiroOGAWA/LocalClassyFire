from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MolecularFramework(Base):
    """ClassyFire molecular framework.

    Examples
    --------
    Aromatic heteropolycyclic compounds
    """

    __tablename__ = "MolecularFramework"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_MolecularFramework_Name",
        ),
    )

    molecular_framework_id: Mapped[int] = mapped_column(
        "MolecularFrameworkID",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        "Name",
        String(255),
        nullable=False,
    )

    queries = relationship(
        "ClassyFireQuery",
        back_populates="molecular_framework",
    )