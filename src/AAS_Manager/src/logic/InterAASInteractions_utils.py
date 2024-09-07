"""This class groups the methods related to the Inter AAS interactions between I4.0 SMIA entities."""
import logging

_logger = logging.getLogger(__name__)


def get_inter_aas_request_by_thread(agent, thread):
    """
    This method creates the dictionary with all the required data of the service request from an ACL message.

    Args:
        agent (spade.agent.Agent): the AAS Manager SPADE agent object
        thread (str): thread of the conversation

    Returns:
        dict: dictionary with all the information about the service request that matches with the given thread
    """
    print()
    # todo


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
    print()
    # todo
