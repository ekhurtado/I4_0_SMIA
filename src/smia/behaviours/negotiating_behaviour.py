import json
import logging

from spade.behaviour import CyclicBehaviour

from smia.behaviours.specific_handle_behaviours.handle_negotiation_behaviour import HandleNegotiationBehaviour
from smia.behaviours.specific_handle_behaviours.handle_svc_response_behaviour import HandleSvcResponseBehaviour
from smia.css_ontology.css_ontology_utils import CapabilitySkillACLInfo, CapabilitySkillOntologyUtils
from smia.logic import negotiation_utils, inter_aas_interactions_utils
from smia.logic.exceptions import RequestDataError
from smia.utilities import smia_archive_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLJSONSchemas, ServiceTypes
from smia.utilities.smia_info import SMIAInteractionInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


class NegotiatingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles the negotiation requests made by other standardized SMIAs
    through ACL messages in the I4.0 System.
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

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("NegotiationBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.aclinfo("         + Message received on SMIA (NegotiatingBehaviour) from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # TODO quizas hay que comprobar que el thread no existe? Para hacer al igual que en la peticion de
            #  servicios, utilizar el thread como identificador. Hay que pensarlo, ya que de este modo el thread
            #  serviría para un unico servicio a un AAS

            # Depending on the performative of the message, the agent will have to perform some actions or others
            match msg.get_metadata('performative'):
                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP:
                    _logger.aclinfo("The agent has received a request to start a negotiation (CFP) with thread ["
                                    + msg.thread + "]")

                    # Since the negotiation is an agent capability, it will be checked the validity of the received data
                    cap_req_data = None
                    try:
                        cap_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        await self.check_received_capability_request_data(cap_req_data)
                    except RequestDataError as cap_request_error:
                        # The data are not valid, so the requester must be informed.
                        acl_msg = inter_aas_interactions_utils.create_inter_smia_response_msg(
                            receiver=GeneralUtils.get_sender_from_acl_msg(msg),
                            thread=msg.thread,
                            performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                            ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION,   # TODO pensar si definir un NegRequest y NegResponse
                            service_id=msg_json_body['serviceID'],
                            service_type=msg_json_body['serviceType'],
                            service_params=json.dumps({'reason': cap_request_error.message})
                        )
                        await self.send(acl_msg)
                        _logger.warning("Capability request with thread [{}] has invalid data, therefore the requester"
                                        " has been informed".format(msg.thread))
                        return  # The run method is terminated to restart checking for new messages.

                    # First, some useful information is obtained from the msg
                    targets_list = cap_req_data['serviceData']['serviceParams']['targets'].split(',')
                    neg_requester_jid = GeneralUtils.get_sender_from_acl_msg(msg)
                    neg_criteria = cap_req_data['serviceData']['serviceParams'][CapabilitySkillACLInfo.REQUIRED_SKILL_NAME]
                    if len(targets_list) == 1:
                        # There is only one target available (therefore, it is the only one, so it is the winner)
                        _logger.info("The SMIA has won the negotiation with thread [" + msg.thread + "]")

                        # As the winner, it will reply to the sender with the result of the negotiation
                        acl_response_msg = negotiation_utils.create_neg_response_msg(
                            receiver=neg_requester_jid,
                            thread=msg.thread,
                            service_id=msg_json_body['serviceID'],
                            service_type=msg_json_body['serviceType'],
                            winner=str(self.myagent.jid))
                        await self.send(acl_response_msg)
                        _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                        + msg.thread + "]")

                        # The information will be stored in the log
                        execution_info = {'capName': 'Negotiation',
                                          'capType': CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE,
                                          'participants': str(self.myagent.jid), 'criteria': neg_criteria,
                                          'winner': 'True'}
                        smia_archive_utils.save_completed_svc_log_info(
                            GeneralUtils.get_current_timestamp(), GeneralUtils.get_current_timestamp(),
                            inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg), execution_info,
                            ServiceTypes.CSS_RELATED_SERVICE)

                        # Finally, the data is stored in the SMIA
                        # TODO pensar si esto es necesario (ya se almacena todo en el JSON del Archive)
                        neg_data_json = negotiation_utils.create_neg_json_to_store(
                            neg_requester_jid=neg_requester_jid,
                            participants=msg_json_body['serviceData']['serviceParams']['targets'],
                            neg_criteria=neg_criteria,
                            is_winner=True)
                        await self.myagent.save_negotiation_data(thread=msg.thread, neg_data=neg_data_json)

                    else:
                        # If there are more targets, a management behavior is added to the SMIA, which will be
                        # in charge of this particular negotiation. To this end, some information has to be passed to
                        # the behaviour
                        behaviour_info = {
                            'thread': msg.thread,
                            'neg_requester_jid': neg_requester_jid,
                            'targets': msg_json_body['serviceData']['serviceParams']['targets'],
                            'neg_criteria': neg_criteria
                        }
                        # The FIPA-ACL template added to this behavior ensures that you will only receive PROPOSE
                        # messages but also only with the thread of that specific thread
                        handle_neg_template = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_PROPOSE
                        handle_neg_template.thread = msg.thread
                        neg_req_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        handle_neg_behav = HandleNegotiationBehaviour(self.agent, behaviour_info, neg_req_data)
                        self.myagent.add_behaviour(handle_neg_behav, handle_neg_template)

                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                    _logger.aclinfo("The agent has received an Inter AAS interaction message related to a negotiation:"
                                    " Inform")
                    if msg_json_body['serviceID'] == 'negotiationResult':
                        _logger.aclinfo("The agent has received the result of the negotiation with thread ["+
                                        msg.thread+"].")
                        # TODO BORRAR (enfoque antiguo): pensar como gestionar las respuestas de
                        # As the result of a negotiation is a response to a previous request, a new
                        # HandleSvcResponseBehaviour to handle this service response will be added to the agent
                        svc_resp_data = inter_aas_interactions_utils.create_svc_json_data_from_acl_msg(msg)
                        svc_resp_handling_behav = HandleSvcResponseBehaviour(self.agent,
                                                                             'Inter AAS interaction',
                                                                             svc_resp_data)
                        self.myagent.add_behaviour(svc_resp_handling_behav)
                    else:
                        _logger.warning('serviceID not available')

                case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE:
                    _logger.aclinfo("The agent has received a response in a negotiation: Failure")
                    # TODO pensar como se deberian gestionar este tipo de mensajes en una negociacion
                case _:
                    _logger.error("ACL performative type not available.")
        else:
            _logger.info("         - No message received within 10 seconds on SMIA (NegotiatingBehaviour)")


    async def check_received_capability_request_data(self, cap_req_data):
        """
        This method checks whether the data received contains the necessary information to be able to execute
        the agent capability. If an error occurs, it throws a CapabilityDataError exception.

        Args:
            cap_req_data: (dict): all the information about the agent capability request
        """
        # First, the structure and attributes of the received data are checked and validated
        await inter_aas_interactions_utils.check_received_request_data_structure(
            cap_req_data, ACLJSONSchemas.JSON_SCHEMA_CAPABILITY_REQUEST)
        received_cap_data = cap_req_data['serviceData']['serviceParams']
        cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
        cap_ontology_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)
        if cap_ontology_instance is None:
            raise RequestDataError("The capability {} does not an instance defined in the ontology of this "
                                   "DT".format(cap_name))
        if CapabilitySkillACLInfo.REQUIRED_SKILL_NAME not in received_cap_data:
            raise RequestDataError("The skill need to be defined in negotiation requests.")
        skill_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_NAME]
        result, skill_instance = cap_ontology_instance.check_and_get_related_instance_by_instance_name(skill_name)
        if result is False:
            raise RequestDataError("The capability {} and skill {} are not linked in the ontology of this "
                                   "DT, or the skill does not have an instance"
                                   ".".format(cap_name, skill_name))
        if CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME in received_cap_data:
            # Solo si se ha definido la skill se define la skill interface, sino no tiene significado
            # TODO pensar la frase anterior. Realmente tiene significado o no? Si no se define la skill, podriamos
            #  definir una interfaz que queremos utilizar si o si? En ese caso, habria que buscar una skill con esa
            #  interfaz para ejecutarla
            skill_interface_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME]
            result, instance = skill_instance.check_and_get_related_instance_by_instance_name(skill_interface_name)
            if result is False:
                raise RequestDataError("The skill {} and skill interface {} are not linked in the ontology of "
                                       "this DT, or the skill interface does not have an instance"
                                       ".".format(skill_name, skill_interface_name))
        # Negotiation requests require some mandatory values
        if 'targets' not in received_cap_data:
            raise RequestDataError("The negotiation capability request cannot be fulfilled due to lack of objectives "
                                   "in the negotiation data.")