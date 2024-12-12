import json
import logging

from spade.behaviour import CyclicBehaviour

from smia.behaviours.handle_capability_behaviour import HandleCapabilityBehaviour
from smia.behaviours.handle_svc_request_behaviour import HandleSvcRequestBehaviour
from smia.behaviours.HandleSvcResponseBehaviour import HandleSvcResponseBehaviour
from smia.logic import inter_aas_interactions_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


class ACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA will receive from the
    others standardized SMIAs in the I4.0 System.
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
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.aclinfo("         + Message received on AAS Manager Agent (ACLHandlingBehaviour)"
                            " from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # Depending on the performative of the message, the agent will have to perform some actions or others
            match msg.get_metadata('performative'):
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:
                    _logger.aclinfo("The performative of the message is Request, so the DT needs to perform some"
                                    " action.")

                    # service_id = msg_json_body['serviceID']
                    # if service_id == 'capabilityRequest':
                    # TODO pensar si generar un behaviour para recibir peticiones de servicios y otro para peticiones
                    #  de capacidades (en ese caso solo hay que comprobar la ontologia, no la performativa, ya que esta
                    #  se analiza en los behaviours de gestion individuales)
                    if msg.get_metadata('ontology') == FIPAACLInfo.FIPA_ACL_ONTOLOGY_CAPABILITY_REQUEST:
                        _logger.aclinfo("The agent has received a request to perform a capability")
                        # The behaviour to handle this specific capability will be added to the agent
                        svc_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        capability_handling_behav = HandleCapabilityBehaviour(self.agent, svc_req_data)
                        self.myagent.add_behaviour(capability_handling_behav)
                    if msg.get_metadata('ontology') == FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST:
                        _logger.aclinfo("The agent has received a request to perform a service")
                        # The behaviour to handle this specific capability will be added to the agent
                        svc_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        svc_req_handling_behav = HandleSvcRequestBehaviour(self.agent,
                                                                           None,    # TODO ELIMINAR (es del enfoque viejo)
                                                                           svc_req_data)
                        self.myagent.add_behaviour(svc_req_handling_behav)
                    else:
                        service_category = msg_json_body['serviceData']['serviceCategory']
                        if service_category == 'service-request':
                            # The new service request is looked up in the agent's global ACL request dictionary.
                            if await self.myagent.get_acl_svc_request(thread=msg.thread) is not None:
                                _logger.error("A request has been made for an ACL service that already exists.")
                            else:
                                # The thread is the identifier of the conversation, so all the information will be
                                # saved using it
                                msg_json_body['performative'] = msg.get_metadata('performative')
                                msg_json_body['ontology'] = msg.get_metadata('ontology')

                                msg_json_body['sender'] = GeneralUtils.get_sender_from_acl_msg(msg)
                                await self.myagent.save_new_acl_svc_request(thread=msg.thread,
                                                                            request_data=msg_json_body)
                                _logger.aclinfo(
                                    "acl_svc_requests shared object updated by " + str(self.__class__.__name__)
                                    + " responsible for thread [" + msg.thread + "]. Action: request data added")

                                svc_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)

                                # A new behaviour is added to the SPADE agent to handle this specific service request
                                svc_req_handling_behav = HandleSvcRequestBehaviour(self.agent,
                                                                                   'Inter AAS interaction',
                                                                                   svc_req_data)
                                self.myagent.add_behaviour(svc_req_handling_behav)

                        elif service_category == 'service-response':
                            _logger.aclinfo(
                                "The agent has received the response of a service with thread [" + msg.thread + "].")

                            # As it is a response to a previous request, a new HandleSvcResponseBehaviour to handle this service
                            # response will be added to the agent
                            svc_resp_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                            svc_resp_handling_behav = HandleSvcResponseBehaviour(self.agent,
                                                                                 'Inter AAS interaction',
                                                                                 svc_resp_data)
                            self.myagent.add_behaviour(svc_resp_handling_behav)

                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF:
                    _logger.aclinfo("The performative of the message is Query-If, so the DT has been asked about some "
                                    "aspect of it.")

                    # service_category = msg_json_body['serviceID']
                    # if service_category == 'capabilityChecking':
                    if msg.get_metadata('ontology') == FIPAACLInfo.FIPA_ACL_ONTOLOGY_CAPABILITY_CHECKING:
                        _logger.info("The DT has been asked to check if it has a given capability.")
                        svc_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        capability_handling_behav = HandleCapabilityBehaviour(self.agent, svc_req_data)
                        self.myagent.add_behaviour(capability_handling_behav)
                case _:
                    _logger.error("ACL performative type not available.")

        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (ACLHandlingBehaviour)")
