"""
File to group useful methods related to interactions between AAS Manager and AAS Core.
"""
import calendar
import time

from utilities.AASArchive_utils import file_to_json, update_json_file
from utilities.AASarchiveInfo import AASarchiveInfo


def get_next_svc_request():
    print("Obtaining the next service request from AAS Manager.")
    svc_requests_file_path = AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    if len(svc_requests_json['serviceRequests']) != 0:
        return svc_requests_json['serviceRequests'][0]
    else:
        return None


def delete_svc_request(svc_request_object):
    print("Deleting the service request with ID " + str(svc_request_object['interactionID']) + " from AAS Archive.")
    svc_requests_file_path = AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    for i in range(len(svc_requests_json['serviceRequests'])):
        if svc_requests_json['serviceRequests'][i]["interactionID"] == svc_request_object['interactionID']:
            svc_requests_json['serviceRequests'].pop(i)
            break
    update_json_file(svc_requests_file_path, svc_requests_json)

def create_response_json_object(svc_request_info):

    return {
        'interactionID': svc_request_info['interactionID'],
        'serviceType': svc_request_info['serviceType'],
        'serviceID': svc_request_info['serviceID'],
        'serviceStatus': 'Completed',
        'serviceData': {
            'timestamp': calendar.timegm(time.gmtime())
        }
    }

def add_new_svc_response(new_response_json):
    """
    This method adds a new service response to the related service interaction file of the core and updates it
    in the AAS Archive.

    Args:
        new_response_json: The service requests content in JSON format.
    """

    # Get the content of the service requests interaction file
    svc_requests_file_path = AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    if svc_requests_json is None:
        svc_requests_json = {'serviceResponses': [new_response_json]}
    else:
        svc_requests_json['serviceResponses'].append(new_response_json)

    update_json_file(svc_requests_file_path, svc_requests_json)