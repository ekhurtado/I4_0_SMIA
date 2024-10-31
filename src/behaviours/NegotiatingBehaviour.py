import json
import logging

from spade.behaviour import CyclicBehaviour

from behaviours.HandleNegotiationBehaviour import HandleNegotiationBehaviour
from behaviours.HandleSvcResponseBehaviour import HandleSvcResponseBehaviour
from logic import Negotiation_utils, InterAASInteractions_utils
from utilities.AASmanagerInfo import AASmanagerInfo
from utilities.GeneralUtils import GeneralUtils

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

                    if msg_json_body['serviceID'] == 'capabilityRequest':
                        _logger.aclinfo("The agent has been asked to perform a capability to negotiate.")
                        # TODO pensar como gestionar las negociaciones en forma de capacidades
                        # TODO PROXIMO PASO: ahora la negociacion vendran solicitadas cmo una capacidad del agente
                        #  (agentCapability). Por ello, primero se comprobará si el criterio que se ha enviado para
                        #  participar en la negociacion es valido, es decir, si su valor esta entre los definidos para
                        #  este activo. El criterio para las negociaciones es una constraint que en realidad es un SME
                        #  Reference que apunta al skill parameter del criterio, que está en el SME de la skill, el cual es una
                        #  operación con un input con el criterio. Esta variable de entrada 'criterio' tiene asociada
                        #  un conceptDescription con los posibles valores. En este punto, se tendra que comprobar si el
                        #  criterio solicitado en el mensaje ACL existe entre los valores posibles definidos en el
                        #  conceptDescription. Si el resultado es que no, el agente deberá responder con un mensaje
                        #  indicando que no puede ejecutar esa capacidad, junto a la razon (p.e. con una performativa
                        #  Refuse)
                        msg_json_body['serviceData']['serviceParams']['criteria'] = msg_json_body['serviceData']['serviceParams']['NegotiationCriteria']

                    # First, some useful information is obtained from the msg
                    targets_list = msg_json_body['serviceData']['serviceParams']['targets'].split(',')
                    neg_requester_jid = GeneralUtils.get_sender_from_acl_msg(msg)
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
                    _logger.aclinfo("The agent has received an Inter AAS interaction message related to a negotiation:"
                                    " Inform")
                    if msg_json_body['serviceID'] == 'negotiationResult':
                        _logger.aclinfo("The agent has received the result of the negotiation with thread ["+
                                        msg.thread+"].")
                        # As the result of a negotiation is a response to a previous request, a new
                        # HandleSvcResponseBehaviour to handle this service response will be added to the agent
                        svc_resp_data = InterAASInteractions_utils.create_svc_json_data_from_acl_msg(msg)
                        svc_resp_handling_behav = HandleSvcResponseBehaviour(self.agent,
                                                                             'Inter AAS interaction',
                                                                             svc_resp_data)
                        self.myagent.add_behaviour(svc_resp_handling_behav)
                    else:
                        # TODO
                        print('serviceID not available')

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
