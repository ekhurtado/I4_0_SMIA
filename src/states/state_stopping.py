import logging

from spade.behaviour import State

_logger = logging.getLogger(__name__)


class StateStopping(State):
    """
    This class contains the Stop state of the common AAS Manager.
    """

    # TODO sin acabar

    async def run(self):
        """
        This method implements the stop state of the common AAS Manager.
        """
        _logger.info("## STATE 3: STOPPING ##")
        # sb = StoppingBehaviour(self.agent)
        # self.agent.add_behaviour(sb)
        _logger.info("     [Stopping Behaviour]")
        _logger.info("         |___ Stopping MachineAgent...")
        # No se ha indicado un estado final, por lo que este se considera el último
