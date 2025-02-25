"""
This is the main package of SMIA, that includes all source code and all subpackages.
"""

__author__ = """Ekaitz Hurtado"""
__email__ = "ekaitz.hurtado@ehu.eus"
__version__ = '0.2.1'

__all__ = ['launchers', 'agents', 'utilities', 'assetconnection']

import logging
import ntpath

import spade

from .aas_model.aas_model_utils import AASModelUtils
from .logic.exceptions import CriticalError
from .utilities.aas_model_extension_utils import AASModelExtensionUtils
from .utilities import properties_file_utils, smia_archive_utils
from .utilities.general_utils import GeneralUtils
from .utilities.smia_general_info import SMIAGeneralInfo


def initial_self_configuration():
    """
    This method executes the initial configuration of the SMIA software.
    """
    # First, the BaSyx Python SDK is extended to have all new methods available
    AASModelExtensionUtils.extend_basyx_aas_model()

    # Initialize SMIA archive
    smia_archive_utils.initialize_smia_archive()

    # Configure logging
    GeneralUtils.configure_logging()


def run(agent_object):
    """
    This method runs the SMIA software with a given agent.
    """

    _logger = logging.getLogger(__name__)

    if agent_object is None:
        _logger.error('To launch SMIA, an agent must be passed to the method "smia.run".')
        return

    async def main():
        await agent_object.start()

        await spade.wait_until_finished(agent_object)

        # In the general properties file you can select the web interface (provided by SPADE).
        web_ui = properties_file_utils.get_dt_general_property('web-ui')
        if web_ui.lower() in ('yes', 'true', 't', '1'):
            # bool(string) cannot be used as it is true as long as the string is not empty.
            agent_object.web.start(hostname="0.0.0.0", port="10002")

    spade.run(main())


def load_aas_model(file_path):
    """
    This method loads the AAS model using a given path to the AASX package file.

    Args:
        file_path (str): path to the AASX package file.
    """
    # If the user has not run the initial self-configuration method, it is now executed
    initial_self_configuration()

    _logger = logging.getLogger(__name__)
    # TODO At the moment it only collects models in AASX, think about whether to leave option to XML and JSON as well.

    if file_path is None:
        _logger.error("The file path to the AAS model is None, so it cannot be loaded.")
        return

    # The variable with the AAS model file name is updated
    aas_model_file_name = ntpath.split(file_path)[1] or ntpath.basename(ntpath.split(file_path)[0])
    # SMIAGeneralInfo.CM_AAS_MODEL_FILENAME = aas_model_file_name
    GeneralUtils.update_aas_model(aas_model_file_name)

    # The file will be copied into the SMIA archive
    try:
        smia_archive_utils.copy_file_into_archive(file_path, SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH)
    except Exception as e:
        raise CriticalError('It is not possible to copy the specified AAS model into the SMIA Archive, so the SMIA '
                      'cannot be started. Reason: {}'.format(e))
    _logger.info("AAS model {} copied to the SMIA Archive.".format(SMIAGeneralInfo.CM_AAS_MODEL_FILENAME))

    # When the AAS model is inside the SMIA archive, it will be checked if it is valid
    try:
        config_file_path = AASModelUtils.get_configuration_file_path_from_standard_submodel()
        init_config_file_name = ntpath.split(config_file_path)[1] or ntpath.basename(ntpath.split(config_file_path)[0])
        config_file_bytes = AASModelUtils.get_file_bytes_from_aasx_by_path(config_file_path)
        properties_file_utils.update_properties_file_by_bytes(config_file_bytes)
        # with open(SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH + '/' + init_config_file_name, "wb") as binary_file:
        #     binary_file.write(config_file_bytes)  # Write bytes to file
        # SMIAGeneralInfo.CM_GENERAL_PROPERTIES_FILENAME = init_config_file_name
    except Exception as e:
        _logger.warning("The AAS model does not contain the initialization configuration file. Make sure that it is "
                        "not necessary.")

        # _logger.error(e)
