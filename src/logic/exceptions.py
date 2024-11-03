"""
This file contains all the classes for handling errors in exceptions that may occur during code execution.
"""
import logging

from logic import inter_aas_interactions_utils

_logger = logging.getLogger(__name__)


class CriticalError(Exception):
    """
    This exception class is defined for errors that are critical to the program, so that execution must be terminated.
    """

    def __init__(self, message):
        _logger.error(f"{message}")
        _logger.error("The program must end.")
        exit(-1)


class CapabilityRequestExecutionError(Exception):
    """
    This exception class is defined for errors that are relate to the execution of a requested Capability. Since it has
    been requested, this class also must response to the requester with a Failure of the capability execution.
    """

    def __init__(self, message, requester_jid, thread, service_id, behav_class):
        self.message = message
        self.requester_jid = requester_jid
        self.thread = thread
        self.service_id = service_id
        self.behav_class = behav_class

    async def handle_capability_execution_error(self):
        _logger.error(f"{self.message}")

        _logger.info("Due to an incorrect execution of a capability, the requester shall be informed with a Failure "
                     "message.")
        failure_acl_msg = inter_aas_interactions_utils.create_inter_aas_response_msg(receiver=self.requester_jid,
                                                                                     thread=self.thread,
                                                                                     performative='Failure',
                                                                                     service_id=self.service_id)
        await self.behav_class.send(failure_acl_msg)
        _logger.info("Failure message sent to the requester of the capability.")
