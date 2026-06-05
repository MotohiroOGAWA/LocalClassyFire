from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import (
    Classification,
    ClassyFireQuery,
    MolecularFramework,
)
from local_classyfire.services.classyfire_result import (
    ClassificationNodeData,
    ClassyFireResult,
)

from .utils import get_or_create, update_existing_columns


class ClassificationWriter:
    """Write Classification and MolecularFramework."""

    @classmethod
    def upsert_classification(
        cls,
        session: Session,
        result: ClassyFireResult,
    ) -> Classification:
        existing_classification = cls._get_existing_classification(
            session=session,
            inchikey=result.inchikey,
        )

        molecular_framework = cls._get_or_create_molecular_framework(
            session=session,
            framework_name=result.molecular_framework,
        )

        values = {
            "kingdom": cls._node_name(result.kingdom),
            "superclass": cls._node_name(result.superclass),
            "class_name": cls._node_name(result.class_node),
            "subclass": cls._node_name(result.subclass),
            "direct_parent": cls._node_name(result.direct_parent),
            "molecular_framework_id": (
                molecular_framework.molecular_framework_id
                if molecular_framework is not None
                else None
            ),
            "description": result.description,
            "classification_version": result.classification_version,
        }

        if existing_classification is not None:
            update_existing_columns(
                existing_classification,
                values,
                skip_none=False,
            )
            session.flush()
            return existing_classification

        classification = Classification(**values)
        session.add(classification)
        session.flush()

        return classification

    @classmethod
    def _get_existing_classification(
        cls,
        session: Session,
        inchikey: str,
    ) -> Classification | None:
        query = session.execute(
            select(ClassyFireQuery).where(
                ClassyFireQuery.inchikey == inchikey,
            )
        ).scalar_one_or_none()

        if query is None:
            return None

        return query.classification

    @classmethod
    def _get_or_create_molecular_framework(
        cls,
        session: Session,
        framework_name: str | None,
    ) -> MolecularFramework | None:
        if not framework_name:
            return None

        return get_or_create(
            session=session,
            model=MolecularFramework,
            lookup={"framework_name": framework_name},
            create_values={"framework_name": framework_name},
        )

    @staticmethod
    def _node_name(node: ClassificationNodeData | None) -> str | None:
        if node is None:
            return None

        return node.name