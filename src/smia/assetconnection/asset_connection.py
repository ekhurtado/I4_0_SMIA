import abc
import json
import re
from enum import Enum, unique

from jsonpath_ng import parse
from lxml import etree

from smia.logic.exceptions import AssetConnectionError
from smia.utilities.smia_info import AssetInterfacesInfo


class AssetConnection(metaclass=abc.ABCMeta):
    """
    This class is an abstract class for all AssetConnections.
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

        # General attributes for all Asset Connections
        self.interface_title = None
        self.endpoint_metadata_elem = None

    @abc.abstractmethod
    async def configure_connection_by_aas_model(self, interface_aas_elem):
        """
        This method configures the Asset Connection using the interface element defined in the AAS model.

        Args:
            interface_aas_elem (basyx.aas.model.SubmodelElement): element of the AAS model with the asset interface information.
        """
        pass

    @abc.abstractmethod
    async def check_asset_connection(self):
        """
        This method checks the Asset Connection.
        """
        pass

    @abc.abstractmethod
    async def connect_with_asset(self):
        """
        This method performs the connection process to the Asset Connection.
        """
        pass

    @abc.abstractmethod
    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        """
        This method sends a message to the asset and returns the response. The connection of the interface of the asset
        is already configured in 'configure_connection_by_aas_model' method, but the interaction metadata is provided
        in form of a Python object of AAS model (SubmodelElement).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElement): element of the AAS model with all metadata for the interaction with the asset.
            service_input_data: object with the input data of the service

        Returns:
            object: response information defined in the interaction metadata.
        """
        pass

    @abc.abstractmethod
    async def receive_msg_from_asset(self):
        """
        This method receives a message from the asset through the Asset Connection.
        """
        pass

    # ------------------------------------------------------------
    # Useful methods for the configuration of the asset connection
    # ------------------------------------------------------------
    @classmethod
    async def check_interface_element(cls, interface_elem):
        """
        This method checks the given interface AAS element from the 'AssetInterfacesDescription' submodel. In case of
        identifying any error it raises an 'AssetConnectionError' exception.

        Args:
            interface_elem(basyx.aas.model.SubmodelElementCollection): SubmodelElement of AAS interface SubmodelElement.
        """
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


    async def check_endpoint_metadata(self):
        """
        This method checks if the given endpointMetadata object is valid (if it is within the correct submodel and if
        it has all required attributes).
        """
        # The endpointMetadata object is initialized in 'configure_connection_by_aas_model' method, but if it is None,
        # then the Interface Element is invalid
        if self.endpoint_metadata_elem is None:
            raise AssetConnectionError("The Interface Element object is invalid because it does not have the"
                                       " EndpointMetadata", "invalid interface",
                                       "EndpointMetadata is not within the Interface Element")

        # It is checked that the metadata SMC offered is within the Submodel 'AssetInterfacesDescription'.
        parent_submodel = self.endpoint_metadata_elem.get_parent_submodel()
        if not parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            raise AssetConnectionError("The EndpointMetadata object is invalid because it is not within"
                                       " the required submodel", "invalid endpoint metadata",
                                       "EndpointMetadata is not within the required submodel")
        # Then, if required submodel elements are missing is checked
        await self.check_submodel_element_exist_by_semantic_id(self.endpoint_metadata_elem, 'base',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        await self.check_submodel_element_exist_by_semantic_id(self.endpoint_metadata_elem, 'contentType',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        await self.check_submodel_element_exist_by_semantic_id(self.endpoint_metadata_elem, 'securityDefinitions',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        # TODO comprobar que no haya mas atributos requeridos

    # -----------------------------------------------------------------
    # Useful methods for the processes prior to connection to the asset
    # -----------------------------------------------------------------
    async def check_interaction_metadata(self, interaction_metadata):
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
        await self.check_submodel_element_exist_by_semantic_id(interaction_metadata, 'forms',
                                                              AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        await self.check_submodel_element_exist_by_semantic_id(
            interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS),
            'href', AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        # TODO comprobar que no haya mas atributos requeridos

        # If dataQuery is defined, the dataQueryType must be appropriate to the content type of the interaction metadata
        data_query_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_DATA_QUERY)
        if data_query_elem is not None:
            content_type_elem = await self.get_interaction_metadata_content_type(interaction_metadata)
            await self.check_data_query_type(interaction_metadata.id_short, content_type_elem.value, data_query_elem)

    async def get_interaction_metadata_content_type(self, interaction_metadata):
        """
        This method gets the content type of the interaction metadata. If it is not defined, the type defined in the
        EndpointMetadata will be
        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): interactionMetadata Python object.

        Returns:
            basyx.aas.model.SubmodelElementElement: Python object of the content type
        """
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        content_type_elem = forms_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        if content_type_elem is None:
            # If content type is not defined in the interactionMetada, it should be got from the EndpointMetadata
            content_type_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        return content_type_elem

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
    async def check_data_query_type(cls, interaction_elem_name, content_type, data_query_elem):
        """
        This method checks if the data query of the interaction metadata element is valid. It is valid when the type
        specified in the data query is the appropriate for the content type of the element.

        Args:
            interaction_elem_name (str): name of the interaction element to show in case of invalid data query.
            content_type (str): type of the content of the interaction metadata element.
            data_query_elem (basyx.aas.model.SubmodelElementCollection): SubmodelElement of dataQuery.

        Returns:

        """
        if data_query_elem is not None:
            data_query_type = data_query_elem.get_qualifier_value_by_type('DataQueryType')
            if (content_type == 'application/json' and data_query_type != 'jsonpath') or \
                (content_type == 'text/plain' and data_query_type != 'regex') or \
                (content_type == 'application/x-www-form-urlencoded' and data_query_type != 'regex') or \
                (content_type == 'application/xml' and data_query_type != 'xpath'):
                        raise AssetConnectionError("The dataQuery type of interaction metadata {} is not valid for "
                                                   "content type {}".format(interaction_elem_name, content_type),
                                                   'invalid data query', "{} does no have a valid data"
                                                                         " query".format(interaction_elem_name))



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
        if data_query_elem is not None:
            # The type of the content must be obtained
            forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
            content_type = forms_elem.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE).value
            # The general method for all Asset Connections will be used
            response_content = await cls.extract_information_with_data_query(content_type, response_content,
                                                                             data_query_elem.value)
            return response_content
        # If the type of the interaction element of the interface is added, it needs a transformation of data type
        data_type = interaction_metadata.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_TYPE)
        if data_type is not None:
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
            case 'object':
                if isinstance(content_data, str):
                    return json.loads(content_data)
                return content_data
            case _:
                return content_data

    @classmethod
    def extract_from_json(cls, data, query):
        """
        This method extracts the required information from a JSON object. It uses the 'jsonpath-ng' Python package to
        perform the extraction.

        Args:
            data (dict): JSON object with the given data.
            query (str): query to extract information from the content. In this case, it has to be a JSONPath expression.

        Returns:
            object: extracted information (result of the query in the given data).
        """
        jsonpath_expr = parse(query)
        extracted_data = [match.value for match in jsonpath_expr.find(json.loads(data))]
        return extracted_data[0] if len(extracted_data) == 1 else extracted_data

    @classmethod
    def extract_from_xml(cls, data, query):
        """
        This method extracts the required information from an XML object. It uses the 'lxml' Python package to
        perform the extraction.

        Args:
            data (str): XML object with the given data in string format.
            query (str): query to extract information from the content. In this case, it has to be a XPath expression.

        Returns:
            object: extracted information (result of the query in the given data).
        """
        root = etree.fromstring(data)
        extracted_data = root.xpath(query)
        return extracted_data[0] if len(extracted_data) == 1 else extracted_data

    @classmethod
    def extract_from_string(cls, data, query):
        """
        This method extracts the required information from a string object. It uses the 're' Python package to
        perform the extraction.

        Args:
            data (str): string object with the given data.
            query (str): query to extract information from the content. In this case, it has to be a Regex expression.

        Returns:
            object: extracted information (result of the query in the given data).
        """
        regex_pattern = re.compile(query)
        extracted_data = regex_pattern.findall(data)
        return extracted_data[0] if len(extracted_data)==1 else extracted_data
