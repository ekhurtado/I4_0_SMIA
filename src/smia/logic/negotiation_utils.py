"""
This class contains methods related to negotiation management of the SMIA.
"""
import json
import logging

from spade.message import Message

from smia.utilities.smia_info import SMIAInteractionInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


def create_neg_cfp_msg(thread, targets, neg_requester_jid, neg_criteria):
    """
    This method creates the FIPA-ACL CallForProposal (CFP) message that will be sent to all participants to start
    a negotiation.

    Args:
        thread (str): the thread of the ACL message.
        targets (str): the JIDs of the SPADE agents that are participating in the negotiation. Is it a string that has the JIDs divided by ','
        neg_requester_jid (str):  the JID of the SPADE agent that has requested the negotiation.
        neg_criteria (str): criteria of the negotiation.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """
    cfp_msg = Message(thread=thread)
    cfp_msg.metadata = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_CFP.metadata

    neg_cfp_json = {
        'serviceID': 'startNegotiation',
        'serviceType': 'AssetRelatedService',  # TODO cambiarlo si se decide que es de otro tipo
        'serviceData': {
            'serviceCategory': 'service-request',
            'timestamp': GeneralUtils.get_current_timestamp(),
            'serviceParams': {
                'targets': targets,
                'neg_requester_jid': neg_requester_jid,
                'criteria': neg_criteria
            }
        }
    }
    cfp_msg.body = json.dumps(neg_cfp_json)
    return cfp_msg


def create_neg_propose_msg(thread, targets, neg_requester_jid, neg_criteria, neg_value):
    """
    This method creates the FIPA-ACL propose message that will be sent to all participants in a negotiation to check
    their negotiation values against the value of this SMIA.

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
    propose_msg.metadata = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_PROPOSE.metadata

    neg_propose_json = {
        'serviceID': 'proposeNegotiation',
        'serviceType': 'AssetRelatedService',  # TODO cambiarlo si se decide que es de otro tipo
        'serviceData': {
            'serviceCategory': 'service-request',
            'timestamp': GeneralUtils.get_current_timestamp(),
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


def create_neg_response_msg(receiver, thread, service_id, service_type, winner):
    """
    This method creates the FIPA-ACL message to respond to a negotiation request with its result.

    Args:
        receiver (str): the JID of the receiver of the ACL message, that it will be the requester of the negotiation.
        thread (str): the thread of the ACL message.
        service_id (str): the serviceID of the ACL message.
        service_type (str): the serviceType of the ACL message.
        winner (str): the JID of the winner of the negotiation.

    Returns:
        spade.message.Message: SPADE message object FIPA-ACL-compliant.
    """
    response_msg = Message(to=receiver, thread=thread)
    response_msg.metadata = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_INFORM.metadata

    neg_response_json = {
        'serviceID': service_id,
        'serviceType': service_type,
        'serviceData': {
            'serviceCategory': 'service-response',
            'serviceStatus': 'Completed',
            'timestamp': GeneralUtils.get_current_timestamp(),
            'serviceParams': {
                'winner': winner
            }
        }
    }
    response_msg.body = json.dumps(neg_response_json)
    return response_msg


def create_neg_json_to_store(neg_requester_jid, participants, neg_criteria, is_winner):
    """
    This method creates the JSON object to be stored in the global object of the SMIA for the information of all
    negotiations in which it has participated.

    Args:
        neg_requester_jid (str):  the JID of the SPADE agent that has requested the negotiation.
        participants (str): JIDs of the SPADE agents that have participated in the negotiation. Is it a string that has the JIDs divided by ','
        neg_criteria (str): criteria of the negotiation.
        is_winner (bool): it determines whether the SMIA has been the winner of the negotiation.

    Returns:
        dict: object with all the information of the negotiation in JSON format.
    """
    return {
        'neg_requester_jid': neg_requester_jid,
        'participants': participants,
        'neg_criteria': neg_criteria,
        'is_winner': str(is_winner)
    }


def create_intra_aas_neg_req_data(performative, ontology, thread, service_data):
    """
    This method creates the dictionary with all the required data for an Intra AAS interaction request.

    Args:
        performative (str): performative of the FIPA-ACL message.
        ontology (str): ontology of the FIPA-ACL message.
        thread (str): thread of the FIPA-ACL message.
        service_data (dict): all the data of the service for the Intra AAS interaction request.

    Returns:
        dict: dictionary with all the information about the Intra AAS interaction request
    """
    intra_ass_req_data_json = {
        'performative': performative,
        'ontology': ontology,
        'thread': thread,
        'serviceID': 'getNegotiationValue',
        'serviceType': 'AssetRelatedService',
        'serviceData': service_data
    }
    return intra_ass_req_data_json


def add_value_and_unlock_neg_handling_behaviour(agent, thread, neg_value):
    """
    This method adds the value to the HandleNegotiationBehaviour which is in charge of the negotiation with the given
    thread. Since this behaviour is waiting for this value, this method also unlocks its execution, so it can continue
    with its logic.

    Args:
        agent (spade.agent.Agent): the SPADE agent object that represents the SMIA.
        thread (str): the thread of the negotiation, which is its identifier.
        neg_value (int): value of the AAS in the negotiation-
    """
    # First, it will get the exact behaviour responsible for the negotiation for the given thread
    for behaviour in agent.behaviours:
        behav_class_name = str(behaviour.__class__.__name__)
        if behav_class_name == 'HandleNegotiationBehaviour':
            if behaviour.thread == thread:
                # Once the exact behaviour has been found, the negotiation value will be stored as an attribute, and the
                # method will be concluded
                behaviour.neg_value = float(neg_value)
                # The execution of this behaviour is also unlocked
                behaviour.neg_value_event.set()
                break


def get_neg_intra_aas_request_by_thread(agent, thread):
    """
    This method gets the data of an Intra AAS Interaction using the thread value.
    Args:
        agent (agents.smia_agent): the SPADE agent object that represents the SMIA.
        thread (str): the thread of the negotiation, which is its identifier.

    Returns:
        dict: dictionary with all the information about the Intra AAS interaction request. None if it does not exist.
    """
    for req_interaction_id, req_data in agent.interaction_requests.items():
        if req_data['thread'] == thread:
            req_data['interactionID'] = req_interaction_id
            return req_data
    return None
