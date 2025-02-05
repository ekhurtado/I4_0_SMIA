import logging
from spade.behaviour import State

from smia.behaviours.init_aas_model_behaviour import InitAASModelBehaviour
from smia.utilities import smia_archive_utils
from smia.utilities.general_utils import SMIAGeneralInfo

_logger = logging.getLogger(__name__)


class StateBooting(State):
    """
    This class contains the Boot state of the common SMIA.
    """

    async def run(self):
        """
        This method implements the boot state of the common SMIA. Here all the required initialization tasks
        are performed.
        """

        await self.booting_state_logic()
        self.set_next_state(SMIAGeneralInfo.RUNNING_STATE_NAME)

    async def booting_state_logic(self):
        """
        This method contains the logic of the boot state of the common SMIA. This method can be used by any
        inherited class.
        """
        _logger.info("## STATE 1: BOOTING ##  (Initial state)")

        # First, it is ensured that the attributes of the SMIA are initialized
        self.agent.initialize_smia_attributes()

        # The ontology has to be initialized in order to be available during the AAS model analysis
        await self.agent.css_ontology.initialize_ontology()

        # The submodels also have to be initialized, so its behaviour is also added
        init_aas_model_behav = InitAASModelBehaviour(self.agent)
        self.agent.add_behaviour(init_aas_model_behav)

        # Wait until the behaviours have finished because the AAS Archive has to be initialized to pass to running state
        await init_aas_model_behav.join()

        # If the initialization behaviour has completed, SMIA is in the InitializationReady status
        smia_archive_utils.update_status('InitializationReady')

        # Finished the Boot State the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Boot state.")
