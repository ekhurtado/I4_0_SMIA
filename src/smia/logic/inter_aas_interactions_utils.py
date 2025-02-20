"""This class groups the methods related to the Inter AAS interactions between I4.0 SMIA entities."""
import json
import logging

import jsonschema
from jsonschema.exceptions import ValidationError
from spade.message import Message

from smia.logic.exceptions import RequestDataError
from smia.utilities.smia_info import SMIAInteractionInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


def create_svc_json_data_from_acl_msg(acl_msg):
    """
    This method creates the dictionary with all the required data of a service related to an ACL message.

    Args:
        acl_msg (spade.message.Message): ACL message where to get the information

    Returns:
        dict: dictionary with all the information about the service
    """
    svc_req_data_json = {
        'performative': acl_msg.get_metadata('performative'),
        'ontology': acl_msg.get_metadata('ontology'),
        'thread': acl_msg.thread,
        'sender': GeneralUtils.get_sender_from_acl_msg(acl_msg),
        'receiver': str(acl_msg.to),
    }
    # The body of the ACL message contains the rest of the information
    svc_req_data_json.update(json.loads(acl_msg.body))
    return svc_req_data_json

def create_inter_smia_response_msg(receiver, thread, performative, ontology, service_id=None, service_type=None,
                                   service_params=None):
    """
    This method creates the Inter AAS interaction response object.

    Args:
        receiver (str): the JID of the receiver of the ACL message from which the service is requested.
        thread (str): the thread of the ACL message.
        performative (str): the performative of the ACL message.
        ontology (str): the ontology of the ACL message.
        service_id (str): the serviceID of the ACL message.
        service_type (str): the serviceType of the ACL message.
        service_params (str): the serviceParams of the "serviceData" section of the ACL message.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """

    request_msg = Message(to=receiver, thread=thread)
    request_msg.set_metadata('performative', performative)
    request_msg.set_metadata('ontology', ontology)
    # request_msg.set_metadata('ontology', 'SvcResponse')

    request_msg_body_json = {
        'serviceID': service_id,
        'serviceType': service_type,
        'serviceData': {
            'serviceCategory': 'service-response',
            'timestamp': GeneralUtils.get_current_timestamp(),
        }
    }
    if service_params is not None:
        request_msg_body_json['serviceData']['serviceParams'] = service_params
    request_msg.body = json.dumps(request_msg_body_json)
    return request_msg

async def check_received_request_data_structure(received_data, json_schema):
    """
    This method checks if the received data for a request is valid. The JSON object with the specific
    data is also validated against the given associated JSON Schema. In any case, if it is invalid, it raises a
    RequestDataError exception.

    Args:
        received_data (dict): received data in form of a JSON object.
        json_schema (dict): JSON Schema in form of a JSON object.
    """
    # TODO modificarlo cuando se piense la estructura del lenguaje I4.0
    if 'serviceData' not in received_data:
        raise RequestDataError("The received request is invalid due to missing #serviceData field in the"
                               "request message.")
    if 'serviceParams' not in received_data['serviceData']:
        raise RequestDataError("The received request is invalid due to missing #serviceParams field within "
                               "the #serviceData section of the request message.")
    # The received JSON object is also validated against the associated JSON Schema
    try:
        jsonschema.validate(instance=received_data['serviceData']['serviceParams'],
                            schema=json_schema)
    except ValidationError as e:
        raise RequestDataError("The received JSON data within the request message is invalid against the required "
                               "JSON schema. Invalid part: {}. Reason: {}.".format(e.instance, e.message))