import asyncio
import logging
import sys

import basyx.aas.adapter.xml
import basyx.aas.adapter.json
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.model import ModelReference
from owlready2 import ThingClass
from spade.behaviour import OneShotBehaviour
from tqdm.asyncio import tqdm

from aas_model import extended_submodel
from aas_model.extended_submodel import ExtendedSkill, ExtendedSkillInterface, ExtendedCapabilityConstraint, \
    ExtendedComplexSkillInterface, ExtendedComplexSkill, ExtendedSimpleSkill, ExtendedSimpleSkillInterface, \
    ExtendedCapability
from assetconnection.http_asset_connection import HTTPAssetConnection
from logic.exceptions import AASModelReadingError, AASModelOntologyError, \
    OntologyReadingError, CriticalError
from utilities import configmap_utils
from css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils, AssetInterfacesInfo, \
    CapabilitySkillOntologyInfo, CSSModelAASModelInfo

_logger = logging.getLogger(__name__)


class InitAASModelBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for reading the AAS model to obtain all submodels, submodel elements
     and concept descriptions. The necessary checks are performed to ensure the valid  initial conditions to start the
     running state of the DT. The AAS model is defined in the ConfigMap associated to the deployed container and in
     order to successfully read the definition in any serialization format (JSON or XML), BaSyx Python SDK will be used.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        self.progress_bar = None

        # The counters for all type of analyzed elements are initialized
        self.analyzed_capabilities = []
        self.analyzed_capability_constraints = []
        self.analyzed_skills = []
        self.analyzed_skill_interfaces = []
        self.analyzed_asset_connections = []
        self.errors_found = []

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # First, the AAS model serialization format is obtained
        aas_model_serialization_format = configmap_utils.get_aas_general_property('model.serialization')

        # Depending on the serialization format, the required BaSyx read method shall be executed. This will store all
        # the received elements of the model in the corresponding global object of the agent.
        object_store = await self.read_aas_model_object_store(aas_model_serialization_format)
        await self.myagent.aas_model.set_aas_model_object_store(object_store)

        # A progress bar is used for showing how the AAS model is being read.
        await self.create_progress_bar_object()

        # When the object store is created, the required values and information is obtained from the AAS model
        _logger.info("Reading the AAS model to get all defined ontology elements...")
        await self.get_and_save_ontology_classes_information()

        await asyncio.sleep(.5)
        _logger.info("Reading the AAS model to get all relationships between ontology elements...")
        await self.get_and_save_ontology_relationships_information()

        # After the AAS model has been analyzed, the AssetConnection class can be specified
        _logger.info("Reading the AAS model to get all asset connections...")
        await self.get_and_configure_asset_connections()

        # The progress bar is closed
        self.progress_bar.close()
        await asyncio.sleep(1)

        # The final results of the analysis are shown
        await self.print_analysis_result()

        _logger.info("AAS model initialized.")
        self.exit_code = 0

    async def read_aas_model_object_store(self, aas_model_serialization_format):
        """
        This method reads the AAS model according to the selected serialization format.

        Args:
            aas_model_serialization_format (str): serialization format of the AAS model.

        Returns:
            basyx.aas.model.DictObjectStore:  object with all Python elements of the AAS model.
        """
        object_store = None
        try:
            if aas_model_serialization_format == 'JSON':
                object_store = basyx.aas.adapter.json.read_aas_json_file(configmap_utils.get_aas_model_filepath())
            elif aas_model_serialization_format == 'XML':
                object_store = basyx.aas.adapter.xml.read_aas_xml_file(configmap_utils.get_aas_model_filepath())
            elif aas_model_serialization_format == 'AASX':
                    with aasx.AASXReader(configmap_utils.get_aas_model_filepath()) as reader:
                        # Read all contained AAS objects and all referenced auxiliary files
                        object_store = model.DictObjectStore()
                        suppl_file_store = aasx.DictSupplementaryFileContainer()
                        reader.read_into(object_store=object_store,
                                         file_store=suppl_file_store)
        except ValueError as e:
            _logger.error("Failed to read AAS model: invalid file.")
            _logger.error(e)
            raise CriticalError("Failed to read AAS model: invalid file.")
        if object_store is None or len(object_store) == 0:
            raise CriticalError("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                          "metamodel.")
        else:
            return object_store


    # async def get_and_save_capabilities_information(self):
    #     """
    #     This method stores all the information related to the Capabilities. Since the data is defined in the AAS model,
    #     it will be used to create the Capability instances within the proposed Capability-Skill-Service ontology.
    #     """
    #     # All types of Capabilities are obtained
    #     # TODO de momento se hace manualmente. Hay que pensar si queremos dejar al usuario añadir el semanticID que
    #     #  quiera de la ontologia, o solo hasta el nivel de Agent o AssetCapability. Es decir, todas las capacidades
    #     #  seran de esos dos tipos en el AAS Model, pero despues en la ontología se podrán estructurar las capacidades
    #     #  como se quiera. Otra opcion es primero estructurar la ontologia y despues utilizar esos IDs únicos de cada
    #     #  instancia para añadirlo en el AAS Model (para esta forma habria que leer el AAS model junto con la ontologia,
    #     #  para primero recoger los IRIs de la ontologia y despues realizar la busqueda en el AAS model)
    #     # First, the Capabilities are analyzed
    #     cap_iris_list = [CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI]
    #     cap_ontology_elem = await self.myagent.css_ontology.get_ontology_class_by_iri(
    #         CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
    #     cap_iris_list.extend(
    #         await self.myagent.css_ontology.get_all_subclasses_iris_of_class(cap_ontology_elem))
    #     cap_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id_list(cap_iris_list,
    #                                                                                       basyx.aas.model.Capability)
    #     for cap in cap_list:
    #         await self.add_step_progress_bar()
    #
    #         # For each Capability an instance within the CSS ontology is created
    #         ontology_iri = cap.get_semantic_id_of_css_ontology()
    #         await self.create_ontology_instance_from_sme_element(cap, ontology_iri)
    #
    #         # The counter for analyzed capabilities is increased
    #         self.analyzed_capabilities.append(cap.id_short)
    #
    #     # Once all Capabilities have been analyzed, the capability-related elements will be analyzed (i.e. constraints)
    #     cap_constraint_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
    #         CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
    #     for constraint in cap_constraint_list:
    #         # For each Capability Constraint an instance within the CSS ontology is created
    #         await self.create_ontology_instance_from_sme_element(constraint,
    #                                                              CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
    #         # The capability constraint element will be converted from the Basyx class to the extended one
    #         await self.convert_sme_class_to_extended(constraint, ExtendedCapabilityConstraint)
    #
    #         # The counter for analyzed capability constraints is increased
    #         self.analyzed_capability_constraints.append(constraint.id_short)

    # async def get_and_save_skills_information(self):
    #     """
    #     This method stores all the information related to the Skills. Since the data is defined in the AAS model,
    #     it will be used to create all Skill-related instances within the proposed Capability-Skill-Service ontology.
    #     """
    #     # First, the Skills are analyzed
    #     skills_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
    #         CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)
    #     for skill in skills_list:
    #         await self.add_step_progress_bar()
    #
    #         # For each Skill an instance within the CSS ontology is created
    #         await self.create_ontology_instance_from_sme_element(skill,
    #                                                              CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)
    #
    #         # The skill element will be converted from the Basyx class to the extended one
    #         if skill.check_if_element_is_structural():
    #             await self.convert_sme_class_to_extended(skill, ExtendedComplexSkill)
    #         else:
    #             await self.convert_sme_class_to_extended(skill, ExtendedSimpleSkill)
    #
    #         # The counter for analyzed capabilities is increased
    #         self.analyzed_skills.append(skill.id_short)
    #     # Once all Skills have been analyzed, the skill-related elements will be analyzed (i.e. interfaces)
    #     skill_interfaces_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
    #         CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI)
    #     for interface in skill_interfaces_list:
    #         await self.add_step_progress_bar()
    #
    #         # For each Skill an instance within the CSS ontology is created
    #         await self.create_ontology_instance_from_sme_element(interface,
    #                                                              CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI)
    #
    #         # The skill interface element will be converted from the Basyx class to the extended one
    #         if interface.check_if_element_is_structural():
    #             await self.convert_sme_class_to_extended(interface, ExtendedComplexSkillInterface)
    #         else:
    #             await self.convert_sme_class_to_extended(interface, ExtendedSimpleSkillInterface)
    #
    #         # The counter for analyzed capabilities is increased
    #         self.analyzed_skill_interfaces.append(interface.id_short)

    async def get_and_save_ontology_classes_information(self):
        """
        This method stores all the information related to the class elements defined in the ontology. Since the data is
         defined in the AAS model, it will be used to check whether the required data defined in the ontology has been
          added in the AAS model. If the elements are valid, they will be created their associated ontology instance and
          the AAS SubmodelElement will be associated to these instances.
        """
        for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
            await self.check_and_create_instances_by_iri(ontology_class_iri)


    async def get_and_save_ontology_relationships_information(self):
        """
        This method stores all the information related to the relationships between elements defined in the ontology.
        Since the data is defined in the AAS model, it will be used to check whether the linked elements have their
        associated ontology instance (created just before the execution of this method).
        """
        for ontology_relationship_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS:
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
            sme_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(ontology_class_iri)
        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")

        for submodel_elem in sme_list:
            await self.add_step_progress_bar()

            try:
                # For each SubmodelElement an instance within the CSS ontology is created
                await self.create_ontology_instance_from_sme_element(submodel_elem, ontology_class_iri)
                # created_instance = await self.myagent.css_ontology.create_ontology_object_instance(ontology_class,
                #                                                                                    submodel_elem.id_short)

                # The submodel element will be converted from the Basyx class to the extended one (of the SMIA approach)
                await self.convert_sme_class_to_extended_by_iri(submodel_elem, ontology_class_iri)

                # The element is saved as analyzed
                await self.add_new_analyzed_element(submodel_elem)

            except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
                if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                    _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
                else:
                    _logger.warning("Check the CSS ontology definition.")
                self.errors_found.append(submodel_elem.id_short)


    async def create_ontology_instance_from_sme_element(self, sme_elem, ontology_iri):
        """
        This method creates the ontology instance from the AAS Submodel Element.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model with all configured data.
            ontology_iri (str): IRI of the ontology class of the instance to be created.
        """
        try:
            ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(ontology_iri)
            # The class is used as constructor to build the instance of the CSS ontology
            created_instance = await self.myagent.css_ontology.create_ontology_object_instance(ontology_class,
                                                                                               sme_elem.id_short)
            # TODO de momento se crean las instancias de las ontologias con el id_short, pero habria que pensar si el
            #  id_short puede repetirse (el id_short es único dentro del submodelo)
            await self.add_ontology_required_information(sme_elem, created_instance)

        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")
            self.errors_found.append(sme_elem.id_short)

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
        new_class = CSSModelAASModelInfo.CSS_ONTOLOGY_AAS_MODEL_LINK[ontology_iri]
        if new_class is ExtendedSkill:
            # In this case there are two types of classes (Simple and Complex)
            if sme_elem.check_if_element_is_structural():
                sme_elem.__class__ = ExtendedComplexSkill
            else:
                sme_elem.__class__ = ExtendedSimpleSkill
        elif new_class is ExtendedSkillInterface:
            # In this case there are two types of classes (Simple and Complex)
            if sme_elem.check_if_element_is_structural():
                sme_elem.__class__ = ExtendedComplexSkillInterface
            else:
                sme_elem.__class__ = ExtendedSimpleSkillInterface
        else:
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
            rels_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
                relationship_iri, basyx.aas.model.RelationshipElement)
            rel_ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(relationship_iri)
            # The required AAS classes for the elements within this relationship is obtained from the CSS ontology
            domain_aas_class, range_aas_class = CapabilitySkillOntologyUtils.get_attribute_from_classes_in_object_property(
                rel_ontology_class, 'aas_sme_class')
        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")

        domain_aas_elem, range_aas_elem = None, None
        for rel in rels_list:
            await self.add_step_progress_bar()

            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            try:
                domain_aas_elem, range_aas_elem = await self.myagent.aas_model.get_elements_from_relationship(rel,
                                                                                                      domain_aas_class,
                                                                                                      range_aas_class)
                # It is checked if the capability and the skill have the required semanticIDs within the ontology
                # if not domain_aas_elem.check_semantic_id_exist(domain_class_iri):
                domain_aas_elem.get_semantic_id_of_css_ontology()
                range_aas_elem.get_semantic_id_of_css_ontology()

                # When both are checked, if the ontology instances exist the link is set in the ontology
                await self.myagent.css_ontology.add_object_property_to_instances_by_names(rel_ontology_class.name,
                                                                                          domain_aas_elem.id_short,
                                                                                          range_aas_elem.id_short)

            except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
                if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                    _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
                else:
                    _logger.warning("Check the CSS ontology definition.")
                if None not in (domain_aas_elem, range_aas_elem):
                    self.errors_found.append("{} ({},{})".format(rel.id_short, domain_aas_elem.id_short,
                                                                 range_aas_elem.id_short))
                else:
                    self.errors_found.append("{} ({},{})".format(rel.id_short, domain_aas_class, range_aas_class))

    # async def get_and_save_capabilities_skills_information(self):
    #     """
    #     This method saves all the information related to Capabilities and Skills defined in the AAS model into the
    #     agent global variables.
    #     """
    #     _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
    #     rels_cap_skill_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
    #         CapabilitySkillOntologyUtils.SEMANTICID_REL_CAPABILITY_SKILL, basyx.aas.model.RelationshipElement)
    #     for rel_cap_skill in rels_cap_skill_list:
    #         await self.add_step_progress_bar()
    #
    #         # First, the elements of capability and skill are determined (no matter in which order of the
    #         # relationship they are listed).
    #         capability_elem, skill_elem = await self.myagent.aas_model.get_cap_skill_elem_from_relationship(
    #             rel_cap_skill)
    #
    #         if capability_elem is None or skill_elem is None:
    #             continue
    #
    #         if capability_elem.check_cap_skill_ontology_semantics_and_qualifiers() is False:
    #             continue
    #
    #         # The capability_type is obtained using the semanticID
    #         capability_type = capability_elem.get_capability_type_in_ontology()
    #         _logger.info(
    #             "Analyzing {} [{}] and its associated skill [{}]...".format(capability_type, capability_elem.id_short,
    #                                                                         skill_elem.id_short))
    #
    #         # If the capability has constraints, they will be obtained
    #         capability_constraints = await self.myagent.aas_model.get_capability_associated_constraints(capability_elem)
    #         if capability_constraints:
    #             # TODO PROXIMO PASO: si se ha definido algun constraint, se comprobará que tiene un Qualifier valido
    #             #  (FeasibilityCheckingCondition con Pre-,Post-condition o invariant). Despues, comprobará si ese
    #             #  constraint (siendo una propiedad) tiene un valueId o no. Si lo tiene, este será la referencia al
    #             #  ConceptDescription que define el valor de ese constraint. Este ConceptDescription, puede tener un
    #             #  valueList con los posibles valores de ese constraint. (Un ejemplo es el de NegotiationCriteria. La
    #             #  capacidad de negociar viene limitada por los criterios por los que puede negociar, y estos se
    #             #  definen en el ConceptDescription añadido en el valueId de la propiedad del constraint). Por lo tanto,
    #             #  si el valueId del constraint no está vacío, hay que analizar el ConceptDescription y añadir los
    #             #  posibles valores en la información del constraint
    #             str_contraints = "\t\tThe capability associated constraints are: "
    #             for constraint in capability_constraints:
    #                 str_contraints += constraint.id_short + ', '
    #             # _logger.info(str_contraints)
    #         # else:
    #         #     _logger.info("\t\tThe capability does not have associated constraints.")
    #         # TODO properties have not been taken into account for the time being for the capacities, add in the future
    #
    #         # Once the information about the capability has been obtained, the associated skill will be analyzed
    #         if skill_elem.check_cap_skill_ontology_semantics_and_qualifiers() is False:
    #             continue
    #
    #         # TODO PROXIMO PASO: falta analizar los inputs y outputs parameters del skill. Si es una operación, los
    #         #  tiene integrados, pero si no, se deben localizar usando el semanticID 'HasParameter'. En los parametros,
    #         #  también habra que comprobar si tienen un valueId, es decir, un ConceptDescription asociado con los
    #         #  posibles valores que puede coger esa variable. En ese caso (p.e. el input de negociacion es el criterio
    #         #  y solo puede ser bateria, o localizacion o memoria RAM), se deberá añadir la información de los posibles
    #         #  valores junto al SkillParameters: analizar el ConceptDescription y ver si el valueList está o no vacio,
    #         #  si no lo está, recoger esos valores y alamacenarlos en una lista, la cual será la lista para posibles
    #         #  valores de ese parametro.
    #
    #         # The necessary Skill interface to implement the skill must be obtained
    #         skill_interface_elem = await self.myagent.aas_model.get_skill_interface_by_skill_elem(skill_elem)
    #         # TODO PROXIMO PASO: habra que analizar que el SkillInterface propuesto tenga un semanticID del Submodelo
    #         #  AssetInterfacesDescription (https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface)
    #         if skill_interface_elem is None and capability_type != CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE:
    #             _logger.error("The interface of the skill {} does not exist.".format(skill_elem))
    #             continue
    #
    #         # At this point of the execution, all checks ensure that the necessary information is available
    #         # All the information will be saved in the global variables of the agent
    #         cap_skill_info = {capability_elem: {
    #             'skillObject': skill_elem,
    #             'skillInterface': skill_interface_elem,
    #         }}
    #         if capability_constraints:
    #             cap_skill_info[capability_elem]['capabilityConstraints'] = capability_constraints
    #         await self.myagent.aas_model.save_capability_skill_information(capability_type, cap_skill_info)
    #         _logger.info("{} information saved in the global variables.".format(capability_elem))

    async def get_and_configure_asset_connections(self):
        """
        This method gets all Asset Interfaces Descriptions in the AAS model, configures each case with associated
        'AssetConnection' class and saves the information in the global variable of the agent for all asset connections.
        """
        # TODO PROXIMO PASO: hay que modificicar la variable global para assetconnection del agente ya que se debe
        #  habilitar añadir mas de un AssetConnection. Para ello, se analizara el Submodelo "AssetInterfacesDescription"
        #  y se recogerá cada SMC dentro de el, el cual determinara una interfaz diferente. Por cada interfaz,
        #  dependiendo del tipo (HTTP, OPC UA...) se generará una clase AssetConnection. Esta deberá tener, por una
        #  parte, la referencia al SMC del modelo AAS. Utilizando esta referencia, leera toda la informacion de ese
        #  submodelo y configurará la interfaz (p.e. añadiendo los datos del endpoint), para dejar la interfaz lista
        #  para ser usada (se hará referencia a los SMEs dentro de "InteractionMetada" del submodelo de la interfaz,
        #  que es donde estan los datapoints)
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning("AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to "
                            "be connected to the asset.")
            return
        for interface_elem in asset_interfaces_submodel.submodel_element:
            await self.add_step_progress_bar()

            if interface_elem.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACE) is False:
                _logger.warning("There is a submodel element inside the interfaces submodel with invalid semanticID.")
                continue
            # Dependiendo del tipo de interfaz se generara una clase u otra (de momento solo HTTP)
            if interface_elem.check_suppl_semantic_id_exist(AssetInterfacesInfo.SUPPL_SEMANTICID_HTTP):
                # Hay una interfaz de tipo HTTP
                http_connection_class = HTTPAssetConnection()
                await http_connection_class.configure_connection_by_aas_model(interface_elem)
                interface_model_ref = ModelReference.from_referable(interface_elem)
                await self.myagent.add_new_asset_connection(interface_model_ref, http_connection_class)
            if interface_elem.check_suppl_semantic_id_exist('id de opc ua'):
                # TODO Hay una interfaz de tipo OPC CUA
                pass

            self.analyzed_asset_connections.append(interface_elem.id_short)

        _logger.info("All asset connections defined in the AAS model have been configured and saved.")

    async def print_analysis_result(self):
        """
        This method simply prints the result of the complete analysis of the AAS model.
        """
        _logger.info("AAS model analysis results. \n\t- Analyzed capabilities: {}\n\t- Analyzed capability constraints"
                     ": {}\n\t- Analyzed skills {}\n\t- Analyzed skill interfaces {}\n\t- Analyzed asset connections"
                     " {}\n\t- Errors found {}".format(self.analyzed_capabilities,
                                                       self.analyzed_capability_constraints, self.analyzed_skills,
                                   self.analyzed_skill_interfaces, self.analyzed_asset_connections, self.errors_found))

    async def create_progress_bar_object(self):
        """
        This method creates the object for showing by console the progress of the analysis of the AAS model in form of
        a progress bar. The object is
        """
        # The iterations during the analysis of the AAS model will be the number of steps in the progress bar
        # The iteration number will be the sum of the possible Asset Connections and the Capability-Skill relationships.
        ontology_elements_semantic_ids = CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS + \
                                          CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS
        ontology_elements_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id_list(
            ontology_elements_semantic_ids)
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning(
                "AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to be"
                " connected to the asset.")
            asset_interfaces_submodel = type('obj', (object,), {
                'submodel_element': []})  # This is a solution to not brake the next commmand
        total_iterations = len(asset_interfaces_submodel.submodel_element) + len(ontology_elements_list)
        # with logging_redirect_tqdm():
        self.progress_bar = tqdm(total=total_iterations, desc='Analyzing AAS model', file=sys.stdout, ncols=75,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} ontology submodel elements \n')

    async def add_step_progress_bar(self):
        """
        This method adds a new step in the progress bar to show the status of the AAS model analysis.
        """
        # Add a new step in the progress bar
        self.progress_bar.update(1)
        await asyncio.sleep(.2)  # Simulate some processing time


    async def add_new_analyzed_element(self, aas_elem):
        """
        This method adds the new analyzed element in the corresponding list of class variables.

        Args:
            aas_elem (basyx.aas.model.SubmodelElement): analyzed SubmodelElement,
        """

        if isinstance(aas_elem, extended_submodel.ExtendedCapability):
            self.analyzed_capabilities.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedSkill):
            self.analyzed_skills.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedSkillInterface):
            self.analyzed_skill_interfaces.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedCapabilityConstraint):
            self.analyzed_capability_constraints.append(aas_elem.id_short)


