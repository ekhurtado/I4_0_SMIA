import asyncio
import json
import logging

from spade.behaviour import CyclicBehaviour

from behaviours.HandleSvcRequestBehaviour import HandleSvcRequestBehaviour
from logic import Negotiation_utils
from utilities.GeneralUtils import GeneralUtils

_logger = logging.getLogger(__name__)


# TODO analizar clase NegotiatingBehaviour de Alejandro para ver como manejaba las negociaciones entre agentes


class HandleNegotiationBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handle a particular negotiation.
    """
    myagent = None  #: the SPADE agent object of the AAS Manager agent.
    thread = None  #: thread of the negotiation
    neg_requester_jid = None  #: JID of the SPADE agent that has requested the negotiation
    targets = None  #: targets of the negotiation
    neg_criteria = None  #: criteria of the negotiation
    neg_value = None  #: value of the negotiation
    targets_processed = set()  #: targets that their values have been processed
    neg_value_event = None

    def __init__(self, agent_object, negotiation_info):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        self.thread = negotiation_info['thread']
        self.neg_requester_jid = negotiation_info['neg_requester_jid']
        self.targets = negotiation_info['targets']
        self.neg_criteria = negotiation_info['neg_criteria']
        self.targets_processed = set()  # TODO pensar si cambiarlo a un set para evitar valores repetidos

        # This event object will allow waiting for the negotiation value if it is necessary to request it from an
        # external entity (such as the AAS Core)
        self.neg_value_event = asyncio.Event()

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleNegotiationBehaviour starting...")

        #  The value of the criterion must be obtained just before starting to manage the negotiation, so that at the
        #  time of sending the PROPOSE and receiving that of the others it will be the same value. Therefore, if to
        #  obtain the value you have to make an Intra AAS interaction request, the behaviour will not be able to start
        #  managing the negotiation until you get the answer to that request (together with the requested value).
        # TODO buscar una forma de dormir el behaviour hasta que neg_value deje de ser None
        await self.get_neg_value_with_criteria(self.neg_criteria)

        # Once the negotiation value is reached, the negotiation management can begin. The first step is to send the
        # PROPOSE message with your own value to the other participants in the negotiation.
        acl_propose_msg = Negotiation_utils.create_neg_propose_msg(thread=self.thread,
                                                                   targets=self.targets,
                                                                   neg_requester_jid=self.neg_requester_jid,
                                                                   neg_criteria=self.neg_criteria,
                                                                   neg_value=str(self.neg_value))
        # This PROPOSE FIP-ACL message is sent to all participants of the negotiation (except for this AAS Manager)
        targets_list = eval(self.targets)
        for jid_target in targets_list:
            if jid_target != str(self.agent.jid):
                acl_propose_msg.to = jid_target
                await self.send(acl_propose_msg)
                _logger.aclinfo("ACL PROPOSE negotiation message sent to " + jid_target +
                                " on negotiation with thread [" + self.thread + "]")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.aclinfo("         + PROPOSE Message received on AAS Manager Agent (HandleNegotiationBehaviour "
                            "in charge of the negotiation with thread [" + self.thread + "])")
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # The negotiation information is obtained from the message
            criteria = msg_json_body['serviceData']['serviceParams']['criteria']
            sender_agent_neg_value = msg_json_body['serviceData']['serviceParams']['neg_value']

            # The value of this AAS Manager and the received value are compared
            if float(sender_agent_neg_value) > self.neg_value:
                # As the received value is higher than this AAS Manager value, it must exit the negotiation.
                await self.exit_negotiation(is_winner=False)
                return  # killing a behaviour does not cancel its current run loop
            if (float(sender_agent_neg_value) == self.neg_value) and not self.agent.tie_break:
                # In this case the negotiation is tied but this AAS Manager is not the tie breaker.
                await self.exit_negotiation(is_winner=False)
                return  # killing a behaviour does not cancel its current run loop
            # The target is added as processed in the local object (as it is a Python 'set' object there is no problem
            # of duplicate agents)
            self.targets_processed.add(str(msg.sender))
            if len(self.targets_processed) == len(eval(self.targets)) - 1:
                # In this case all the values have already been received, so the value of this AAS Manager is the best
                _logger.info("The AAS has won the negotiation with thread [" + msg.thread + "]")

                # As the winner, it will reply to the sender with the result of the negotiation
                acl_response_msg = Negotiation_utils.create_neg_response_msg(receiver=self.neg_requester_jid,
                                                                             thread=self.thread,
                                                                             service_id='negotiationResult', # TODO pensar como llamarlo
                                                                             service_type='AssetRelatedService',
                                                                             # TODO ojo si decidimos que es de otro tipo
                                                                             winner=str(self.myagent.jid)
                                                                             )
                await self.send(acl_response_msg)
                _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                + msg.thread + "]")

                # The negotiation can be terminated, in this case being the winner
                await self.exit_negotiation(is_winner=True)

        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (NegotiatingBehaviour)")

    async def get_neg_value_with_criteria(self, criteria):
        """
        This method gets the negotiation value based on a given criteria.

        Args:
            criteria (str): criteria of the negotiation

        Returns:
            int: value of the negotiation
        """
        # TODO aqui hay que actualizarlo cuando pensemos como hacerlo, de momento se ha hecho una peticion de Intra AAS
        #  interaction al Core directamente, pero el AAS Manager deberia ser capaz de analizar el criterio y ver si el
        #  mismo tiene el valor (p.e. de un submodelo), o en cambio se lo tiene que pedir al AAS Core
        _logger.info("Getting the neg value with Intra AAS interaction...")
        intra_aas_svc_data = {
            'serviceCategory': 'service-request',
            'timestamp': GeneralUtils.get_current_timestamp(),
            'serviceParams': {
                'criteria': self.neg_criteria
            }
        }
        intra_aas_req_data = Negotiation_utils.create_intra_aas_neg_req_data(
            performative=self.template.metadata['performative'],
            ontology=self.template.metadata['ontology'],
            thread=self.thread,
            service_data=intra_aas_svc_data)

        # A new behaviour is added to the SPADE agent to handle this specific service request
        intra_aas_neg_req_handling_behav = HandleSvcRequestBehaviour(self.agent,
                                                                     'Inter AAS interaction',
                                                                     intra_aas_req_data)
        self.myagent.add_behaviour(intra_aas_neg_req_handling_behav)

        # In this case, as the Intra AAS interactions are asynchronous, the behaviour will wait until the request is
        # answered and the negotiation value is available
        _logger.info(str(self.__class__.__name__) + " behaviour will be waiting for the negotiation value...")
        await self.neg_value_event.wait()
        # If the behaviour continues from this line, it means that the Intra AAS interaction has been answered and the
        # value is available
        self.neg_value_event.clear()
        _logger.info("The negotiation value for the negotiation with thread [" + self.thread + "] has been obtained. ")

    async def exit_negotiation(self, is_winner):
        """
        This method is executed when the trade has ended, either as a winner or a loser. In any case, all the
        information of the negotiation is added to the global variable with all the information of all the negotiations
         of the agent. The thread is used to differentiate the information of each negotiation, since this is the
         identifier of each one of them.

        Args:
            is_winner (bool): it determines whether the AAS Manager has been the winner of the negotiation.

        """
        if is_winner:
            _logger.info("The AAS has finished the negotiation with thread [" + self.thread + "] as the winner")
        else:
            _logger.info("The AAS has finished the negotiation with thread [" + self.thread + "] not as the winner")

        # The negotiation information is stored in the global object of the AAS Manager
        neg_data_json = Negotiation_utils.create_neg_json_to_store(neg_requester_jid=self.neg_requester_jid,
                                                                   participants=self.targets,
                                                                   neg_criteria=self.neg_criteria,
                                                                   is_winner=is_winner)
        await self.myagent.save_negotiation_data(thread=self.thread, neg_data=neg_data_json)

        # In order to correctly complete the negotiation process, this behavior is removed from the agent.
        self.kill(exit_code=10)
