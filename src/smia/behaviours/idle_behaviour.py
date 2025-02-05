import logging
from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)


class IdleBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour responsible for the idle state tasks.
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
        _logger.info(str(self.agent.id) + ":     [Idle Behaviour]")
        _logger.info("         |___ Resource entering IDLE state...")

        # TODO pensar el comportamiento del SMIA en este estado (p.e. avisar del cambio de estado al Core,
        #  si llegan mensajes ACL almacenarlos para su posterior procesamiento cuando vuelva a running...)

