from __future__ import annotations

from .classification_level_resolver import (
    get_class_id,
    get_direct_parent_id,
    get_kingdom_id,
    get_or_create_class_id,
    get_or_create_direct_parent_id,
    get_or_create_kingdom_id,
    get_or_create_subclass_id,
    get_or_create_superclass_id,
    get_subclass_id,
    get_superclass_id,
)
from .classification_level_batch_resolver import (
    get_class_ids,
    get_direct_parent_ids,
    get_kingdom_ids,
    get_or_create_class_ids,
    get_or_create_direct_parent_ids,
    get_or_create_kingdom_ids,
    get_or_create_subclass_ids,
    get_or_create_superclass_ids,
    get_subclass_ids,
    get_superclass_ids,
)

from .molecular_framework_resolver import (
    get_molecular_framework_id,
    get_or_create_molecular_framework_id,
)
from .molecular_framework_batch_resolver import (
    get_molecular_framework_ids,
    get_or_create_molecular_framework_ids,
)

from .node_resolver import (
    get_alternative_parent_id,
    get_ancestor_id,
    get_intermediate_node_id,
    get_or_create_alternative_parent_id,
    get_or_create_ancestor_id,
    get_or_create_intermediate_node_id,
)
from .node_batch_resolver import (
    get_alternative_parent_ids,
    get_ancestor_ids,
    get_intermediate_node_ids,
    get_or_create_alternative_parent_ids,
    get_or_create_ancestor_ids,
    get_or_create_intermediate_node_ids,
)

from .term_resolver import (
    get_or_create_predicted_chebi_term_id,
    get_or_create_predicted_lipidmaps_term_id,
    get_or_create_substituent_id,
    get_predicted_chebi_term_id,
    get_predicted_lipidmaps_term_id,
    get_substituent_id,
)
from .term_batch_resolver import (
    get_or_create_predicted_chebi_term_ids,
    get_or_create_predicted_lipidmaps_term_ids,
    get_or_create_substituent_ids,
    get_predicted_chebi_term_ids,
    get_predicted_lipidmaps_term_ids,
    get_substituent_ids,
)

from .external_descriptor_resolver import (
    get_external_descriptor_annotation_id,
    get_external_descriptor_id,
    get_or_create_external_descriptor_annotation_id,
    get_or_create_external_descriptor_id,
)
from .external_descriptor_batch_resolver import (
    ExternalDescriptorKey,
    get_external_descriptor_annotation_ids,
    get_external_descriptor_ids,
    get_or_create_external_descriptor_annotation_ids,
    get_or_create_external_descriptor_ids,
    make_external_descriptor_key,
)

from .set_resolver import (
    get_alternative_parent_set_id,
    get_ancestor_set_id,
    get_external_descriptor_set_id,
    get_intermediate_node_set_id,
    get_or_create_alternative_parent_set_id,
    get_or_create_ancestor_set_id,
    get_or_create_external_descriptor_set_id,
    get_or_create_intermediate_node_set_id,
    get_or_create_predicted_chebi_term_set_id,
    get_or_create_predicted_lipidmaps_term_set_id,
    get_or_create_substituent_set_id,
    get_predicted_chebi_term_set_id,
    get_predicted_lipidmaps_term_set_id,
    get_substituent_set_id,
)
from .set_batch_resolver import (
    get_alternative_parent_set_ids,
    get_ancestor_set_ids,
    get_external_descriptor_set_ids,
    get_intermediate_node_set_ids,
    get_or_create_alternative_parent_set_ids,
    get_or_create_ancestor_set_ids,
    get_or_create_external_descriptor_set_ids,
    get_or_create_intermediate_node_set_ids,
    get_or_create_predicted_chebi_term_set_ids,
    get_or_create_predicted_lipidmaps_term_set_ids,
    get_or_create_substituent_set_ids,
    get_predicted_chebi_term_set_ids,
    get_predicted_lipidmaps_term_set_ids,
    get_substituent_set_ids,
)