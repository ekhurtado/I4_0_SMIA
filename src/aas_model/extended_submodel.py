import abc
import logging
import basyx.aas.model
from basyx.aas.model import SubmodelElementList, SubmodelElement, Operation, Submodel, RelationshipElement, \
    AnnotatedRelationshipElement, BasicEventElement, SubmodelElementCollection, Property, MultiLanguageProperty, \
    Range, Blob, File, ReferenceElement, Capability

from aas_model.extended_aas import ExtendedGeneralMethods
from logic.exceptions import AASModelReadingError, AASModelOntologyError
from css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils, CapabilitySkillOntologyInfo

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
            return self.parent.get_parent_submodel()

    def check_cap_skill_ontology_semantics_and_qualifiers(self):
        """
        This method checks if the SubmodelElement of the Skill has the required semanticIDs and qualifiers defined in
        the Capability-Skill ontology.

        Returns:
            bool: result of the check (only True if both semanticIDs and qualifiers of Capability-Skill ontology exist).
        """
        # It will be checked if the semantic id of the skill is valid within the ontology
        if self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_MANUFACTURING_SKILL) is False:
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
        skill_qualifier = self.get_qualifier_by_type(CapabilitySkillOntologyUtils.QUALIFIER_SKILL_TYPE)
        if skill_qualifier is not None:
            if skill_qualifier.value in CapabilitySkillOntologyUtils.QUALIFIER_SKILL_POSSIBLE_VALUES:
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

    def get_qualifier_value_by_type(self, qualifier_type_value):
        """
        This method gets the value of the qualifier that has a given type.

        Args:
            qualifier_type_value (str): type of the qualifier.

        Returns:
            str: value of the qualifier with the given type
        """
        try:
            qualifier_object = self.get_qualifier_by_type(qualifier_type_value)
            if qualifier_object is None:
                raise AASModelReadingError("Qualifier type {} not found in the element {}".format(
                    qualifier_type_value, self), self, 'KeyError in qualifiers')
            else:
                return qualifier_object.value
        except KeyError as e:
            raise AASModelReadingError("Qualifier type {} not found in the element {}".format(
                qualifier_type_value, self), self, 'KeyError in qualifiers')


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
        if ((self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_MANUFACTURING_CAPABILITY))
                or (self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_ASSET_CAPABILITY))
                or (self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_AGENT_CAPABILITY))):
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
        capability_qualifier = self.get_qualifier_by_type(CapabilitySkillOntologyUtils.QUALIFIER_CAPABILITY_TYPE)
        if capability_qualifier is not None:
            if capability_qualifier.value in CapabilitySkillOntologyUtils.QUALIFIER_CAPABILITY_POSSIBLE_VALUES:
                return True
        _logger.error("ERROR: the qualifier is not valid in the capability {}".format(self))
        return False

    def get_capability_type_in_ontology(self):
        """
        This method gets the type of the capability within the Capability-Skill ontology.

        Returns:
            str: value of the type of the capability within the Capability-Skill ontology.
        """
        if self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_MANUFACTURING_CAPABILITY):
            return CapabilitySkillOntologyUtils.MANUFACTURING_CAPABILITY_TYPE
        elif self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_ASSET_CAPABILITY):
            return CapabilitySkillOntologyUtils.ASSET_CAPABILITY_TYPE
        elif self.check_semantic_id_exist(CapabilitySkillOntologyUtils.SEMANTICID_AGENT_CAPABILITY):
            return CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE
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
            # TODO HACER AHORA: hay que crear una excepcion para lectura del AAS Model
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


