"""File to group useful methods for accessing and managing the AAS Archive."""
import calendar
import configparser
import json
import logging
import os
import time

from utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


# ------------------------
# Methods related to files
# ------------------------
def create_status_file():
    """This method creates the status file of the AAS Manager and sets it to "initializing"."""
    initial_status_info = {'name': 'AAS_Core', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}

    try :
        f = open(AASarchiveInfo.CORE_STATUS_FILE_PATH, 'x')
    except FileExistsError as e:
        f = open(AASarchiveInfo.CORE_STATUS_FILE_PATH, 'w')
    json.dump(initial_status_info, f)
    f.close()

def create_interaction_files():
    """This method creates the necessary interaction files to exchange information between AAS Core and AAS Manager."""

    # First interaction folders are created
    os.mkdir(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH)
    os.mkdir(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH)

    # Then the interaction files are added in each folder
    core_requests_file = open(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH,'x')
    core_responses_file = open(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH,'x')
    manager_requests_file = open(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH,'x')
    manager_responses_file = open(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH,'x')

    core_requests_file.write('{"serviceRequests": []}')
    core_requests_file.close()

    manager_requests_file.write('{"serviceRequests": []}')
    manager_requests_file.close()

    core_responses_file.write('{"serviceResponses": []}')
    core_responses_file.close()

    manager_responses_file.write('{"serviceResponses": []}')
    manager_responses_file.close()

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

def change_status(new_status):
    """
    This method updated the status of an AAS Manager instance.

    Args:
        new_status (str): the new status of the AAS Manager instance.
    """
    status_file_json = file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)
    status_file_json['status'] = new_status
    status_file_json['timestamp'] = calendar.timegm(time.gmtime())
    update_json_file(AASarchiveInfo.CORE_STATUS_FILE_PATH, status_file_json)


def get_aas_general_property(property_name):
    """
    This method returns the property of the AAS set in the ConfigMap by the AAS Controller during the deployment process. This information is stored in "aas.properties" file within "general-information" section.

    Args:
        property_name (str): The name of the property.
    Returns:
        str: The general property of the AAS.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(AASarchiveInfo.CONFIG_MAP_PATH + '/' + AASarchiveInfo.CM_AAS_PROPERTIES_FILENAME)
    return config_sm['general-information'][property_name]