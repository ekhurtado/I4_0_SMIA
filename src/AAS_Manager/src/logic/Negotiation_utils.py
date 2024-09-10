"""
This class contains methods related to negotiation management of the AAS Manager.
"""
import calendar
import json
import logging
import time

from spade.message import Message

from utilities.AASmanagerInfo import AASmanagerInfo

_logger = logging.getLogger(__name__)

def create_neg_propose_msg(thread, targets, neg_requester_jid, neg_criteria, neg_value):
    """
    This method creates the FIPA-ACL propose message that will be sent to all participants in a negotiation to check
    their negotiation values against the value of this AAS Manager.

    Args:
        thread (str): the thread of the ACL message.
        targets (str): the JIDs of the SPADE agents that are participating in the negotiation. Is it a string that has the JIDs divided by ','
        neg_requester_jid (str):  the JID of the SPADE agent that has requested the negotiation.
        neg_criteria (str): criteria of the negotiation.
        neg_value (str): value of the negotiation.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """
    propose_msg = Message(thread=thread)
    propose_msg.metadata = AASmanagerInfo.NEG_STANDARD_ACL_TEMPLATE_PROPOSE.metadata

    neg_propose_json = {
        'serviceID': 'proposeNegotiation',
        'serviceType': 'AssetRelatedService',   # TODO cambiarlo si se decide que es de otro tipo
        'serviceData': {
            'serviceCategory': 'service-request',
            'timestamp': calendar.timegm(time.gmtime()),
            'serviceParams': {
                'targets': targets,
                'neg_requester_jid': neg_requester_jid,
                'criteria': neg_criteria,
                'neg_value': neg_value
            }
        }
    }
    propose_msg.body = json.dumps(neg_propose_json)
    return propose_msg

def create_neg_response_msg(receiver, thread, serviceID, serviceType, winner):
    """
    This method creates the FIPA-ACL message to respond to a negotiation request with its result.

    Args:
        receiver (str): the JID of the receiver of the ACL message, that it will be the requester of the negotiation.
        thread (str): the thread of the ACL message.
        serviceID (str): the serviceID of the ACL message.
        serviceType (str): the serviceType of the ACL message.
        winner (str): the JID of the winner of the negotiation.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """
    response_msg = Message(to=receiver, thread=thread)
    response_msg.metadata = AASmanagerInfo.NEG_STANDARD_ACL_TEMPLATE_INFORM.metadata

    neg_response_json = {
        'serviceID': serviceID,
        'serviceType': serviceType,
        'serviceData': {
            'serviceCategory': 'service-response',
            'serviceStatus': 'Completed',
            'timestamp': calendar.timegm(time.gmtime()),
            'serviceParams': {
                'winner': winner
            }
        }
    }
    response_msg.body = json.dumps(neg_response_json)
    return response_msg


def create_neg_json_to_store(neg_requester_jid, participants, neg_criteria, is_winner):
    """
    This method creates the JSON object to be stored in the global object of the AAS Manager for the information of all
    negotiations in which it has participated.

    Args:
        neg_requester_jid (str):  the JID of the SPADE agent that has requested the negotiation.
        participants (str): JIDs of the SPADE agents that have participated in the negotiation. Is it a string that has the JIDs divided by ','
        neg_criteria (str): criteria of the negotiation.
        is_winner (bool): it determines whether the AAS Manager has been the winner of the negotiation.

    Returns:
        dict: object with all the information of the negotiation in JSON format.
    """
    return {
        'neg_requester_jid': neg_requester_jid,
        'participants': participants,
        'neg_criteria': neg_criteria,
        'is_winner': str(is_winner)
    }

def create_intra_aas_neg_req_data(performative, ontology, thread, serviceData):
    """
    This method creates the dictionary with all the required data for an Intra AAS interaction request.

    Args:
        performative (str): performative of the FIPA-ACL message.
        ontology (str): ontology of the FIPA-ACL message.
        thread (str): thread of the FIPA-ACL message.
        serviceData (dict): all the data of the service for the Intra AAS interaction request.

    Returns:
        dict: dictionary with all the information about the Intra AAS interaction request
    """
    intra_ass_req_data_json = {
        'performative': performative,
        'ontology': ontology,
        'thread': thread,
        'serviceID': 'getNegotiationValue',
        'serviceType': 'AssetRelatedInformation',
        'serviceData': serviceData
    }
    return intra_ass_req_data_json