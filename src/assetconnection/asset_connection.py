import abc
import json
import re
from enum import Enum, unique

from jsonpath_ng import parse
from lxml import etree

from logic.exceptions import AssetConnectionError
from utilities.capability_skill_ontology import AssetInterfacesInfo


class AssetConnection(metaclass=abc.ABCMeta):
    """
    This class is an abstract class for all AssetConnections.
    TODO desarrollarlo mas
    """

    @unique
    class ArchitectureStyle(Enum):
        PUBSUB = 0
        CLIENTSERVER = 1
        NOTAPPLICABLE = 2

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.architecture_style: AssetConnection.ArchitectureStyle = AssetConnection.ArchitectureStyle.NOTAPPLICABLE

    @abc.abstractmethod
    async def configure_connection_by_aas_model(self, interface_aas_elem):
        """
        This method configures de Asset Connection using the interface element defined in the AAS model.

        Args:
            interface_aas_elem (basyx.aas.model.SubmodelElement): element of the AAS model with the asset interface information.
        """
        pass

    @abc.abstractmethod
    async def check_asset_connection(self):
        pass

    @abc.abstractmethod
    async def connect_with_asset(self):
        pass

    @abc.abstractmethod
    async def execute_skill_by_asset_service(self, interaction_metadata, skill_params_exposure_elems, skill_input_params= None, skill_output_params=None):
        """
        This method sends a message to the asset and returns the response. The connection of the interface of the asset
        is already configured in 'configure_connection_by_aas_model' method, but the interaction metadata is provided
        in form of a Python object of AAS model (SubmodelElement).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElement): element of the AAS model with all metadata for the interaction with the asset.
            skill_params_exposure_elems (list(basyx.aas.model.SubmodelElement)): submodel elements that exposes all skill parameters.
            skill_input_params (dict): skill input parameters in form of JSON object (None if the skill does not have inputs).
            skill_output_params (dict): skill output parameters in form of JSON object (None if the skill does not have outputs).

        Returns:
            object: response information defined in the interaction metadata.
        """
        pass

    @abc.abstractmethod
    async def execute_asset_service(self, interaction_metadata, service_data=None):
        """
        This method sends a message to the asset and returns the response. The connection of the interface of the asset
        is already configured in 'configure_connection_by_aas_model' method, but the interaction metadata is provided
        in form of a Python object of AAS model (SubmodelElement).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElement): element of the AAS model with all metadata for the interaction with the asset.
            service_data: object with the data of the service

        Returns:
            object: response information defined in the interaction metadata.
        """
        pass

    @abc.abstractmethod
    async def receive_msg_from_asset(self):
        pass

    # -----------------------------------------------------------------
    # Useful methods for the processes prior to connection to the asset
    # -----------------------------------------------------------------
    async def check_interaction_metadata(cls, interaction_metadata):
        # First, it is checked that the metadata SMC offered is within the Submodel 'AssetInterfacesDescription'.
        parent_submodel = interaction_metadata.get_parent_submodel()
        if not parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            raise AssetConnectionError("The interaction_metadata object is invalid because it is not within"
                                       " the required submodel", "invalid interaction metadata",
                                       "Interaction_metadata is not within the required submodel")
        # Then, if required submodel elements are missing is checked
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        if not forms_elem:
            raise AssetConnectionError("The asset service cannot be executed because the given "
                                       "interaction_metadata object does not have required 'forms' element",
                                       "missing submodel element",
                                       "Interaction_metadata does not have required 'forms' element")
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        if not forms_elem:
            raise AssetConnectionError("The asset service cannot be executed because the given "
                                       "interaction_metadata object does not have required 'forms' element",
                                       "missing submodel element",
                                       "Interaction_metadata does not have required 'forms' element")

    # --------------------------------------------------------
    # Useful methods to extract information from asset message
    # --------------------------------------------------------
    @classmethod
    async def extract_information_with_data_query(cls, content_type, content_data, query):
        """
        This method extracts the information of the content using the query defined in the interface element.

        Args:
            content_type (str): format of the content.
            content_data: data of the content.
            query (str): query to extract information from the content.

        Returns:
             object: extracted information (result of the query in the given data).
        """
        if 'application/json' in content_type:
            return cls.extract_from_json(content_data, query)
        elif 'application/xml' in content_type:
            return cls.extract_from_xml(content_data, query)
        elif ('text/plain' in content_type) or ('application/x-www-form-urlencoded' in content_type):
            return cls.extract_from_string(content_data, query)
        else:
            raise ValueError(f'Unsupported Content-Type: {content_type}')

    @classmethod
    async def transform_data_by_type(cls, content_data, data_type):
        """
        This method transforms the data by its type.

        Args:
            content_data: data of the content to be transformed.
            data_type: type of the data.

        Returns:
            object: transformed data.
        """
        match data_type:
            case 'string':
                return str(content_data)
            case 'number':
                return float(content_data)
            case 'integer':
                return int(content_data)
            case 'boolean':
                return bool(content_data)
            case _:
                return content_data

    @classmethod
    def extract_from_json(cls, data, query):
        jsonpath_expr = parse(query)
        extracted_data = [match.value for match in jsonpath_expr.find(json.loads(data))]
        return extracted_data[0] if len(extracted_data) == 1 else extracted_data

    @classmethod
    def extract_from_xml(cls, data, query):
        root = etree.fromstring(data)
        extracted_data = root.xpath(query)
        return extracted_data[0] if len(extracted_data) == 1 else extracted_data

    @classmethod
    def extract_from_string(cls, data, query):
        regex_pattern = re.compile(query)
        extracted_data = regex_pattern.findall(data)
        return extracted_data[0] if len(extracted_data)==1 else extracted_data
