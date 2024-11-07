import json
import logging
import requests
from basyx.aas.util.traversal import walk_submodel
from lxml import etree

from assetconnection.asset_connection import AssetConnection
from logic.exceptions import AssetConnectionError
from utilities.capability_skill_ontology import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HTTPAssetConnection(AssetConnection):
    """
    This class implements the asset connection for HTTP protocol.
    TODO desarrollarlo mas
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.CLIENTSERVER

        # Other data
        self.interface_title = None
        self.base = None
        self.security_scheme_elem = None

        # Data of each request
        self.request_uri = None
        self.request_headers = {}
        self.request_params = None
        self.request_method = None

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        # Vamos a conseguir los datos necesarios del modelo AAS para configurar la conexion HTTP
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_TITLE)
        # La informacion general de la conexion con el activo se define en el SMC 'EndpointMetadata'
        endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_ENDPOINT_METADATA)
        self.base = endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_BASE)
        content_type_elem = endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_CONTENT_TYPE)
        if content_type_elem is not None:
            self.request_headers['Content-Type'] = content_type_elem.value

        security_definitions_elem = endpoint_metadata_elem.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_SECURITY_DEFINITIONS)
        if security_definitions_elem is not None:
            self.security_scheme_elem = security_definitions_elem.value
        # TODO: pensar como añadir el resto , p.e. tema de seguridad o autentificacion (bearer). De momento se ha dejado sin seguridad (nosec_sc)

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_skill_by_asset_service(self, interaction_metadata, skill_params_exposure_elem=None, skill_input_params= None, skill_output_params=None):

        if not interaction_metadata:
            raise AssetConnectionError("The skill cannot be executed by asset service because the given "
                                       "interaction_metadata object is None", "invalid method parameter","Interaction_metadata object is None")

        await self.extract_general_interaction_metadata(interaction_metadata)

        # Then, the data of the skill is added in the required field. To do that, the 'SkillParameterExposedThrough'
        # relationship should be obtained, which indicates where the parameter data should be added
        if skill_input_params:
            await self.add_asset_service_data(skill_params_exposure_elem, skill_input_params)

        # At this point, the HTTP request is performed
        http_response = await self.send_http_request()
        if http_response:
            if http_response.status_code != 200:
                _logger.warning("The HTTP request has not been answered correctly.")
            return await self.get_response_content(interaction_metadata, http_response)
        return None

    async def execute_asset_service(self, interaction_metadata, service_data=None):
        await self.extract_general_interaction_metadata(interaction_metadata)
        # TODO hacer
        pass

    async def receive_msg_from_asset(self):
        pass

    # --------------------
    # Other useful methods
    # --------------------
    async def extract_general_interaction_metadata(self, interaction_metadata):
        # The interaction_metada element will be an SMC of the HTTP interface.
        await self.check_interaction_metadata(interaction_metadata)

        # First, the full URI of the HTTP request is obtained.
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACE_FORMS)
        if not forms_elem:
            raise AssetConnectionError("The asset service cannot be executed because the given "
                                       "interaction_metadata object does not have required 'forms' element",
                                       "missing submodel element","Interaction_metadata does not have required 'forms' element")
        await self.get_complete_request_uri(forms_elem)

        # Then, headers are obtained
        await self.get_headers(forms_elem)

        # Eventually, the method name is also obtained
        await self.get_method_name(forms_elem)

    async def get_complete_request_uri(self, forms_elem):
        href_elem = forms_elem.get_sm_element_by_semantic_id(AssetInterfacesInfo.SEMANTICID_INTERFACE_HREF)
        if ('http://' in href_elem.value) or ('https://' in href_elem.value):
            self.request_uri = href_elem.value
        else:
            self.request_uri = self.base.value + href_elem.value

    async def get_headers(self, forms_elem):
        headers_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_HEADERS)
        request_headers = {}
        for header_smc in headers_elem:
            field_name = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_NAME).value
            field_value = header_smc.get_sm_element_by_semantic_id(
                HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_VALUE).value
            request_headers[field_name] = field_value
        if len(request_headers) != 0:
            self.request_headers.update(request_headers)

    async def get_method_name(self, forms_elem):
        method_name_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_METHOD_NAME)
        self.request_method = method_name_elem.value

    async def add_asset_service_data(self, skill_params_exposure_elem, skill_input_params):
        if skill_params_exposure_elem:
            if skill_params_exposure_elem.check_semantic_id_exist(
                    HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAMS):
                request_params = {}
                for param_smc_elem in skill_params_exposure_elem.value:
                    param_name = param_smc_elem.get_sm_element_by_semantic_id(
                        HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_PARAM_NAME).value
                    # TODO CUIDADO, LOS PARAMETROS SE AÑADEN DE UNO EN UNO DESDE LOS SKILL PARAMS (quizas habria que obligar
                    #  a que los nombres de los skill params sean los mismo que necesita la interfaz, y de esa forma directamente añadirlos)
                    request_params[param_name] = skill_input_params[param_name]
                self.request_params = request_params
            else:
                # TODO pensar como se haria si no hay que añadirlo en los parametros (p.e. en el body)
                print("Interface skill parameters exposure not with HTTP params field")
                # TODO PENSAR EN MAS OPCIONES DE AÑADIR LOS PARAMETROS (P.E. EN LA URI)


    async def send_http_request(self):
        if self.request_method == 'GET':
            return requests.get(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif self.request_method == 'DELETE':
            # TODO a probar
            return requests.delete(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif self.request_method == 'HEAD':
            # TODO a probar
            return requests.head(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif self.request_method == 'PATCH':
            # TODO a probar
            return requests.patch(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif self.request_method == 'POST':
            return requests.post(url=self.request_uri, headers=self.request_headers, data=msg)
        elif self.request_method == 'PUT':
            # TODO a probar
            return requests.put(url=self.request_uri, headers=self.request_headers, params=self.request_params)

    async def get_response_content(self, interaction_metadata, http_response):
        response_content = http_response.text

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
            response_content = await AssetConnection.extract_information_with_data_query(content_type,
                                                                                         response_content,
                                                                                         data_query_elem.value)
        # Now, if the type of the interaction element of the interface is added, it needs a transformation of data type
        data_type = interaction_metadata.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE_INTERACTION_TYPE)
        if data_type:
            return await AssetConnection.transform_data_by_type(response_content, data_type.value)
        else:
            return response_content


class HTTPAssetInterfaceSemantics:

    SEMANTICID_HTTP_INTERFACE_METHOD_NAME = 'https://www.w3.org/2011/http#methodName'
    SEMANTICID_HTTP_INTERFACE_HEADERS = 'https://www.w3.org/2011/http#headers'
    SEMANTICID_HTTP_INTERFACE_FIELD_NAME = 'https://www.w3.org/2011/http#fieldName'
    SEMANTICID_HTTP_INTERFACE_FIELD_VALUE = 'https://www.w3.org/2011/http#fieldValue'

    # TODO nuevo
    SEMANTICID_HTTP_INTERFACE_PARAMS = 'https://www.w3.org/2011/http#params'
    SEMANTICID_HTTP_INTERFACE_PARAM_NAME = 'https://www.w3.org/2011/http#paramName'
    SEMANTICID_HTTP_INTERFACE_PARAM_VALUE = 'https://www.w3.org/2011/http#paramValue'
