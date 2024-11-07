import asyncio
import logging
import sys
import time

import basyx.aas.adapter.xml
import basyx.aas.adapter.json
from basyx.aas.model import ModelReference
from spade.behaviour import OneShotBehaviour
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from assetconnection.http_asset_connection import HTTPAssetConnection
from utilities import configmap_utils
from utilities.capability_skill_ontology import CapabilitySkillOntology, AssetInterfacesInfo

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
        # Both the agent and asset capabilities are stored in the global variables of the agents, with their related
        # information (constraints, associated skill, skill interface...).
        await self.get_and_save_capabilities_skills_information()

        # After the AAS model has been analyzed, the AssetConnection class can be specified
        await self.get_and_configure_asset_connections()

        # The progress bar is closed
        self.progress_bar.close()

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
        if object_store is None:
            _logger.error("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                          "metamodel.")
            self.kill(exit_code=10)
        else:
            return object_store

    async def get_and_save_capabilities_skills_information(self):
        """
        This method saves all the information related to Capabilities and Skills defined in the AAS model into the
        agent global variables.
        """
        _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
        rels_cap_skill_list = await self.myagent.aas_model.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_SKILL)
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
            if skill_interface_elem is None and capability_type != CapabilitySkillOntology.AGENT_CAPABILITY_TYPE:
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
            elif interface_elem.check_suppl_semantic_id_exist('id de opc ua'):
                # TODO Hay una interfaz de tipo OP CUA
                pass

        _logger.info("All asset connections defined in the AAS model have been configured and saved.")

        # capabilities_dict = await self.myagent.aas_model.get_capability_dict_by_type(CapabilitySkillOntology.ASSET_CAPABILITY_TYPE)
        # for cap_elem, cap_info in capabilities_dict.items():
        #     # TODO, pensar que pasaria si las capacidades tienen diferentes protocolos. De momento se ha dejado de forma sencilla, se recoge el primero
        #     skill_interface = await self.myagent.aas_model.get_skill_interface_by_skill_elem(cap_info['skillObject'])
        #     for semantic_id in traversal.walk_semantic_ids_recursive(skill_interface):
        #         for reference in semantic_id.key:
        #             if str(reference) == CapabilitySkillOntology.SEMANTICID_SKILL_INTERFACE_HTTP:
        #                 await self.myagent.set_asset_connection(HTTPAssetConnection())

    async def create_progress_bar_object(self):
        """
        This method creates the object for showing by console the progress of the analysis of the AAS model in form of
        a progress bar. The object is
        """
        # The iterations during the analysis of the AAS model will be the number of steps in the progress bar
        # The iteration number will be the sum of the possible Asset Connections and the Capability-Skill relationships.
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        rels_cap_skill_list = await self.myagent.aas_model.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_SKILL)
        if not asset_interfaces_submodel:
            _logger.warning("AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to be"
                            " connected to the asset.")
            asset_interfaces_submodel = type('obj', (object,), {'submodel_element': []})    # This is a solution to not brake the next commmand
        total_iterations = len(asset_interfaces_submodel.submodel_element) + len(rels_cap_skill_list)
        # with logging_redirect_tqdm():
        self.progress_bar = tqdm(total=total_iterations, desc='Analyzing AAS model', file=sys.stdout, ncols=75,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} ontology elements \n')
