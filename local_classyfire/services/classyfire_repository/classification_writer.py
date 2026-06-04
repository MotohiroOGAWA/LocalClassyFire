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
    """
    Write Classification and MolecularFramework.

    This class does not update ClassyFireQuery status.
    Query status is handled by ClassyFireQueryWriter.
    """

    @classmethod
    def upsert_classification(
        cls,
        session: Session,
        result: ClassyFireResult,
    ) -> Classification:
        classification = cls._get_or_create_classification(
            session=session,
            inchikey=result.inchikey,
        )

        molecular_framework = cls._get_or_create_molecular_framework(
            session=session,
            framework_name=result.molecular_framework,
        )

        update_existing_columns(
            classification,
            {
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
            },
            skip_none=False,
        )

        session.flush()

        return classification

    @staticmethod
    def _node_name(node: ClassificationNodeData | None) -> str | None:
        if node is None:
            return None

        return node.name

    @classmethod
    def _get_or_create_classification(
        cls,
        session: Session,
        inchikey: str,
    ) -> Classification:
        query = session.execute(
            select(ClassyFireQuery).where(
                ClassyFireQuery.inchikey == inchikey,
            )
        ).scalar_one_or_none()

        if query is not None and query.classification is not None:
            return query.classification

        classification = Classification()
        session.add(classification)
        session.flush()

        return classification

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
        )