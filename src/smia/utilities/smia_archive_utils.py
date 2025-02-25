""" File to group useful methods for accessing and managing the AAS Archive."""
import json
import logging
import os
import shutil
import time
from shutil import SameFileError

from smia.utilities import properties_file_utils
from smia.utilities.fipa_acl_info import ServiceTypes
from smia.utilities.smia_general_info import SMIAGeneralInfo
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


def initialize_smia_archive():
    """
    This method initializes the SMIA Archive, performing the necessary actions to let the archive in the initial
    necessary conditions to start the software.
    """
    # Create the required folders
    create_archive_folders()

    # Create the status file
    create_status_file()

    # Create the properties file
    create_properties_file()

    # Create log file
    create_log_files()

    _logger.info("SMIA Archive initialized.")


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

def create_archive_folders():
    """
    This method ensures that all main folders of the archive exist, as well ass the parent archive folder.
    """
    required_folders_paths = [SMIAGeneralInfo.SMIA_ARCHIVE_PATH, SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH,
                              SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH, SMIAGeneralInfo.STATUS_FOLDER_PATH,
                              SMIAGeneralInfo.LOG_FOLDER_PATH]
    for folder_path in required_folders_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def create_status_file():
    """This method creates the status file of the SMIA and sets it to "initializing". If the file exists because
    the SMIA has been restarted without terminating the Pod where it is running, the status file will be
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

def create_properties_file():
    """
    This method creates the properties file of the SMIA adding default values for each attribute. If the file exists
    because the SMIA has been restarted without terminating the Pod where it is running, the file will be
    rewritten.
    """
    properties_file_utils.create_empty_file()


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

    all_log_folders = [SMIAGeneralInfo.SVC_LOG_FOLDER_PATH, SMIAGeneralInfo.ERROR_LOG_FOLDER_PATH]

    # Then the log files are added in each folder
    all_svc_log_file_names = [SMIAGeneralInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                              SMIAGeneralInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME,
                              SMIAGeneralInfo.AAS_SERVICES_LOG_FILENAME, SMIAGeneralInfo.SUBMODEL_SERVICES_LOG_FILENAME,
                              SMIAGeneralInfo.SUBMODEL_CSS_LOG_FILENAME]
    for log_folder in all_log_folders:
        if not os.path.exists(log_folder):
            # If necessary, folders are also created for each log
            os.mkdir(log_folder)
        for log_file_name in all_svc_log_file_names:
            with safe_open_file(log_folder + '/' + log_file_name) as log_file:
                log_file.write('[]')
                log_file.close()


def save_cli_added_files(init_config=None, aas_model=None):
    """
    This method saves the specified files in the Command Line Interface into the SMIA Archive.

    Args:
        init_config (str): path to the initialization configuration properties file.
        aas_model (str): path to the AAS model file.
    """
    # for cli_file in [init_config, aas_model]:
    #     if cli_file is not None:
    #         copy_file_into_archive(cli_file, SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
    # The initialization configuration properties file is stored in the main configuration folder of the SMIA Archive
    if init_config is not None:
        copy_file_into_archive(init_config, SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH)
    # The AAS model file is stored in the AAS-related configuration folder of the SMIA Archive
    if aas_model is not None:
        copy_file_into_archive(aas_model, SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH)


def copy_file_into_archive(source_file, dest_file):
    """
    This method copies a file into the SMIA archive.

    Args:
        source_file (str): path of the source file.
        dest_file (str): path of the destiny file (it must be inside the SMIA archive).
    """
    # If the archive does not exist, it must be initialized
    if not os.path.exists(SMIAGeneralInfo.SMIA_ARCHIVE_PATH):
        create_archive_folders()

    if SMIAGeneralInfo.SMIA_ARCHIVE_PATH not in dest_file:
        dest_file = SMIAGeneralInfo.SMIA_ARCHIVE_PATH + '/' + dest_file
    try:
        shutil.copy(source_file, dest_file)
    except SameFileError as e:
        _logger.info("The {} file is already in SMIA archive.".format(source_file))


# ----------------------
# Methods related to log
# ----------------------
def get_log_file_by_service_type(log_type, svc_type):
    """
    This method obtains the path to the log file associated to the type of the service.
    Args:
        log_type (str): the type of the log.
        svc_type (str): type of the service.

    Returns:
        str: path to the log file
    """
    log_file_path = None
    if log_type == 'services':
        log_folder_path = SMIAGeneralInfo.SVC_LOG_FOLDER_PATH
    elif log_type == 'errors':
        log_folder_path = SMIAGeneralInfo.ERROR_LOG_FOLDER_PATH
    else:
        _logger.error("Log type not available.")
        return None

    match svc_type:
        case ServiceTypes.ASSET_RELATED_SERVICE:
            log_file_path = log_folder_path + '/' + SMIAGeneralInfo.ASSET_RELATED_SVC_LOG_FILENAME
        case ServiceTypes.AAS_INFRASTRUCTURE_SERVICE:
            log_file_path = log_folder_path + '/' + SMIAGeneralInfo.AAS_INFRASTRUCTURE_SVC_LOG_FILENAME
        case ServiceTypes.AAS_SERVICE:
            log_file_path = log_folder_path + '/' + SMIAGeneralInfo.AAS_SERVICES_LOG_FILENAME
        case ServiceTypes.SUBMODEL_SERVICE:
            log_file_path = log_folder_path + '/' + SMIAGeneralInfo.SUBMODEL_SERVICES_LOG_FILENAME
        case ServiceTypes.CSS_RELATED_SERVICE:
            log_file_path = log_folder_path + '/' + SMIAGeneralInfo.SUBMODEL_CSS_LOG_FILENAME
        case _:
            _logger.error("Service type not available.")
    return log_file_path


def save_completed_svc_log_info(started_timestamp, finished_timestamp, acl_info, result, svc_type):
    """
    This method saves the information about a realized service in the log file associated to the type of the service.

    Args:
        started_timestamp (int): the timestamp when the service has been requested.
        finished_timestamp (int): the timestamp when the service has finished.
        acl_info (dict): JSON object with the information of the service request.
        result: the result of the service execution.
        svc_type (str): type of the service.
    """
    # First, the required paths are obtained
    log_file_path = get_log_file_by_service_type('services', svc_type)

    # Then, the information object is built and added
    svc_log_info = {
        'startedTimestamp': started_timestamp,
        'finishedTimestamp': finished_timestamp,
        'status': 'Completed',
        'requestInfo': acl_info,
        'result': result
    }
    log_file_json = file_to_json(log_file_path)
    log_file_json.append(svc_log_info)

    # Finally, the file is updated
    update_json_file(log_file_path, log_file_json)

    _logger.info("Saved new completed service information in the log.")

def get_file_by_extension(folder_path, file_extension):
    """
    This method obtains the path of a file inside a given folder with a given extension.

    Args:
        folder_path (str): path to the folder to be searched.
        file_extension (str): extension of the file (without dot '.').

    Returns:
        str: path of the file to search (None if it does not exist).
    """
    if not os.path.exists(folder_path):
        _logger.warning('The folder path to be searched does not exist')
        return None
    dir_files = os.listdir(folder_path)
    for file in dir_files:
        file_name, file_ext = os.path.splitext(file)
        if file_extension == file_ext:
            return  folder_path + '/' + file
    _logger.warning('A file with extension {} was not found inside the {} folder.'.format(file_extension, folder_path))
    return None

def save_svc_error_log_info(occurrence_timestamp, acl_info, reason, svc_type):
    """
    This method saves the information about a realized service in the log file associated to the type of the service.

    Args:
        occurrence_timestamp (int): the timestamp when the error occurred.
        acl_info (dict): JSON object with the information of the service request.
        reason (str): the reason of the error.
        svc_type (str): type of the service.
    """
    # First, the required paths are obtained
    log_file_path = get_log_file_by_service_type('errors', svc_type)

    # Then, the information object is built and added
    svc_log_info = {
        'timestamp': occurrence_timestamp,
        'status': 'Error',
        'requestInfo': acl_info,
        'reason': reason
    }
    log_file_json = file_to_json(log_file_path)
    log_file_json.append(svc_log_info)

    # Finally, the file is updated
    update_json_file(log_file_path, log_file_json)

    _logger.info("Saved new completed service information in the log.")


# -------------------------
# Methods related to status
# -------------------------
def update_status(new_status):
    """
    This method updated the status of an SMIA instance.

    Args:
        new_status (str): the new status of the SMIA instance.
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
    _logger.info('AAS Core has initialized, so the SMIA is starting.')


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
