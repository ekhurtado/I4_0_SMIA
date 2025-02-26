import logging
from os import path

import basyx
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.util import traversal

from smia.logic.exceptions import CriticalError, AASModelReadingError
from smia.utilities import properties_file_utils
from smia.utilities.smia_general_info import SMIAGeneralInfo

_logger = logging.getLogger(__name__)


class AASModelUtils:
    """This class contains utility methods related to the AAS model."""

    @staticmethod
    def read_aas_model_object_store():
        """
        This method reads the AAS model according to the selected serialization format.

        Returns:
            basyx.aas.model.DictObjectStore:  object with all Python elements of the AAS model.
        """
        object_store = None
        aas_model_file_path = properties_file_utils.get_aas_model_filepath()
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

    # Methods related to AASX Package
    # -------------------------------
    @staticmethod
    def get_file_bytes_from_aasx_by_path(file_path):
        """
        This method gets the bytes of a file appended inside an AASX package by a given internal path.

        Args:
            file_path (str): the internal path of the file within the AASX package.

        Returns:
            obj: the content of the file in the form of bytes.
        """
        with aasx.AASXReader(properties_file_utils.get_aas_model_filepath()) as aasx_reader:
            for part_name, content_type in aasx_reader.reader.list_parts():
                if part_name == file_path:
                    return aasx_reader.reader.open_part(part_name).read()
            else:
                _logger.warning("The file with path {} does not find within the AASX Package.".format(file_path))
            return None

    # Methods related to the AAS model
    # --------------------------------
    @staticmethod
    def get_configuration_file_path_from_standard_submodel():
        """
        This method gets the configuration file defined in the 'Software Nameplate' submodel, used as standard submodel
        for the SMIA software definition.

        Returns:
            str: path inside the AASX package of the configuration file.
        """
        # First, the AAS model need to be read
        object_store = AASModelUtils.read_aas_model_object_store()
        soft_nameplate_config_paths = AASModelUtils.get_elem_of_software_nameplate_by_semantic_id(object_store)
        if soft_nameplate_config_paths is None:
            raise CriticalError(
                "Configuration of SMIA is required and it is not defined within the Software Nameplate submodel.")
        for config_path_elem in soft_nameplate_config_paths:
            sm_elem = config_path_elem.get_sm_element_by_semantic_id(
                AASModelInfo.SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_TYPE)
            if (sm_elem is not None) and (sm_elem.value == 'initial configuration'):
                return config_path_elem.get_sm_element_by_semantic_id(
                    AASModelInfo.SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_URI).value
        return None

    @staticmethod
    def get_elem_of_software_nameplate_by_semantic_id(object_store):
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

    @staticmethod
    async def get_key_type_by_string(key_type_string):
        """
        This method gets the KeyType defined in BaSyx SDK related to the given string.

        Args:
            key_type_string (str): string of the desired KeyType.

        Returns:
            basyx.aas.model.KeyTypes: object of the KeyType defined in BaSyx.
        """
        try:
            return getattr(basyx.aas.model.KeyTypes, key_type_string)
        except AttributeError as e:
            _logger.error(e)
            raise AASModelReadingError("The KeyType with string {} does not exist in the AAS model defined"
                                       " types".format(key_type_string), sme_class=None, reason='KeyTypeAttributeError')

    @staticmethod
    async def get_model_type_by_key_type(key_type):
        """
        This method gets the AAS model class by a given KeyType defined in BaSyx SDK.

        Args:
            key_type (basyx.aas.model.KeyTypes): desired KeyType.

        Returns:
            object of the AAS model class.
        """
        for model_class, key_type_class in basyx.aas.model.KEY_TYPES_CLASSES.items():
            if key_type_class == key_type:
                return model_class
        return None

    @staticmethod
    async def create_aas_reference_object(reference_type, keys_dict=None, external_ref=None):
        """
        This method creates the AAS BaSyx Reference Python object. Depending on the reference type to create (ModelReference or ExternalReference), some information is required. If a Reference cannot be created, it returns None.

        Args:
            reference_type (str): type of the reference to be created (ModelReference or ExternalReference).
            keys_dict (list): if ModelReference is selected, the required keys information in form of a JSON array.
            external_ref (str): if ExternalReference is selected, the required globally unique identifier.

        Returns:
           basyx.aas.model.Reference: BaSyx Python object of the AAS Reference.
        """
        ref_object = None
        if 'ModelReference' == reference_type:
            keys = ()
            last_type = None
            for key in keys_dict:
                basyx_key_type = await AASModelUtils.get_key_type_by_string(key['type'])
                keys += (model.Key(basyx_key_type, key['value']),)
                last_type = basyx_key_type
            ref_object = basyx.aas.model.ModelReference(
                key=keys, type_=await AASModelUtils.get_model_type_by_key_type(last_type))

        elif 'ExternalReference' == reference_type:
            ref_object = model.ExternalReference((model.Key(type_=model.KeyTypes.GLOBAL_REFERENCE,
                                                            value=external_ref),))
        return ref_object


class AASModelInfo:
    """This class contains the information related to AAS model."""
    SEMANTICID_SOFTWARE_NAMEPLATE_SUBMODEL = 'https://admin-shell.io/idta/SoftwareNameplate/1/0'
    SEMANTICID_SOFTWARE_NAMEPLATE_INSTANCE_NAME = ('https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate'
                                              '/SoftwareNameplateInstance/InstanceName')
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_PATHS = ('https://admin-shell.io/idta/SoftwareNameplate/1/0'
                                                   '/SoftwareNameplate/SoftwareNameplateInstance/ConfigurationPaths')
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_TYPE = ('https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate'
                                                  '/SoftwareNameplateInstance/ConfigurationType')
    SEMANTIC_ID_SOFTWARE_NAMEPLATE_CONFIG_URI = ('https://admin-shell.io/idta/SoftwareNameplate/1/0/SoftwareNameplate'
                                                 '/SoftwareNameplateInstance/ConfigurationURI')

    # TODO pasar aqui todos los IDs requeridos en el AAS (p.e el de AID submodel)
