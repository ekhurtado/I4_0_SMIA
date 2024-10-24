import logging

import basyx.aas.adapter.xml
import basyx.aas.adapter.json
from basyx.aas.util import traversal
from spade.behaviour import OneShotBehaviour

from assetconnection.HTTPAssetConnection import HTTPAssetConnection
from utilities import ConfigMap_utils, Submodels_utils
from utilities.CapabilitySkillOntology import CapabilitySkillOntology

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

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # First, the AAS model serialization format is obtained
        aas_model_serialization_format = ConfigMap_utils.get_aas_general_property('model.serialization')

        # Depending on the serialization format, the required BaSyx read method shall be executed. This will store all
        # the received elements of the model in the corresponding global object of the agent.
        object_store = await self.read_aas_model_object_store(aas_model_serialization_format)
        await self.myagent.aas_model.set_aas_model_object_store(object_store)

        # When the object store is created, the required values and information is obtained from the AAS model
        # Both the agent and asset capabilities are stored in the global variables of the agents, with their related
        # information (constraints, associated skill, skill interface...).
        await self.save_capabilities_skills_information()

        # After the AAS model has been analyzed, the AssetConnection class can be specified
        await self.update_asset_connection()

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
        if aas_model_serialization_format == 'JSON':
            object_store = basyx.aas.adapter.json.read_aas_json_file(ConfigMap_utils.get_aas_model_filepath())
        elif aas_model_serialization_format == 'XML':
            object_store = basyx.aas.adapter.xml.read_aas_xml_file(ConfigMap_utils.get_aas_model_filepath())
        if object_store is None:
            _logger.error("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                          "metamodel.")
            self.kill(exit_code=10)
        else:
            return object_store

    async def save_capabilities_skills_information(self):
        """
        This method saves all the information related to Capabilities and Skills defined in the AAS model into the
        agent global variables.
        """
        _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
        rels_cap_skill_list = await self.myagent.aas_model.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_SKILL)
        for rel_cap_skill in rels_cap_skill_list:
            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            capability_elem, skill_elem = await self.myagent.aas_model.get_cap_skill_elem_from_relationship(rel_cap_skill)

            if capability_elem is None or skill_elem is None:
                continue

            if capability_elem.check_cap_skill_ontology_semantics_and_qualifiers() is False:
                continue

            # The capability_type is obtained using the semanticID
            capability_type = capability_elem.get_capability_type_in_ontology()
            _logger.info("Analyzing {} [{}] and its associated skill [{}]...".format(capability_type,capability_elem.id_short,
                                                                                             skill_elem.id_short))

            # If the capability has constraints, they will be obtained
            capability_constraints = await self.myagent.aas_model.get_capability_associated_constraints(capability_elem)
            if capability_constraints:
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

            # The necessary Skill interface to implement the skill must be obtained
            skill_interface_elem = await self.myagent.aas_model.get_skill_interface_by_skill_elem(skill_elem)
            if skill_interface_elem is None and capability_type != CapabilitySkillOntology.AGENT_CAPABILITY_TYPE:
                _logger.error("The interface of the skill {} does not exist.")
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


    async def update_asset_connection(self):
        """
        This method updates the Asset Connection class of the agent based on the Skill interface defined in the AAS
        model.
        """
        capabilities_dict = await self.myagent.aas_model.get_capability_dict_by_type(CapabilitySkillOntology.ASSET_CAPABILITY_TYPE)
        for cap_elem, cap_info in capabilities_dict.items():
            # TODO, pensar que pasaria si las capacidades tienen diferentes protocolos. De momento se ha dejado de forma sencilla, se recoge el primero
            skill_interface = await self.myagent.aas_model.get_skill_interface_by_skill_elem(cap_info['skillObject'])
            for semantic_id in traversal.walk_semantic_ids_recursive(skill_interface):
                for reference in semantic_id.key:
                    if str(reference) == CapabilitySkillOntology.SEMANTICID_SKILL_INTERFACE_HTTP:
                        await self.myagent.set_asset_connection(HTTPAssetConnection())