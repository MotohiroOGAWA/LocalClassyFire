from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from collections.abc import Iterable
from typing import Any

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from ..models import (
    AlternativeParentSetItem,
    AncestorSetItem,
    ExternalDescriptorAnnotationLink,
    ExternalDescriptorSetItem,
    IntermediateNodeSetItem,
    PredictedChebiTermSetItem,
    PredictedLipidmapsTermSetItem,
    SubstituentSetItem,
)
from .classyfire_result import (
    ClassyFireResult,
    ExternalDescriptorData,
)
from .resolvers import (
    ExternalDescriptorKey,
    get_or_create_alternative_parent_ids,
    get_or_create_alternative_parent_set_ids,
    get_or_create_ancestor_ids,
    get_or_create_ancestor_set_ids,
    get_or_create_class_ids,
    get_or_create_direct_parent_ids,
    get_or_create_external_descriptor_annotation_ids,
    get_or_create_external_descriptor_ids,
    get_or_create_external_descriptor_set_ids,
    get_or_create_intermediate_node_ids,
    get_or_create_intermediate_node_set_ids,
    get_or_create_kingdom_ids,
    get_or_create_molecular_framework_ids,
    get_or_create_predicted_chebi_term_ids,
    get_or_create_predicted_chebi_term_set_ids,
    get_or_create_predicted_lipidmaps_term_ids,
    get_or_create_predicted_lipidmaps_term_set_ids,
    get_or_create_subclass_ids,
    get_or_create_substituent_ids,
    get_or_create_substituent_set_ids,
    get_or_create_superclass_ids,
    make_external_descriptor_key,
)


@dataclass(frozen=True)
class ResolvedExternalDescriptor:
    """Resolved external descriptor IDs."""

    external_descriptor_id: int
    annotation_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class ResolvedClassyFireResult:
    """ClassyFireResult with resolved database IDs."""

    inchikey: str
    smiles: str | None = None

    kingdom_id: int | None = None
    superclass_id: int | None = None
    class_id: int | None = None
    subclass_id: int | None = None
    direct_parent_id: int | None = None

    intermediate_node_ids: list[int] = field(default_factory=list)
    intermediate_node_set_id: int | None = None

    alternative_parent_ids: list[int] = field(default_factory=list)
    alternative_parent_set_id: int | None = None

    ancestor_ids: list[int] = field(default_factory=list)
    ancestor_set_id: int | None = None

    molecular_framework_id: int | None = None

    substituent_ids: list[int] = field(default_factory=list)
    substituent_set_id: int | None = None

    external_descriptors: list[ResolvedExternalDescriptor] = field(
        default_factory=list
    )
    external_descriptor_set_id: int | None = None

    predicted_chebi_term_ids: list[int] = field(default_factory=list)
    predicted_chebi_term_set_id: int | None = None

    predicted_lipidmaps_term_ids: list[int] = field(default_factory=list)
    predicted_lipidmaps_term_set_id: int | None = None

    description: str | None = None
    classification_version: str | None = None


