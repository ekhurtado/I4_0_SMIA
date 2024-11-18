import inspect

from owlready2 import Thing, get_ontology, DatatypeProperty, DataPropertyClass, ThingClass, OneOf, CallbackList, \
    DatatypeClass

from capability_skill_onto_utils import CapabilitySkillOntologyUtils, CapabilitySkillOntologyNS

# css_ontology = get_ontology("CSS-Ontology-RDF-XML.owl")
# css_ontology = get_ontology("CSS-ontology-module.owl")
css_ontology = get_ontology("CSS-ontology-smia.owl")
# css_ontology = None

base_namespace = css_ontology.get_namespace(CapabilitySkillOntologyNS.CSS_NAMESPACE)

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
        self.lifecycle = lifecycle_value

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

    def method_skill(self):
        print("method of skill")


class SkillInterface(Thing):
    namespace = base_namespace

    def method_skill_interface(self):
        print("method of skill interface")

