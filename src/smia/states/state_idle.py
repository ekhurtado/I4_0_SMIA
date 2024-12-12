import logging
from spade.behaviour import State

from smia.behaviours.idle_behaviour import IdleBehaviour
from smia.utilities import smia_archive_utils

_logger = logging.getLogger(__name__)


class StateIdle(State):
    """
    This class contains the Idle state of the AAS Manager.
    """

    async def run(self):
        """
        This method implements the idle state of the common AAS Manager. Here all requests services are handled,
        both from ACL of another AAS Manager or from the AAS Core.
        """

        _logger.info("## STATE 4: IDLE ##")
        smia_archive_utils.update_status('Idle')

        idle_behav = IdleBehaviour(self.agent)
        self.agent.add_behaviour(idle_behav)
