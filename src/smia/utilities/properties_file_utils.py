"""This class contains utility methods related to the ConfigMap file."""
import logging
import configparser
import os.path

from smia.logic.exceptions import CriticalError
from smia.utilities.smia_general_info import SMIAGeneralInfo

_logger = logging.getLogger(__name__)

# ---------------
# General methods
# ---------------
def create_empty_file():
    """
    This method creates a properties configuration file for SMIA with default values ('#').
    """

    config_prop = configparser.RawConfigParser()
    config_prop['DT'] = {'dt.version': '#', 'dt.agentID': '#', 'dt.password': '#', 'dt.xmpp-server': '#',
                         'dt.web-ui': '#'}
    config_prop['AAS'] = {'aas.meta-model.version': '#', 'aas.model.serialization': '#', 'aas.model.folder': '#',
                          'aas.model.file': '#'}
    config_prop['ONTOLOGY'] = {'ontology.file': '#', 'ontology.inside-aasx': '#'}
    update_properties_file_by_parser(config_prop)


def update_properties_file_by_parser(new_config_parser):
    """
    This method updates the content of the properties file by a given parser.

    Args:
        new_config_parser (configparser.RawConfigParser): the parser with the new content for the properties file.
    """
    with (open(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME, 'w')
          as propertiesFile):
        new_config_parser.write(propertiesFile)

def update_properties_file_by_bytes(new_config_bytes):
    """
    This method updates the content of the properties file by given properties in the form of bytes.

    Args:
        new_config_bytes (configparser.RawConfigParser): the parser with the new content for the properties file.
    """
    config_parser = configparser.RawConfigParser()
    new_config_str = new_config_bytes.decode('utf-8')
    config_parser.read_string(new_config_str)

    # Only not defined data need to be updated
    archive_config_parser = configparser.RawConfigParser()
    archive_config_parser.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    for section in archive_config_parser.sections():
        for key, value in archive_config_parser.items(section):
            if value == '#':
                archive_config_parser[section][key] = config_parser[section][key]

    update_properties_file_by_parser(archive_config_parser)

# ----------------------------------
# Methods related to AAS information
# ----------------------------------
def get_aas_general_property(property_name):
    """
    This method returns the property of the AAS set in the ConfigMap by the AAS Controller during the deployment
    process. This information is stored in "general.properties" file within "AAS" section (with the 'aas.' prefix).

    Args:
        property_name (str): The name of the property.
    Returns:
        str: The general property of the AAS.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)

    try:
        return config_sm['AAS']['aas.' + property_name]
    except KeyError as e:
        _logger.error("The 'general.properties' file in the ConfigMap is not valid.")
        return None

def set_aas_general_property(property_name, property_value):
    """
    This method sets a new value for a property of the AAS. The information is stored in "general.properties" file
    within "AAS" section (with the 'aas.' prefix).

    Args:
        property_name (str): The name of the property.
        property_value (str): The new value of the property.
    """
    # Read submodels configuration
    config_prop = configparser.RawConfigParser()
    config_prop.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)

    try:
        config_prop['AAS']['aas.' + property_name] = property_value
        update_properties_file_by_parser(config_prop)
    except KeyError as e:
        _logger.error("The 'general.properties' file in the ConfigMap is not valid regarding 'AAS' section.")
        return None

def get_aas_model_filepath():
    """
    This method returns the AAS model file path. The AAS model is specified in the ‘general.properties’ file
    within the ‘AAS’ section, with 'aas.model.file' attribute.

    Returns:
        str: The AAS model file path within the SMIA Archive.
    """
    # config_sm = configparser.RawConfigParser()
    # config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    # return SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + config_sm['AAS']['aas.model.file']
    return SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_AAS_MODEL_FILENAME


# --------------------------------------
# Methods related to DT information
# --------------------------------------
def get_dt_general_property(property_name):
    """
    This method returns the DT property set in the ConfigMap during the deployment process. This information is stored
    in the ‘general.properties’ file within the ‘DT’ section (with the 'dt.' prefix).

    Returns:
        str: The general property of the DT.
    """
    config_sm = configparser.RawConfigParser()
    if not os.path.exists(
            SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME):
        raise CriticalError("General properties file not found in [" + SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' +
                            SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME + "], the path is invalid.")
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    try:
        return config_sm['DT']['dt.' + property_name]
    except KeyError as e:
        raise CriticalError("The 'general.properties' file in the ConfigMap does not have valid keys.")

# --------------------------------------
# Methods related to ontology information
# --------------------------------------
def get_ontology_general_property(property_name):
    """
    This method returns the property of the OWL set in the ConfigMap by the AAS Controller during the deployment
    process. This information is stored in "general.properties" file within "ONTOLOGY" section (with the 'ontology.'
    prefix).

    Args:
        property_name (str): The name of the property.
    Returns:
        str: The general property of the ontology.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)

    try:
        return config_sm['ONTOLOGY']['ontology.' + property_name]
    except KeyError as e:
        _logger.error("The 'initialization.properties' file in the SMIA Archive is not valid or it is not defined.")
        return None

def get_defined_ontology_filepath():
    """
    This method returns the OWL ontology file path. If the file for the OWL ontology is specified in the
    ‘general.properties’ file, it is located within the ‘ONTOLOGY’ section, with 'ontology.owl.file' attribute.

    Returns:
        str: The ontology file path within the SMIA Archive.
    """
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    return SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + config_sm['ONTOLOGY']['ontology.file']

def create_ontology_file(file_bytes_content):
    """
    This method creates the ontology OWL file with the given file content. This method is used when the ontology file
    is inside the AASX package, so it must be created outside in order to be available for loading.

    Returns:
        str: The new ontology OWL file path within the SMIA Archive.
    """
    # The new ontology file is created in SMIA Archive inside configuration folder
    new_ontology_file_path = SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + "ontology.owl"
    with open(new_ontology_file_path, "wb") as binary_file:
        # Write bytes to file
        binary_file.write(file_bytes_content)
    return new_ontology_file_path

# --------------------------------------
# Methods related to asset information
# --------------------------------------
def get_asset_type():
    """
    This method returns the asset type of the AAS set in the ConfigMap by the AAS Controller during the deployment process. This information is stored in "asset.properties" file.

    Returns:
        str: The asset type of the AAS.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_ASSET_PROPERTIES_FILENAME)
    return config_sm['DEFAULT']['assetType']


# ----------------------------
# Methods related to submodels
# ----------------------------
def get_submodel_names():
    """
    This method returns all submodel names that have been selected for the AAS instance. It is the submodel
    properties file sections of the AAS configuration in the ConfigMap that will determine which submodels these
    are.

    Returns:
        list(str): A list with the sections of the submodel properties file, and therefore, the submodel names."""
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_SM_PROPERTIES_FILENAME)

    return config_sm.sections()


def get_submodel_information(submodel_name):
    """
    This method returns the submodel information of a specific submodel, from the submodel properties file of the
    configuration from the ConfigMap.

    Args:
        submodel_name  (str): The name of the submodel. To read from the submodel properties file, it is also
        the name of the section.

    Returns:
        dict: The submodel information in the same format as the submodel properties file content.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_SM_PROPERTIES_FILENAME)

    return config_sm.items(submodel_name)
