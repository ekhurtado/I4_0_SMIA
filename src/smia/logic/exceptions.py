"""
This file contains all the classes for handling errors in exceptions that may occur during code execution.
"""
import logging

from smia.utilities.fipa_acl_info import FIPAACLInfo, ServiceTypes

_logger = logging.getLogger(__name__)


class CriticalError(Exception):
    """
    This exception class is defined for errors that are critical to the program, so that execution must be terminated.
    """

    def __init__(self, message):
        _logger.error(f"{message}")
        _logger.error("The program must end.")
        exit(-1)

class RequestDataError(Exception):
    """
    This exception class is defined for errors that are related to a request received by the DT (request of a service
    or a capability).
    """

    def __init__(self, message):
        self.message = message
        _logger.error(f"{self.message}")

# AAS model-related exceptions
# ----------------------------------------
class AASModelReadingError(Exception):
    """
    This exception class is defined for errors that occur during AAS model management (reading, updating...).
    """
    def __init__(self, message, sme_class, reason):
        self.message = message
        self.sme_class = sme_class
        self.reason = reason
        _logger.error(f"{self.message}")


class AASModelOntologyError(Exception):
    """
    This exception class is defined for errors that occur during AAS model management (reading, updating...).
    """
    def __init__(self, message, sme_class, reason):
        self.message = message
        self.sme_class = sme_class
        self.reason = reason
        _logger.error(f"{self.message}")


# Service management-related exceptions
# -------------------------------------
class ServiceRequestExecutionError(Exception):
    """
    This exception class is defined for errors that are related to the execution of a requested service. Since it has
    been requested, this class also must response to the requester with a Failure of the execution.
    """

    def __init__(self, thread, message, svc_type, behav_class):
        self.thread = thread
        self.message = message
        self.svc_type = svc_type
        self.behav_class = behav_class

    async def handle_service_execution_error(self):
        """
        This method handles the error during an execution of a service, sending the Failure message to the requester.
        """
        _logger.error(f"{self.message}")

        _logger.info("Due to an incorrect execution of the service related to the thread [{}], the requester shall be "
                     "informed with a Failure message.".format(self.thread))

        await self.behav_class.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                                                           {'reason': self.message})
        _logger.info("Failure message sent to the requester related to the thread [{}].".format(self.thread))

        # The information about the error is also saved in the log
        from smia.behaviours.specific_handle_behaviours.handle_svc_request_behaviour import HandleSvcRequestBehaviour
        from smia.behaviours.specific_handle_behaviours.handle_capability_behaviour import HandleCapabilityBehaviour
        from smia import GeneralUtils  # Local imports to avoid circular import error
        from smia.utilities import smia_archive_utils

        if isinstance(self.behav_class, (HandleSvcRequestBehaviour, HandleCapabilityBehaviour)):
            acl_info = self.behav_class.svc_req_data
        else:
            acl_info = {'thread': self.thread}
        smia_archive_utils.save_svc_error_log_info(GeneralUtils.get_current_timestamp(), acl_info, self.message,
                                                   self.svc_type)

        # The behaviour for the execution of the service must be killed
        self.behav_class.kill(exit_code=10)

# Capability management-related exceptions
# ----------------------------------------
class CapabilityRequestExecutionError(Exception):
    """
    This exception class is defined for errors that are related to the execution of a requested Capability. Since it has
    been requested, this class also must response to the requester with a Failure of the capability execution.
    """

    def __init__(self, cap_name, message, behav_class):
        self.cap_name = cap_name  # TODO pensar si en lugar de nombre de capacidad añadir el thread de la conversacion (quizas es mas identificativo)
        self.message = message
        self.behav_class = behav_class

    async def handle_capability_execution_error(self):
        """
        This method handles the error during an execution of a capability, sending the Failure message to the requester.
        """
        _logger.error(f"{self.message}")

        _logger.info("Due to an incorrect execution of the capability [{}], the requester shall be informed with a "
                     "Failure message.".format(self.cap_name))

        await self.behav_class.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                                                           {'reason': self.message})
        _logger.info("Failure message sent to the requester of the capability [{}].".format(self.cap_name))

        # The information about the error is also saved in the log
        from smia.behaviours.specific_handle_behaviours.handle_svc_request_behaviour import HandleSvcRequestBehaviour
        from smia.behaviours.specific_handle_behaviours.handle_capability_behaviour import HandleCapabilityBehaviour
        from smia.behaviours.specific_handle_behaviours.handle_negotiation_behaviour import HandleNegotiationBehaviour
        from smia.utilities import smia_archive_utils
        from smia import GeneralUtils  # Local imports to avoid circular import error

        if isinstance(self.behav_class, (HandleSvcRequestBehaviour, HandleCapabilityBehaviour,
                                         HandleNegotiationBehaviour)):
            acl_info = self.behav_class.svc_req_data
        else:
            acl_info = {}
        smia_archive_utils.save_svc_error_log_info(GeneralUtils.get_current_timestamp(), acl_info, self.message,
                                                   ServiceTypes.CSS_RELATED_SERVICE)

        # The behaviour for the execution of the capability must be killed
        self.behav_class.kill(exit_code=10)


class CapabilityCheckingError(Exception):
    """
    This exception class is defined for errors that are related to the execution of the Capability checking process.
    Since this process is requested by another DT, this class also must response to the requester with a Failure of the
    capability checking as well as the reason of it.
    """

    def __init__(self, cap_name, reason, behav_class):
        self.cap_name = cap_name
        self.reason = reason
        self.behav_class = behav_class

    async def handle_capability_checking_error(self):
        """
        This method handles the error during an execution of a capability, sending the Failure message to the requester.
        """
        _logger.error(f"Capability checking of capability [{self.cap_name}] failed. Reason: {self.reason}")

        _logger.info("Due to an incorrect checking of a capability, the requester shall be informed with a Failure "
                     "message.")

        await self.behav_class.send_response_msg_to_sender(
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
            {'message': "Capability checking of capability [{}] failed".format(self.cap_name), 'reason': self.reason})
        _logger.info("Failure message sent to the requester of the capability.")

        # TODO Pensar si añadir un objeto global en el agente para almacenar informacion sobre errores
        # The behaviour for the execution of the capability must be killed
        self.behav_class.kill(exit_code=10)


class AssetConnectionError(Exception):
    """
    This exception class is defined for errors that are related to the asset connection processes.
    """

    def __init__(self, message, error_type, reason):
        self.message = message
        self.error_type = error_type
        self.reason = reason
        _logger.error(f"{self.message}")

# Capability-Skill ontology exceptions
# ------------------------------------
class OntologyInstanceCreationError(Exception):
    def __init__(self, message):
        self.message = message
        _logger.error(f"{self.message}")


class OntologyReadingError(Exception):
    def __init__(self, message):
        self.message = message
        _logger.error(f"{self.message}")


class OntologyCheckingAttributeError(Exception):

    def __init__(self, message, invalid_instance):
        self.message = message
        self.invalid_instance = invalid_instance
        _logger.error(f"{self.message}")


class OntologyCheckingPropertyError(Exception):

    def __init__(self, message, concerned_property_name, invalid_instance):
        self.message = message
        self.concerned_property_name = concerned_property_name
        self.invalid_instance = invalid_instance
        _logger.error(f"{self.message}")
