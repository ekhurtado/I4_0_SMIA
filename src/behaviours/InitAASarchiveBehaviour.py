import logging
from spade.behaviour import OneShotBehaviour

from utilities import AAS_Archive_utils

_logger = logging.getLogger(__name__)


class InitAASarchiveBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for initialize the AAS Archive, performing the necessary actions
    to let the AAS Archive in the initial conditions to start the main program.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # Create the status file
        AAS_Archive_utils.create_status_file()

        # Create the interaction files
        AAS_Archive_utils.create_interaction_files()

        # Create log file
        AAS_Archive_utils.create_log_files()

        _logger.info("AAS Archive initialized.")
