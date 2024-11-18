"""This class contains utility methods related to the ConfigMap file."""
import logging
import configparser
import os.path

from logic.exceptions import CriticalError
from utilities.aas_general_info import SMIAGeneralInfo

_logger = logging.getLogger(__name__)


# --------------------------------------
# Methods related to aas information
# --------------------------------------
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


def get_aas_model_filepath():
    """
    This method returns the AAS model file path. The AAS model is specified in the ‘general.properties’ file
    within the ‘AAS’ section, with 'aas.model.file' attribute.

    Returns:
        str: The AAS model file path within the AAS Archive.
    """
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    return SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + config_sm['AAS']['aas.model.file']

def get_ontology_filepath():
    """
    This method returns the OWL ontology file path. The file for the OWL ontology is specified in the
    ‘general.properties’ file within the ‘ONTOLOGY’ section, with 'ontology.owl.file' attribute.

    Returns:
        str: The AAS model file path within the AAS Archive.
    """
    config_sm = configparser.RawConfigParser()
    config_sm.read(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME)
    return SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + config_sm['ONTOLOGY']['ontology.owl.file']


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