class ClassyFireRepository:
    """Resolve ClassyFireResult objects into database IDs.

    This class does not create ClassyFireQuery directly.
    ClassyFireQueryRepository should call this class first, then use the
    resolved IDs to create ClassyFireQuery records.
    """

    @classmethod
    def resolve_results(
        cls,
        session: Session,
        results: list[ClassyFireResult],
        *,
        flush: bool = True,
    ) -> list[ResolvedClassyFireResult]:
        """Resolve IDs for multiple ClassyFireResult objects."""
        result_by_inchikey = cls._deduplicate_results_by_inchikey(results)

        if not result_by_inchikey:
            return []

        unique_results = list(result_by_inchikey.values())

        level_ids = cls._resolve_classification_level_ids(
            session=session,
            results=unique_results,
        )

        molecular_framework_ids = cls._resolve_molecular_framework_ids(
            session=session,
            results=unique_results,
        )

        intermediate = cls._resolve_intermediate_nodes(
            session=session,
            results=unique_results,
        )

        alternative = cls._resolve_alternative_parents(
            session=session,
            results=unique_results,
        )

        ancestors = cls._resolve_ancestors(
            session=session,
            results=unique_results,
        )

        substituents = cls._resolve_substituents(
            session=session,
            results=unique_results,
        )

        external_descriptors = cls._resolve_external_descriptors(
            session=session,
            results=unique_results,
        )

        predicted_chebi_terms = cls._resolve_predicted_chebi_terms(
            session=session,
            results=unique_results,
        )

        predicted_lipidmaps_terms = cls._resolve_predicted_lipidmaps_terms(
            session=session,
            results=unique_results,
        )

        resolved_results: list[ResolvedClassyFireResult] = []

        for result in unique_results:
            inchikey = result.inchikey.strip()

            resolved_results.append(
                ResolvedClassyFireResult(
                    inchikey=inchikey,
                    smiles=result.smiles,
                    kingdom_id=level_ids.kingdom_id_by_inchikey.get(
                        inchikey
                    ),
                    superclass_id=level_ids.superclass_id_by_inchikey.get(
                        inchikey
                    ),
                    class_id=level_ids.class_id_by_inchikey.get(inchikey),
                    subclass_id=level_ids.subclass_id_by_inchikey.get(
                        inchikey
                    ),
                    direct_parent_id=(
                        level_ids.direct_parent_id_by_inchikey.get(
                            inchikey
                        )
                    ),
                    molecular_framework_id=(
                        molecular_framework_ids.get(inchikey)
                    ),
                    intermediate_node_ids=(
                        intermediate.ids_by_inchikey.get(inchikey, [])
                    ),
                    intermediate_node_set_id=(
                        intermediate.set_id_by_inchikey.get(inchikey)
                    ),
                    alternative_parent_ids=(
                        alternative.ids_by_inchikey.get(inchikey, [])
                    ),
                    alternative_parent_set_id=(
                        alternative.set_id_by_inchikey.get(inchikey)
                    ),
                    ancestor_ids=ancestors.ids_by_inchikey.get(
                        inchikey, []
                    ),
                    ancestor_set_id=ancestors.set_id_by_inchikey.get(
                        inchikey
                    ),
                    substituent_ids=substituents.ids_by_inchikey.get(
                        inchikey, []
                    ),
                    substituent_set_id=(
                        substituents.set_id_by_inchikey.get(inchikey)
                    ),
                    external_descriptors=(
                        external_descriptors.descriptors_by_inchikey.get(
                            inchikey, []
                        )
                    ),
                    external_descriptor_set_id=(
                        external_descriptors.set_id_by_inchikey.get(
                            inchikey
                        )
                    ),
                    predicted_chebi_term_ids=(
                        predicted_chebi_terms.ids_by_inchikey.get(
                            inchikey, []
                        )
                    ),
                    predicted_chebi_term_set_id=(
                        predicted_chebi_terms.set_id_by_inchikey.get(
                            inchikey
                        )
                    ),
                    predicted_lipidmaps_term_ids=(
                        predicted_lipidmaps_terms.ids_by_inchikey.get(
                            inchikey, []
                        )
                    ),
                    predicted_lipidmaps_term_set_id=(
                        predicted_lipidmaps_terms.set_id_by_inchikey.get(
                            inchikey
                        )
                    ),
                    description=result.description,
                    classification_version=result.classification_version,
                )
            )

        if flush:
            session.flush()

        return resolved_results

    @staticmethod
    def _deduplicate_results_by_inchikey(
        results: list[ClassyFireResult],
    ) -> dict[str, ClassyFireResult]:
        result_by_inchikey: dict[str, ClassyFireResult] = {}

        for result in results:
            inchikey = result.inchikey.strip()

            if not inchikey:
                continue

            result_by_inchikey.setdefault(inchikey, result)

        return result_by_inchikey

    # ------------------------------------------------------------------
    # Classification levels
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_classification_level_ids(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedClassificationLevelIDs:
        kingdom_id_by_name = get_or_create_kingdom_ids(
            session=session,
            records=[result.kingdom for result in results],
        )

        superclass_id_by_name = get_or_create_superclass_ids(
            session=session,
            records=[result.superclass for result in results],
        )

        class_id_by_name = get_or_create_class_ids(
            session=session,
            records=[result.class_ for result in results],
        )

        subclass_id_by_name = get_or_create_subclass_ids(
            session=session,
            records=[result.subclass for result in results],
        )

        direct_parent_id_by_name = get_or_create_direct_parent_ids(
            session=session,
            records=[result.direct_parent for result in results],
        )

        return _ResolvedClassificationLevelIDs(
            kingdom_id_by_inchikey={
                result.inchikey: _get_level_id(
                    result.kingdom,
                    kingdom_id_by_name,
                )
                for result in results
            },
            superclass_id_by_inchikey={
                result.inchikey: _get_level_id(
                    result.superclass,
                    superclass_id_by_name,
                )
                for result in results
            },
            class_id_by_inchikey={
                result.inchikey: _get_level_id(
                    result.class_,
                    class_id_by_name,
                )
                for result in results
            },
            subclass_id_by_inchikey={
                result.inchikey: _get_level_id(
                    result.subclass,
                    subclass_id_by_name,
                )
                for result in results
            },
            direct_parent_id_by_inchikey={
                result.inchikey: _get_level_id(
                    result.direct_parent,
                    direct_parent_id_by_name,
                )
                for result in results
            },
        )

    # ------------------------------------------------------------------
    # Molecular framework
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_molecular_framework_ids(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> dict[str, int | None]:
        id_by_name = get_or_create_molecular_framework_ids(
            session=session,
            names=[result.molecular_framework for result in results],
        )

        return {
            result.inchikey: _get_id_from_name(
                result.molecular_framework,
                id_by_name,
            )
            for result in results
        }

    # ------------------------------------------------------------------
    # Node collections
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_intermediate_nodes(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        node_id_by_name = get_or_create_intermediate_node_ids(
            session=session,
            records=[
                node
                for result in results
                for node in result.intermediate_nodes
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                node_id_by_name[node.name.strip()]
                for node in result.intermediate_nodes
                if node.name.strip() in node_id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_intermediate_node_set_ids,
            item_model=IntermediateNodeSetItem,
            set_id_attr_name="intermediate_node_set_id",
            item_id_attr_name="intermediate_node_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    @classmethod
    def _resolve_alternative_parents(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        parent_id_by_name = get_or_create_alternative_parent_ids(
            session=session,
            records=[
                parent
                for result in results
                for parent in result.alternative_parents
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                parent_id_by_name[parent.name.strip()]
                for parent in result.alternative_parents
                if parent.name.strip() in parent_id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_alternative_parent_set_ids,
            item_model=AlternativeParentSetItem,
            set_id_attr_name="alternative_parent_set_id",
            item_id_attr_name="alternative_parent_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    @classmethod
    def _resolve_ancestors(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        ancestor_id_by_name = get_or_create_ancestor_ids(
            session=session,
            names=[
                ancestor
                for result in results
                for ancestor in result.ancestors
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                ancestor_id_by_name[ancestor.strip()]
                for ancestor in result.ancestors
                if ancestor.strip() in ancestor_id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_ancestor_set_ids,
            item_model=AncestorSetItem,
            set_id_attr_name="ancestor_set_id",
            item_id_attr_name="ancestor_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    # ------------------------------------------------------------------
    # Term collections
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_substituents(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        id_by_name = get_or_create_substituent_ids(
            session=session,
            names=[
                substituent
                for result in results
                for substituent in result.substituents
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                id_by_name[name.strip()]
                for name in result.substituents
                if name.strip() in id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_substituent_set_ids,
            item_model=SubstituentSetItem,
            set_id_attr_name="substituent_set_id",
            item_id_attr_name="substituent_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    @classmethod
    def _resolve_predicted_chebi_terms(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        id_by_name = get_or_create_predicted_chebi_term_ids(
            session=session,
            names=[
                term
                for result in results
                for term in result.predicted_chebi_terms
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                id_by_name[name.strip()]
                for name in result.predicted_chebi_terms
                if name.strip() in id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_predicted_chebi_term_set_ids,
            item_model=PredictedChebiTermSetItem,
            set_id_attr_name="predicted_chebi_term_set_id",
            item_id_attr_name="predicted_chebi_term_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    @classmethod
    def _resolve_predicted_lipidmaps_terms(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedSetIDs:
        id_by_name = get_or_create_predicted_lipidmaps_term_ids(
            session=session,
            names=[
                term
                for result in results
                for term in result.predicted_lipidmaps_terms
            ],
        )

        ids_by_inchikey = {
            result.inchikey: [
                id_by_name[name.strip()]
                for name in result.predicted_lipidmaps_terms
                if name.strip() in id_by_name
            ]
            for result in results
        }

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=ids_by_inchikey,
            get_or_create_set_ids=get_or_create_predicted_lipidmaps_term_set_ids,
            item_model=PredictedLipidmapsTermSetItem,
            set_id_attr_name="predicted_lipidmaps_term_set_id",
            item_id_attr_name="predicted_lipidmaps_term_id",
        )

        return _ResolvedSetIDs(
            ids_by_inchikey=ids_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    # ------------------------------------------------------------------
    # External descriptors
    # ------------------------------------------------------------------

    @classmethod
    def _resolve_external_descriptors(
        cls,
        session: Session,
        results: list[ClassyFireResult],
    ) -> _ResolvedExternalDescriptorSetIDs:
        descriptor_key_by_object_id: dict[int, ExternalDescriptorKey] = {}
        annotations_by_key: dict[ExternalDescriptorKey, list[str]] = {}

        for result in results:
            for descriptor in result.external_descriptors:
                annotation_hash = make_string_set_hash(
                    descriptor.annotations
                )

                if annotation_hash is None:
                    annotation_hash = make_string_set_hash([])

                key = make_external_descriptor_key(
                    source=descriptor.source,
                    source_id=descriptor.source_id,
                    annotation_hash=annotation_hash,
                )

                if key is None:
                    continue

                descriptor_key_by_object_id[id(descriptor)] = key
                annotations_by_key[key] = descriptor.annotations

        descriptor_id_by_key = get_or_create_external_descriptor_ids(
            session=session,
            keys=descriptor_key_by_object_id.values(),
        )

        annotation_id_by_name = get_or_create_external_descriptor_annotation_ids(
            session=session,
            annotations=[
                annotation
                for annotations in annotations_by_key.values()
                for annotation in annotations
            ],
        )

        cls._ensure_external_descriptor_annotation_links(
            session=session,
            descriptor_id_by_key=descriptor_id_by_key,
            annotations_by_key=annotations_by_key,
            annotation_id_by_name=annotation_id_by_name,
        )

        descriptors_by_inchikey: dict[str, list[ResolvedExternalDescriptor]] = {}

        descriptor_ids_by_inchikey: dict[str, list[int]] = {}

        for result in results:
            resolved_descriptors: list[ResolvedExternalDescriptor] = []
            descriptor_ids: list[int] = []

            for descriptor in result.external_descriptors:
                key = descriptor_key_by_object_id.get(id(descriptor))

                if key is None:
                    continue

                descriptor_id = descriptor_id_by_key.get(key)

                if descriptor_id is None:
                    continue

                annotation_ids = [
                    annotation_id_by_name[annotation.strip()]
                    for annotation in descriptor.annotations
                    if annotation.strip() in annotation_id_by_name
                ]

                resolved_descriptors.append(
                    ResolvedExternalDescriptor(
                        external_descriptor_id=descriptor_id,
                        annotation_ids=annotation_ids,
                    )
                )
                descriptor_ids.append(descriptor_id)

            descriptors_by_inchikey[result.inchikey] = resolved_descriptors
            descriptor_ids_by_inchikey[result.inchikey] = descriptor_ids

        set_id_by_inchikey = cls._create_sets_and_items(
            session=session,
            ids_by_inchikey=descriptor_ids_by_inchikey,
            get_or_create_set_ids=get_or_create_external_descriptor_set_ids,
            item_model=ExternalDescriptorSetItem,
            set_id_attr_name="external_descriptor_set_id",
            item_id_attr_name="external_descriptor_id",
        )

        return _ResolvedExternalDescriptorSetIDs(
            descriptors_by_inchikey=descriptors_by_inchikey,
            set_id_by_inchikey=set_id_by_inchikey,
        )

    @classmethod
    def _ensure_external_descriptor_annotation_links(
        cls,
        session: Session,
        *,
        descriptor_id_by_key: dict[ExternalDescriptorKey, int],
        annotations_by_key: dict[ExternalDescriptorKey, list[str]],
        annotation_id_by_name: dict[str, int],
    ) -> None:
        pairs: set[tuple[int, int]] = set()

        for key, descriptor_id in descriptor_id_by_key.items():
            for annotation in annotations_by_key.get(key, []):
                annotation_id = annotation_id_by_name.get(annotation.strip())

                if annotation_id is None:
                    continue

                pairs.add((descriptor_id, annotation_id))

        cls._ensure_pair_links(
            session=session,
            item_model=ExternalDescriptorAnnotationLink,
            left_attr_name="external_descriptor_id",
            right_attr_name="external_descriptor_annotation_id",
            pairs=pairs,
        )

    # ------------------------------------------------------------------
    # Generic set item creation
    # ------------------------------------------------------------------

    @classmethod
    def _create_sets_and_items(
        cls,
        session: Session,
        *,
        ids_by_inchikey: dict[str, list[int]],
        get_or_create_set_ids,
        item_model: type[Any],
        set_id_attr_name: str,
        item_id_attr_name: str,
    ) -> dict[str, int | None]:
        hash_by_inchikey = {
            inchikey: make_id_set_hash(ids)
            for inchikey, ids in ids_by_inchikey.items()
        }

        set_id_by_hash = get_or_create_set_ids(
            session=session,
            set_hashes=[
                set_hash
                for set_hash in hash_by_inchikey.values()
                if set_hash is not None
            ],
        )

        set_id_by_inchikey = {
            inchikey: (
                set_id_by_hash.get(set_hash)
                if set_hash is not None
                else None
            )
            for inchikey, set_hash in hash_by_inchikey.items()
        }

        pairs: set[tuple[int, int]] = set()

        for inchikey, item_ids in ids_by_inchikey.items():
            set_id = set_id_by_inchikey.get(inchikey)

            if set_id is None:
                continue

            for item_id in set(item_ids):
                pairs.add((set_id, item_id))

        cls._ensure_pair_links(
            session=session,
            item_model=item_model,
            left_attr_name=set_id_attr_name,
            right_attr_name=item_id_attr_name,
            pairs=pairs,
        )

        return set_id_by_inchikey

    @staticmethod
    def _ensure_pair_links(
        session: Session,
        *,
        item_model: type[Any],
        left_attr_name: str,
        right_attr_name: str,
        pairs: set[tuple[int, int]],
    ) -> None:
        if not pairs:
            return

        left_column = getattr(item_model, left_attr_name)
        right_column = getattr(item_model, right_attr_name)

        stmt = select(left_column, right_column).where(
            tuple_(left_column, right_column).in_(list(pairs))
        )

        existing_pairs = {
            (left_id, right_id)
            for left_id, right_id in session.execute(stmt).all()
        }

        missing_pairs = pairs - existing_pairs

        if not missing_pairs:
            return

        session.add_all(
            [
                item_model(
                    **{
                        left_attr_name: left_id,
                        right_attr_name: right_id,
                    }
                )
                for left_id, right_id in missing_pairs
            ]
        )


@dataclass(frozen=True)
class _ResolvedClassificationLevelIDs:
    kingdom_id_by_inchikey: dict[str, int | None]
    superclass_id_by_inchikey: dict[str, int | None]
    class_id_by_inchikey: dict[str, int | None]
    subclass_id_by_inchikey: dict[str, int | None]
    direct_parent_id_by_inchikey: dict[str, int | None]


@dataclass(frozen=True)
class _ResolvedSetIDs:
    ids_by_inchikey: dict[str, list[int]]
    set_id_by_inchikey: dict[str, int | None]


@dataclass(frozen=True)
class _ResolvedExternalDescriptorSetIDs:
    descriptors_by_inchikey: dict[str, list[ResolvedExternalDescriptor]]
    set_id_by_inchikey: dict[str, int | None]


def _get_level_id(
    level,
    id_by_name: dict[str, int],
) -> int | None:
    if level is None:
        return None

    return _get_id_from_name(level.name, id_by_name)


def _get_id_from_name(
    name: str | None,
    id_by_name: dict[str, int],
) -> int | None:
    if name is None:
        return None

    normalized_name = name.strip()

    if not normalized_name:
        return None

    return id_by_name.get(normalized_name)


def make_id_set_hash(
    ids: Iterable[int],
) -> str | None:
    unique_sorted_ids = sorted(set(ids))

    if not unique_sorted_ids:
        return None

    payload_json = json.dumps(
        unique_sorted_ids,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()


def make_string_set_hash(
    values: Iterable[str],
) -> str | None:
    unique_sorted_values = sorted(
        {
            value.strip()
            for value in values
            if value and value.strip()
        }
    )

    if not unique_sorted_values:
        return None

    payload_json = json.dumps(
        unique_sorted_values,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()