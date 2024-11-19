import asyncio
import logging
import sys
import time

import basyx.aas.adapter.xml
import basyx.aas.adapter.json
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.model import ModelReference
from owlready2 import ThingClass
from spade.behaviour import OneShotBehaviour
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from aas_model.extended_submodel import ExtendedSkill, ExtendedSkillInterface
from assetconnection.http_asset_connection import HTTPAssetConnection
from logic.exceptions import OntologyInstanceCreationError, AASModelReadingError, AASModelOntologyError, \
    OntologyReadingError
from utilities import configmap_utils
from utilities.css_ontology_utils import CapabilitySkillOntologyUtils, AssetInterfacesInfo, CapabilitySkillOntologyInfo

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
        self.analyzed_capabilities = 0
        self.analyzed_capability_constraints = 0
        self.analyzed_skills = 0
        self.analyzed_skill_interfaces = 0
        self.analyzed_asset_connections = 0
        self.errors_found = 0

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

        await self.get_and_save_capabilities_information()  # TODO PRUEBAS (pero seran los metodo finales)
        await self.get_and_save_skills_information()  # TODO PRUEBAS
        await self.get_and_save_relationships_information()  # TODO PRUEBAS

        # When the object store is created, the required values and information is obtained from the AAS model
        # Both the agent and asset capabilities are stored in the global variables of the agents, with their related
        # information (constraints, associated skill, skill interface...).
        await self.get_and_save_capabilities_skills_information()

        # After the AAS model has been analyzed, the AssetConnection class can be specified
        await self.get_and_configure_asset_connections()

        # The progress bar is closed
        # self.progress_bar.close()

        # The final results of the analysis are shown
        await self.print_analysis_result()

        # TODO: pensar si faltaria comprobar mas cosas a recoger en el modelo de AAS
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
        # TODO HACER AHORA: AÑADIR EL PODER LEER AASX
        if aas_model_serialization_format == 'JSON':
            object_store = basyx.aas.adapter.json.read_aas_json_file(configmap_utils.get_aas_model_filepath())
        elif aas_model_serialization_format == 'XML':
            object_store = basyx.aas.adapter.xml.read_aas_xml_file(configmap_utils.get_aas_model_filepath())
        elif aas_model_serialization_format == 'AASX':
            try:
                with aasx.AASXReader(configmap_utils.get_aas_model_filepath()) as reader:
                    # Read all contained AAS objects and all referenced auxiliary files
                    object_store = model.DictObjectStore()
                    suppl_file_store = aasx.DictSupplementaryFileContainer()
                    reader.read_into(object_store=object_store,
                                     file_store=suppl_file_store)
            except ValueError as e:
                _logger.error("Failed to read AAS model: invalid AASX package.")
                _logger.error(e)
        if object_store is None:
            _logger.error("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                          "metamodel.")
            self.kill(exit_code=10)
        else:
            return object_store

    async def get_and_save_capabilities_information(self):
        """
        This method stores all the information related to the Capabilities. Since the data is defined in the AAS model,
        it will be used to create the Capability instances within the proposed Capability-Skill-Service ontology.
        """
        _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
        # All types of Capabilities are obtained
        # TODO de momento se hace manualmente. Hay que pensar si queremos dejar al usuario añadir el semanticID que
        #  quiera de la ontologia, o solo hasta el nivel de Agent o AssetCapability. Es decir, todas las capacidades
        #  seran de esos dos tipos en el AAS Model, pero despues en la ontología se podrán estructurar las capacidades
        #  como se quiera. Otra opcion es primero estructurar la ontologia y despues utilizar esos IDs únicos de cada
        #  instancia para añadirlo en el AAS Model (para esta forma habria que leer el AAS model junto con la ontologia,
        #  para primero recoger los IRIs de la ontologia y despues realizar la busqueda en el AAS model)
        # First, the Capabilities are analyzed
        cap_iris_list = [CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI]
        cap_ontology_elem = await self.myagent.css_ontology.get_ontology_class_by_iri(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
        cap_iris_list.extend(
            await self.myagent.css_ontology.get_all_subclasses_iris_of_class(cap_ontology_elem))
        cap_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id_list(cap_iris_list,
                                                                                          basyx.aas.model.Capability)
        for cap in cap_list:
            # A new step in the progress bar is added
            self.progress_bar.update(1)
            await asyncio.sleep(.5)  # Simulate some processing time

            # For each Capability an instance within the CSS ontology is created
            ontology_iri = cap.get_semantic_id_of_css_ontology()
            await self.create_ontology_instance_from_sme_element(cap, ontology_iri)

            # The counter for analyzed capabilities is increased
            self.analyzed_capabilities += 1

        # Once all Capabilities have been analyzed, the capability-related elements will be analyzed (i.e. constraints)
        cap_constraint_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
        _logger.info("Reading the AAS model to get all capability constraints...")
        for constraint in cap_constraint_list:
            # For each Capability Constraint an instance within the CSS ontology is created
            await self.create_ontology_instance_from_sme_element(constraint,
                                                                 CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI)
            # The counter for analyzed capability constraints is increased
            self.analyzed_capability_constraints += 1

    async def get_and_save_skills_information(self):
        """
        This method stores all the information related to the Skills. Since the data is defined in the AAS model,
        it will be used to create all Skill-related instances within the proposed Capability-Skill-Service ontology.
        """
        _logger.info("Reading the AAS model to get all skills of the asset and the industrial agent...")
        # First, the Skills are analyzed
        skills_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)
        for skill in skills_list:
            # A new step in the progress bar is added
            self.progress_bar.update(1)
            await asyncio.sleep(.5)  # Simulate some processing time

            # For each Skill an instance within the CSS ontology is created
            await self.create_ontology_instance_from_sme_element(skill,
                                                                 CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)

            # The skill element will be converted from the Basyx class to the extended one
            await self.convert_sme_class_to_extended(skill, ExtendedSkill)

            # The counter for analyzed capabilities is increased
            self.analyzed_skills += 1
        # Once all Skills have been analyzed, the skill-related elements will be analyzed (i.e. interfaces)
        _logger.info("Reading the AAS model to get all skill interfaces...")
        skill_interfaces_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI)
        for interface in skill_interfaces_list:
            # A new step in the progress bar is added
            self.progress_bar.update(1)
            await asyncio.sleep(.5)  # Simulate some processing time

            # For each Skill an instance within the CSS ontology is created
            await self.create_ontology_instance_from_sme_element(interface,
                                                                 CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI)

            # The skill interface element will be converted from the Basyx class to the extended one
            await self.convert_sme_class_to_extended(interface, ExtendedSkillInterface)

            # The counter for analyzed capabilities is increased
            self.analyzed_skill_interfaces += 1

    async def get_and_save_relationships_information(self):
        """
        This method stores all the information related to the relationships between elements defined in the ontology.
        Since the data is defined in the AAS model, it will be used to check whether the linked elements have their
        associated ontology instance (created just before the execution of this method).
        """
        _logger.info("Reading the AAS model to get all relationships between capabilities and skills...")
        rels_cap_skill_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI, basyx.aas.model.RelationshipElement)
        rel_ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI)
        for rel in rels_cap_skill_list:
            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            try:
                capability_elem, skill_elem = await self.myagent.aas_model.get_cap_skill_elem_from_relationship(rel)
                # It is checked if the capability and the skill have the required semanticIDs within the ontology
                capability_elem.get_semantic_id_of_css_ontology()
                skill_elem.check_semantic_id_of_css_ontology()

                # When both are checked, if the ontology instances exist the link is set in the ontology
                await self.myagent.css_ontology.add_object_property_to_instances_by_names(rel_ontology_class.name,
                                                                                          capability_elem.id_short,
                                                                                          skill_elem.id_short)
                # TODO VOY POR AQUI (pensar como se puede desarrollar un metodo general para todas las relaciones. P.e., que al metodo le pases dos clases, en orden de que la segunda se añadira a la priemra, y el IRI de la relacion de ambas. P.e. para saber cual es cual se podria hacer un metodo para devolver siempre las dos clases, en orden, es decir, a la que añadir la relacion la primera )
            except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
                # TODO
                pass


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
            await self.add_ontology_required_information(sme_elem, created_instance)
        except (OntologyInstanceCreationError, AASModelReadingError) as e:
            _logger.error("The ontology instance of SubmodelElement {} cannot be created.".format(sme_elem.id_short))
            if isinstance(e, AASModelReadingError):
                _logger.warning("Check the Submodel Element {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            self.errors_found += 1

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
        ontology_required_value_names = ontology_instance.get_data_properties_names()
        for required_value_name in ontology_required_value_names:
            required_value = aas_model_elem.get_qualifier_value_by_type(required_value_name)
            ontology_instance.set_data_property_value(required_value_name, required_value)
        # The Submodel Element is also added to be available to the ontology instance object in form of a
        # reference
        ontology_instance.set_aas_sme_ref(ModelReference.from_referable(aas_model_elem))

    @staticmethod
    async def convert_sme_class_to_extended(sme_elem, new_class):
        """
        This method converts the class of a SubmodelElement to the Extended class, in order to add the required method
        to be used during the execution of the software.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model to be modified.
            new_class: new class to which the SubmodelElement shall be converted.
        """
        current_class = sme_elem.__class__
        sme_elem.__class__ = new_class
        # The old class new to be added to the Extended class
        sme_elem.add_old_sme_class(current_class)

    async def get_and_save_capabilities_skills_information(self):
        """
        This method saves all the information related to Capabilities and Skills defined in the AAS model into the
        agent global variables.
        """
        _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
        rels_cap_skill_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyUtils.SEMANTICID_REL_CAPABILITY_SKILL, basyx.aas.model.RelationshipElement)
        for rel_cap_skill in rels_cap_skill_list:
            # Add a new step in the progress bar
            self.progress_bar.update(1)
            await asyncio.sleep(.5)  # Simulate some processing time

            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            capability_elem, skill_elem = await self.myagent.aas_model.get_cap_skill_elem_from_relationship(
                rel_cap_skill)

            if capability_elem is None or skill_elem is None:
                continue

            if capability_elem.check_cap_skill_ontology_semantics_and_qualifiers() is False:
                continue

            # The capability_type is obtained using the semanticID
            capability_type = capability_elem.get_capability_type_in_ontology()
            _logger.info(
                "Analyzing {} [{}] and its associated skill [{}]...".format(capability_type, capability_elem.id_short,
                                                                            skill_elem.id_short))

            # If the capability has constraints, they will be obtained
            capability_constraints = await self.myagent.aas_model.get_capability_associated_constraints(capability_elem)
            if capability_constraints:
                # TODO PROXIMO PASO: si se ha definido algun constraint, se comprobará que tiene un Qualifier valido
                #  (FeasibilityCheckingCondition con Pre-,Post-condition o invariant). Despues, comprobará si ese
                #  constraint (siendo una propiedad) tiene un valueId o no. Si lo tiene, este será la referencia al
                #  ConceptDescription que define el valor de ese constraint. Este ConceptDescription, puede tener un
                #  valueList con los posibles valores de ese constraint. (Un ejemplo es el de NegotiationCriteria. La
                #  capacidad de negociar viene limitada por los criterios por los que puede negociar, y estos se
                #  definen en el ConceptDescription añadido en el valueId de la propiedad del constraint). Por lo tanto,
                #  si el valueId del constraint no está vacío, hay que analizar el ConceptDescription y añadir los
                #  posibles valores en la información del constraint
                str_contraints = "\t\tThe capability associated constraints are: "
                for constraint in capability_constraints:
                    str_contraints += constraint.id_short + ', '
                # _logger.info(str_contraints)
            # else:
            #     _logger.info("\t\tThe capability does not have associated constraints.")
            # TODO properties have not been taken into account for the time being for the capacities, add in the future

            # Once the information about the capability has been obtained, the associated skill will be analyzed
            if skill_elem.check_cap_skill_ontology_semantics_and_qualifiers() is False:
                continue

            # TODO PROXIMO PASO: falta analizar los inputs y outputs parameters del skill. Si es una operación, los
            #  tiene integrados, pero si no, se deben localizar usando el semanticID 'HasParameter'. En los parametros,
            #  también habra que comprobar si tienen un valueId, es decir, un ConceptDescription asociado con los
            #  posibles valores que puede coger esa variable. En ese caso (p.e. el input de negociacion es el criterio
            #  y solo puede ser bateria, o localizacion o memoria RAM), se deberá añadir la información de los posibles
            #  valores junto al SkillParameters: analizar el ConceptDescription y ver si el valueList está o no vacio,
            #  si no lo está, recoger esos valores y alamacenarlos en una lista, la cual será la lista para posibles
            #  valores de ese parametro.

            # The necessary Skill interface to implement the skill must be obtained
            skill_interface_elem = await self.myagent.aas_model.get_skill_interface_by_skill_elem(skill_elem)
            # TODO PROXIMO PASO: habra que analizar que el SkillInterface propuesto tenga un semanticID del Submodelo
            #  AssetInterfacesDescription (https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface)
            if skill_interface_elem is None and capability_type != CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE:
                _logger.error("The interface of the skill {} does not exist.".format(skill_elem))
                continue

            # At this point of the execution, all checks ensure that the necessary information is available
            # All the information will be saved in the global variables of the agent
            cap_skill_info = {capability_elem: {
                'skillObject': skill_elem,
                'skillInterface': skill_interface_elem,
            }}
            if capability_constraints:
                cap_skill_info[capability_elem]['capabilityConstraints'] = capability_constraints
            await self.myagent.aas_model.save_capability_skill_information(capability_type, cap_skill_info)
            _logger.info("{} information saved in the global variables.".format(capability_elem))

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
        _logger.info("Reading the AAS model to get all connections of the asset...")
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning("AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to "
                            "be connected to the asset.")
            return
        for interface_elem in asset_interfaces_submodel.submodel_element:
            # Add a new step in the progress bar
            self.progress_bar.update(1)
            await asyncio.sleep(.5)  # Simulate some processing time

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

            self.analyzed_asset_connections += 1

        _logger.info("All asset connections defined in the AAS model have been configured and saved.")

        # capabilities_dict = await self.myagent.aas_model.get_capability_dict_by_type(CapabilitySkillOntology.ASSET_CAPABILITY_TYPE)
        # for cap_elem, cap_info in capabilities_dict.items():
        #     # TODO, pensar que pasaria si las capacidades tienen diferentes protocolos. De momento se ha dejado de forma sencilla, se recoge el primero
        #     skill_interface = await self.myagent.aas_model.get_skill_interface_by_skill_elem(cap_info['skillObject'])
        #     for semantic_id in traversal.walk_semantic_ids_recursive(skill_interface):
        #         for reference in semantic_id.key:
        #             if str(reference) == CapabilitySkillOntology.SEMANTICID_SKILL_INTERFACE_HTTP:
        #                 await self.myagent.set_asset_connection(HTTPAssetConnection())

    async def print_analysis_result(self):
        """
        This method simply prints the result of the complete analysis of the AAS model.
        """
        _logger.info("AAS model analysis results. Analized elements: capabilities [{}], capability constraints [{}], "
                     "skills [{}], skill interfaces [{}], asset connections [{}]. Errors found [{}]".format(
            self.analyzed_capabilities, self.analyzed_capability_constraints, self.analyzed_skills,
            self.analyzed_skill_interfaces, self.analyzed_asset_connections, self.errors_found))

    async def create_progress_bar_object(self):
        """
        This method creates the object for showing by console the progress of the analysis of the AAS model in form of
        a progress bar. The object is
        """
        # The iterations during the analysis of the AAS model will be the number of steps in the progress bar
        # The iteration number will be the sum of the possible Asset Connections and the Capability-Skill relationships.
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        ontology_elements_semantic_ids = [CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI,
                                          CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI,
                                          CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI]
        # All subclasses IRIs of Capabilities are also obtained
        cap_ontology_elem = await self.myagent.css_ontology.get_ontology_class_by_iri(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI)
        ontology_elements_semantic_ids.extend(
            await self.myagent.css_ontology.get_all_subclasses_iris_of_class(cap_ontology_elem))
        ontology_elements_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id_list(
            ontology_elements_semantic_ids)
        if not asset_interfaces_submodel:
            _logger.warning(
                "AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to be"
                " connected to the asset.")
            asset_interfaces_submodel = type('obj', (object,), {
                'submodel_element': []})  # This is a solution to not brake the next commmand
        total_iterations = len(asset_interfaces_submodel.submodel_element) + len(ontology_elements_list)
        # with logging_redirect_tqdm():
        self.progress_bar = tqdm(total=total_iterations, desc='Analyzing AAS model', file=sys.stdout, ncols=75,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} submodel elements \n')
