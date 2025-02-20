import json
import logging

from spade.behaviour import CyclicBehaviour

from smia import GeneralUtils
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils
from smia.logic import negotiation_utils, inter_aas_interactions_utils
from smia.logic.exceptions import CapabilityRequestExecutionError, AssetConnectionError
from smia.utilities import smia_archive_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ServiceTypes
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HandleNegotiationBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handle a particular negotiation.
    """
    myagent = None  #: the SPADE agent object of the SMIA agent.
    thread = None  #: thread of the negotiation
    neg_requester_jid = None  #: JID of the SPADE agent that has requested the negotiation
    targets = None  #: targets of the negotiation
    neg_criteria = None  #: criteria of the negotiation
    neg_value = None  #: value of the negotiation
    targets_processed = set()  #: targets that their values have been processed
    neg_value_event = None

    def __init__(self, agent_object, negotiation_info, neg_req_data):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
            negotiation_info (dict): all the required information to perform the negotiation.
            neg_req_data (dict): all the information related to the FIPA-ACL negotiation request.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        self.thread = negotiation_info['thread']
        self.neg_requester_jid = negotiation_info['neg_requester_jid']
        self.targets = negotiation_info['targets']
        self.neg_criteria = negotiation_info['neg_criteria']
        self.targets_processed = set()

        self.myagent.tie_break = True   # In case of equal value neg is set as tie-breaker TODO check these cases (which need to be tie-breaker?)

        self.svc_req_data = neg_req_data

        self.requested_timestamp = GeneralUtils.get_current_timestamp()

        # This event object will allow waiting for the negotiation value if it is necessary to request it from an
        # external entity (such as the AAS Core)
        # self.neg_value_event = asyncio.Event()

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleNegotiationBehaviour starting...")

        try:
            #  The value of the criterion must be obtained just before starting to manage the negotiation, so that at the
            #  time of sending the PROPOSE and receiving that of the others it will be the same value. Therefore, if to
            #  obtain the value you have to make an Intra AAS interaction request, the behaviour will not be able to start
            #  managing the negotiation until you get the answer to that request (together with the requested value).
            await self.get_neg_value_with_criteria()


            # Once the negotiation value is reached, the negotiation management can begin. The first step is to send the
            # PROPOSE message with your own value to the other participants in the negotiation.
            acl_propose_msg = negotiation_utils.create_neg_propose_msg(thread=self.thread,
                                                                       targets=self.targets,
                                                                       neg_requester_jid=self.neg_requester_jid,
                                                                       neg_criteria=self.neg_criteria,
                                                                       neg_value=str(self.neg_value))
            # This PROPOSE FIPA-ACL message is sent to all participants of the negotiation (except for this SMIA)
            for jid_target in self.targets.split(','):
                if jid_target != str(self.agent.jid):
                    acl_propose_msg.to = jid_target
                    await self.send(acl_propose_msg)
                    _logger.aclinfo("ACL PROPOSE negotiation message sent to " + jid_target +
                                    " on negotiation with thread [" + self.thread + "]")
        except (CapabilityRequestExecutionError, AssetConnectionError) as cap_neg_error:
            if isinstance(cap_neg_error, AssetConnectionError):
                cap_neg_error = CapabilityRequestExecutionError('Negotiation', f"The error "
                                                                f"[{cap_neg_error.error_type}] has appeared during the"
                                                                f" asset connection. Reason: {cap_neg_error.reason}.", self)

            await cap_neg_error.handle_capability_execution_error()
            return  # killing a behaviour does not cancel its current run loop


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.aclinfo("         + PROPOSE Message received on SMIA Agent (HandleNegotiationBehaviour "
                            "in charge of the negotiation with thread [" + self.thread + "])")
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # The negotiation information is obtained from the message
            # criteria = msg_json_body['serviceData']['serviceParams']['criteria']
            sender_agent_neg_value = msg_json_body['serviceData']['serviceParams']['neg_value']

            # The value of this SMIA and the received value are compared
            if float(sender_agent_neg_value) > self.neg_value:
                # As the received value is higher than this SMIA value, it must exit the negotiation.
                await self.exit_negotiation(is_winner=False)
                return  # killing a behaviour does not cancel its current run loop
            if (float(sender_agent_neg_value) == self.neg_value) and not self.agent.tie_break:
                # In this case the negotiation is tied but this SMIA is not the tie breaker.
                await self.exit_negotiation(is_winner=False)
                return  # killing a behaviour does not cancel its current run loop
            # The target is added as processed in the local object (as it is a Python 'set' object there is no problem
            # of duplicate agents)
            self.targets_processed.add(str(msg.sender))
            if len(self.targets_processed) == len(self.targets.split(',')) - 1:
                # In this case all the values have already been received, so the value of this SMIA is the best
                _logger.info("The AAS has won the negotiation with thread [" + msg.thread + "]")

                # As the winner, it will reply to the sender with the result of the negotiation
                await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                       {'winner': str(self.myagent.jid)})

                _logger.aclinfo("ACL response sent for the result of the negotiation request with thread ["
                                + msg.thread + "]")

                # The negotiation can be terminated, in this case being the winner
                await self.exit_negotiation(is_winner=True)

        else:
            _logger.info("         - No message received within 10 seconds on SMIA Agent (NegotiatingBehaviour)")

    async def get_neg_value_with_criteria(self):
        """
        This method gets the negotiation value based on a given criteria.

        Returns:
            int: value of the negotiation
        """
        _logger.info("Getting the negotiation value for [{}]...".format(self.thread))

        # Since negotiation is a capability of the agent, it is necessary to analyze which skill has been defined. The
        # associated skill interface will be the one from which the value of negotiation can be obtained.
        # Thus, skill is the negotiation criterion for which the ontological instance will be obtained.
        neg_skill_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(self.neg_criteria)

        # The related skill interface will be obtained
        skill_interface = list(neg_skill_instance.get_associated_skill_interface_instances())[0]
        # The AAS element of the skill interface will be used to analyze the skill implementation
        aas_skill_interface_elem = await self.myagent.aas_model.get_object_by_reference(
            skill_interface.get_aas_sme_ref())

        parent_submodel = aas_skill_interface_elem.get_parent_submodel()
        if parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            # In this case, the value need to be obtained through an asset service
            # With the AAS SubmodelElement of the asset interface the related Python class, able to connect to the
            # asset, can be obtained.
            aas_asset_interface_elem = aas_skill_interface_elem.get_associated_asset_interface()
            asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(aas_asset_interface_elem)
            _logger.assetinfo("The Asset connection of the Skill Interface has been obtained.")
            # Now the negotiation value can be obtained through an asset service
            _logger.assetinfo("Obtaining the negotiation value for [{}] through an asset service...".format(self.thread))
            current_neg_value = await asset_connection_class.execute_asset_service(
                interaction_metadata=aas_skill_interface_elem)
            _logger.assetinfo("Negotiation value for [{}] through an asset service obtained: {}.".format(
                self.thread, current_neg_value))
            if not isinstance(current_neg_value, float):
                try:
                    current_neg_value = float(current_neg_value)
                except ValueError as e:
                    # TODO PENSAR OTRAS EXCEPCIONES EN NEGOCIACIONES (durante el asset connection...)
                    _logger.error(e)
                    raise CapabilityRequestExecutionError('Negotiation', "The requested negotiation {} cannot be "
                                                          "executed because the negotiation value returned by the asset does"
                                                          " not have a valid format.".format(self.thread), self)
        else:
            # In this case, the value need to be obtained through an agent service
            try:
                current_neg_value = await self.myagent.agent_services.execute_agent_service_by_id(aas_skill_interface_elem.id_short)
            except (KeyError, ValueError) as e:
                _logger.error(e)
                raise CapabilityRequestExecutionError('Negotiation', "The requested negotiation {} cannot be "
                                                      "executed because the negotiation value cannot be obtained through"
                                                      " the agent service {}.".format(self.thread,
                                                      aas_skill_interface_elem.id_short), self)

        self.neg_value = current_neg_value


    async def send_response_msg_to_sender(self, performative, service_params):
        """
        This method creates and sends a FIPA-ACL message with the given serviceParams and performative.

        Args:
            performative (str): performative according to FIPA-ACL standard.
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_aas_interactions_utils.create_inter_smia_response_msg(
            receiver=self.neg_requester_jid,
            thread=self.thread,
            performative=performative,
            ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION,  # TODO pensar si definir un NegRequest y NegResponse
            service_id='negotiationResult',  # TODO pensar como llamarlo
            service_type='AssetRelatedService',  # TODO ojo si decidimos que es de otro tipo
            service_params=json.dumps(service_params)
        )
        await self.send(acl_msg)


    async def exit_negotiation(self, is_winner):
        """
        This method is executed when the trade has ended, either as a winner or a loser. In any case, all the
        information of the negotiation is added to the global variable with all the information of all the negotiations
         of the agent. The thread is used to differentiate the information of each negotiation, since this is the
         identifier of each one of them.

        Args:
            is_winner (bool): it determines whether the SMIA has been the winner of the negotiation.

        """
        if is_winner:
            _logger.info("The AAS has finished the negotiation with thread [" + self.thread + "] as the winner")
        else:
            _logger.info("The AAS has finished the negotiation with thread [" + self.thread + "] not as the winner")

        # The negotiation information is stored in the global object of the SMIA
        neg_data_json = negotiation_utils.create_neg_json_to_store(neg_requester_jid=self.neg_requester_jid,
                                                                   participants=self.targets,
                                                                   neg_criteria=self.neg_criteria,
                                                                   is_winner=is_winner)
        await self.myagent.save_negotiation_data(thread=self.thread, neg_data=neg_data_json)

        # The information will be stored in the log
        execution_info = {'capName': 'Negotiation', 'capType': CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE,
                          'participants': self.targets, 'criteria': self.neg_criteria, 'winner': str(is_winner)}
        smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp, GeneralUtils.get_current_timestamp(),
                                                       self.svc_req_data, execution_info,
                                                       ServiceTypes.CSS_RELATED_SERVICE)

        # In order to correctly complete the negotiation process, this behavior is removed from the agent.
        self.kill(exit_code=10)
