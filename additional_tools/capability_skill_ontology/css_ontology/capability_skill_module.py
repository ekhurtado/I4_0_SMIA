from owlready2 import Thing, get_ontology, DataPropertyClass, DatatypeClass

from capability_skill_onto_utils import CapabilitySkillOntologyUtils, CapabilitySkillOntologyInfo, OntologyExceptions

# css_ontology = get_ontology("CSS-Ontology-RDF-XML.owl")
# css_ontology = get_ontology("CSS-ontology-module.owl")
css_ontology = get_ontology(CapabilitySkillOntologyInfo.ONTOLOGY_FILE_PATH)
base_namespace = css_ontology.get_namespace(CapabilitySkillOntologyInfo.CSS_NAMESPACE)

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

    def check_instance(self):
        """
        This method checks whether the Capability instance is valid: if the required attributes are set and if all the
        added properties are valid. In case of invalid Capability, it raises the exception related to the checking error.
        """
        if self.has_lifecycle is None:
            # TODO CAMBIARLO EN SMIA (generar una excepcion custom en la que se añade la razon de que haya salido mal
            #  el chequeo, y la clase a eliminar)
            # raise AttributeError("has_lifecycle attribute is required in Capability instances.", self)
            raise OntologyExceptions.CheckingPropertyError("The 'has_lifecycle' attribute is required in "
                                                            "Capability instances.", self)
        for skill in self.isRealizedBy:
            if not isinstance(skill, Skill):
                raise OntologyExceptions.CheckingPropertyError("The instance {} is added in 'isRealizedBy' and it is "
                                                               "not a Skill".format(skill), 'isRealizedBy', skill)
        for constraint in self.isRestrictedBy:
            if not isinstance(constraint, CapabilityConstraint):
                raise OntologyExceptions.CheckingPropertyError("The instance {} is added in 'isRestrictedBy' and it is"
                                                                " not a CapabilityConstraint".format(constraint),
                                                               'isRestrictedBy', constraint)

        # TODO pensar mas tipos de validaciones

    # TODO ELIMINAR
    def method(self):
        print("method of capability")

    def method2(self):
        print("method2 of capability")

class CapabilityConstraint(Thing):
    namespace = base_namespace

    def a(self):
        print()

class Skill(Thing):
    namespace = base_namespace

    def check_instance(self):
        """
        This method checks whether the Skill instance is valid: if the required attributes are set and if all the added
         properties are valid. In case of invalid Skill, it raises the exception related to the checking error.
        """
        if len(self.accessibleThrough) == 0:
            raise OntologyExceptions.OntologyCheckingAttributeError("The instance {} does not have any SkillInterface "
                                                            "associated".format(self), self)
        # TODO pensar mas comprobaciones

    def method_skill(self):
        print("method of skill")




class SkillInterface(Thing):
    namespace = base_namespace

    def check_instance(self):
        """
        This method checks whether the SkillInterface instance is valid: if the required attributes are set and if all
        the added properties are valid. In case of invalid SkillInterface, it raises the exception related to the
        checking error.
        """
        pass
        # TODO pensar mas comprobaciones

    def method_skill_interface(self):
        print("method of skill interface")

