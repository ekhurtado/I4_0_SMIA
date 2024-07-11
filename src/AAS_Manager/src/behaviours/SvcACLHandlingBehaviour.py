import json
import logging
import time

from spade.behaviour import CyclicBehaviour

from logic import Interactions_utils
from utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


class SvcACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the AAS Manager will receive from the
    others standardized AAS Manager in the I4.0 System.
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

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("ACLHandlingBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
<<<<<<< HEAD
        msg = await self.receive(timeout=10) # Timeout set to 10 seconds so as not to continuously execute the behavior.
=======
        msg = await self.receive(timeout=5)  # Timeout set to 5 seconds so as not to continuously execute the behavior.
>>>>>>> bef2e4cd69b773fced98c40691a08b0385784d8c
        if msg:
            # An ACL message has been received by the agent
            _logger.info("         + Message received on AAS Manager Agent (ACLHandlingBehaviour)")
            _logger.info("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # As the performative is set to CallForProposals, the service type will be analyzed directly
            match msg_json_body['serviceType']:
                # TODO esta hecho asi para pruebas, pero hay que pensar el procedimiento a seguir a la hora de
                #  gestionar los mensajes ACL
                case "AssetRelatedService":
                    self.handle_asset_related_svc(msg_json_body)
                case "AASInfrastructureServices":
                    self.handle_aas_infrastructure_svc(msg_json_body)
                case "AASservices":
                    self.handle_aas_services(msg_json_body)
                case "SubmodelServices":
                    self.handle_submodel_services(msg_json_body)
                case _:
                    _logger.error("Service type not available.")
        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (ACLHandlingBehaviour)")

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    def handle_asset_related_svc(self, svc_data):
        """
        This method handles Asset Related Services. These services are part of I4.0 Application Component (application
        relevant).

        Args:
            svc_data (dict): the information of the data in JSON format.
        """
        # Create the valid JSON structure to save in svcRequests.json
        svc_request_json = Interactions_utils.create_svc_request_json(interaction_id=self.agent.interaction_id,
                                                                      svc_id=svc_data['serviceID'],
                                                                      svc_type=svc_data['serviceType'],
                                                                      svc_data=svc_data['serviceData'])
        # Save the JSON in svcRequests.json
        Interactions_utils.add_new_svc_request(svc_request_json)
        current_interaction_id = self.agent.interaction_id
        self.agent.interaction_id += 1  # increment the interaction id as new requests has been made

        # Wait until the service is completed
        # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
        #  haber una espera hasta que se complete el servicio
        while True:
            _logger.info(str(svc_data['serviceID']) + " service not completed yet.")
            svc_response = Interactions_utils.get_svc_response_info(current_interaction_id)
            if svc_response is not None:
                print(svc_response)
                # Set the service as completed
                # Write the information in the log file
                Interactions_utils.save_svc_info_in_log_file('Manager',
                                                             AASarchiveInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                                                             current_interaction_id)
                # Return message to the sender
                _logger.info("Service completed! Response: " + str(svc_response))
                break
            time.sleep(2)

    def handle_aas_infrastructure_svc(self, svc_data):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services (
        Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an
        AAS, but by the platform (computational infrastructure). These include the AAS Create Service (for creating
        AASs with unique identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery
        Services (for searching for AASs).

        Args:
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))

    def handle_aas_services(self, svc_data):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        Args:
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))

    def handle_submodel_services(self, svc_data):
        """
        This method handles Submodel Services. These services are part of I4.0 Application Component (application
        relevant).

        Args:
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))
