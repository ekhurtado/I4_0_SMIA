import logging
from spade.behaviour import OneShotBehaviour

from logic import IntraAASInteractions_utils
from utilities import submodels_utils
from utilities.aas_general_info import SMIAGeneralInfo

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
        # TODO se podria realizar una comprobacion de si el activo fisico es accesible usando todos los asset
        #  connections definidos en el modelo AAS

        # First it is checked if the submodel file exists has to be checked
        if submodels_utils.check_if_submodel_exists("asset_identification") is False:
            # TODO pensar que hacer en el caso de que no exista (matar al agente?)
            _logger.error("The submodel asset identification does not exist.")
        _logger.info("The submodel 'Asset identification' of the asset exists.")

        # Besides, it is necessary to check whether the connection to the asset is established. To do that, a message
        # to the AAS Core has to be sent.
        # Create the valid JSON structure to save in svcRequests.json
        current_interaction_id = self.myagent.get_interaction_id()
        # TODO comprobarlo, no se realiza bien la peticion de servicio Intra AAS interaction
        svc_request_json = IntraAASInteractions_utils.create_svc_request_interaction_json(
            interaction_id=self.agent.get_interaction_id(),
            svc_id='checkAssetConnection',
            svc_type='AssetRelatedService')
        # Save the JSON in svcRequests.json
        IntraAASInteractions_utils.add_new_svc_request(svc_request_json)

        # Since a new service has been request, the interaction of the agent has to be incremented
        self.myagent.increase_interaction_id_num()

        # Check i
        # Wait until the service is completed
        # TODO cambiarlo. No debe haber una espera hasta que se complete el servicio de esta manera
        while True:
            _logger.info("checkAssetConnection service not completed yet.")
            svc_response = IntraAASInteractions_utils.get_svc_response_info(current_interaction_id)
            if svc_response is not None:
                print(svc_response)
                # Set the service as completed
                # Write the information in the log file
                IntraAASInteractions_utils.save_svc_info_in_log_file('Manager',
                                                                     SMIAGeneralInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                                                                     current_interaction_id)
                # Return message to the sender
                _logger.info("Service completed! Response: " + str(svc_response))
                break

        _logger.info("The connection with the asset is established.")
