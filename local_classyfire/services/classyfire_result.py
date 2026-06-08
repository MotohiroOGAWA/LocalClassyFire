from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClassyFireLevelData:
    """One ClassyFire classification level.

    Examples
    --------
    kingdom, superclass, class, subclass, direct_parent
    """

    name: str
    description: str | None = None
    chemont_id: str | None = None
    url: str | None = None

    @classmethod
    def from_api_json(
        cls,
        data: dict[str, Any] | None,
    ) -> ClassyFireLevelData | None:
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
class IntermediateNodeData:
    """One ClassyFire intermediate node."""

    name: str
    description: str | None = None
    chemont_id: str | None = None
    url: str | None = None

    @classmethod
    def from_api_json(
        cls,
        data: dict[str, Any] | None,
    ) -> IntermediateNodeData | None:
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
class AlternativeParentData:
    """One ClassyFire alternative parent."""

    name: str
    description: str | None = None
    chemont_id: str | None = None
    url: str | None = None

    @classmethod
    def from_api_json(
        cls,
        data: dict[str, Any] | None,
    ) -> AlternativeParentData | None:
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
    def from_api_json(
        cls,
        data: dict[str, Any] | None,
    ) -> ExternalDescriptorData | None:
        if not data:
            return None

        source = data.get("source")
        source_id = data.get("source_id")

        if not source or not source_id:
            return None

        annotations = _to_string_list(data.get("annotations"))

        return cls(
            source=source,
            source_id=source_id,
            annotations=annotations,
        )


@dataclass(frozen=True)
class ClassyFireResult:
    """Parsed successful ClassyFire result.

    This object is an application-level representation of one successful
    ClassyFire API response. It does not represent missing or failed queries.
    """

    inchikey: str
    smiles: str | None = None

    kingdom: ClassyFireLevelData | None = None
    superclass: ClassyFireLevelData | None = None
    class_: ClassyFireLevelData | None = None
    subclass: ClassyFireLevelData | None = None
    direct_parent: ClassyFireLevelData | None = None

    intermediate_nodes: list[IntermediateNodeData] = field(default_factory=list)
    alternative_parents: list[AlternativeParentData] = field(default_factory=list)
    ancestors: list[str] = field(default_factory=list)

    molecular_framework: str | None = None

    substituents: list[str] = field(default_factory=list)
    external_descriptors: list[ExternalDescriptorData] = field(default_factory=list)
    predicted_chebi_terms: list[str] = field(default_factory=list)
    predicted_lipidmaps_terms: list[str] = field(default_factory=list)

    description: str | None = None
    classification_version: str | None = None

    @classmethod
    def from_api_json(
        cls,
        data: dict[str, Any],
    ) -> ClassyFireResult:
        """Create ClassyFireResult from ClassyFire API JSON."""

        inchikey = data.get("inchikey")

        if not inchikey:
            raise ValueError("ClassyFire API JSON does not contain inchikey.")

        intermediate_nodes = [
            node
            for node in (
                IntermediateNodeData.from_api_json(item)
                for item in data.get("intermediate_nodes", [])
            )
            if node is not None
        ]

        alternative_parents = [
            parent
            for parent in (
                AlternativeParentData.from_api_json(item)
                for item in data.get("alternative_parents", [])
            )
            if parent is not None
        ]

        external_descriptors = [
            descriptor
            for descriptor in (
                ExternalDescriptorData.from_api_json(item)
                for item in data.get("external_descriptors", [])
            )
            if descriptor is not None
        ]

        return cls(
            inchikey=inchikey.strip(),
            smiles=data.get("smiles"),
            kingdom=ClassyFireLevelData.from_api_json(data.get("kingdom")),
            superclass=ClassyFireLevelData.from_api_json(data.get("superclass")),
            class_=ClassyFireLevelData.from_api_json(data.get("class")),
            subclass=ClassyFireLevelData.from_api_json(data.get("subclass")),
            direct_parent=ClassyFireLevelData.from_api_json(
                data.get("direct_parent")
            ),
            intermediate_nodes=intermediate_nodes,
            alternative_parents=alternative_parents,
            ancestors=_to_string_list(data.get("ancestors")),
            molecular_framework=_to_optional_string(
                data.get("molecular_framework")
            ),
            substituents=_to_string_list(data.get("substituents")),
            external_descriptors=external_descriptors,
            predicted_chebi_terms=_to_string_list(
                data.get("predicted_chebi_terms")
            ),
            predicted_lipidmaps_terms=_to_string_list(
                data.get("predicted_lipidmaps_terms")
            ),
            description=data.get("description"),
            classification_version=data.get("classification_version"),
        )


def _to_optional_string(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def _to_string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        return []

    items: list[str] = []

    for item in value:
        if item is None:
            continue

        text = str(item).strip()

        if text:
            items.append(text)

    return items