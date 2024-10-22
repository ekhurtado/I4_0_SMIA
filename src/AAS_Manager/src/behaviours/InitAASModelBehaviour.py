import logging

import basyx.aas.adapter.xml
import basyx.aas.adapter.json
from spade.behaviour import OneShotBehaviour
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
        aas_model_serialization_format = ConfigMap_utils.get_dt_general_property('aas.model.serialization')
        _logger.error(aas_model_serialization_format)   # TODO ELIMINAR

        # Depending on the serialization format, the required BaSyx read method shall be executed. This will store all
        # the received elements of the model in the corresponding global object of the agent.
        object_store = await self.read_aas_model_object_store(aas_model_serialization_format)
        await self.myagent.aas_model.set_aas_model_object_store(object_store)

        # When the object store is created, the required values and information is obtained from the AAS model
        # Both the agent and asset capabilities are stored in the global variables of the agents, with their related
        # information (constraints, associated skill, skill interface...).
        capabilities_skills_information = await self.get_capabilities_skills_information()
        await self.myagent.aas_model.set_capabilities_skills_object(capabilities_skills_information)

        # TODO: pensar si faltaria comprobar mas cosas a recoger en el modelo de AAS
        _logger.info("AAS model initialized.")

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
            self.kill()
        else:
            return object_store

    async def get_capabilities_skills_information(self):
        """
        This method gets all the information related to Capabilities and Skills defined in the AAS model.

        Returns:
            dict: object with all the information about Capabilities and Skills of the DT and the asset.
        """
        _logger.info("Reading the AAS model to get all capabilities of the asset and the industrial agent...")
        rels_cap_skill_list = self.myagent.aas_model.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_SKILL)
        for rel_cap_skill in rels_cap_skill_list:
            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            capability_elem, skill_elem = rel_cap_skill.get_cap_skill_elem_from_relationship()

            # It will be checked if the semantic id of the capability is valid within the ontology
            capability_elem.check_cap_skill_ontology_semantic_id()

            # It will also be checked if it has any of the qualifiers defined in the ontology for the capabilities


