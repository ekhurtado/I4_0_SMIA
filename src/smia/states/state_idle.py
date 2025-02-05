import logging
from spade.behaviour import State

from smia.behaviours.idle_behaviour import IdleBehaviour
from smia.utilities import smia_archive_utils

_logger = logging.getLogger(__name__)


class StateIdle(State):
    """
    This class contains the Idle state of the SMIA.
    """

    async def run(self):
        """
        This method implements the idle state of the common SMIA. Here all requests services are handled,
        both from ACL of another SMIA or from the own SMIA.
        """

        _logger.info("## STATE 4: IDLE ##")
        smia_archive_utils.update_status('Idle')

        idle_behav = IdleBehaviour(self.agent)
        self.agent.add_behaviour(idle_behav)
