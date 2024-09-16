"""This class groups the methods related to the Inter AAS interactions between I4.0 SMIA entities."""
import json
import logging

from utilities.GeneralUtils import GeneralUtils

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
        'sender': acl_msg.sender,
        'receiver': acl_msg.to,
    }
    # The body of the ACL message contains the rest of the information
    svc_req_data_json.update(json.loads(acl_msg.body))
    return svc_req_data_json


def create_inter_aas_response_object(inter_aas_request, intra_aas_response):
    """
    This method creates the Inter AAS interaction response object using the initial Inter AAS interaction request and
    the Intra AAS interaction response needed to perform the initial service request.

    Args:
        inter_aas_request (dict): all the information about the Inter AAS interaction request
        intra_aas_response (dict): all the information about the Intra AAS interaction response

    Returns:
        dict: Inter AAS response object in JSON format
    """

    response_json = {'performative': inter_aas_request['performative'],
                     'ontology': inter_aas_request['ontology'],
                     'thread': intra_aas_response['thread'],
                     'serviceType': inter_aas_request['serviceType'],
                     'serviceID': inter_aas_request['serviceID'],
                     'serviceData': {
                         'serviceCategory': 'service-response',
                         'timestamp': GeneralUtils.get_current_timestamp(),
                         'serviceStatus': intra_aas_response['serviceData']['serviceStatus'],  # The status of the
                                                                                # Intra AAS Interaction is obtained
                     }
                     }
    if 'serviceParams' in intra_aas_response['serviceData']:
        response_json['serviceData']['serviceParams'] = intra_aas_response['serviceData']['serviceParams']
    return response_json
