import logging
from os import path

import basyx
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.util import traversal

from logic.exceptions import CriticalError
from utilities import configmap_utils
from utilities.smia_general_info import SMIAGeneralInfo

_logger = logging.getLogger(__name__)

class AASModelUtils:
    """This class contains utility methods related to the AAS model."""

    @staticmethod
    async def read_aas_model_object_store():
        """
        This method reads the AAS model according to the selected serialization format.

        Returns:
            basyx.aas.model.DictObjectStore:  object with all Python elements of the AAS model.
        """
        object_store = None
        aas_model_file_path = configmap_utils.get_aas_model_filepath()
        aas_model_file_name, aas_model_file_extension = path.splitext(SMIAGeneralInfo.CM_AAS_MODEL_FILENAME)
        try:
            # The AAS model is read depending on the serialization format (extension of the AAS model file)
            if aas_model_file_extension == '.json':
                object_store = basyx.aas.adapter.json.read_aas_json_file(aas_model_file_path)
            elif aas_model_file_extension == '.xml':
                object_store = basyx.aas.adapter.xml.read_aas_xml_file(aas_model_file_path)
            elif aas_model_file_extension == '.aasx':
                    with aasx.AASXReader(aas_model_file_path) as reader:
                        # Read all contained AAS objects and all referenced auxiliary files
                        object_store = model.DictObjectStore()
                        suppl_file_store = aasx.DictSupplementaryFileContainer()
                        reader.read_into(object_store=object_store,
                                         file_store=suppl_file_store)
        except ValueError as e:
            _logger.error("Failed to read AAS model: invalid file.")
            _logger.error(e)
            raise CriticalError("Failed to read AAS model: invalid file.")
        if object_store is None or len(object_store) == 0:
            raise CriticalError("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                          "metamodel.")
        else:
            return object_store

    @staticmethod
    async def get_configuration_file_path_from_standard_submodel():
        """
        This method gets the configuration file defined in the 'Software Nameplate' submodel, used as standard submodel
        for the SMIA software definition.

        Returns:
            str: path inside the AASX package of the configuration file.
        """
        # First, the AAS model need to be read
        object_store = await AASModelUtils.read_aas_model_object_store()
        soft_nameplate_config_paths = await AASModelUtils.get_elem_of_software_nameplate_by_semantic_id(object_store)
        if soft_nameplate_config_paths is None:
            raise CriticalError("Configuration of SMIA is required and it is not defined within the Software Nameplate submodel.")
        for config_path_elem in soft_nameplate_config_paths:
            if config_path_elem.get_sm_element_by_semantic_id(
                    AASModelInfo.SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_TYPE).value == 'initial configuration':
                return config_path_elem.get_sm_element_by_semantic_id(
                    AASModelInfo.SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_URI).value
        return None

    @staticmethod
    async def get_elem_of_software_nameplate_by_semantic_id(object_store):
        """
        This method obtains a SubmodelElement of the Software Nameplate submodel.

        Args:
            object_store (basyx.aas.model.DictObjectStore): storage with all AAS information,

        Returns:
            basyx.aas.model.SubmodelElement: submodelElement with the given semanticID
        """
        for object in object_store:
            if isinstance(object, basyx.aas.model.Submodel):
                if object.check_semantic_id_exist(AASModelInfo.SEMANTICID_SOFTWARE_NAMEPLATE_SUBMODEL):
                    for elem in traversal.walk_submodel(object):
                        if isinstance(elem, basyx.aas.model.SubmodelElement):
                            if elem.check_semantic_id_exist(AASModelInfo.SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_PATHS):
                                return elem
        return None


class AASModelInfo:
    """This class contains the information related to AAS model."""
    SEMANTICID_SOFTWARE_NAMEPLATE_SUBMODEL = 'https://admin-shell.io/idta/SoftwareNameplate/1/0'
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_PATHS = 'https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate/SoftwareNameplateInstance/ConfigurationPaths'
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_TYPE = 'https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate/SoftwareNameplateInstance/ConfigurationType'
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_URI = 'https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate/SoftwareNameplateInstance/ConfigurationURI'

    # TODO pasar aqui todos los IDs requeridos en el AAS (p.e el de AID submodel)

