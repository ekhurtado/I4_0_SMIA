import logging
from spade.behaviour import State

from behaviours.init_aas_archive_behaviour import InitAASarchiveBehaviour
from behaviours.init_aas_model_behaviour import InitAASModelBehaviour
from logic import IntraAASInteractions_utils
from utilities import smia_archive_utils
from utilities.smia_info import SMIAInfo

_logger = logging.getLogger(__name__)


class StateBooting(State):
    """
    This class contains the Boot state of the common AAS Manager.
    """

    async def run(self):
        """
        This method implements the boot state of the common AAS Manager. Here all the required initialization tasks
        are performed.
        """

        await self.booting_state_logic()
        self.set_next_state(SMIAInfo.RUNNING_STATE_NAME)

    async def booting_state_logic(self):
        """
        This method contains the logic of the boot state of the common AAS Manager. This method can be used by any
        inherited class.
        """
        _logger.info("## STATE 1: BOOTING ##  (Initial state)")

        # First, it is ensured that the attributes of the AAS Manager are initialized
        self.agent.initialize_aas_manager_attributes()

        # The submodels also have to be initalized, so its behaviour is also added
        init_aas_model_behav = InitAASModelBehaviour(self.agent)
        self.agent.add_behaviour(init_aas_model_behav)

        # Wait until the behaviours have finished because the AAS Archive has to be initialized to pass to running state
        await init_aas_model_behav.join()

        # If the initialization behaviour has completed, SMIA is in the InitializationReady status
        smia_archive_utils.update_status('InitializationReady')
        # Change of status must be notified to the AAS core
        # result = await IntraAASInteractions_utils.send_interaction_msg_to_core(client_id='i4-0-smia-manager',
        #                                                                        msg_key='manager-status',
        #                                                                        msg_data={
        #                                                                            'status': 'InitializationReady'})
        # TODO cuidado, en los envios de estado no se está añadiendo el interaction_id. Es necesario? Estas
        #  interacciones son como las demas? En realidad el key es solo de estado, no de peticion ni respuesta...

        # if result != "OK":
        #     _logger.error("The AAS Manager-Core interaction is not working: " + str(result))
        # else:
        #     _logger.info("The AAS Manager has notified the AAS Core that its initialization has been completed.")

        # Wait until the AAS Core has initialized
        # _logger.info('AAS Manager is waiting until its AAS Core has initialized.')
        # TODO revisar, ya que en el nuevo enfoque no hay AAS Core
        # check_core_initialization_behav = CheckCoreInitializationBehaviour(self.agent)
        # self.agent.add_behaviour(check_core_initialization_behav)
        # await check_core_initialization_behav.join()
        # _logger.info('AAS Core has initialized.')

        # Finished the Boot State the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Boot state.")
