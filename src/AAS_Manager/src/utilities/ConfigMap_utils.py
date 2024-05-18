"""This file contains utility methods related to the ConfigMap file."""
import configparser

from utilities.AAS_archive_info import AASarchiveInfo


# ----------------------------
# Methods related to submodels
# ----------------------------
def get_submodel_names():
    """This method returns all submodel names that have been selected for the AAS instance. It is the submodel
    properties file sections of the AAS configuration in the ConfigMap that will determine which submodels these are.

    Returns
    -------
    :return A list with the sections of the submodel properties file, and therefore, the submodel names."""
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(AASarchiveInfo.CONFIG_MAP_PATH + '/' + AASarchiveInfo.CM_SM_PROPERTIES_FILENAME)

    return config_sm.sections()


def get_submodel_information(submodel_name):
    """This method returns the submodel information of a specific submodel, from the submodel properties file of the
    configuration from the ConfigMap.

    Parameters
    ----------
    Args:
        submodel_name (str): The name of the submodel. To read from the submodel properties file, it is also the name of
    the section.

    Returns
    -------
    Returns:
        submodel_info (dict): The submodel information in the same format as the submodel properties file content.
    """
    # Read submodels configuration
    config_sm = configparser.RawConfigParser()
    config_sm.read(AASarchiveInfo.CONFIG_MAP_PATH + '/' + AASarchiveInfo.CM_SM_PROPERTIES_FILENAME)

    return config_sm.items(submodel_name)
