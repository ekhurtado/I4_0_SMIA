import logging
from spade.behaviour import FSMBehaviour

_logger = logging.getLogger(__name__)


class AASFSMBehaviour(FSMBehaviour):
    """
    This class is an extension of the own FMSBehaviour of SPADE, which allows to print the start and the finish of
    the Finite State Machine.
    """
    async def on_start(self):
        """This method prints that the FSM has started."""
        _logger.info(f"    ** FSM starting at initial state --> {self.current_state}")

    async def on_end(self):
        """This method prints that the FSM has stopped and execute the agent-related stopping method."""
        _logger.info(f"    ** FSM finished at state --> {self.current_state}")
        await self.agent.stop()
