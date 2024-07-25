"""
This module implements the global structures of the AAS meta-model, including the referencing classes.
"""
from enum import unique, Enum

from aas_definition_reader.aas_class_structure import common
from aas_definition_reader.aas_class_structure.aas import AssetAdministrationShell
from aas_definition_reader.aas_class_structure.submodel import Submodel


class ConceptDescription(common.Identifiable, common.HasDataSpecification):
    def __init__(self,
                 id_: common.KeyTypes.Identifier,
                 is_case_of: set[common.KeyTypes.Reference] = None,
                 id_short: common.KeyTypes.NameType = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 administration: common.Identifiable.AdministrativeInformation = None,
                 embedded_data_specifications=(),
                 extension: set[common.Extension] = ()):
        super().__init__()
        self.id: common.KeyTypes.Identifier = id_
        self.is_case_of: set[common.KeyTypes.Reference] = is_case_of
        self.id_short = id_short
        self.display_name = display_name
        self.category = category
        self.description = description
        self.parent = parent
        self.administration: common.Identifiable.AdministrativeInformation = administration
        self.embedded_data_specifications = embedded_data_specifications
        self.extension = extension


class Environment:
    """
    Container for different identifiable sets.
    """

    def __init__(self,
                 asset_administration_shell: AssetAdministrationShell,
                 submodel: set[Submodel],
                 concept_description: ConceptDescription):
        super().__init__()
        self.asset_administration_shell: AssetAdministrationShell = asset_administration_shell
        self.submodel: set[Submodel] = submodel
        self.concept_description: ConceptDescription = concept_description


# -----------
# Referencing
# -----------
class Reference:
    @unique
    class ReferenceTypes(Enum):
        GLOBAL_REFERENCE = 0
        MODEL_REFERENCE = 1

    def __init__(self,
                 type_: ReferenceTypes,
                 referred_semantic_id: common.KeyTypes.Reference,
                 key: set[common.KeyTypes]):
        super().__init__()
        self.type: Reference.ReferenceTypes = type_
        self.referred_semantic_id: common.KeyTypes.Reference = referred_semantic_id
        self.key: set[common.KeyTypes] = key
