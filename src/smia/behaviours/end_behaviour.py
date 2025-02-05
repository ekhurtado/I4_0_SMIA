import logging
from spade.behaviour import OneShotBehaviour

_logger = logging.getLogger(__name__)


class EndBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for ending the agent.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        _logger.info(str(self.agent.id) + ":     [End Behaviour]")
        _logger.info("         |___ Agent entering Ending state...")
        self.kill()
        _logger.info("         |___ Agent killed...")
