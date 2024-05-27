import json
import logging

from spade.behaviour import CyclicBehaviour

from logic import Services_utils

_logger = logging.getLogger(__name__)


class ACLHandlingBehaviour(CyclicBehaviour):
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

    # async def on_start(self):
    #     """
    #     This method implements the initialization process of this behaviour. Here the template of the ACL message
    #     that will be received by the agent is set.
    #     """
    #     logging.basicConfig(level=logging.INFO)

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        _logger.info("ACLHandlingBehaviour running...")

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(timeout=5) # Timeout set to 5 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.info("         + Message received on AAS Manager Agent (ACLHandlingBehaviour)")
            _logger.info("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # As the performative is set to CallForProposals, the service type will be analyzed directly
            match msg_json_body['serviceType']:
                # TODO esta hecho asi para pruebas, pero hay que pensar el procedimiento a seguir a la hora de gestionar los mensajes ACL
                case "AssetRelatedService":
                    Services_utils.handle_asset_related_svc(self.agent.interaction_id, msg_json_body)
                case "AASInfrastructureServices":
                    Services_utils.handle_aas_infrastructure_svc(self.agent.interaction_id, msg_json_body)
                case "AASservices":
                    Services_utils.handle_aas_services(self.agent.interaction_id, msg_json_body)
                case "SubmodelServices":
                    Services_utils.handle_submodel_services(self.agent.interaction_id, msg_json_body)
                case _:
                    _logger.error("Service type not available.")
        else:
            _logger.info("         - No message received within 5 seconds on AAS Manager Agent (ACLHandlingBehaviour)")
