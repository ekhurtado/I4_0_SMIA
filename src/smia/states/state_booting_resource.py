import logging

from smia.behaviours.CheckPhysicalAssetBehaviour import CheckPhysicalAssetBehaviour
from smia.states.state_booting import StateBooting
from smia.utilities.general_utils import SMIAGeneralInfo

_logger = logging.getLogger(__name__)


class StateBootingResource(StateBooting):
    """
    This class contains the Boot state of the common AAS Manager.
    """

    async def run(self):
        """
        This method implements the boot state of the AAS Manager of type resource. Here all the required initialization
        tasks are performed.
        """

        # First the common initialization tasks perfomed by any AAS Manager will be executed
        await super().booting_state_logic()

        # In the booting state of type resource the physical asset has to be checked
        check_physical_asset_behav = CheckPhysicalAssetBehaviour(self.agent)
        self.agent.add_behaviour(check_physical_asset_behav)

        # Wait until the behaviour has finished to pass to running state.
        await check_physical_asset_behav.join()

        _logger.info(f"{self.agent.jid} agent has finished it Boot state.")

        self.set_next_state(SMIAGeneralInfo.RUNNING_STATE_NAME)

