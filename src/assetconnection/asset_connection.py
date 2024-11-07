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

    # ------------------------------------------------------------
    # Useful methods for the configuration of the asset connection
    # ------------------------------------------------------------
    @classmethod
    async def check_interface_element(cls, interface_elem):
        # First, it is checked that the Interface element offered is within the Submodel 'AssetInterfacesDescription'.
        parent_submodel = interface_elem.get_parent_submodel()
        if not parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            raise AssetConnectionError("The Interface element object is invalid because it is not within"
                                       " the required submodel", "invalid interface element",
                                       "Interface element is not within the required submodel")
        # The semanticID of the Interface element is also checked
        if not interface_elem.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACE):
            raise AssetConnectionError("The Interface element object is invalid because it does not have"
                                       " the required semanticID", "invalid interface element",
                                       "Interface element does not have the required semanticID")
        # Then, if required submodel elements are missing is checked
        await cls.check_submodel_element_exist_by_semantic_id(interface_elem, 'title',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        await cls.check_submodel_element_exist_by_semantic_id(interface_elem, 'EndpointMetadata',
                                                              AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)
        await cls.check_submodel_element_exist_by_semantic_id(interface_elem, 'InteractionMetadata',
                                                              AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
        # TODO comprobar que no haya mas atributos requeridos

    @classmethod
    async def check_endpoint_metadata(cls, endpoint_metadata):
        """
        This method checks if the given endpointMetadata object is valid (if it is within the correct submodel and if
        it has all required attributes).

        Args:
            endpoint_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of endpointMetadata.
        """
        # First, it is checked that the metadata SMC offered is within the Submodel 'AssetInterfacesDescription'.
        parent_submodel = endpoint_metadata.get_parent_submodel()
        if not parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            raise AssetConnectionError("The EndpointMetadata object is invalid because it is not within"
                                       " the required submodel", "invalid endpoint metadata",
                                       "EndpointMetadata is not within the required submodel")
        # Then, if required submodel elements are missing is checked
        await cls.check_submodel_element_exist_by_semantic_id(endpoint_metadata, 'base',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        await cls.check_submodel_element_exist_by_semantic_id(endpoint_metadata, 'contentType',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        await cls.check_submodel_element_exist_by_semantic_id(endpoint_metadata, 'securityDefinitions',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        # TODO comprobar que no haya mas atributos requeridos

    # -----------------------------------------------------------------
    # Useful methods for the processes prior to connection to the asset
    # -----------------------------------------------------------------
    @classmethod
    async def check_interaction_metadata(cls, interaction_metadata):
        """
        This method checks if the given interactionMetadata object is valid (if it is within the correct submodel and if
        it has all required attributes).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
        """
        # First, it is checked that the metadata SMC offered is within the Submodel 'AssetInterfacesDescription'.
        parent_submodel = interaction_metadata.get_parent_submodel()
        if not parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            raise AssetConnectionError("The InteractionMetadata object is invalid because it is not within"
                                       " the required submodel", "invalid interaction metadata",
                                       "InteractionMetadata is not within the required submodel")
        # Then, if required submodel elements are missing is checked
        await cls.check_submodel_element_exist_by_semantic_id(interaction_metadata, 'forms',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        await cls.check_submodel_element_exist_by_semantic_id(
            interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS),
            'href', AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        # TODO comprobar que no haya mas atributos requeridos

    @classmethod
    async def check_submodel_element_exist_by_semantic_id(cls, submodel_elem_col, sm_id_short, semantic_id):
        """
        This method checks if a submodelElement with the given semanticID exists within the given
        SubmodelElementCollection.

        Args:
            submodel_elem_col (basyx.aas.model.SubmodelElementCollection): SubmodelElementCollection where the SubmodelElement has to be found.
            sm_id_short (str): idShort of the SubmodelElement to find.
            semantic_id (str): semantic ID to find the required SubmodelElement.
        """
        elem_to_find = submodel_elem_col.get_sm_element_by_semantic_id(semantic_id)
        if not elem_to_find:
            raise AssetConnectionError(f"The {submodel_elem_col.id_short} object is invalid because the given "
                                       f"object does not have required '{sm_id_short}' element",
                                       "missing submodel element",
                                       f"{submodel_elem_col.id_short} does not have required '{sm_id_short}'")

    # --------------------------------------------------------
    # Useful methods to extract information from asset message
    # --------------------------------------------------------
    @classmethod
    async def get_response_content(cls, interaction_metadata, response_content):
        """
        This method gets the required information from the content of the response message from the asset using the
        interactionMetadata information.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            response_content (str): The content of the response message from the asset in string format.
        """
        # First, if 'dataQuery' attribute is set has to be analyzed
        data_query_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_DATA_QUERY)
        if data_query_elem:
            # The type of the content must be obtained
            forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
            content_type = forms_elem.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE).value
            # The general method for all Asset Connections will be used
            response_content = await cls.extract_information_with_data_query(content_type, response_content,
                                                                             data_query_elem.value)
        # Now, if the type of the interaction element of the interface is added, it needs a transformation of data type
        data_type = interaction_metadata.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_TYPE)
        if data_type:
            return await cls.transform_data_by_type(response_content, data_type.value)
        else:
            return response_content

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
