"""
This file contains all the classes for handling errors in exceptions that may occur during code execution.
"""
import json
import logging

from logic import inter_aas_interactions_utils
from utilities.fipa_acl_info import FIPAACLInfo

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

    def __init__(self, message, behav_class):
        self.message = message
        self.behav_class = behav_class

    async def handle_capability_execution_error(self):
        """
        This method handles the error during an execution of a capability, sending the Failure message to the requester.
        """
        _logger.error(f"{self.message}")

        _logger.info("Due to an incorrect execution of a capability, the requester shall be informed with a Failure "
                     "message.")

        await self.behav_class.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                                                           {'reason': self.message})
        _logger.info("Failure message sent to the requester of the capability.")

        # TODO Pensar si añadir un objeto global en el agente para almacenar informacion sobre errores
        # The behaviour for the execution of the capability must be killed
        self.behav_class.kill(exit_code=10)
