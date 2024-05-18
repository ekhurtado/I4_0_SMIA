""" File to group useful methods for accessing and managing the AAS Archive."""
import calendar
import json
import os
import time

from utilities.AAS_archive_info import AASarchiveInfo


# ------------------------
# Methods related to files
# ------------------------
def create_status_file():
    """This method creates the status file of the AAS Manager and sets it to "initializing"."""
    initial_status_info = {'name': 'AAS_Manager', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}

    with (open(AASarchiveInfo.MANAGER_STATUS_FILE_PATH, 'x') as status_file):
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


# -------------------------
# Methods related to status
# -------------------------
def change_status(new_status):
    """This method updated the status of an AAS Manager instance.

    Parameters
    ----------
    :param new_status: the new status of the AAS Manager instance.
    """
    status_file_json = file_to_json(AASarchiveInfo.MANAGER_STATUS_FILE_PATH)
    status_file_json['status'] = new_status
    status_file_json['timestamp'] = calendar.timegm(time.gmtime())
    update_json_file(AASarchiveInfo.MANAGER_STATUS_FILE_PATH, status_file_json)


def get_status(entity):
    """This method gets the status of the requested entity.

    Parameters
    ----------
    :param entity: The entity to get the status for.

    Returns
    -------
    :return status in JSON format.
    """
    status_file_json = None
    if entity == "Manager":
        status_file_json = file_to_json(AASarchiveInfo.MANAGER_STATUS_FILE_PATH)
    elif entity == "Core":
        status_file_json = file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)
    return status_file_json['status']


def check_core_initialization():
    """This method checks if the core has initialized so the Manager can be started."""
    core_initialized = False
    while core_initialized is False:
        if os.path.isfile(AASarchiveInfo.CORE_STATUS_FILE_PATH) is True:
            if file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)['status'] != "Initializing":
                core_initialized = True
        time.sleep(1)  # waits 1s
    print('AAS Core has initialized, so the AAS Manager is starting.')


# ------------------------
# Methods related to JSON
# ------------------------
def file_to_json(file_path):
    """This method gets the content of a JSON file.

    Parameters
    ----------
    :param file_path: the path of the JSON file.

    Returns
    -------
    :return content of the file in JSON format."""
    f = open(file_path)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)
        return None
    return content


def update_json_file(file_path, content):
    """This method updates the content of a JSON file.

    Parameters
    ----------
    :param file_path: the path to the JSON file.
    :param content: the content of the JSON file.
    """
    with open(file_path, "w") as outfile:
        json.dump(content, outfile)


# ------------------------
# Methods related to XML
# ------------------------
def xml_to_file(file_path, xml_content):
    """This method writes the content of an XML in a file.

    Parameters
    ----------
    :param file_path: the path to the XML file.
    :param xml_content: the content of the XML file.
    """
    with open(file_path, 'wb') as xml_file:
        xml_file.write(xml_content)
