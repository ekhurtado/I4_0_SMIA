import logging
import basyx.aas.model
from basyx.aas.model import SubmodelElementList, SubmodelElement, Operation, Submodel, RelationshipElement, \
    AnnotatedRelationshipElement, BasicEventElement, Entity, SubmodelElementCollection, Property, MultiLanguageProperty, \
    Range, Blob, File, ReferenceElement, Capability

from aas_model.extended_aas import ExtendedGeneralMethods
from utilities.capability_skill_ontology import CapabilitySkillOntology

_logger = logging.getLogger(__name__)

class ExtendedSubmodel(Submodel):
    """This class contains methods to be added to Submodel class of Basyx Python SDK model."""

    def print_submodel_information(self):
        print("Submodel information:")
        print("\tid: {}".format(self.id))
        print("\tid_short: {}".format(self.id_short))
        print("\tdisplayName: {}".format(self.display_name))
        print("\tdescription: {}".format(self.description))
        print("\tcategory: {}".format(self.category))
        print("\tkind: {}".format(self.kind))
        print("\tsemanticId: {}".format(self.semantic_id))
        print("\tsupplementalSemanticId: {}".format(self.supplemental_semantic_id))
        print("\tadministration: {}".format(ExtendedGeneralMethods.print_administration(self.administration)))
        print("\textension: " + "{}".format(ExtendedGeneralMethods.print_namespace_set(self.extension)))
        print("\tdataSpecifications: " + "{}".format(
            ExtendedGeneralMethods.print_data_specifications(self.embedded_data_specifications)))
        print("\tqualifiers: " + "{}".format(ExtendedGeneralMethods.print_namespace_set(self.qualifier)))


class ExtendedSubmodelElement(SubmodelElement):
    """This class contains methods to be added to SubmodelElement class of Basyx Python SDK model."""

    def print_submodel_element_information(self):
        print("Submodel element information:")
        print("\tid_short: {}".format(self.id_short))
        print("\tdescription: {}".format(self.description))
        print("\tsemanticId: {}".format(self.semantic_id))
        print("\tsupplementalSemanticId: {}".format(self.supplemental_semantic_id))
        print("\tqualifiers: " + "{}".format(ExtendedGeneralMethods.print_namespace_set(self.qualifier)))

    def get_qualifier_by_semantic_id(self, semantic_id_reference):
        if self.qualifier is None:
            return None
        else:
            for qualifier in self.qualifier:
                if qualifier.check_semantic_id_exist(semantic_id_reference):
                    return qualifier
            return None

    def get_parent_submodel(self):
        if isinstance(self.parent, basyx.aas.model.Submodel):
            return self.parent
        else:
            self.parent.get_parent_submodel()

    def check_cap_skill_ontology_semantics_and_qualifiers(self):
        """
        This method checks if the SubmodelElement of the Skill has the required semanticIDs and qualifiers defined in
        the Capability-Skill ontology.

        Returns:
            bool: result of the check (only True if both semanticIDs and qualifiers of Capability-Skill ontology exist).
        """
        # It will be checked if the semantic id of the skill is valid within the ontology
        if self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_MANUFACTURING_SKILL) is False:
            _logger.error("The skill {} has not valid semanticID regarding the "
                          "Capability-Skill ontology.".format(self))
            return False

        if self.check_cap_skill_ontology_qualifier_for_skills() is False:
            _logger.error("The skill {} has not valid qualifiers regarding the "
                          "Capability-Skill ontology.".format(self))
            return False
        return True

    def check_cap_skill_ontology_qualifier_for_skills(self):
        """
        This method checks if the SubmodelElement of the Skill has valid qualifiers defined in the Capability-Skil
        ontology.

        Returns:
            bool: result of the check (only True if the qualifier of Capability-Skill ontology exists).
        """
        skill_qualifier = self.get_qualifier_by_type(CapabilitySkillOntology.QUALIFIER_SKILL_TYPE)
        if skill_qualifier is not None:
            if skill_qualifier.value in CapabilitySkillOntology.QUALIFIER_SKILL_POSSIBLE_VALUES:
                return True
        _logger.error("ERROR: the qualifier is not valid in the skill {}".format(self))
        return False

    def get_parent_ref_by_semantic_id(self, semantic_id):
        """
        This method gets the reference of a parent element of the SubmodelElement by the semanticID.

        Args:
            semantic_id (str): semantic identifier of the parent element.

        Returns:
            basyx.aas.model.ModelReference: model reference of the parent element (None if the parent does not exist)
        """
        parent_elem = self.parent
        while parent_elem:
            if parent_elem.check_semantic_id_exist(semantic_id):
                return basyx.aas.model.ModelReference.from_referable(parent_elem)
            else:
                parent_elem = parent_elem.parent
        return None


class ExtendedRelationshipElement(RelationshipElement):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of RelationshipElements:")
        print("\t\tfirst: {}".format(self.first))
        print("\t\tsecond: {}".format(self.second))


class ExtendedAnnotatedRelationshipElement(AnnotatedRelationshipElement):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("\t\tannotation: {}".format(self.annotation))


