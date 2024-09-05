import logging
from spade.behaviour import State

from behaviours.InteractionHandlingBehaviour import InteractionHandlingBehaviour
from behaviours.NegotiatingBehaviour import NegotiatingBehaviour
from behaviours.SvcACLHandlingBehaviour import SvcACLHandlingBehaviour
from utilities import AAS_Archive_utils
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

        # IAAS Manager is in the Running status
        AAS_Archive_utils.change_status('Running')

        # On the one hand, a behaviour is required to handle ACL messages
        svc_acl_handling_behav = SvcACLHandlingBehaviour(self.agent)
        self.agent.add_behaviour(svc_acl_handling_behav, AASmanagerInfo.SVC_STANDARD_ACL_TEMPLATE)

        # On the other hand, a behaviour is required to handle interaction messages
        interaction_handling_behav = InteractionHandlingBehaviour(self.agent)
        self.agent.add_behaviour(interaction_handling_behav)

        # Besides, the negotiation behaviour has to be added to the agent
        negotiation_behav = NegotiatingBehaviour(self.agent)
        self.agent.add_behaviour(negotiation_behav, AASmanagerInfo.NEG_STANDARD_ACL_TEMPLATE)

        # Wait until the behaviour has finished. Is a CyclicBehaviour, so it will not end until an error occurs or, if
        # desired, it can be terminated manually using "behaviour.kill()".
        await svc_acl_handling_behav.join()
        await interaction_handling_behav.join()
        await negotiation_behav.join()

        # If the Execution Running State has been completed, the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Running state.")
        self.set_next_state(AASmanagerInfo.STOPPING_STATE_NAME)
