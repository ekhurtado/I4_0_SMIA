import logging
import spade

from agents.smia_agent import AASManagerAgent
from agents.smia_app_agent import AASManagerAppAgent
from agents.smia_resource_agent import AASManagerResourceAgent
from utilities import configmap_utils, smia_archive_utils
from utilities.AASModelExtension_utils import AASModelExtensionUtils
from utilities.general_utils import GeneralUtils
from utilities.KafkaInfo import KafkaInfo

# XMPP_SERVER = 'worker4'
# XMPP_SERVER = 'ejabberd'

_logger = logging.getLogger(__name__)

"""
This is the launch file of the AASManager, which runs the logic of the program.
"""


async def main():
    """
    This is the main method of the AAS Manager, where the agent will be created and started. Depending on the type of
    asset to be represented, the associated SPADE agent type will be created. The AAS is defined in the glossary:
    :term:`AAS`.
    """
    # The AAS_ID will be set in the associated ConfigMap, within the general-information of the AAS
    aas_id = configmap_utils.get_dt_general_property('agentID')
    # aas_id = 'aasmanager001'  # For testing

    # The XMPP server of the MAS will also be set in the associated ConfiMap
    xmpp_server = configmap_utils.get_dt_general_property('xmpp-server')

    # The AAS ID will be also the topic of Kafka, for AAS Manager-Core interactions
    KafkaInfo.KAFKA_TOPIC = aas_id

    # Get the type of the asset
    # aas_type = ConfigMap_utils.get_asset_type()
    aas_type = ''  # For testing

    # Build the agent jid and password
    agent_jid = aas_id + '@' + xmpp_server
    passwd = 'gcis1234'  # TODO pensar que passwords utilizar (algo relacionado con el nombre del deployment quizas?)

    # Depending on the asset type, the associated SPADE agent will be created
    aas_manager_agent = None
    match aas_type:
        case "physical":
            _logger.info("The asset is physical")
            aas_manager_agent = AASManagerResourceAgent(agent_jid, passwd)
        case "digital":
            _logger.info("The asset is logical")
            aas_manager_agent = AASManagerAppAgent(agent_jid, passwd)
        case _:
            _logger.info("The asset is not defined, so it is a generic AAS Manager")
            # Create the agent object
            aas_manager_agent = AASManagerAgent(agent_jid, passwd)

    # Since the agent object has already been created, the agent will start
    await aas_manager_agent.start()

    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(aas_manager_agent)


if __name__ == '__main__':

    # Initialize SMIA archive
    smia_archive_utils.initialize_smia_archive()

    # Configure logging
    GeneralUtils.configure_logging()

    _logger.info("Initializing SMIA software...")

    # Extend BaSyx Python SDK
    AASModelExtensionUtils.extend_basyx_aas_model()

    # Run main program with SPADE
    spade.run(main())
