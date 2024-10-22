"""This class contains utility methods related to the ConfigMap file."""

import configparser

from utilities.AASGeneralInfo import AASGeneralInfo

# --------------------------------------
# Methods related to aas information
# --------------------------------------
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
    config_sm.read(AASGeneralInfo.CONFIG_MAP_PATH + '/' + AASGeneralInfo.CM_AAS_PROPERTIES_FILENAME)
    return config_sm['general-information'][property_name]


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
    config_sm.read(AASGeneralInfo.CONFIG_MAP_PATH + '/' + AASGeneralInfo.CM_ASSET_PROPERTIES_FILENAME)
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
    config_sm.read(AASGeneralInfo.CONFIG_MAP_PATH + '/' + AASGeneralInfo.CM_SM_PROPERTIES_FILENAME)

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
    config_sm.read(AASGeneralInfo.CONFIG_MAP_PATH + '/' + AASGeneralInfo.CM_SM_PROPERTIES_FILENAME)

    return config_sm.items(submodel_name)