class ExtendedCapability(Capability):
    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of Capabilities:")

    def check_cap_skill_ontology_semantics_and_qualifiers(self):
        """
        This method checks if the Capability has the required semanticIDs and qualifiers defined in the Capability-Skill
        ontology, exactly for Capabilities.

        Returns:
            bool: result of the check (only True if both semanticIDs and qualifiers of Capability-Skill ontology exist).
        """
        # It will be checked if the semantic id of the capability is valid within the ontology
        if self.check_cap_skill_ontology_semantic_id() is False:
            _logger.error("The capability {} has not valid semanticID regarding the "
                          "Capability-Skill ontology.".format(self))
            return False

        # It will also be checked if it has any of the qualifiers defined in the ontology for the capabilities
        if self.check_cap_skill_ontology_qualifiers() is False:
            _logger.error("The capability {} has not valid qualifiers regarding the "
                          "Capability-Skill ontology.".format(self))
            return False
        return True

    def check_cap_skill_ontology_semantic_id(self):
        """
        This method checks if the Capability has one of the required semanticIDs defined in the Capability-Skill
        ontology, exactly for Capabilities.

        Returns:
            bool: result of the check (only True if the semanticID of Capability-Skill ontology exists).
        """
        if ((self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_MANUFACTURING_CAPABILITY))
                or (self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_ASSET_CAPABILITY))
                or (self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_AGENT_CAPABILITY))):
            return True
        else:
            _logger.error("ERROR: the capability is not valid within the ontology.")
            return False

    def check_cap_skill_ontology_qualifiers(self):
        """
        This method checks if the Capability has valid qualifiers, defined in the Capability-Skil ontology.

        Returns:
            bool: result of the check (only True if the qualifier of Capability-Skill ontology exists).
        """
        capability_qualifier = self.get_qualifier_by_type(CapabilitySkillOntology.QUALIFIER_CAPABILITY_TYPE)
        if capability_qualifier is not None:
            if capability_qualifier.value in CapabilitySkillOntology.QUALIFIER_CAPABILITY_POSSIBLE_VALUES:
                return True
        _logger.error("ERROR: the qualifier is not valid in the capability {}".format(self))
        return False

    def get_capability_type_in_ontology(self):
        """
        This method gets the type of the capability within the Capability-Skill ontology.

        Returns:
            str: value of the type of the capability within the Capability-Skill ontology.
        """
        if self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_MANUFACTURING_CAPABILITY):
            return CapabilitySkillOntology.MANUFACTURING_CAPABILITY_TYPE
        elif self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_ASSET_CAPABILITY):
            return CapabilitySkillOntology.ASSET_CAPABILITY_TYPE
        elif self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_AGENT_CAPABILITY):
            return CapabilitySkillOntology.AGENT_CAPABILITY_TYPE
        else:
            _logger.error("ERROR: the capability type is not valid within the ontology.")
            return None



class ExtendedOperation(Operation):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of Operations:")
        print("\t\tinputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.input_variable)))
        print("\t\toutputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.output_variable)))
        print("\t\tinoutputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.in_output_variable)))


class ExtendedBasicEventElement(BasicEventElement):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of BasicEventElements:")
        # TODO


class ExtendedEntity:
    # class ExtendedEntity(Entity):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of Entities:")
        print("\t\tstatement: {}".format(self.statement))
        print("\t\tentityType: {}".format(self.entity_type))
        print("\t\tglobalAssetId: {}".format(self.global_asset_id))
        print("\t\tspecificAssetId: {}".format(self.specific_asset_id))


class ExtendedSubmodelElementList(SubmodelElementList):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of SubmodelElementLists:")
        # TODO


class ExtendedSubmodelElementCollection(SubmodelElementCollection):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of SubmodelElementCollections:")
        print("\t\tvalue: (SME in the collection)")
        for sm_elem_in_collection in self.value:
            print("\t\t\tSubmodelElement: {}".format(sm_elem_in_collection))

    def get_sm_element_by_id_short(self, id_short):
        """
        This method gets a submodel element inside a SubmodelElementCollection by its id_short.
        Args:
            id_short (str): id_short of the submodel element to find.

        Returns:
           basyx.aas.model.SubmodelElement: submodel element in form of Python object.
        """
        return self.value.get('id_short', id_short)

    def get_sm_element_by_semantic_id(self, semantic_id_ref):
        """
        This method gets a submodel element inside a SubmodelElementCollection by its semantic identifier.
        Args:
            semantic_id_ref (str): semantic identifier of the submodel element to find.

        Returns:
           basyx.aas.model.SubmodelElement: submodel element in form of Python object.
        """
        for sm_elem in self.value:
            for reference in sm_elem.semantic_id.key:
                if reference.value == semantic_id_ref:
                    return sm_elem

# ------------
# DataElements
# ------------
class ExtendedProperty(Property):
    """This class contains methods to be added to Property class of Basyx Python SDK model."""

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("Specific attributes of Properties:")
        print("\t\tvalueType: {}".format(self.value_type))
        print("\t\tvalueId: {}".format(self.value_id))
        print("\t\tvalue: {}".format(self.value))


class ExtendedMultiLanguageProperty(MultiLanguageProperty):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("Specific attributes of MultiLanguageProperties:")
        print("\t\tvalueId: {}".format(self.value_id))
        print("\t\tvalue: {}".format(self.value))


class ExtendedRange(Range):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of Ranges:")
        # TODO


class ExtendedBlob(Blob):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of Blobs:")
        # TODO


class ExtendedFile(File):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("Specific attributes of Files:")
        print("\t\tvalue: {}".format(self.value))
        print("\t\tcontentType: {}".format(self.content_type))


class ExtendedReferenceElement(ReferenceElement):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of ReferenceElements:")
        # TODO
