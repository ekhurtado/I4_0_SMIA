"""

"""
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
    # svc_requests_json['serviceRequests'].pop(svc_request_object)
    for i in svc_requests_json['serviceRequests']:
        if i['interactionID'] == svc_request_object['interactionID']:
            svc_requests_json['interactionID'].pop(i)
            break
    update_json_file(svc_requests_file_path, svc_requests_json)
