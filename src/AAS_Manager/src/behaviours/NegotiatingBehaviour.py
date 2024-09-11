import json
import logging

from spade.behaviour import CyclicBehaviour

from behaviours.HandleNegotiationBehaviour import HandleNegotiationBehaviour
from logic import Negotiation_utils
from utilities.AASmanagerInfo import AASmanagerInfo

_logger = logging.getLogger(__name__)


# TODO analizar clase NegotiatingBehaviour de Alejandro para ver como manejaba las negociaciones entre agentes


class NegotiatingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles the negotiation requests made by other standardized AAS Managers
    through ACL messages in the I4.0 System.
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
            _logger.aclinfo("         + Message received on AAS Manager Agent (NegotiatingBehaviour)")
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # TODO quizas hay que comprobar que el thread no existe? Para hacer al igual que en la peticion de
            #  servicios, utilizar el thread como identificador. Hay que pensarlo, ya que de este modo el thread
            #  serviría para un unico servicio a un AAS

            # Depending on the performative of the message, the agent will have to perform some actions or others
            match msg.get_metadata('performative'):
                case "CallForProposal":
                    _logger.aclinfo("The agent has received a request to start a negotiation (CFP) with thread ["
                                    + msg.thread + "]")
                    # First, some useful information is obtained from the msg
                    targets_list = eval(msg_json_body['serviceData']['serviceParams']['targets'])

                    if '/' in str(msg.sender):  # XMPP server can add a random string to differentiate the agent JID
                        neg_requester_jid = str(msg.sender).split('/')[0]
                    else:
                        neg_requester_jid = str(msg.sender)

                    if len(targets_list) == 1:
                        # There is only one target available (therefore, it is the only one, so it is the winner)
                        _logger.info("The AAS has won the negotiation with thread [" + msg.thread + "]")

                        # As the winner, it will reply to the sender with the result of the negotiation
                        acl_response_msg = Negotiation_utils.create_neg_response_msg(
                            receiver=neg_requester_jid,
                            thread=msg.thread,
                            service_id=msg_json_body['serviceID'],
                            service_type=msg_json_body['serviceType'],
                            winner=str(self.myagent.jid))
                        await self.send(acl_response_msg)
                        _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                        + msg.thread + "]")

                        # Finally, the data is stored in the AAS Manager
                        neg_data_json = Negotiation_utils.create_neg_json_to_store(
                            neg_requester_jid=neg_requester_jid,
                            participants=msg_json_body['serviceData']['serviceParams']['targets'],
                            neg_criteria=msg_json_body['serviceData']['serviceParams']['criteria'],
                            is_winner=True)
                        await self.myagent.save_negotiation_data(thread=msg.thread, neg_data=neg_data_json)

                    else:
                        # If there are more targets, a management behavior is added to the AAS Manager, which will be
                        # in charge of this particular negotiation. To this end, some information has to be passed to
                        # the behaviour
                        neg_criteria = msg_json_body['serviceData']['serviceParams']['criteria']
                        behaviour_info = {
                            'thread': msg.thread,
                            'neg_requester_jid': neg_requester_jid,
                            'targets': msg_json_body['serviceData']['serviceParams']['targets'],
                            'neg_criteria': neg_criteria
                        }
                        # The FIPA-ACL template added to this behavior ensures that you will only receive PROPOSE
                        # messages but also only with the thread of that specific thread
                        handle_neg_template = AASmanagerInfo.NEG_STANDARD_ACL_TEMPLATE_PROPOSE
                        handle_neg_template.thread = msg.thread
                        handle_neg_behav = HandleNegotiationBehaviour(self.agent, behaviour_info)
                        self.myagent.add_behaviour(handle_neg_behav, handle_neg_template)

                case "Inform":
                    _logger.aclinfo("The agent has received a request to participate in a negotiation: Inform")
                    # TODO pensar como se deberian gestionar este tipo de mensajes en una negociacion
                case "Propose":
                    _logger.aclinfo("The agent has received a response in a negotiation: Propose")
                    # TODO en teoria estos mensajes nunca llegaran aqui, ya que lo recibira el behaviour encargado de
                    #  la negociacion
                case "Failure":
                    _logger.aclinfo("The agent has received a response in a negotiation: Failure")
                    # TODO pensar como se deberian gestionar este tipo de mensajes en una negociacion
                case _:
                    _logger.error("ACL performative type not available.")
        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (NegotiatingBehaviour)")
