""" File to group useful methods for accessing and managing the AAS Archive."""
import json
import logging
import os
import time

from utilities.AASarchiveInfo import AASarchiveInfo
from utilities.GeneralUtils import GeneralUtils

_logger = logging.getLogger(__name__)


# ------------------------
# Methods related to files
# ------------------------
def create_status_file():
    """This method creates the status file of the AAS Manager and sets it to "initializing". If the file exists because
    the AAS Manager has been restarted without terminating the Pod where it is running, the status file will be
    rewritten."""
    initial_status_info = {'name': 'AAS_Manager', 'status': 'Initializing',
                           'timestamp': GeneralUtils.get_current_timestamp()}
    try:
        status_file = open(AASarchiveInfo.MANAGER_STATUS_FILE_PATH, 'x')
    except FileExistsError as e:
        status_file = open(AASarchiveInfo.MANAGER_STATUS_FILE_PATH, 'w')
    json.dump(initial_status_info, status_file)
    status_file.close()


def create_interaction_files():
    """This method creates the necessary interaction files to exchange information between AAS Core and AAS Manager."""

    # First interaction folders are created
    os.mkdir(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH)
    os.mkdir(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH)

    # Then the interaction files are added in each folder
    with (open(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH,
               'x') as core_requests_file,
          open(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH,
               'x') as core_responses_file,
          open(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH,
               'x') as manager_requests_file,
          open(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH,
               'x') as manager_responses_file):
        core_requests_file.write('{"serviceRequests": []}')
        core_requests_file.close()

        manager_requests_file.write('{"serviceRequests": []}')
        manager_requests_file.close()

        core_responses_file.write('{"serviceResponses": []}')
        core_responses_file.close()

        manager_responses_file.write('{"serviceResponses": []}')
        manager_responses_file.close()


def create_log_files():
    """This method creates the necessary log files to save services information."""

    # First the log folder is created
    os.mkdir(AASarchiveInfo.LOG_FOLDER_PATH)
    # The folder for services log is also created
    os.mkdir(AASarchiveInfo.SVC_LOG_FOLDER_PATH)

    # Then the log files are added in each folder
    all_svc_log_file_names = [AASarchiveInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                              AASarchiveInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME,
                              AASarchiveInfo.AAS_SERVICES_LOG_FILENAME, AASarchiveInfo.SUBMODEL_SERVICES_LOG_FILENAME]
    for log_file_name in all_svc_log_file_names:
        with open(AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + log_file_name, 'x') as log_file:
            log_file.write('[]')
            log_file.close()


def get_log_file_by_service_type(svc_type):
    """
    This method obtains the path to the log file associated to the type of the service.
    Args:
        svc_type (str): type of the service.

    Returns:
        str: path to the log file
    """
    log_file_path = None
    match svc_type:
        case "AssetRelatedService":
            log_file_path = AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + AASarchiveInfo.ASSET_RELATED_SVC_LOG_FILENAME
        case "AASInfrastructureServices":
            log_file_path = AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + AASarchiveInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME
        case "AASservices":
            log_file_path = AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + AASarchiveInfo.AAS_SERVICES_LOG_FILENAME
        case "SubmodelServices":
            log_file_path = AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + AASarchiveInfo.SUBMODEL_SERVICES_LOG_FILENAME
        case _:
            _logger.error("Service type not available.")
    return log_file_path


def save_svc_log_info(svc_info, svc_type):
    """
    This method saves the information about a realized service in the log file associated to the type of the service.

    Args:
        svc_info (dict): the information of the service in JSON format.
        svc_type (str): type of the service.
    """
    # First, the required paths are obtained
    log_file_path = get_log_file_by_service_type(svc_type)

    # Then, the new information is added
    log_file_json = file_to_json(log_file_path)
    log_file_json.append(svc_info)

    # Finally, the file is updated
    update_json_file(log_file_path, log_file_json)


# -------------------------
# Methods related to status
# -------------------------
def change_status(new_status):
    """
    This method updated the status of an AAS Manager instance.

    Args:
        new_status (str): the new status of the AAS Manager instance.
    """
    status_file_json = file_to_json(AASarchiveInfo.MANAGER_STATUS_FILE_PATH)
    status_file_json['status'] = new_status
    status_file_json['timestamp'] = GeneralUtils.get_current_timestamp()
    update_json_file(AASarchiveInfo.MANAGER_STATUS_FILE_PATH, status_file_json)


def get_status(entity):
    """
    This method gets the status of the requested entity.

    Args:
        entity (str): The entity to get the status for.

    Returns:
        dict: status in JSON format.
    """
    status_file_json = None
    if entity == "Manager":
        status_file_json = file_to_json(AASarchiveInfo.MANAGER_STATUS_FILE_PATH)
    elif entity == "Core":
        status_file_json = file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)
    return status_file_json['status']


def check_core_initialization():
    """This method checks if the core has initialized so the Manager can be started."""
    while True:
        if os.path.isfile(AASarchiveInfo.CORE_STATUS_FILE_PATH) is True:
            if file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)['status'] != "Initializing":
                break
        time.sleep(1)  # waits 1s
    _logger.info('AAS Core has initialized, so the AAS Manager is starting.')


# ------------------------
# Methods related to JSON
# ------------------------
def file_to_json(file_path):
    """
    This method gets the content of a JSON file.

    Args:
        file_path (str): the path of the JSON file.

    Returns:
        dict: content of the file in JSON format."""
    f = open(file_path)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        _logger.error("Invalid JSON syntax:" + str(e))
        return None
    return content


def update_json_file(file_path, content):
    """
    This method updates the content of a JSON file.

    Args:
        file_path (str): the path to the JSON file.
        content (dict): the content of the JSON file.
    """
    with open(file_path, "w") as outfile:
        json.dump(content, outfile)


# ------------------------
# Methods related to XML
# ------------------------
def xml_to_file(file_path, xml_content):
    """
    This method writes the content of an XML in a file.

    Args:
        file_path (str): the path to the XML file.
        xml_content (bytes): the content of the XML file.
    """
    with open(file_path, 'wb') as xml_file:
        xml_file.write(xml_content)
