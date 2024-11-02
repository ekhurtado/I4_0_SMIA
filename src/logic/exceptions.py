"""
This file contains all the classes for handling errors in exceptions that may occur during code execution.
"""
import logging

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

    def __init__(self, message, requester_jid, thread, source_class):
        _logger.error(f"{message}")
        # TODO HACER AHORA
