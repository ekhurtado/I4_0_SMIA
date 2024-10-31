import logging

from agents.AASManagerAgent import AASManagerAgent
from states.StateRunning import StateRunning
from states.StateStopping import StateStopping
from utilities.AASmanagerInfo import AASmanagerInfo
from behaviours.AASFSMBehaviour import AASFSMBehaviour
from states.StateBooting import StateBooting

_logger = logging.getLogger(__name__)


class AASManagerAppAgent(AASManagerAgent):
    """
    This is the AAS Manager Agent for logical resource assets. It extends the generic class AASManagerAgent.
    """

    async def setup(self):
        """
        This method performs the setup of logical resource type of Managers. It defines the Finite State Machine (FSM)
        of the AAS Manager Agent.
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
