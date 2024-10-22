"""This class contains utility methods related to submodels."""
import logging
import os
from lxml import etree

from utilities import AAS_Archive_utils, ConfigMap_utils
from utilities.AASGeneralInfo import AASGeneralInfo

_logger = logging.getLogger(__name__)


# ------------------------
# Methods related to files
# ------------------------
def create_submodel_folder():
    """Create folder to save submodels."""
    os.mkdir(AASGeneralInfo.SUBMODEL_FOLDER_PATH)


def create_submodel_files(submodel_names_list):
    """
    This method creates all the files associated to the selected submodels.

    Args:
        submodel_names_list (list(str)): list of submodel names.
        """
    for submodel_name in submodel_names_list:
        # Get the submodel information from ConfigMap
        submodel_data = ConfigMap_utils.get_submodel_information(submodel_name)

        match submodel_name:
            case "technical-data-submodel":
                create_technical_data_sm(submodel_data)
            case "configuration-submodel":
                create_configuration_sm(submodel_data)
            case _:
                _logger.warning("Submodel not found.")
                break


# -------------------------------------
# Methods related to specific submodels
# -------------------------------------
def create_technical_data_sm(submodel_data):
    """
    This method creates the 'Technical Data' submodel XML file.

    Args:
        submodel_data (dict): information of the submodel in the same format as the submodel properties file
        content.
    """

    # Generate the XML of the submodel
    submodel_xml_content = etree.Element("submodel", name="technical_data_submodel")
    technical_data_level = etree.SubElement(submodel_xml_content, "technical_data")

    # Add data to XML
    for (key, val) in submodel_data:
        # print(key + ": " + val)
        etree.SubElement(technical_data_level, key).text = val

    # Write the content of submodel in a file
    AAS_Archive_utils.xml_to_file(
        AASGeneralInfo.SUBMODEL_FOLDER_PATH + '/' + AASGeneralInfo.TECHNICAL_DATA_SM_FILENAME,
        etree.tostring(submodel_xml_content))


def create_configuration_sm(submodel_data):
    """
    This method creates the 'Configuration' submodel XML file.

    Args:
        submodel_data (dict): information of the submodel in the same format as the submodel properties file
        content.
    """

    # Generate the XML of the submodel
    submodel_xml_content = etree.Element("submodel", name="configuration_submodel")
    configuration_level = etree.SubElement(submodel_xml_content, "configuration")

    # Add data to XML
    for (key, val) in submodel_data:
        # print(key + ": " + val)
        etree.SubElement(configuration_level, key).text = val

    # Write the content of submodel in a file
    AAS_Archive_utils.xml_to_file(
        AASGeneralInfo.SUBMODEL_FOLDER_PATH + '/' + AASGeneralInfo.CONFIGURATION_SM_FILENAME,
        etree.tostring(submodel_xml_content))


def check_if_submodel_exists(submodel_name):
    """
    This method checks if a submodel exist by its name.

    Args:
        submodel_name(str): Name of the submodel

    Returns:
        boolean: True if submodel exists and False if not.
    """

    # First, if the submodel.properties file exists has to be checked
    if os.path.isfile(AASGeneralInfo.CONFIG_MAP_PATH + '/' + AASGeneralInfo.CM_SM_PROPERTIES_FILENAME) is False:
        return False
    else:
        # Read each submodel definition files to get the submodel
        # TODO
        return True  # Under developing
