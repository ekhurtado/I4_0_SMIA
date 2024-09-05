import logging
import spade

from agents.AASManagerAgent import AASManagerAgent
from agents.AASManagerAppAgent import AASManagerAppAgent
from agents.AASManagerResourceAgent import AASManagerResourceAgent
from utilities import ConfigMap_utils
from utilities.GeneralUtils import GeneralUtils
from utilities.KafkaInfo import KafkaInfo

# XMPP_SERVER = 'worker4'
XMPP_SERVER = 'ejabberd'

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
    aas_id = ConfigMap_utils.get_aas_general_property('logicalID')
    # aas_id = 'aasmanager001'  # For testing

    # The AAS ID will be also the topic of Kafka, for AAS Manager-Core interactions
    KafkaInfo.KAFKA_TOPIC = aas_id

    # Get the type of the asset
    # aas_type = ConfigMap_utils.get_asset_type()
    aas_type = ''  # For testing

    # Build the agent jid and password
    agent_jid = aas_id + '@' + XMPP_SERVER
    passwd = '123'  # TODO pensar que passwords utilizar (algo relacionado con el nombre del deployment quizas?)

    # Depending on the asset type, the associated SPADE agent will be created
    aas_manager_agent = None
    match aas_type:
        case "physical":
            print("The asset is physical")
            aas_manager_agent = AASManagerResourceAgent(agent_jid, passwd)
        case "logical":
            print("The asset is logical")
            aas_manager_agent = AASManagerAppAgent(agent_jid, passwd)
        case _:
            print("A generic AAS Manager")
            # Create the agent object
            aas_manager_agent = AASManagerAgent(agent_jid, passwd)

    # Since the agent object has already been created, the agent will start
    await aas_manager_agent.start()

    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(aas_manager_agent)


if __name__ == '__main__':

    # Configure logging
    GeneralUtils.configure_logging()
    _logger.info("Initializing AAS Manager program...")

    # Run main program with SPADE
    spade.run(main())
