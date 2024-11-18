"""This module contains all OWL clases in form of Python classes, in order to add required methods to the correct
execution of SMIA software. This module is associated to the OWL ontology since it is defined inside the file of the
definition of OWL. When the owlready2 package loads the ontology, it will automatically import this Python module """
from owlready2 import Thing, get_ontology, DataPropertyClass, DatatypeClass, onto_path

from logic.exceptions import CheckingAttributeError, CheckingPropertyError
from utilities import configmap_utils
from utilities.aas_general_info import SMIAGeneralInfo
from utilities.css_ontology_utils import CapabilitySkillOntologyInfo, CapabilitySkillOntologyUtils

css_ontology = get_ontology(configmap_utils.get_ontology_filepath())
# onto_path.append(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
base_namespace = css_ontology.get_namespace(CapabilitySkillOntologyInfo.CSS_BASE_NAMESPACE)

# TODO PENSAR SI DEFINIR UNA CLASE (ExtendedThing) CON ALGUNOS METODOS UTILES QUE PUEDAN USAR EN TODAS LAS CLASES
#  (p.e. seek_limited_values())

# with css_ontology:
class Capability(Thing):
    """
    This class represent the OWL class for Capabilities. It contains all necessary methods to ensure the correct
    execution of SMIA software.
    """
    namespace = base_namespace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Some attributes of Capability have limited values, so it have to be obtained
        self.limited_values_dict = {}
        self.seek_limited_values()

        self.aas_sme_ref = None
        self.has_lifecycle = None


    def seek_limited_values(self):
        """
        This method seeks possible limited values for attributes of Capability, in order to validate when the attribute
        value is assigned. The possible values for limited attributes are stored in a global dictionary.
        """
        for prop in css_ontology.properties():
            if isinstance(prop, DataPropertyClass):
                for range_value in prop.range:
                    if isinstance(range_value, DatatypeClass):
                        possible_values = CapabilitySkillOntologyUtils.get_possible_values_of_datatype(range_value)
                        if possible_values is not None:
                            self.limited_values_dict[prop.name] = possible_values

    def set_lifecycle(self, lifecycle_value):
        """
        This method sets the lifecycle of Capability only if the given value is within the possible values for this
        attribute.

        Args:
            lifecycle_value (str): The value of the lifecycle of Capability.
        """
        if 'hasLifecycle' in self.limited_values_dict:
            if lifecycle_value not in self.limited_values_dict['hasLifecycle']:
                print("The lifecycle value [{}] for Capabilities is not valid.".format(lifecycle_value))
                return
        self.has_lifecycle = lifecycle_value

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to the instance of the Capability.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref

    def check_instance(self):
        """
        This method checks whether the Capability instance is valid: if the required attributes are set and if all the
        added properties are valid. In case of invalid Capability, it raises the exception related to the checking error.
        """
        if self.has_lifecycle is None:
            raise CheckingAttributeError("The 'has_lifecycle' attribute is required in Capability instances.",
                                         self)
        for skill in self.isRealizedBy:
            if not isinstance(skill, Skill):
                raise CheckingPropertyError("The instance {} is added in 'isRealizedBy' and it is not a "
                                            "Skill".format(skill), 'isRealizedBy', skill)
        for constraint in self.isRestrictedBy:
            if not isinstance(constraint, CapabilityConstraint):
                raise CheckingPropertyError("The instance {} is added in 'isRestrictedBy' and it is not a "
                                            "CapabilityConstraint".format(constraint),'isRestrictedBy', constraint)
        # TODO añadir validacion de que tiene una referencia de AAS valida
        # TODO pensar mas tipos de validaciones


class CapabilityConstraint(Thing):
    namespace = base_namespace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aas_sme_ref = None

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to the instance of the Capability.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref

    # TODO PENSAR METODOS PARA CONSTRAINTS

class Skill(Thing):
    namespace = base_namespace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aas_sme_ref = None

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to the instance of the Capability.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref

    def check_instance(self):
        """
        This method checks whether the Skill instance is valid: if the required attributes are set and if all the added
         properties are valid. In case of invalid Skill, it raises the exception related to the checking error.
        """
        if len(self.accessibleThrough) == 0:
            raise CheckingAttributeError("The instance {} does not have any SkillInterface associated".format(self),
                                         self)
        # TODO pensar mas comprobaciones

class SkillInterface(Thing):
    namespace = base_namespace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aas_sme_ref = None

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to the instance of the Capability.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref

    def check_instance(self):
        """
        This method checks whether the SkillInterface instance is valid: if the required attributes are set and if all
        the added properties are valid. In case of invalid SkillInterface, it raises the exception related to the
        checking error.
        """
        pass
        # TODO pensar mas comprobaciones

