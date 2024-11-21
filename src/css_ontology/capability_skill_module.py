"""This module contains all OWL clases in form of Python classes, in order to add required methods to the correct
execution of SMIA software. This module is associated to the OWL ontology since it is defined inside the file of the
definition of OWL. When the owlready2 package loads the ontology, it will automatically import this Python module """
import logging

import basyx.aas.model
from owlready2 import Thing, get_ontology, DataPropertyClass, DatatypeClass

from aas_model import extended_submodel
from logic.exceptions import OntologyCheckingAttributeError, OntologyCheckingPropertyError, \
    OntologyInstanceCreationError
from utilities import configmap_utils
from css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo, CapabilitySkillOntologyUtils

_logger = logging.getLogger(__name__)

css_ontology = get_ontology(CapabilitySkillOntologyUtils.get_ontology_file_path())
# onto_path.append(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
base_namespace = css_ontology.get_namespace(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_BASE_NAMESPACE)


# with css_ontology:
class ExtendedThing(Thing):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Some dictionaries related to the Data Properties are initialized
        self.data_properties_dict = set()
        self.data_properties_types_dict = {}
        self.data_properties_values_dict = {}

        # The reference to the associated AAS model element will be necessary
        self.aas_sme_ref = None

        # The data properties associated to this instance class are found
        self.seek_associated_data_properties()

    def seek_associated_data_properties(self):
        """
        This method seeks possible limited values for attributes of Capability, in order to validate when the attribute
        value is assigned. The possible values for limited attributes are stored in a global dictionary.
        """
        for prop in css_ontology.properties():
            if isinstance(prop, DataPropertyClass):
                if CapabilitySkillOntologyUtils.check_whether_part_of_domain(self, prop.domain):
                    # First, the data property object is saved
                    self.data_properties_dict.add(prop)
                    # The possible values of the data properties are also stored
                    for range_value in prop.range:
                        if isinstance(range_value, DatatypeClass):
                            possible_values = CapabilitySkillOntologyUtils.get_possible_values_of_datatype(range_value)
                            if possible_values is not None:
                                self.data_properties_types_dict[prop.name] = possible_values
                        else:
                            self.data_properties_types_dict[prop.name] = range_value

    def check_valid_data_property_value(self, data_property_name, data_property_value):
        """
        This method checks if the given value of a given data property is valid, in terms of the type of the data. If
        the data property type is simple, the type will be directly checked, and in case of an enumeration, if the given
        value is within the possible values will be checked.

        Args:
            data_property_name (str): the name of the data property.
            data_property_value (str): the value of the data property to be checked.
        """
        if data_property_name not in self.data_properties_types_dict:
            _logger.warning("The data property does not exist in this OWL class.")
        else:
            data_property_type = self.data_properties_types_dict[data_property_name]
            if isinstance(data_property_type, set):
                if data_property_value not in data_property_type:
                    raise OntologyInstanceCreationError("The data property value {} for the OWL class {} is not within "
                                                        "the valid values.".format(data_property_value, self))
            else:
                if not isinstance(data_property_value, data_property_type):
                    raise OntologyInstanceCreationError("The data property value {} for the OWL class {} is not valid."
                                                        .format(data_property_value, self))

    def set_data_property_value(self, data_property_name, data_property_value):
        """
        This method sets the value of a data property associated to the self instance only if the given value is within
         the possible values for this attribute.

        Args:
            data_property_name (str): the name of the data property.
            data_property_value (str): the value of the data property to be stored.
        """
        self.check_valid_data_property_value(data_property_name, data_property_value)
        # If the result of the check is True the execution reaches this point
        self.data_properties_values_dict[data_property_name] = data_property_value

    def get_data_properties_names(self):
        """
        This method gets all names of the data properties associated to the self instance class (obtained during the
        initialization of the class).

        Returns:
            list(str): list with all names of the data properties.
        """
        data_properties_iris = []
        for prop in self.data_properties_dict:
            data_properties_iris.append(prop.name)
        return data_properties_iris

    def set_aas_sme_ref(self, aas_ref):
        """
        This method sets the AAS submodel element (SME) related to this instance class.

        Args:
            aas_ref (str): reference to the submodel element of the AAS model.
        """
        self.aas_sme_ref = aas_ref


class Capability(Thing, ExtendedThing):
    """
    This class represent the OWL class for Capabilities. It contains all necessary methods to ensure the correct
    execution of SMIA software.
    """
    # The namespace of the base CSS ontology must be defined
    namespace = base_namespace

    # The associated SubmodelElement class of the AAS is also defined
    aas_sme_class = basyx.aas.model.Capability

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def check_instance(self):
        """
        This method checks whether the Capability instance is valid: if the required attributes are set and if all the
        added properties are valid. In case of invalid Capability, it raises the exception related to the checking error.
        """
        if self.has_lifecycle is None:
            raise OntologyCheckingAttributeError("The 'has_lifecycle' attribute is required in "
                                                 "Capability instances.", self)
        for skill in self.isRealizedBy:
            if not isinstance(skill, Skill):
                raise OntologyCheckingPropertyError("The instance {} is added in 'isRealizedBy' and it is not a "
                                                    "Skill".format(skill), 'isRealizedBy', skill)
        for constraint in self.isRestrictedBy:
            if not isinstance(constraint, CapabilityConstraint):
                raise OntologyCheckingPropertyError("The instance {} is added in 'isRestrictedBy' and it is not a "
                                                    "CapabilityConstraint".format(constraint), 'isRestrictedBy',
                                                    constraint)
        # TODO añadir validacion de que tiene una referencia de AAS valida
        # TODO pensar mas tipos de validaciones


class CapabilityConstraint(Thing, ExtendedThing):
    # The namespace of the base CSS ontology must be defined
    namespace = base_namespace

    # The associated SubmodelElement class of the AAS is also defined
    # aas_sme_class = basyx.aas.model.SubmodelElement
    aas_sme_class = extended_submodel.ExtendedCapabilityConstraint

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    # TODO PENSAR METODOS PARA CONSTRAINTS


class Skill(Thing, ExtendedThing):
    # The namespace of the base CSS ontology must be defined
    namespace = base_namespace

    # The associated SubmodelElement class of the AAS is also defined
    aas_sme_class = extended_submodel.ExtendedSkill

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_instance(self):
        """
        This method checks whether the Skill instance is valid: if the required attributes are set and if all the added
         properties are valid. In case of invalid Skill, it raises the exception related to the checking error.
        """
        if len(self.accessibleThrough) == 0:
            raise OntologyCheckingAttributeError(
                "The instance {} does not have any SkillInterface associated".format(self), self)
        # TODO pensar mas comprobaciones


class SkillInterface(Thing, ExtendedThing):
    # The namespace of the base CSS ontology must be defined
    namespace = base_namespace

    # The associated SubmodelElement class of the AAS is also defined
    aas_sme_class = extended_submodel.ExtendedSkillInterface

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_instance(self):
        """
        This method checks whether the SkillInterface instance is valid: if the required attributes are set and if all
        the added properties are valid. In case of invalid SkillInterface, it raises the exception related to the
        checking error.
        """
        pass
        # TODO pensar mas comprobaciones
