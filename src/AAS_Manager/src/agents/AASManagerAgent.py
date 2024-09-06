from spade.agent import Agent
import logging

from spade.message import Message

from states.StateRunning import StateRunning
from states.StateStopping import StateStopping
from utilities.AASmanagerInfo import AASmanagerInfo
from behaviours.AASFSMBehaviour import AASFSMBehaviour
from states.StateBooting import StateBooting

_logger = logging.getLogger(__name__)


class AASManagerAgent(Agent):
    """
    This is the top level in the hierarchy of SPADE Agents. It extends the own class Agent of SPADE. The AAS Manager
    Agent will be the generic and from which all other types of AAS Managers will start.
    """

    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)

        self.interaction_id_num = 0 # The interactionId number is set to 0

    async def setup(self):
        """
        This method performs the common setup of all types of Managers. It defines the Finite State Machine (FSM) of
        the general AAS Manager Agent.
        """

        # First, the FSMBehaviour is instantiated
        fsm_behaviour = AASFSMBehaviour()

        # A common AAS Manager has three states
        fsm_behaviour.add_state(name=AASmanagerInfo.BOOTING_STATE_NAME, state=StateBooting(), initial=True)
        fsm_behaviour.add_state(name=AASmanagerInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=AASmanagerInfo.STOPPING_STATE_NAME, state=StateStopping())

        # Transitions are defined to determine from which state to which other state you are allowed to move to.
        fsm_behaviour.add_transition(source=AASmanagerInfo.BOOTING_STATE_NAME, dest=AASmanagerInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=AASmanagerInfo.RUNNING_STATE_NAME, dest=AASmanagerInfo.STOPPING_STATE_NAME)

        # The FSM behaviour is added to the agent
        self.add_behaviour(fsm_behaviour)
        _logger.info(f"{self.jid} setup finished correctly.")


    def get_interaction_id(self):
        """
        This method returns the identifier of the AAS Intra interactions of the AAS Manager.

        Returns:
            str: identifier of the interaction id.
        """
        return 'manager-' + str(self.interaction_id_num)

