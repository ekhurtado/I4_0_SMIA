import basyx
from basyx.aas.util import traversal
from owlready2 import ThingClass, OneOf


class AASModelUtils:

    def __init__(self, object_store):
        self.aas_model_object_store = object_store

    async def get_submodel_elements_by_semantic_id(self, semantic_id_external_ref, sme_class=None):
        """
        This method gets all SubmodelElements by the semantic id in form of an external reference. The SubmodelElements
        to obtain can be filtered by the meta-model class.

        Args:
            semantic_id_external_ref (str): semantic id in form of an external reference
            sme_class (basyx.aas.model.SubmodelElement): Submodel Element class of the elements to be found (None if no
             filtering is required).

        Returns:
            list(basyx.aas.model.SubmodelElement): list with all SubmodelElements of the given class.
        """
        if sme_class is None:
            sme_class = basyx.aas.model.SubmodelElement
        rels_elements = []
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(aas_object):
                    if isinstance(submodel_element, sme_class):
                        if submodel_element.check_semantic_id_exist(semantic_id_external_ref):
                            rels_elements.append(submodel_element)
                        if isinstance(submodel_element, basyx.aas.model.Operation):
                            # In case of Operation, OperationVariables need to be analyzed
                            rels_elements.extend(submodel_element.get_operation_variables_by_semantic_id(
                                semantic_id_external_ref))
        return rels_elements

    async def get_elements_from_relationship(self, rel_element, first_elem_class=None, second_elem_class=None):
        """
        This method returns the objects of a given Relationship element taking into account the type of class that is
        required for the objects referenced within the relationship. The objects will be returned in the order
        specified by the classes, no matter in which order they are defined in the AAS model (in the case of not
        specifying any class, it is returned in the original order).

        Args:
            rel_element (basyx.aas.model.RelationshipElement): Python object of the RelationshipElement.
            first_elem_class (basyx.aas.model.SubmodelElement): Class required for the first element returned.
            second_elem_class (basyx.aas.model.SubmodelElement): Class required for the second element returned.

        Returns:
            basyx.aas.model.SubmodelElement, basyx.aas.model.SubmodelElement: SME Python objects with the required format.
        """
        # Using the references within the relationship, both SubmodelElement are obtained
        first_rel_elem = rel_element.first.resolve(self.aas_model_object_store)
        second_rel_elem = rel_element.second.resolve(self.aas_model_object_store)
        if first_rel_elem is None or second_rel_elem is None:
            print("Elements of the relationship {} does not exist in the AAS model".format(rel_element.id_short))
        if None in (first_rel_elem, second_rel_elem):
            # If no one is required, it simply returns the elements
            return first_rel_elem, second_rel_elem
        if None not in (first_rel_elem, second_rel_elem):
            # If both are required, both have to be checked
            if isinstance(first_rel_elem, first_elem_class) and isinstance(second_rel_elem, second_elem_class):
                return first_rel_elem, second_rel_elem
            elif isinstance(first_rel_elem, second_elem_class) and isinstance(second_rel_elem, first_elem_class):
                return second_rel_elem, first_rel_elem
            else:
                print("Elements of the relationship {} are not exist of the required classes {}, {}".format(
                    rel_element.id_short, first_elem_class, second_elem_class))
        if first_elem_class is not None:
            if isinstance(first_rel_elem, first_elem_class):
                return first_rel_elem, second_rel_elem
            elif isinstance(second_rel_elem, first_elem_class):
                return second_rel_elem, first_rel_elem
            else:
                print("The element {} within the relationship {} is not of the required class {}".format(
                    first_rel_elem, rel_element.id_short, first_elem_class))
        if second_elem_class is not None:
            if isinstance(first_rel_elem, second_elem_class):
                return second_rel_elem, first_rel_elem
            elif isinstance(second_rel_elem, second_elem_class):
                return first_rel_elem, second_rel_elem
            else:
                print("The element {} within the relationship {} is not of the required class {}".format(
                    second_rel_elem, rel_element.id_short, second_elem_class))


