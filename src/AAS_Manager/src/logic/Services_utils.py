"""
This class contains methods related to service management. It contains all type of services proposed in the
Functional View of RAMI 4.0.
"""
import json
import logging

_logger = logging.getLogger(__name__)


def create_svc_req_data_from_acl_msg(acl_msg):
    """
    This method creates the dictionary with all the required data of the service request from an ACL message.

    Args:
        acl_msg (spade.message.Message): ACL message where to get the information

    Returns:
        dict: dictionary with all the information about the service request
    """
    svc_req_data_json = {
        'performative': acl_msg.get_metadata('performative'),
        'ontology': acl_msg.get_metadata('ontology'),
        'thread': acl_msg.thread,
        'sender': acl_msg.sender,
        'receiver': acl_msg.to,
    }
    # The body of the ACL message contains the rest of the information
    svc_req_data_json.update(json.loads(acl_msg.body))
    return svc_req_data_json

