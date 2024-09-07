"""This class groups the methods related to the Inter AAS interactions between I4.0 SMIA entities."""
import calendar
import logging
import time

_logger = logging.getLogger(__name__)


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
    # TODO comprobar que esta bien
    return {'performative': inter_aas_request['performative'],
            'ontology': inter_aas_request['ontology'],
            'thread': inter_aas_request['thread'],
            'serviceType': inter_aas_request['serviceType'],
            'serviceID': inter_aas_request['serviceID'],
            'serviceData': {
                'serviceCategory': 'service-response',
                'timestamp': calendar.timegm(time.gmtime()),
                'serviceStatus': intra_aas_response['serviceData']['serviceStatus'],  # The status of the Intra AAS
                                                                                      # Interaction is obtained
                'serviceParams': intra_aas_response['serviceData']['serviceParams']
            }
    }