class OntologyUtils:

    def __init__(self, ontology):
        self.ontology = ontology
        self.ontology.load()

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
            print("ERROR: class not found with IRI [{}]".format(class_iri))
            return None
        if len(result_classes) > 1:
            print("WARNING: THERE IS MORE THAN ONE CLASS WITH IRI [{}], BE CAREFUL".format(class_iri))
        return result_classes[0]

    async def get_ontology_instance_by_name(self, instance_name):
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
            print("ERROR: the instance cannot be created because the given constructor is not of ThingClass.")
        else:
            # The object of the class is used as constructor of the instance
            return class_object(instance_name)

    @staticmethod
    def get_aas_classes_from_object_property(object_property_class):
        """
        This method gets the AAS class related to the of the ontology classes of a given Object Property. If the
        attribute of the AAS class does not exist, it raises an exception.

        Args:
            object_property_class (ObjectPropertyClass): class object of the ObjectProperty.

        Returns:
            object, object: AAS class value of the domain and range ontology classes.
        """
        if object_property_class is None:
            print("The object property object {} is None".format(object_property_class))
        if len(object_property_class.domain) == 0 or len(object_property_class.range) == 0:
            print("The domain or range of object property {} are empty".format(object_property_class))
        try:
            for domain_class in object_property_class.domain:
                if hasattr(domain_class, 'get_associated_aas_class'):
                    domain_aas_class = domain_class.get_associated_aas_class()
                    break
            else:
                # In this case no domain class is of the defined CSS model of the SMIA approach.
                print("The domain of object property object {} does not have any associated "
                                           "AAS model classes defined".format(object_property_class))
            for range_class in object_property_class.range:
                if hasattr(range_class, 'get_associated_aas_class'):
                    range_aas_class = range_class.get_associated_aas_class()
                    break
            else:
                # In this case no range class is of the defined CSS model of the SMIA approach.
                print("The range of object property object {} does not have any associated "
                                           "AAS model classes defined".format(object_property_class))
            return domain_aas_class, range_aas_class
        except KeyError as e:
            print(e)

    async def add_object_property_to_instances_by_names(self, object_property_name, domain_object_name, range_object_name):
        """
        This method adds a new ObjectProperty to link two instances within the ontology. Checks are performed to ensure
        that the ObjectProperty is valid to link the instances.

        Args:
            object_property_name (str): name of the ObjectProperty to be added.
            domain_object_name (str): name of the instance to which the ObjectProperty will be added.
            range_object_name (str): name of the instance to be added to the domain instance within the given property.
        """
        # Preliminary checks are performed
        if domain_object_name is None or range_object_name is None:
            print("The object property cannot be added because the domain or range are invalid.")
        domain_instance = await self.get_ontology_instance_by_name(domain_object_name)
        range_instance = await self.get_ontology_instance_by_name(range_object_name)
        try:
            getattr(domain_instance, object_property_name).append(range_instance)
        except AttributeError as e:
            print("ERROR: The class {} does not have the attribute {}".format(domain_instance, object_property_name))
            print(e)

    @staticmethod
    def check_whether_part_of_domain(owl_instance, domain):
        """
        This method checks whether a given instance class is part of a given domain.

        Args:
            owl_instance (ThingClass): instance of the OWL class to be checked.
            domain (CallbackList): list of all classes within the given domain.

        Returns:
            bool: result of the check.
        """
        for domain_class in domain:
            for owl_class in owl_instance.is_a:
                if owl_class == domain_class or domain_class in owl_class.ancestors():
                    return True
        return False

    @staticmethod
    def get_possible_values_of_datatype(datatype):
        """
        This method returns all possible values of an OWL data type. If the data type does not have the equivalent
        'OneOf', so the values do not need to be constrained and validated, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            set: possible values of datatype in form of a list of strings.
        """
        possible_values = set()
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.add(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

    @staticmethod
    def check_and_get_xsd_datatypes(datatype):
        """
        This method checks whether the given OWL data type is one of those defined in XSD and, if true, returns the
        associated data type. If false, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            object: value of datatype defined in XSD (None if it is not found).
        """
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if equivalent == str:
                    return str
            return None

