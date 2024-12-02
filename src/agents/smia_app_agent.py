import logging

from agents.smia_agent import SMIAAgent
from states.state_running import StateRunning
from states.state_stopping import StateStopping
from utilities.smia_info import SMIAInteractionInfo
from behaviours.aas_fsm_behaviour import AASFSMBehaviour
from states.state_booting import StateBooting

_logger = logging.getLogger(__name__)


class SMIAAppAgent(SMIAAgent):
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
        fsm_behaviour.add_state(name=SMIAInteractionInfo.BOOTING_STATE_NAME, state=StateBooting(), initial=True)
        fsm_behaviour.add_state(name=SMIAInteractionInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=SMIAInteractionInfo.STOPPING_STATE_NAME, state=StateStopping())

        # Transitions are defined to determine from which state to which other state you are allowed to move to.
        fsm_behaviour.add_transition(source=SMIAInteractionInfo.BOOTING_STATE_NAME, dest=SMIAInteractionInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAInteractionInfo.RUNNING_STATE_NAME, dest=SMIAInteractionInfo.STOPPING_STATE_NAME)

        # The FSM behaviour is added to the agent
        self.add_behaviour(fsm_behaviour)
        _logger.info(f"{self.jid} setup finished correctly.")
