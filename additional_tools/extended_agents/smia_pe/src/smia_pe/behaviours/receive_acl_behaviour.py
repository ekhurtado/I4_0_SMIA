import logging

from smia.logic import acl_smia_messages_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo
from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)

class ReceiveACLBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the SMIA PE will receive from the
    others SMIAs in the I4.0 System. If some of these messages are responses to previous SMIA PE requests, the associated
    BPMNPerformerBehaviour will be unlocked to continue execution of the production plan.
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
        _logger.info("ReceiveACLBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # This method will receive all ACL messages to the SMIA PE, so it will check if some of them are responses to
            # previous SMIA PE requests to unlock the associated BPMNPerformerBehaviour
            _logger.aclinfo("Analyzing ACL message... Checking if it is a response from previous SMIA PE message... "
                            "Unlocking SMIA PE...")
            # Let's check if the BPMN performer behaviour is waiting for a response
            for behaviour in self.myagent.behaviours:
                if str(behaviour.__class__.__name__) == 'BPMNPerformerBehaviour':
                    for thread, content in behaviour.acl_messages_responses.items():
                        if thread == msg.thread and content is None:
                            # In this case, the behaviour is waiting for the content
                            _logger.aclinfo("BPMNPerformerBehaviour is waiting for a content [{}] that has arrived with"
                                            " thread [{}] from [{}].".format(msg.body, msg.thread, msg.sender))
                            self.myagent.smia_pe_info['ReceivedACLmsg'] += 1
                            msg_parsed_body = acl_smia_messages_utils.get_parsed_body_from_acl_msg(msg)
                            if (msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) ==
                                    FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE):

                                _logger.error("SMIA PE has received a Failure for the thread [{}], so it cannot continue. "
                                              "Reason: {}".format(thread, msg_parsed_body['reason']))

                                # The information to be displayed in the GUI is also added
                                self.myagent.smia_pe_info['InteractionsDict'].append(
                                    {'type': 'acl_recv', 'response_type':
                                        msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB), 'title':
                                        'FIPA-ACL failure response received ...', 'response_title':
                                        'FIPA-ACL failure response received from {}'.format(
                                            acl_smia_messages_utils.get_sender_from_acl_msg(msg)),
                                     'response_msg': msg_parsed_body['reason']})

                                _logger.error('SMIA PE cannot continue due to a received FAILURE ACL message. '
                                                    'Reason: {}'.format(msg_parsed_body['reason']))
                                _logger.warning("BPMNPerformerBehaviour will remain blocked due to the receipt of an "
                                                "ACL failure message.... ")

                                # Mark failure in GUI visualization (to_graphviz will render it in yellow)
                                if hasattr(self.myagent, 'bpmn_process_parser'):
                                    try:
                                        task_specs = self.myagent.bpmn_process_parser.get_spec().task_specs
                                        for elem in task_specs.values():
                                            if getattr(elem, 'current_exec_elem', False):
                                                elem.error_exec_elem = True
                                                break
                                    except Exception as e:
                                        _logger.warning("Could not mark BPMN element as failed for GUI: {}".format(e))

                            if (msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB) ==
                                    FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM):
                                # In this case the content is valid
                                behaviour.acl_messages_responses[thread] = msg
                                # Now the behaviour can be unlocked
                                behaviour.acl_request_event.set()
                                _logger.info("BPMNPerformerBehaviour unlocked and added the response content data.")

                                # The information to be displayed in the GUI is also added
                                self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_recv',
                                    'response_type': msg.get_metadata(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_ATTRIB),
                                    'title': 'FIPA-ACL response received ...', 'response_title': 'FIPA-ACL response '
                                    'received from {}'.format(acl_smia_messages_utils.get_sender_from_acl_msg(msg)),
                                    'response_msg': msg.body})
        else:
            _logger.info("         - No message received within 10 seconds on SMIA PE (ReceiveACLBehaviour)")