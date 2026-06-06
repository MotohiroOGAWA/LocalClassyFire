from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClassyFireQuery(Base):
    """Successful ClassyFire query result for one InChIKey.

    This table stores only successfully found ClassyFire results.
    Missing or failed queries are stored in ClassyFireMissingQuery.
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
        String(27),
        nullable=False,
        unique=True,
        index=True,
    )

    smiles: Mapped[str | None] = mapped_column(
        "SMILES",
        Text,
        nullable=True,
    )

    kingdom_id: Mapped[int | None] = mapped_column(
        "KingdomID",
        Integer,
        ForeignKey(
            "ClassyFireKingdom.ClassyFireKingdomID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    superclass_id: Mapped[int | None] = mapped_column(
        "SuperclassID",
        Integer,
        ForeignKey(
            "ClassyFireSuperclass.ClassyFireSuperclassID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    class_id: Mapped[int | None] = mapped_column(
        "ClassID",
        Integer,
        ForeignKey(
            "ClassyFireClass.ClassyFireClassID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    subclass_id: Mapped[int | None] = mapped_column(
        "SubclassID",
        Integer,
        ForeignKey(
            "ClassyFireSubclass.ClassyFireSubclassID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    direct_parent_id: Mapped[int | None] = mapped_column(
        "DirectParentID",
        Integer,
        ForeignKey(
            "ClassyFireDirectParent.ClassyFireDirectParentID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    intermediate_node_set_id: Mapped[int | None] = mapped_column(
        "IntermediateNodeSetID",
        Integer,
        ForeignKey(
            "IntermediateNodeSet.IntermediateNodeSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    alternative_parent_set_id: Mapped[int | None] = mapped_column(
        "AlternativeParentSetID",
        Integer,
        ForeignKey(
            "AlternativeParentSet.AlternativeParentSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    ancestor_set_id: Mapped[int | None] = mapped_column(
        "AncestorSetID",
        Integer,
        ForeignKey(
            "AncestorSet.AncestorSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    molecular_framework_id: Mapped[int | None] = mapped_column(
        "MolecularFrameworkID",
        Integer,
        ForeignKey(
            "MolecularFramework.MolecularFrameworkID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    substituent_set_id: Mapped[int | None] = mapped_column(
        "SubstituentSetID",
        Integer,
        ForeignKey(
            "SubstituentSet.SubstituentSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    external_descriptor_set_id: Mapped[int | None] = mapped_column(
        "ExternalDescriptorSetID",
        Integer,
        ForeignKey(
            "ExternalDescriptorSet.ExternalDescriptorSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    predicted_chebi_term_set_id: Mapped[int | None] = mapped_column(
        "PredictedChebiTermSetID",
        Integer,
        ForeignKey(
            "PredictedChebiTermSet.PredictedChebiTermSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    predicted_lipidmaps_term_set_id: Mapped[int | None] = mapped_column(
        "PredictedLipidmapsTermSetID",
        Integer,
        ForeignKey(
            "PredictedLipidmapsTermSet.PredictedLipidmapsTermSetID",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        "Description",
        Text,
        nullable=True,
    )

    classification_version: Mapped[str | None] = mapped_column(
        "ClassificationVersion",
        String(255),
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

    kingdom = relationship(
        "ClassyFireKingdom",
        back_populates="queries",
    )

    superclass = relationship(
        "ClassyFireSuperclass",
        back_populates="queries",
    )

    classyfire_class = relationship(
        "ClassyFireClass",
        back_populates="queries",
    )

    subclass = relationship(
        "ClassyFireSubclass",
        back_populates="queries",
    )

    direct_parent = relationship(
        "ClassyFireDirectParent",
        back_populates="queries",
    )

    intermediate_node_set = relationship(
        "IntermediateNodeSet",
        back_populates="queries",
    )

    alternative_parent_set = relationship(
        "AlternativeParentSet",
        back_populates="queries",
    )

    ancestor_set = relationship(
        "AncestorSet",
        back_populates="queries",
    )

    molecular_framework = relationship(
        "MolecularFramework",
        back_populates="queries",
    )

    substituent_set = relationship(
        "SubstituentSet",
        back_populates="queries",
    )

    external_descriptor_set = relationship(
        "ExternalDescriptorSet",
        back_populates="queries",
    )

    predicted_chebi_term_set = relationship(
        "PredictedChebiTermSet",
        back_populates="queries",
    )

    predicted_lipidmaps_term_set = relationship(
        "PredictedLipidmapsTermSet",
        back_populates="queries",
    )