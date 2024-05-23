import logging
from spade.behaviour import State

from behaviours.ACLHandlingBehaviour import ACLHandlingBehaviour
from utilities.AASmanagerInfo import AASmanagerInfo

_logger = logging.getLogger(__name__)


class StateRunning(State):
    """
    This class contains the Running state of the common AAS Manager.
    """

    async def run(self):
        """
        This method implements the running state of the common AAS Manager. Here all requests services are handled,
        both from ACL of another AAS Manager or from the AAS Core.
        """

        _logger.info("## STATE 2: RUNNING ##  (Initial state)")

        # On the one hand, a behaviour is required to handle ACL message
        acl_handling_behav = ACLHandlingBehaviour(self.agent)
        self.agent.add_behaviour(acl_handling_behav, AASmanagerInfo.STANDARD_ACL_TEMPLATE)

        # Finished the Boot State the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Boot state.")
        self.set_next_state(AASmanagerInfo.RUNNING_STATE_NAME)
