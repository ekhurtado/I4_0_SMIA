import logging

import aiohttp
from aiohttp import ClientConnectorError, ClientConnectionError
from basyx.aas.util import traversal

from smia.assetconnection.asset_connection import AssetConnection
from smia.logic.exceptions import AssetConnectionError
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HTTPAssetConnection(AssetConnection):
    """
    This class implements the asset connection for HTTP protocol.
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.CLIENTSERVER

        # Other data
        self.interface_title = None
        self.base = None
        self.endpoint_metadata_elem = None
        self.security_scheme_elem = None

        # Data of each request
        self.request_uri = None
        self.request_headers = {}
        self.request_params = None
        self.request_method = None
        self.request_body = None

    async def configure_connection_by_aas_model(self, interface_aas_elem):

        # The Interface element need to be checked
        await self.check_interface_element(interface_aas_elem)

        # Vamos a conseguir los datos necesarios del modelo AAS para configurar la conexion HTTP
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        # La informacion general de la conexion con el activo se define en el SMC 'EndpointMetadata'
        self.endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)

        # The endpointMetadata element need to be checked
        await self.check_endpoint_metadata()

        self.base = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        content_type_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        if content_type_elem is not None:
            self.request_headers['Content-Type'] = content_type_elem.value

        security_definitions_elem = self.endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        if security_definitions_elem is not None:
            self.security_scheme_elem = security_definitions_elem.value
        # TODO: pensar como añadir el resto , p.e. tema de seguridad o autentificacion (bearer).
        #  De momento se ha dejado sin seguridad (nosec_sc)

        # The InteractionMetadata elements also need to be checked
        interaction_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
        for interaction_metadata_type in interaction_metadata_elem:
            # Interaction metadata can be properties, actions or events
            for interaction_element in interaction_metadata_type:
                await self.check_interaction_metadata(interaction_element)

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data = None):
        if interaction_metadata is None:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "InteractionMetadata object is None", "invalid method parameter",
                                       "InteractionMetadata object is None")

        await self.extract_general_interaction_metadata(interaction_metadata)

        # Then, the data of the skill is added in the required field. To do that, the 'SkillParameterExposedThrough'
        # relationship should be obtained, which indicates where the parameter data should be added
        if service_input_data is not None:
            await self.add_asset_service_data(interaction_metadata, service_input_data)

        # At this point, the HTTP request is performed
        http_response = await self.send_http_request()
        if http_response:
            if http_response.status != 200:
                _logger.warning("The HTTP request has not been answered correctly. "
                                "Response: {}".format(await http_response.text()))
            return await self.get_response_content(interaction_metadata, await http_response.text())
        return None

    async def receive_msg_from_asset(self):
        pass

    # ---------------------
    # HTTP specific methods
    # ---------------------
    async def extract_general_interaction_metadata(self, interaction_metadata):
        """
        This method extracts the general interaction information from the interaction metadata object. Since this is an
        HTTP Asset Connection, information about the URI, headers and method name is obtained. All information is saved
        in the global variables of the class.

        Args:
             interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
        """
        # The interaction_metada element will be an SMC of the HTTP interface.
        await self.check_interaction_metadata(interaction_metadata)

        # First, the full URI of the HTTP request is obtained.
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        await self.get_complete_request_uri(forms_elem)

        # Then, headers are obtained
        await self.get_headers(forms_elem)

        # Eventually, the method name is also obtained
        await self.get_method_name(forms_elem)

    async def get_complete_request_uri(self, forms_elem):
        """
        This method gets the complete request URI from the forms element within the InteractionMetadata element. The
        information is saved in the global variables of the class.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.
        """
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        if ('http://' in href_elem.value) or ('https://' in href_elem.value):
            self.request_uri = href_elem.value
        else:
            self.request_uri = self.base.value + href_elem.value

    async def get_headers(self, forms_elem):
        """
        This method gets the headers for the request from the forms element within the InteractionMetadata element. The
        information is saved in the global variables of the class.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.
        """
        headers_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_HEADERS)
        if not headers_elem:
            # This Interaction element does not have headers
            return
        # The old request headers are updated
        self.request_headers = {}
        for header_smc in headers_elem:
            field_name = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_NAME).value
            field_value = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_VALUE).value
            self.request_headers[field_name] = field_value

    async def get_method_name(self, forms_elem):
        """
        This method gets the method name of the request from the forms element within the InteractionMetadata element.
        The information is saved in the global variables of the class.

        Args:
            forms_elem (basyx.aas.model.submodelElementCollection): SubmodelElement of forms within InteractionMetadata.
        """
        method_name_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_METHOD_NAME)
        if method_name_elem:
            self.request_method = method_name_elem.value

    async def add_asset_service_data(self, interaction_metadata, service_input_data):
        """
        This method adds the required data of the asset service, using the skill params information (exposure element
        and skill input data). The information is saved in the global variables of the class.

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElementCollection): SubmodelElement of interactionMetadata.
            service_input_data (dict): dictionary containing the input data of the asset service.
        """
        for submodel_element in traversal.walk_submodel(interaction_metadata):
            # TODO AQUI QUEDA COMPROBAR QUE EXISTE EL SEMANTICID PARA DETERMINAR DONDE HAY QUE AÑADIR LOS DATOS (hay que
            #  pensar el nombre, pero algo estilo 'InputDataLocation')
            # TODO DE MOMENTO SE DEJA CON SOLO PARAMS DE HTTP
            if submodel_element.check_semantic_id_exist(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAMS):
                request_params = {}
                param_name = submodel_element.get_sm_element_by_semantic_id(
                    HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAM_NAME).value
                request_params[param_name] = service_input_data[param_name]
                self.request_params = request_params
                break
            # TODO pensar como se haria si no hay que añadirlo en los parametros (p.e. en el body)
            # TODO PENSAR EN MAS OPCIONES DE AÑADIR LOS PARAMETROS (P.E. EN LA URI)
        else:
            AssetConnectionError("The interface need input data but there is no location defined for it.",
                                 'Invalid interface SubmodelElement', 'MissingAttribute')


    async def send_http_request(self):
        """
        This method sends the required HTTP request message to the asset. All the required information is obtained from
         the global variables of the class.

        Returns:
            aiohttp.ClientResponse: response of the asset.
        """
        async with aiohttp.ClientSession(headers=self.request_headers) as session:
            try:
                # async with session.get(url=self.request_uri, params=self.request_params) as resp:
                #     await resp.text()   # The content is saved in ClientResponse object
                #     return resp
                if self.request_method == 'GET':
                    response = await session.get(url=self.request_uri, params=self.request_params)
                elif self.request_method == 'DELETE':
                    # TODO a probar
                    response = await session.delete(url=self.request_uri, params=self.request_params)
                elif self.request_method == 'HEAD':
                    # TODO a probar
                    response = await session.head(url=self.request_uri, params=self.request_params)
                elif self.request_method == 'PATCH':
                    # TODO a probar
                    response = await session.patch(url=self.request_uri, params=self.request_params)
                elif self.request_method == 'POST':
                    # TODO a probar
                    response = await session.post(url=self.request_uri, params=self.request_params)
                elif self.request_method == 'PUT':
                    # TODO a probar
                    response = await session.put(url=self.request_uri, params=self.request_params)
                await response.text()   # The content is saved in ClientResponse object
                return response
            except (ClientConnectorError, ClientConnectionError) as connection_error:
                if isinstance(connection_error, ClientConnectorError):
                    raise AssetConnectionError("The request to asset timed out, so the asset is not available.",
                                               "AssetConnectTimeout", "The asset connection timed out")
                if isinstance(connection_error, ClientConnectionError):
                    raise AssetConnectionError("The connection with the asset has raised an exception.",
                                               connection_error.__class__.__name__, connection_error.args[0].reason)


class HTTPAssetInterfaceSemantics:
    """
    This class contains the specific semanticIDs of HTTP interfaces.
    """

    SEMANTICID_HTTP_INTERFACE_METHOD_NAME = 'https://www.w3.org/2011/http#methodName'
    SEMANTICID_HTTP_INTERFACE_HEADERS = 'https://www.w3.org/2011/http#headers'
    SEMANTICID_HTTP_INTERFACE_FIELD_NAME = 'https://www.w3.org/2011/http#fieldName'
    SEMANTICID_HTTP_INTERFACE_FIELD_VALUE = 'https://www.w3.org/2011/http#fieldValue'

    # TODO nuevo
    SEMANTICID_HTTP_INTERFACE_PARAMS = 'https://www.w3.org/2011/http#params'
    SEMANTICID_HTTP_INTERFACE_PARAM_NAME = 'https://www.w3.org/2011/http#paramName'
    SEMANTICID_HTTP_INTERFACE_PARAM_VALUE = 'https://www.w3.org/2011/http#paramValue'
