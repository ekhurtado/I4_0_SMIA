import logging
import os

from spade.behaviour import CyclicBehaviour

from logic import Interactions_utils
from utilities import Submodels_utils
from utilities.AAS_Archive_utils import file_to_json
from utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


class CheckCoreInitializationBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour responsible for check that the AAS Core has been initialized.
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
        # If the file does not exist the behaviour continues to start and check again
        if os.path.isfile(AASarchiveInfo.CORE_STATUS_FILE_PATH) is True:
            if file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)['status'] != "Initializing":
                # If the status is not "Initializing" the AAS Core is ready, so the behaviour is finished
                _logger.info('AAS Core has initialized, so the AAS Manager can be switched to the run state.')
                self.kill()
