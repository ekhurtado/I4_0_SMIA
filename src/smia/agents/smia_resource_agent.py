import logging

from smia.agents.smia_agent import SMIAAgent
from smia.states.state_booting_resource import StateBootingResource
from smia.states.state_running import StateRunning
from smia.states.state_stopping import StateStopping
from smia.states.state_idle import StateIdle
from smia.utilities.general_utils import SMIAGeneralInfo
from smia.behaviours.aas_fsm_behaviour import AASFSMBehaviour

_logger = logging.getLogger(__name__)


class SMIAResourceAgent(SMIAAgent):
    """
    This is the SMIA Agent for physical resource assets. It extends the generic class AASManagerAgent.
    """

    async def setup(self):
        """
        This method performs the setup of physical resource type of Managers. It defines the Finite State Machine (FSM)
        of the SMIA Agent.
        """

        # First, the FSMBehaviour is instantiated
        fsm_behaviour = AASFSMBehaviour()

        # A common SMIA has three states
        fsm_behaviour.add_state(name=SMIAGeneralInfo.BOOTING_STATE_NAME, state=StateBootingResource(), initial=True)
        fsm_behaviour.add_state(name=SMIAGeneralInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=SMIAGeneralInfo.STOPPING_STATE_NAME, state=StateStopping())
        fsm_behaviour.add_state(name=SMIAGeneralInfo.IDLE_STATE_NAME, state=StateIdle())

        # Transitions are defined to determine from which state to which other state you are allowed to move to.
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.BOOTING_STATE_NAME, dest=SMIAGeneralInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.RUNNING_STATE_NAME, dest=SMIAGeneralInfo.STOPPING_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.RUNNING_STATE_NAME, dest=SMIAGeneralInfo.IDLE_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.IDLE_STATE_NAME, dest=SMIAGeneralInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.IDLE_STATE_NAME, dest=SMIAGeneralInfo.STOPPING_STATE_NAME)

        # The FSM behaviour is added to the agent
        self.add_behaviour(fsm_behaviour)
        _logger.info(f"{self.jid} setup finished correctly.")
