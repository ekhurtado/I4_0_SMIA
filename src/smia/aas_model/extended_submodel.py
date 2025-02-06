import abc
import logging
import types

import basyx.aas.model
from basyx.aas.model import SubmodelElementList, SubmodelElement, Operation, Submodel, RelationshipElement, \
    AnnotatedRelationshipElement, BasicEventElement, SubmodelElementCollection, Property, MultiLanguageProperty, \
    Range, Blob, File, ReferenceElement, Capability

from smia import AASModelExtensionUtils
from smia.aas_model.extended_aas import ExtendedGeneralMethods
from smia.logic.exceptions import AASModelOntologyError, AASModelReadingError
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo
from smia.utilities.smia_info import AssetInterfacesInfo

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
        """
        This method gets the submodel where the self SubmodelElement is defined.

        Returns:
            basyx.aas.model.Submodel: parent submodel in form of a Python object.
        """
        if isinstance(self.parent, basyx.aas.model.Submodel):
            return self.parent
        else:
            return self.parent.get_parent_submodel()

    def check_cap_skill_ontology_semantics_and_qualifiers(self):
        """
        This method checks if the SubmodelElement of the Skill has the required semanticIDs and qualifiers defined in
        the Capability-Skill ontology.

        Returns:
            bool: result of the check (only True if both semanticIDs and qualifiers of Capability-Skill ontology exist).
        """
        # It will be checked if the semantic id of the skill is valid within the ontology
        if self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI) is False:
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
        skill_qualifier = self.get_qualifier_by_type('SkillImplementationType')
        if skill_qualifier is not None:
            if skill_qualifier.value in ['STATE', 'TRIGGER', 'OPERATION', 'FUNCTIONBLOCK']:
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

    def check_cap_skill_ontology_semantic_id(self):
        """
        This method checks if the Capability has one of the required semanticIDs defined in the Capability-Skill
        ontology, exactly for Capabilities.

        Returns:
            bool: result of the check (only True if the semanticID of Capability-Skill ontology exists).
        """
        if ((self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI))
                or (self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI))
                or (self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI))):
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
        capability_qualifier = self.get_qualifier_by_type('ExpressionSemantic')
        if capability_qualifier is not None:
            if capability_qualifier.value in ['REQUIREMENT', 'OFFER', 'ASSURANCE']:
                return True
        _logger.error("ERROR: the qualifier is not valid in the capability {}".format(self))
        return False

    def get_capability_type_in_ontology(self):
        """
        This method gets the type of the capability within the Capability-Skill ontology.

        Returns:
            str: value of the type of the capability within the Capability-Skill ontology.
        """
        if self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI):
            return 'ManufacturingCapability'
        elif self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI):
            return 'AssetCapability'
        elif self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI):
            return 'AgentCapability'
        else:
            _logger.error("ERROR: the capability type is not valid within the ontology.")
            return None

    def get_semantic_id_of_css_ontology(self):
        """
        This method gets the semanticID of the capability within the Capability-Skill ontology.

        Returns:
            str: value of the semanticID of the capability within the Capability-Skill ontology.
        """
        if self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI):
            return CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI
        elif self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI):
            return CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI
        elif self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI):
            return CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI
        else:
            raise AASModelOntologyError("The capability {} does not have a valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")


