import logging

from spade.behaviour import State

from smia.utilities import smia_archive_utils

_logger = logging.getLogger(__name__)


class StateStopping(State):
    """
    This class contains the Stop state of the common SMIA.
    """

    # TODO sin acabar

    async def run(self):
        """
        This method implements the stop state of the common SMIA.
        """
        _logger.info("## STATE 3: STOPPING ##")
        # sb = StoppingBehaviour(self.agent)
        # self.agent.add_behaviour(sb)
        _logger.info("     [Stopping Behaviour]")
        _logger.info("         |___ Stopping MachineAgent...")
        smia_archive_utils.update_status('Stopping')
        # No se ha indicado un estado final, por lo que este se considera el último
