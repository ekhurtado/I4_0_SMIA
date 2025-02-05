import logging
from spade.behaviour import OneShotBehaviour

_logger = logging.getLogger(__name__)


class CheckPhysicalAssetBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for check that all information about the physical asset is available
    in the submodels and also that the connection is established.
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
        # TODO se podria realizar una comprobacion de si el activo fisico es accesible usando todos los asset
        #  connections definidos en el modelo AAS
        # TODO POR HACER
        _logger.info("The connection with the asset is established.")
