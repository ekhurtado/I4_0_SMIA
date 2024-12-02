""" File to group useful methods for accessing and managing the AAS Archive."""
import json
import logging
import os
import shutil
import time
from shutil import SameFileError

from utilities.smia_general_info import SMIAGeneralInfo
from utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


def initialize_smia_archive():
    """
    This method initializes the SMIA Archive, performing the necessary actions to let the archive in the initial
    necessary conditions to start the software.
    """
    # Create the status file
    create_status_file()

    # Create log file
    create_log_files()

    print("SMIA Archive initialized.")

# ------------------------
# Methods related to files
# ------------------------
def safe_open_file(file_path):
    """
    This method opens a file in a safe way. If the file does not exist, it will be created, and then opened.

    Args:
        file_path (str): The path to the file to be opened.
    """
    try:
        return open(file_path, 'x')
    except FileExistsError as e:
        return open(file_path, 'w')


def create_status_file():
    """This method creates the status file of the AAS Manager and sets it to "initializing". If the file exists because
    the AAS Manager has been restarted without terminating the Pod where it is running, the status file will be
    rewritten."""
    # The status information file will be a list of all the statuses the software has gone through.
    initial_status_info = [{'name': 'SMIA', 'status': 'Initializing',
                            'timestamp': GeneralUtils.get_current_timestamp()}]
    if not os.path.exists(SMIAGeneralInfo.STATUS_FOLDER_PATH):
        # If necessary, the status folder is created
        os.mkdir(SMIAGeneralInfo.STATUS_FOLDER_PATH)
    # try:
    #     status_file = open(SMIAGeneralInfo.STATUS_FOLDER_PATH + SMIAGeneralInfo.SMIA_STATUS_FILE_NAME, 'x')
    # except FileExistsError as e:
    #     status_file = open(SMIAGeneralInfo.STATUS_FOLDER_PATH + SMIAGeneralInfo.SMIA_STATUS_FILE_NAME, 'w')
    status_file = safe_open_file(SMIAGeneralInfo.STATUS_FOLDER_PATH + '/' + SMIAGeneralInfo.SMIA_STATUS_FILE_NAME)
    json.dump(initial_status_info, status_file)
    status_file.close()


def create_interaction_files():
    """This method creates the necessary interaction files to exchange information between AAS Core and AAS Manager."""

    # First interaction folders are created
    os.mkdir(SMIAGeneralInfo.CORE_INTERACTIONS_FOLDER_PATH)
    os.mkdir(SMIAGeneralInfo.MANAGER_INTERACTIONS_FOLDER_PATH)

    # Then the interaction files are added in each folder
    with (open(SMIAGeneralInfo.CORE_INTERACTIONS_FOLDER_PATH + SMIAGeneralInfo.SVC_REQUEST_FILE_SUBPATH,
               'x') as core_requests_file,
          open(SMIAGeneralInfo.CORE_INTERACTIONS_FOLDER_PATH + SMIAGeneralInfo.SVC_RESPONSE_FILE_SUBPATH,
               'x') as core_responses_file,
          open(SMIAGeneralInfo.MANAGER_INTERACTIONS_FOLDER_PATH + SMIAGeneralInfo.SVC_REQUEST_FILE_SUBPATH,
               'x') as manager_requests_file,
          open(SMIAGeneralInfo.MANAGER_INTERACTIONS_FOLDER_PATH + SMIAGeneralInfo.SVC_RESPONSE_FILE_SUBPATH,
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

    if not os.path.exists(SMIAGeneralInfo.LOG_FOLDER_PATH):
        # If necessary, the status folder is created
        os.mkdir(SMIAGeneralInfo.LOG_FOLDER_PATH)

    if not os.path.exists(SMIAGeneralInfo.SVC_LOG_FOLDER_PATH):
        # If necessary, the folder for services log is also created
        os.mkdir(SMIAGeneralInfo.SVC_LOG_FOLDER_PATH)

    # Then the log files are added in each folder
    all_svc_log_file_names = [SMIAGeneralInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                              SMIAGeneralInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME,
                              SMIAGeneralInfo.AAS_SERVICES_LOG_FILENAME, SMIAGeneralInfo.SUBMODEL_SERVICES_LOG_FILENAME]
    for log_file_name in all_svc_log_file_names:
        with safe_open_file(SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + log_file_name) as log_file:
            log_file.write('[]')
            log_file.close()

def save_cli_added_files(init_config, aas_model):
    """
    This method saves the specified files in the Command Line Interface into the SMIA Archive.

    Args:
        init_config (str): path to the initialization configuration properties file.
        aas_model (str): path to the AAS model file.
    """
    for cli_file in [init_config, aas_model]:
        if cli_file is not None:
            copy_file_into_archive(cli_file, SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)


def copy_file_into_archive(source_file, dest_file):
    """
    This method copies a file into the SMIA archive.

    Args:
        source_file (str): path of the source file.
        dest_file (str): path of the destiny file (it must be inside the SMIA archive).
    """
    if SMIAGeneralInfo.SMIA_ARCHIVE_PATH not in dest_file:
        dest_file = SMIAGeneralInfo.SMIA_ARCHIVE_PATH + '/' + dest_file
    try:
        shutil.copy(source_file, dest_file)
    except SameFileError as e:
        _logger.info("The {} file is already in SMIA archive.".format(source_file))


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
            log_file_path = SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.ASSET_RELATED_SVC_LOG_FILENAME
        case "AASInfrastructureServices":
            log_file_path = SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME
        case "AASservices":
            log_file_path = SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.AAS_SERVICES_LOG_FILENAME
        case "SubmodelServices":
            log_file_path = SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.SUBMODEL_SERVICES_LOG_FILENAME
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
def update_status(new_status):
    """
    This method updated the status of an AAS Manager instance.

    Args:
        new_status (str): the new status of the AAS Manager instance.
    """
    status_file_path = SMIAGeneralInfo.STATUS_FOLDER_PATH + '/' + SMIAGeneralInfo.SMIA_STATUS_FILE_NAME
    status_file_json = file_to_json(status_file_path)
    status_file_json.append({'name': 'SMIA', 'status': new_status,
                             'timestamp': GeneralUtils.get_current_timestamp()})
    update_json_file(status_file_path, status_file_json)


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
        status_file_json = file_to_json(SMIAGeneralInfo.SMIA_STATUS_FILE_PATH)
    elif entity == "Core":
        status_file_json = file_to_json(SMIAGeneralInfo.CORE_STATUS_FILE_PATH)
    return status_file_json['status']


def check_core_initialization():
    """This method checks if the core has initialized so the Manager can be started."""
    while True:
        if os.path.isfile(SMIAGeneralInfo.CORE_STATUS_FILE_PATH) is True:
            if file_to_json(SMIAGeneralInfo.CORE_STATUS_FILE_PATH)['status'] != "Initializing":
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
