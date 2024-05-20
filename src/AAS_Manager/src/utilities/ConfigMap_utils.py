import configparser

from utilities.AAS_archive_info import AASarchiveInfo


# ----------------------------
# Methods related to submodels
# ----------------------------
class ConfigMap_utils:
    """This class contains utility methods related to the ConfigMap file."""
    @staticmethod
    def get_submodel_names():
        """This method returns all submodel names that have been selected for the AAS instance. It is the submodel
        properties file sections of the AAS configuration in the ConfigMap that will determine which submodels these are.

        Returns
        -------
        list(str)
            A list with the sections of the submodel properties file, and therefore, the submodel names."""
        # Read submodels configuration
        config_sm = configparser.RawConfigParser()
        config_sm.read(AASarchiveInfo.CONFIG_MAP_PATH + '/' + AASarchiveInfo.CM_SM_PROPERTIES_FILENAME)

        return config_sm.sections()

    @staticmethod
    def get_submodel_information(submodel_name):
        """
        This method returns the submodel information of a specific submodel, from the submodel properties file of the
        configuration from the ConfigMap.

        Args:
            submodel_name  (str, required): The name of the submodel. To read from the submodel properties file, it is also the name of the section.

        Returns:
            dict: The submodel information in the same format as the submodel properties file content.
        """
        # Read submodels configuration
        config_sm = configparser.RawConfigParser()
        config_sm.read(AASarchiveInfo.CONFIG_MAP_PATH + '/' + AASarchiveInfo.CM_SM_PROPERTIES_FILENAME)

        return config_sm.items(submodel_name)
