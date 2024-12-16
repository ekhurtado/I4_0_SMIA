from os import path

import basyx
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.model import ModelReference

from utilities import AASModelUtils, OntologyUtils
from aas_ontology_reader_info import AASOntologyReaderInfo


class AASOntologyReader:

    def __init__(self):
        self.object_store = None
        self.aas_model_utils = None
        self.ontology_utils = None

    @staticmethod
    def read_aas_model_object_store(aas_model_path):
        """
        This method reads the AAS model according to the selected serialization format.

        Args:
            aas_model_path (string): Path to the AAS model file.

        Returns:
            basyx.aas.model.DictObjectStore:  object with all Python elements of the AAS model.
        """
        object_store = None
        aas_model_file_name, aas_model_file_extension = path.splitext(aas_model_path)
        try:
            # The AAS model is read depending on the serialization format (extension of the AAS model file)
            if aas_model_file_extension == '.json':
                object_store = basyx.aas.adapter.json.read_aas_json_file(aas_model_path)
            elif aas_model_file_extension == '.xml':
                object_store = basyx.aas.adapter.xml.read_aas_xml_file(aas_model_path)
            elif aas_model_file_extension == '.aasx':
                with aasx.AASXReader(aas_model_path) as reader:
                    # Read all contained AAS objects and all referenced auxiliary files
                    object_store = model.DictObjectStore()
                    suppl_file_store = aasx.DictSupplementaryFileContainer()
                    reader.read_into(object_store=object_store,
                                     file_store=suppl_file_store)
        except ValueError as e:
            print("Failed to read AAS model: invalid file.")
            print(e)
        else:
            return object_store

    async def read_ontology_based_aas_model(self, aas_model_path, ontology_file_path):
        """
        This method reads an AAS model based on the ontology: all instances defined in the ontology are created and, if
         they are linked in the AAS model, they are also joined within the instances of the ontology.

        Args:
            aas_model_path (string): Path to the AAS model file.
            ontology_file_path (string): Path to the ontology OWL file.
        """
        # Depending on the serialization format, the required BaSyx read method shall be executed. This will store all
        # the received elements of the model in the corresponding global object of the agent.
        self.object_store = AASOntologyReader.read_aas_model_object_store(aas_model_path)
        self.aas_model_utils = AASModelUtils(self.object_store)
        self.ontology_utils = OntologyUtils(ontology_file_path)

        # When the object store is created, the required values and information is obtained from the AAS model
        print("Reading the AAS model to get all defined ontology elements...")
        await self.get_and_save_ontology_classes_information()

        print("Reading the AAS model to get all relationships between ontology elements...")
        await self.get_and_save_ontology_relationships_information()

        print("AAS model read.")

    async def get_and_save_ontology_classes_information(self):
        """
        This method stores all the information related to the class elements defined in the ontology. Since the data is
         defined in the AAS model, it will be used to check whether the required data defined in the ontology has been
          added in the AAS model. If the elements are valid, they will be created their associated ontology instance and
          the AAS SubmodelElement will be associated to these instances.
        """
        for ontology_class_iri in AASOntologyReaderInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
            await self.check_and_create_instances_by_iri(ontology_class_iri)

    async def get_and_save_ontology_relationships_information(self):
        """
        This method stores all the information related to the relationships between elements defined in the ontology.
        Since the data is defined in the AAS model, it will be used to check whether the linked elements have their
        associated ontology instance (created just before the execution of this method).
        """
        for ontology_relationship_iri in AASOntologyReaderInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS:
            await self.check_and_create_relationship_by_iri(ontology_relationship_iri)

    async def check_and_create_instances_by_iri(self, ontology_class_iri):
        """
        This method checks the relationship between two elements and, if it is valid, it creates it (it connects the
        related ontology instances through the appropriate ObjectProperty).

        Args:
            ontology_class_iri (str): identifier in form of IRI for the element within the CSS ontology.
        """
        sme_list = None
        try:
            sme_list = await self.aas_model_utils.get_submodel_elements_by_semantic_id(ontology_class_iri)
        except Exception as e:
            print(e)

        for submodel_elem in sme_list:
            try:
                # For each SubmodelElement an instance within the CSS ontology is created
                await self.create_ontology_instance_from_sme_element(submodel_elem, ontology_class_iri)
                # created_instance = await self.myagent.css_ontology.create_ontology_object_instance(ontology_class,
                #                                                                                    submodel_elem.id_short)

                # The submodel element will be converted from the Basyx class to the extended one (of the SMIA approach)
                await self.convert_sme_class_to_extended_by_iri(submodel_elem, ontology_class_iri)
            except Exception as e:
                print(e)

    async def create_ontology_instance_from_sme_element(self, sme_elem, ontology_iri):
        """
        This method creates the ontology instance from the AAS Submodel Element.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model with all configured data.
            ontology_iri (str): IRI of the ontology class of the instance to be created.
        """
        try:
            ontology_class = await self.ontology_utils.get_ontology_class_by_iri(ontology_iri)
            # The class is used as constructor to build the instance of the CSS ontology
            created_instance = await self.ontology_utils.create_ontology_object_instance(ontology_class,
                                                                                         sme_elem.id_short)

            await self.add_ontology_required_information(sme_elem, created_instance)

        except Exception as e:
            print(e)

    @staticmethod
    async def add_ontology_required_information(aas_model_elem, ontology_instance):
        """
        This method adds the required information defined in the ontology to the given instance. All information is
        obtained from given the AAS Submodel Element.

        Args:
            aas_model_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model with all configured data.
            ontology_instance (ThingClass): instance class on which the information will be added.
        """
        # The ontology may state that it is required to add some attributes
        ontology_required_value_iris = ontology_instance.get_data_properties_iris()
        for required_value_iri in ontology_required_value_iris:
            required_value = aas_model_elem.get_qualifier_value_by_semantic_id(required_value_iri)
            required_value_name = ontology_instance.get_data_property_name_by_iri(required_value_iri)
            ontology_instance.set_data_property_value(required_value_name, required_value)
        # The Submodel Element is also added to be available to the ontology instance object in form of a reference
        ontology_instance.set_aas_sme_ref(ModelReference.from_referable(aas_model_elem))

    @staticmethod
    async def convert_sme_class_to_extended_by_iri(sme_elem, ontology_iri):
        """
        This method converts the class of a SubmodelElement to the Extended class, in order to add the required method
        to be used during the execution of the software. The extended class is obtained from from the CSS ontology utils
         class using the IRI of the ontology class.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model to be modified.
            ontology_iri (iri): ontology class IRI.
        """
        current_class = sme_elem.__class__
        new_class = AASOntologyReaderInfo.CSS_ONTOLOGY_AAS_MODEL_LINK[ontology_iri]
        sme_elem.__class__ = new_class
        # The old class new to be added to the Extended class
        sme_elem.add_old_sme_class(current_class)

    async def check_and_create_relationship_by_iri(self, relationship_iri):
        """
        This method checks the relationship between two elements and, if it is valid, it creates it (it connects the
        related ontology instances through the appropriate ObjectProperty).

        Args:
            relationship_iri (str): identifier in form of IRI for the relationship within the CSS ontology.
        """
        rels_list, rel_ontology_class, domain_aas_class, range_aas_class = None, None, None, None
        try:
            rels_list = await self.aas_model_utils.get_submodel_elements_by_semantic_id(
                relationship_iri, basyx.aas.model.RelationshipElement)
            rel_ontology_class = await self.ontology_utils.get_ontology_class_by_iri(relationship_iri)
            # The required AAS classes for the elements within this relationship is obtained from the CSS ontology
            domain_aas_class, range_aas_class = self.ontology_utils.get_aas_classes_from_object_property(
                rel_ontology_class)
        except Exception as e:
            print(e)

        domain_aas_elem, range_aas_elem = None, None
        for rel in rels_list:

            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            try:
                domain_aas_elem, range_aas_elem = await self.aas_model_utils.get_elements_from_relationship(
                    rel, domain_aas_class, range_aas_class)
                # It is checked if the capability and the skill have the required semanticIDs within the ontology
                # if not domain_aas_elem.check_semantic_id_exist(domain_class_iri):
                domain_aas_elem.get_semantic_id_of_css_ontology()
                range_aas_elem.get_semantic_id_of_css_ontology()

                # When both are checked, if the ontology instances exist the link is set in the ontology
                await self.ontology_utils.add_object_property_to_instances_by_names(
                    rel_ontology_class.name, domain_aas_elem.id_short, range_aas_elem.id_short)

            except Exception as e:
                print(e)
