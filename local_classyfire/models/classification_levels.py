from __future__ import annotations

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassyFireKingdom(Base):
    """ClassyFire kingdom."""

    __tablename__ = "ClassyFireKingdom"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_ClassyFireKingdom_Name",
        ),
    )

    classyfire_kingdom_id: Mapped[int] = mapped_column(
        "ClassyFireKingdomID",
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

    queries = relationship(
        "ClassyFireQuery",
        back_populates="kingdom",
    )


class ClassyFireSuperclass(Base):
    """ClassyFire superclass."""

    __tablename__ = "ClassyFireSuperclass"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_ClassyFireSuperclass_Name",
        ),
    )

    classyfire_superclass_id: Mapped[int] = mapped_column(
        "ClassyFireSuperclassID",
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

    queries = relationship(
        "ClassyFireQuery",
        back_populates="superclass",
    )


class ClassyFireClass(Base):
    """ClassyFire class."""

    __tablename__ = "ClassyFireClass"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_ClassyFireClass_Name",
        ),
    )

    classyfire_class_id: Mapped[int] = mapped_column(
        "ClassyFireClassID",
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

    queries = relationship(
        "ClassyFireQuery",
        back_populates="classyfire_class",
    )


class ClassyFireSubclass(Base):
    """ClassyFire subclass."""

    __tablename__ = "ClassyFireSubclass"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_ClassyFireSubclass_Name",
        ),
    )

    classyfire_subclass_id: Mapped[int] = mapped_column(
        "ClassyFireSubclassID",
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

    queries = relationship(
        "ClassyFireQuery",
        back_populates="subclass",
    )


class ClassyFireDirectParent(Base):
    """ClassyFire direct parent."""

    __tablename__ = "ClassyFireDirectParent"

    __table_args__ = (
        UniqueConstraint(
            "Name",
            name="UQ_ClassyFireDirectParent_Name",
        ),
    )

    classyfire_direct_parent_id: Mapped[int] = mapped_column(
        "ClassyFireDirectParentID",
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

    queries = relationship(
        "ClassyFireQuery",
        back_populates="direct_parent",
    )