from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClassificationNodeData:
    """One ClassyFire classification node.

    Examples
    --------
    kingdom, superclass, class, subclass, direct_parent
    """

    name: str
    description: str | None = None
    chemont_id: str | None = None
    url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ClassificationNodeData | None:
        if not data:
            return None

        name = data.get("name")
        if not name:
            return None

        return cls(
            name=name,
            description=data.get("description"),
            chemont_id=data.get("chemont_id"),
            url=data.get("url"),
        )


@dataclass(frozen=True)
class ExternalDescriptorData:
    """External descriptor returned by ClassyFire."""

    source: str
    source_id: str
    annotations: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExternalDescriptorData | None:
        source = data.get("source")
        source_id = data.get("source_id")

        if not source or not source_id:
            return None

        annotations = data.get("annotations") or []

        return cls(
            source=source,
            source_id=source_id,
            annotations=[
                annotation
                for annotation in annotations
                if isinstance(annotation, str) and annotation
            ],
        )

@dataclass(frozen=True)
class ClassyFireResult:
    """Parsed ClassyFire API result for one InChIKey."""

    inchikey: str
    smiles: str | None = None

    kingdom: ClassificationNodeData | None = None
    superclass: ClassificationNodeData | None = None
    class_node: ClassificationNodeData | None = None
    subclass: ClassificationNodeData | None = None
    direct_parent: ClassificationNodeData | None = None

    intermediate_nodes: list[ClassificationNodeData] = field(default_factory=list)
    alternative_parents: list[ClassificationNodeData] = field(default_factory=list)
    ancestors: list[str] = field(default_factory=list)

    molecular_framework: str | None = None
    substituents: list[str] = field(default_factory=list)

    external_descriptors: list[ExternalDescriptorData] = field(default_factory=list)

    predicted_chebi_terms: list[str] = field(default_factory=list)
    predicted_lipidmaps_terms: list[str] = field(default_factory=list)

    description: str | None = None
    classification_version: str | None = None

    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_json(
        cls,
        inchikey: str,
        data: dict[str, Any],
    ) -> ClassyFireResult:
        """Create ClassyFireResult from raw ClassyFire API JSON."""
        smiles_value = data.get("smiles")

        return cls(
            inchikey=inchikey,
            smiles=smiles_value,

            kingdom=ClassificationNodeData.from_dict(data.get("kingdom")),
            superclass=ClassificationNodeData.from_dict(data.get("superclass")),
            class_node=ClassificationNodeData.from_dict(data.get("class")),
            subclass=ClassificationNodeData.from_dict(data.get("subclass")),
            direct_parent=ClassificationNodeData.from_dict(data.get("direct_parent")),

            intermediate_nodes=[
                node
                for node in (
                    ClassificationNodeData.from_dict(item)
                    for item in _as_dict_list(data.get("intermediate_nodes"))
                )
                if node is not None
            ],
            alternative_parents=[
                node
                for node in (
                    ClassificationNodeData.from_dict(item)
                    for item in _as_dict_list(data.get("alternative_parents"))
                )
                if node is not None
            ],
            ancestors=_as_str_list(
                data.get("ancestors")
            ),

            molecular_framework=data.get("molecular_framework"),
            substituents=_as_str_list(data.get("substituents")),

            external_descriptors=[
                descriptor
                for descriptor in (
                    ExternalDescriptorData.from_dict(item)
                    for item in _as_dict_list(data.get("external_descriptors"))
                )
                if descriptor is not None
            ],

            predicted_chebi_terms=_as_str_list(data.get("predicted_chebi_terms")),
            predicted_lipidmaps_terms=_as_str_list(
                data.get("predicted_lipidmaps_terms")
            ),

            description=data.get("description"),
            classification_version=data.get("classification_version"),
            raw_data=data,
        )


def _extract_first_inchi(data: dict[str, Any]) -> str | None:
    inchis = data.get("inchis")

    if not isinstance(inchis, list) or not inchis:
        return None

    first = inchis[0]

    if isinstance(first, dict):
        return first.get("value")

    if isinstance(first, str):
        return first

    return None


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []

    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, dict)]


def _as_str_list(value: Any) -> list[str]:
    if not value:
        return []

    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str) and item]