# TODO esta es una prueba para generar clases propias para Capability, Skill y SkillInterface (de esta forma podemos
#   añadir metodos utiles que se usen durante la ejecucion del programa y hacerlo t0do mas eficiente. Por ejemplo,
#   un metodo podria ser obtener los parametros de una skill. Antes teniamos el problema que simplemente los teniamos
#   a mano ya que la Skill era una operation y tiene en sus atributos sus variables input y ouput. Ahora,
#   con la clase "SMIASkill" podemos hacer un metodo de obtener los parametros. Este metodo puede analizar de que
#   tipo de era la Skill, y dependiendo de su clase, obtener los parametros (con una Operacion lograrlos con sus
#   atributos, y en otros casos analizar la relacion SkillHasParameter y obtener sus parametros). Para esto,
#   si es cierto que, durante la creacion de esta clase se deberan añadir los parametros, la maquina de estados,
#   sus posibles interfaces, etc. ya que se necesitará t0do el modelo AAS para ello (se tendra que hacer en el
#   init_aas_model_behav)
# CLASSES FOR CSS ONTOLOGY-BASED EXECUTION
# ----------------------------------------
class ExtendedGenericCSSClass(metaclass=abc.ABCMeta):

    def add_old_sme_class(self, sme_class):
        """
        This method adds the old Basyx SubmodelElement class to be stored to the correct execution of the software.

        Args:
            sme_class (basyx.aas.model.SubmodelElement): old submodel element class in BaSyx Python structure.
        """
        self.old_sme_class = sme_class
        # if issubclass(self.old_sme_class, basyx.aas.model.Operation):
        #     print("Antes la Skill era una Operation")
        # if issubclass(self.old_sme_class, basyx.aas.model.SubmodelElement):
        #     print("Antes la Skill era una SubmodelElement")

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        pass

class ExtendedSkill(ExtendedGenericCSSClass):
    # TODO se ha tenido que separar las skills simples (Operation,Event...) de las complejas (Submodel). De
    #  momento estas no se han implementado pero en el White paper de PLattform Industrie se menciona que las Skills
    #  se pueden implementar mediante FunctionBlock (Submodelo)
    pass

class ExtendedSkillInterface(ExtendedGenericCSSClass):
    # TODO se ha tenido que separar las skills interfaces simples (Operation,Event...) de las complejas (SMC). De
    #  momento se tienen ambas opciones ya que las interfaces de servicios de activos son SMC y las de los servicios de
    #  agente son simples
    pass

class ExtendedCapabilityConstraint(ExtendedGenericCSSClass, ExtendedSubmodelElement, ExtendedProperty):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")

class ExtendedSimpleSkill(ExtendedSkill, ExtendedSubmodelElement, ExtendedOperation):

    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")
    def como_convertir_un_skill_a_esta_clase(self, skill_elem):
        # Imaginemos que tenemos un skill_elem (puede ser, p.e. un Operation)
        basyx_class = skill_elem.__class__
        skill_elem.__class__ = ExtendedSkill
        # Ahora es de la clase SMIASkill, por lo que tiene todos sus metodos y los de sus clases extendidas (los Extended nuestros)
        # Aun asi, tenemos que guardar de que tipo de SubmodelElement era antes de convertirlo a SMIASkill
        self.old_sme_class = basyx_class

        # TODO a la hora de ejecutar los metodos que se añadan, se deberá comprobar el tipo de clase que era antes, ya
        #  que va a depender para su ejecución y para saber qué atributos tendrá en cada caso (no todos son iguales)
        if issubclass(self.old_sme_class, basyx.aas.model.Operation):
            print("Antes la Skill era una Operation")


class ExtendedComplexSkill(ExtendedSkill, ExtendedSubmodel):
    def get_semantic_id_of_css_ontology(self):
        """
        This method checks the semanticID of the skill within the Capability-Skill ontology.
        """
        if not self.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
            raise AASModelOntologyError("The skill {} does not have the valid semanticID within the "
                                        "ontology.".format(self.id_short), self, "OntologySemanticIdMissing")


class ExtendedSimpleSkillInterface(ExtendedSkillInterface, ExtendedOperation, ExtendedSubmodelElement):

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