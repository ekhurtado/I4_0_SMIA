import logging

from agents.AASManagerAgent import AASManagerAgent
from states.StateBootingResource import StateBootingResource
from states.StateRunning import StateRunning
from states.StateStopping import StateStopping
from states.StateIdle import StateIdle
from utilities.AASmanagerInfo import AASmanagerInfo
from behaviours.AASFSMBehaviour import AASFSMBehaviour

_logger = logging.getLogger(__name__)


class AASManagerResourceAgent(AASManagerAgent):
    """
    This is the top level in the hierarchy of SPADE Agents. It extends the own class Agent of SPADE. The AAS Manager
    Agent will be the generic and from which all other types of AAS Managers will start.
    """

    async def setup(self):
        """
        This method performs the common setup of all types of Managers. It defines the Finite State Machine of the
        general (FSM) AAS Manager Agent.
        """

        # First, the FSMBehaviour is instantiated
        fsm_behaviour = AASFSMBehaviour()

        # A common AAS Manager has three states
        fsm_behaviour.add_state(name=AASmanagerInfo.BOOTING_STATE_NAME, state=StateBootingResource(), initial=True)
        fsm_behaviour.add_state(name=AASmanagerInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=AASmanagerInfo.STOPPING_STATE_NAME, state=StateStopping())
        fsm_behaviour.add_state(name=AASmanagerInfo.IDLE_STATE_NAME, state=StateIdle())

        # Añadir comportamiento FSM al agente
        self.add_behaviour(fsm_behaviour)
        _logger.info(f"{self.jid} setup finished correctly.")
