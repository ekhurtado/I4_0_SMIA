from owlready2 import get_ontology, OwlReadyOntologyParsingError, sync_reasoner_pellet, \
    OwlReadyInconsistentOntologyError, ThingClass, Ontology, ObjectPropertyClass, destroy_entity

from tests.capability_skill_onto_utils import CapabilitySkillOntologyInfo, OntologyExceptions


class CapabilitySkillOntology:
    """
    This class contains related methods of the Capability-Skill ontology.
    """

    def __init__(self):
        self.ontology: Ontology = None

    async def initialize_ontology(self):

        # Import only ontologies in RDF/XML, OWL/XML or NTriples format (others do not work, e.g. Turtle)
        self.ontology = get_ontology(CapabilitySkillOntologyInfo.ONTOLOGY_FILE_PATH)
        # self.ontology = get_ontology('CSS-Ontology.owl')  # ERROR invalid format
        # self.ontology = get_ontology('CASK-RDF.owl')  # ERROR download
        try:
            self.ontology.load()
        except FileNotFoundError as e:
            print("ERROR: The OWL file of the ontology does not exist.")
            self.ontology = None
            return
        except OwlReadyOntologyParsingError as e:
            if 'NTriples' in e.args[0]:
                print("ERROR: The OWL file is invalid (only RDF/XML, OWL/XML or NTriples format are accepted).")
            if 'Cannot download' in e.args[0]:
                print("ERROR: The OWL has defined imported ontologies that cannot be downloaded.")
            self.ontology = None
            return
        # The ontology has been loaded
        print("CSS ontology initialized")

    # TODO ELIMINAR
    async def print_onto_data(self, namespace):

        print("READING ONTOLOGY:")
        print("-----------------")
        print("Classes: {}".format(list(self.ontology.classes())))
        print("Object properties: {}".format(list(self.ontology.object_properties())))
        print("Data properties: {}".format(list(self.ontology.data_properties())))
        print("Annotation properties: {}".format(list(self.ontology.annotation_properties())))
        print("Properties: {}".format(list(self.ontology.properties())))
        print("Namespace (base iri): {}".format(self.ontology.base_iri))

        await self.print_onto_ns_data(namespace)
        print("-----------------")

    async def print_onto_ns_data(self, namespace):
        if namespace:
            ns = self.ontology.get_namespace(namespace)
        else:
            # El namespace por defecto es SMIA en esta ontologia
            # TODO si mas adelante dejamos definir otras ontologias extendidas de la nuestra, esto habria que cambiarlo
            ns = self.ontology

        print("Ontology namespace data:")
        print("\tCapability class: {}".format(ns.Capability))
        print("\tSkill class: {}".format(ns.Skill))
        print("\tCap-Skill relationship class: {}".format(ns.isRealizedBy))
        print("\tSkillInterface class: {}".format(ns.SkillInterface))
        print("\tCapabilityConstraint class: {}".format(ns.CapabilityConstraint))
        print("\tSkill-State Machine relationship class: {}".format(ns.behaviorConformsTo))

        print("\tSMIA AgentCapability class: {}".format(ns.AgentCapability))
        print("\tSMIA AssetCapability class: {}".format(ns.AssetCapability))
        print("\tSMIA Capability hasLifecycle attribute: {}".format(ns.hasLifecycle))
        print()

    # TODO FIN DE ELIMINAR

    async def execute_ontology_reasoner(self, debug=False):
        """
        This method executes the reasoner for the ontology.

        Args:
            debug (bool): if it is true, the inconsistency of the ontology is explained.
        """
        debug_value = 1
        if debug is True:
            debug_value = 2

        try:
            with self.ontology:
                sync_reasoner_pellet(debug=debug_value)
        except OwlReadyInconsistentOntologyError as e:
            print("ERROR: INCONSISTENT ONTOLOGY!")
            print(e)
            raise OwlReadyInconsistentOntologyError(e)

    async def get_ontology_class_by_iri(self, class_iri):
        """
        This method gets the class within the ontology by its IRI.

        Args:
            class_iri (str): the IRI of the class to be found.

        Returns:
            object: ontology class object.
        """
        result_classes = self.ontology.search(iri=class_iri)
        if len(result_classes) == 0:
            print("ERROR: clase no encontrada con IRI [{}]".format(class_iri))
            return None
        if len(result_classes) > 1:
            print("WARNING: HAY MAS DE UNA CLASE CON IRI [{}], CUIDADO".format(class_iri))
        return result_classes[0]

    async def create_ontology_object_instance(self, class_object, instance_name):
        """
        This method creates a new object instance (individual) within the ontology. To this end, a ThingClass is
        required.
        
        Args:
            class_object (ThingClass): ontology class of the instance.
            instance_name (str): name of the instance.

        Returns:
            ThingClass: created instance object.
        """
        if not isinstance(class_object, ThingClass):
            print("ERROR: the individual cannot be created because it is not a Thing class.")
            return None
        else:
            # The object of the class is used as constructor of the instance
            return class_object(instance_name)

    async def seek_instance_by_name(self, instance_name):
        """
        This method returns an object instance within the ontology by its name.

        Args:
            instance_name (str): name of the instance.

        Returns:
            ThingClass: class of the instance to be found (None if it is not found).
        """
        for instance_class in self.ontology.individuals():
            if instance_class.name == instance_name:
                return instance_class
        return None

    async def add_object_property_to_instances_by_iris(self, object_property, domain_object_name, range_object_name):
        """
        This method adds a new ObjectProperty to link two instances within the ontology. Checks are performed to ensure
        that the ObjectProperty is valid to link the instances.

        Args:
            object_property (ObjectPropertyClass): class of the ObjectProperty to be added.
            domain_object_name (str): name of the instance to which the ObjectProperty will be added.
            range_object_name (str): name of the instance to be added to the domain instance within the given property.
        """
        # Preliminary checks are performed
        if domain_object_name is None or range_object_name is None:
            print("ERROR: the object property cannot be added because the domain or range are invalid.")
            return
        if not isinstance(object_property, ObjectPropertyClass):
            print("ERROR: the object property cannot be added because the domain or range are invalid.")
            return
        domain_instance = await self.seek_instance_by_name(domain_object_name)
        range_instance = await self.seek_instance_by_name(range_object_name)
        try:
            getattr(domain_instance, object_property.name).append(range_instance)
        except AttributeError as e:
            print("ERROR: The class {} does not have the attribute {}".format(domain_instance, object_property))

    async def check_instance_by_name(self, instance_name):
        """
        This method checks an instance and removes the invalid objects. In case the instance itself is invalid, it is
        removed from the ontology. If any of the properties are invalid they are removed from this instance.

        Args:
            instance_name (str): name of the instance to be checked.
        """
        instance_object = await self.seek_instance_by_name(instance_name)
        if instance_object is None:
            return
        try:
            instance_object.check_instance()
        except OntologyExceptions.CheckingAttributeError as e:
            destroy_entity(e.invalid_instance)
        except OntologyExceptions.CheckingPropertyError as e:
            getattr(instance_object, e.concerned_property_name).remove(e.invalid_instance)

    async def get_class_by_name(self, class_name):
        class_object = getattr(self.ontology, class_name)
        if class_object is None:
            base_namespace = self.ontology.get_namespace(CapabilitySkillOntologyInfo.CSS_NAMESPACE)
            class_object = getattr(base_namespace, class_name)
        return class_object

    async def get_all_subclasses_of_class(self, owl_class):
        subclasses = list(owl_class.subclasses())
        all_subclasses = subclasses[:]

        for subclass in subclasses:
            all_subclasses.extend(await self.get_all_subclasses_of_class(subclass))

        return all_subclasses