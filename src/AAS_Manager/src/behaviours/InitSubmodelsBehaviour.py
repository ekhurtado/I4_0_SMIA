import logging

from spade.behaviour import OneShotBehaviour
from utilities import ConfigMap_utils, Submodels_utils

_logger = logging.getLogger(__name__)


class InitSubmodelsBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for initialize the submodels, performing the necessary actions to
    let all submodels in the initial conditions to start the main program: obtain all the information from the
    ConfigMap associated to the component, in order to create the necessary XML submodel files and store them in the
    AAS Archive.
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
        # First, the selected submodels are obtained
        selected_submodel_names = ConfigMap_utils.get_submodel_names()

        # TODO: faltaria comprobar entre los submodelos seleccionados cuales son propios de todos los AASs (los que
        #  seran los propios del AAS Manager). El usuario podra proponer submodelos y tambien se escribira en el
        #  ConfigMap su informacion, pero sera el AAS Core (desarrollado por el usuario) el encargado de generar el
        #  XML (como tambien de actualizarlo, leerlo...), ya que es el usuario el que conoce su estructura

        # Create submodels files for each one
        Submodels_utils.create_submodel_files(selected_submodel_names)

        _logger.info("Submodels initialized.")
