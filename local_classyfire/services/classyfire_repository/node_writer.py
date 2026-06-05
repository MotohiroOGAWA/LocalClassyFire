from __future__ import annotations

from sqlalchemy.orm import Session

from local_classyfire.models import (
    AlternativeParent,
    Ancestor,
    Classification,
    ClassificationAlternativeParent,
    ClassificationAncestor,
    ClassificationIntermediateNode,
    ClassificationNode,
    IntermediateNode,
)
from local_classyfire.services.classyfire_result import (
    ClassificationNodeData,
    ClassyFireResult,
)

from .utils import get_or_create, replace_relationship_items, update_existing_columns


class NodeWriter:
    @classmethod
    def replace_all_nodes(
        cls,
        session: Session,
        classification: Classification,
        *,
        intermediate_nodes: list[ClassificationNodeData],
        alternative_parents: list[ClassificationNodeData],
        ancestors: list[ClassificationNodeData],
    ) -> None:
        cls.replace_intermediate_nodes(
            session=session,
            classification=classification,
            nodes=intermediate_nodes,
        )

        cls.replace_alternative_parents(
            session=session,
            classification=classification,
            nodes=alternative_parents,
        )

        cls.replace_ancestors(
            session=session,
            classification=classification,
            nodes=ancestors,
        )

    @classmethod
    def replace_intermediate_nodes(
        cls,
        session: Session,
        classification: Classification,
        nodes: list[ClassificationNodeData],
    ) -> None:
        links: list[ClassificationIntermediateNode] = []

        for sort_order, node in enumerate(nodes):
            stored_node = cls._get_or_create_intermediate_node(
                session=session,
                node=node,
            )

            link = ClassificationIntermediateNode(
                classification_id=classification.classification_id,
                intermediate_node_id=stored_node.intermediate_node_id,
            )

            update_existing_columns(
                link,
                {"sort_order": sort_order},
                skip_none=False,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="intermediate_node_links",
            new_items=links,
        )

    @classmethod
    def replace_alternative_parents(
        cls,
        session: Session,
        classification: Classification,
        nodes: list[ClassificationNodeData],
    ) -> None:
        links: list[ClassificationAlternativeParent] = []

        for sort_order, node in enumerate(nodes):
            stored_node = cls._get_or_create_alternative_parent(
                session=session,
                node=node,
            )

            link = ClassificationAlternativeParent(
                classification_id=classification.classification_id,
                alternative_parent_id=stored_node.alternative_parent_id,
            )

            update_existing_columns(
                link,
                {"sort_order": sort_order},
                skip_none=False,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="alternative_parent_links",
            new_items=links,
        )

    @classmethod
    def replace_ancestors(
        cls,
        session: Session,
        classification: Classification,
        nodes: list[ClassificationNodeData],
    ) -> None:
        links: list[ClassificationAncestor] = []

        for sort_order, node in enumerate(nodes):
            stored_node = cls._get_or_create_ancestor(
                session=session,
                node=node,
            )

            link = ClassificationAncestor(
                classification_id=classification.classification_id,
                ancestor_id=stored_node.ancestor_id,
            )

            update_existing_columns(
                link,
                {"sort_order": sort_order},
                skip_none=False,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="ancestor_links",
            new_items=links,
        )

    @classmethod
    def _get_or_create_intermediate_node(
        cls,
        session: Session,
        node: ClassificationNodeData,
    ) -> IntermediateNode:
        return get_or_create(
            session=session,
            model=IntermediateNode,
            lookup={"node_name": node.name},
            defaults={
                "description": node.description,
                "chemont_id": node.chemont_id,
                "url": node.url,
            },
        )

    @classmethod
    def _get_or_create_alternative_parent(
        cls,
        session: Session,
        node: ClassificationNodeData,
    ) -> AlternativeParent:
        return get_or_create(
            session=session,
            model=AlternativeParent,
            lookup={"parent_name": node.name},
            defaults={
                "description": node.description,
                "chemont_id": node.chemont_id,
                "url": node.url,
            },
        )

    @classmethod
    def _get_or_create_ancestor(
        cls,
        session: Session,
        node: ClassificationNodeData,
    ) -> Ancestor:
        return get_or_create(
            session=session,
            model=Ancestor,
            lookup={"name": node},
        )
    
    @classmethod
    def upsert_classification_nodes_from_result(
        cls,
        session: Session,
        result: ClassyFireResult,
    ) -> None:
        """Store all classification nodes into ClassificationNode dictionary table."""

        cls._get_or_create_classification_node(
            session=session,
            classification_type="kingdom",
            node=result.kingdom,
        )
        cls._get_or_create_classification_node(
            session=session,
            classification_type="superclass",
            node=result.superclass,
        )
        cls._get_or_create_classification_node(
            session=session,
            classification_type="class",
            node=result.class_node,
        )
        cls._get_or_create_classification_node(
            session=session,
            classification_type="subclass",
            node=result.subclass,
        )
        cls._get_or_create_classification_node(
            session=session,
            classification_type="direct_parent",
            node=result.direct_parent,
        )

    @classmethod
    def _get_or_create_classification_node(
        cls,
        session: Session,
        classification_type: str,
        node: ClassificationNodeData | None,
    ) -> ClassificationNode | None:
        if node is None:
            return None

        return get_or_create(
            session=session,
            model=ClassificationNode,
            lookup={
                "classification_type": classification_type,
                "name": node.name,
            },
            defaults={
                "description": node.description,
                "chemont_id": node.chemont_id,
                "url": node.url,
            },
        )