class ExtendedOperation(Operation):

    def print_submodel_element_information(self):
        ExtendedSubmodelElement.print_submodel_element_information(self)
        print("\tSpecific attributes of Operations:")
        print("\t\tinputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.input_variable)))
        print("\t\toutputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.output_variable)))
        print("\t\tinoutputVariable: {}".format(ExtendedGeneralMethods.print_namespace_set(self.in_output_variable)))

    def get_variable_value_id(self, value_id):
        """
        This method gets the variable of the Operation that matches with the given valueId.

        Args:
             value_id (str): the value id of the variable to find.

        Returns:
            (str): id_short of the variable
        """
        all_variables = [self.input_variable, self.output_variable, self.in_output_variable]
        for var_type_set in all_variables:
            for var in var_type_set:
                if var.value_id:
                    for key in var.value_id.key:
                        if key.value == value_id:
                            return var.id_short
        return None

    def get_operation_variables_by_semantic_id(self, semantic_id):
        """
        This method gets all operation variables that have the given semanticID.

        Args:
            semantic_id (str):  semantic identifier of the operation variables to find.

        Returns:
            list: all valid operation variables in form of a list of SubmodelElements.
        """
        operation_variables = []
        all_var_sets = [self.input_variable, self.output_variable, self.in_output_variable]
        for var_set in all_var_sets:
            for operation_variable in var_set:
                if operation_variable.check_semantic_id_exist(semantic_id):
                    operation_variables.append(operation_variable)
        return operation_variables


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
        return None


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

    def check_value_within_range(self, value):
        """
        This method checks whether a given value is within the range defined in this element.

        Args:
            value: data to be checked.

        Returns:
            bool: the result of the check.
        """
        try:
            formatted_value = value
            if issubclass(self.value_type, basyx.aas.model.datatypes.Float):
                formatted_value = float(value)
            elif issubclass(self.value_type, basyx.aas.model.datatypes.Int):
                formatted_value = int(value)
            # TODO Think about more types
            return True if self.min <= formatted_value <= self.max else False
        except ValueError as e:
            _logger.error("Value error with data {} of type {} in Range {}".format(value, self,value, self))
            return False

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


# CLASSES FOR CSS ONTOLOGY-BASED SOFTWARE
# ----------------------------------------
class ExtendedGenericCSSClass(metaclass=abc.ABCMeta):

    def add_old_sme_class(self, sme_class):
        """
        This method adds the old Basyx SubmodelElement class to be stored to the correct execution of the software. It
        also adds the inheritance to the Extended SMIA class with the method 'add_inheritance_of_extended_class'.

        Args:
            sme_class (basyx.aas.model.SubmodelElement): old submodel element class in BaSyx Python structure.
        """
        self.old_sme_class = sme_class
        # if issubclass(self.old_sme_class, basyx.aas.model.Operation):
        #     print("Antes la Skill era una Operation")
        # if issubclass(self.old_sme_class, basyx.aas.model.SubmodelElement):
        #     print("Antes la Skill era una SubmodelElement")

        # The inheritance to the associated Extended SMIA class is also added
        self.add_inheritance_of_extended_class()

    def add_inheritance_of_extended_class(self):
        """
        This method adds inheritance to SMIA Extended classes from the original BaSyx classes, to add the SMIA methods
        specific to the associated class. To do so, it uses the old_sme_class attribute added during the creation of
        any ExtendedGenericCSSClass.
        """
        associated_extended_class = AASModelExtensionUtils.get_extension_classes_dict()[self.old_sme_class]
        if associated_extended_class != self.__class__:
            new_bases = (self.__class__, associated_extended_class)
            new_class = types.new_class(self.__class__.__name__, new_bases, {})
            self.__class__ = new_class

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        pass


class ExtendedCapability(ExtendedGenericCSSClass, Capability):
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


class ExtendedSkill(ExtendedGenericCSSClass):
    # TODO se ha tenido que separar las skills simples (Operation,Event...) de las complejas (Submodel). De
    #  momento estas no se han implementado pero en el White paper de PLattform Industrie se menciona que las Skills
    #  se pueden implementar mediante FunctionBlock (Submodelo)
    pass


class ExtendedSkillInterface(ExtendedGenericCSSClass):
    # TODO se ha tenido que separar las skills interfaces simples (Operation,Event...) de las complejas (SMC). De
    #  momento se tienen ambas opciones ya que las interfaces de servicios de activos son SMC y las de los servicios de
    #  agente son simples

    def get_associated_asset_interface(self):
        """
        This method gets the asset interface AAS SubmodelElement associated with this skill interface.

        Returns:
            basyx.aas.model.SubmodelElement: submodel element of the asset interface.
        """
        pass


class ExtendedCapabilityConstraint(ExtendedGenericCSSClass, ExtendedSubmodelElement):
# class ExtendedCapabilityConstraint(ExtendedGenericCSSClass, ExtendedSubmodelElement, ExtendedProperty):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")

    def check_constraint(self, constraint_data):
        """
        This method checks the Capability Constraint against the given data to ensure that it is valid.

        Args:
            constraint_data: data to be checked with the Capability Constraint

        Returns:
            bool: the result of the check
        """
        # Initially, the result is set to invalid.
        result = False
        if isinstance(self, ExtendedRange):
            result = self.check_value_within_range(constraint_data)
            if not result:
                _logger.warning("The data ({}) is invalid in the Capability Constraint {} because it is not within "
                                "the defined range values.".format(constraint_data, self))
        # TODO Think about more types of constraints (properties, references...)
        _logger.info('The Capability Constraint {} has been checked with data ({}), resulting in {}'.format(
            self, constraint_data, result))
        return result


class ExtendedSimpleSkill(ExtendedSkill, ExtendedSubmodelElement):
# class ExtendedSimpleSkill(ExtendedSkill, ExtendedSubmodelElement, ExtendedOperation):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")


class ExtendedComplexSkill(ExtendedSkill, ExtendedSubmodel):
    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")


class ExtendedSkillParameter(ExtendedGenericCSSClass):
# class ExtendedSkillParameter(ExtendedGenericCSSClass, ExtendedProperty):
    pass


class ExtendedSimpleSkillInterface(ExtendedSkillInterface, ExtendedSubmodelElement):
# class ExtendedSimpleSkillInterface(ExtendedSkillInterface, ExtendedOperation, ExtendedSubmodelElement):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")


class ExtendedComplexSkillInterface(ExtendedSkillInterface, ExtendedSubmodelElementCollection):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")

    def get_associated_asset_interface(self):
        """
        This method gets the asset interface AAS SubmodelElement associated with this skill interface.

        Returns:
            basyx.aas.model.SubmodelElement: submodel element of the asset interface.
        """
        #
        asset_interface_elem = self.get_parent_ref_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE)
        if asset_interface_elem is None:
            raise AASModelReadingError("The skill interface is not inside the AssetInterfaceSubmodel.", self,
                                       "SubmodelElementNotInValidSubmodel")
        return asset_interface_elem



