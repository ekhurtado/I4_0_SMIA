import logging
import basyx.aas.model
from basyx.aas.model import SubmodelElementList, SubmodelElement, Operation, Submodel, RelationshipElement, \
    AnnotatedRelationshipElement, BasicEventElement, Entity, SubmodelElementCollection, Property, MultiLanguageProperty, \
    Range, Blob, File, ReferenceElement, Capability

from aas_model_extension.ExtendedAssetAdministrationShell import ExtendedGeneralMethods
from utilities.CapabilitySkillOntology import CapabilitySkillOntology

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

    # def check_semantic_id_exist(self, semantic_id_reference):
    #     if self.semantic_id is None:
    #         return False
    #     for reference in self.semantic_id.key:
    #         if str(reference) == semantic_id_reference:
    #             return True
    #     return False

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

class ExtendedRelationshipElement(RelationshipElement):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of RelationshipElements:")
        print("\t\tfirst: {}".format(self.first))
        print("\t\tsecond: {}".format(self.second))

    def get_cap_skill_elem_from_relationship(self):
        """
        This method returns the Capability and Skill objects from the Relationship element, no matter in which order
        they are specified.

        Returns:
            basyx.aas.model.Capability, basyx.aas.model.SubmodelElement: capability and skill SME in Python
            reference objects.
        """
        if isinstance(self.first, basyx.aas.model.Capability):
            return self.first, self.second
        elif isinstance(self.second, basyx.aas.model.Capability):
            return self.second, self.first
        else:
            _logger.error("This method has been used incorrectly. This Relationship does not have a Capability element.")
            return None, None


class ExtendedAnnotatedRelationshipElement(AnnotatedRelationshipElement):

    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("\t\tannotation: {}".format(self.annotation))


class ExtendedCapability(Capability):
    def print_submodel_element_information(self):
        super().print_submodel_element_information()
        print("Specific attributes of Capabilities:")

    def check_cap_skill_ontology_semantic_id(self):
        if self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_MANUFACTURING_CAPABILITY):
            _logger.info('\t\tThe capability is of a manufacturing type.')
        elif self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_ASSET_CAPABILITY):
            _logger.info('\t\tThe capability is of a asset type.')
        elif self.check_semantic_id_exist(CapabilitySkillOntology.SEMANTICID_AGENT_CAPABILITY):
            _logger.info('\t\tThe capability is of a agent type.')
        else:
            _logger.error("ERROR: the capability is not valid within the relationship")


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
