import logging
import spade

from agents.AASManagerAgent import AASManagerAgent
from utilities.GeneralUtils import GeneralUtils

XMPP_SERVER = 'worker4'
_logger = logging.getLogger(__name__)

"""
This is the launch file of the AASManager, which runs the logic of the program.
"""


async def main():
    """
    This is the main method of the AAS Manager, where the agent will be created and started. Depending on the type of
    asset to be represented, the associated SPADE agent type will be created.
    """
    # The AAS_ID will be set in the associated ConfigMap, within the general-information of the AAS
    # aas_id = ConfigMap_utils.get_aas_general_property('logicalID')
    aas_id = 'aasmanager001'  # For testing

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
            # TODO falta crear la clase que herede la general para activos físicos
            print("The asset is physical")
            aas_manager_agent = None
        case "logical":
            # TODO falta crear la clase que herede la general para activos lógicos
            print("The asset is logical")
            aas_manager_agent = None
        case _:
            print("A generic AAS Manager")
            # Create the agent object
            aas_manager_agent = AASManagerAgent(agent_jid, passwd)

    # Since the agent object has already been created, the agent will start
    await aas_manager_agent.start()

    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(aas_manager_agent)


if __name__ == '__main__':
    _logger.info("Initializing AAS Manager program...")

    # Configure logging
    GeneralUtils.configure_logging()

    # Run main program with SPADE
    spade.run(main())
