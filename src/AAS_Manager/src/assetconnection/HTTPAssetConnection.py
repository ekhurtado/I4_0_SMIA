import json
import logging
import requests
from lxml import etree

from assetconnection.AssetConnection import AssetConnection

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
        self.request_uri = None
        self.request_headers = {}

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        # TODO PROBAR QUE FUNCIONE
        # Vamos a conseguir los datos necesarios del modelo AAS para configurar la conexion HTTP
        self.interface_title = interface_aas_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_TITLE)
        # La informacion general de la conexion con el activo se define en el SMC 'EndpointMetadata'
        endpoint_metadata_elem = interface_aas_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_ENDPOINT_METADATA)
        self.base = endpoint_metadata_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_BASE)
        content_type_elem = endpoint_metadata_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_CONTENT_TYPE)
        if content_type_elem is not None:
            self.request_headers['Content-Type'] = content_type_elem.value
        # TODO: pensar como añadir el resto , p.e. tema de seguridad o autentificacion (bearer)

    async def connect_with_asset(self):
        pass

    async def send_msg_to_asset(self, interaction_metadata, msg):
        # El elemento interaction_metada sera un SMC de la interfaz del HTTP
        if not await self.check_interaction_metadata(interaction_metadata):
            _logger.error("ERROR: el interactionMetadata esta mal")
            return 'ERROR'

        # Primero, conseguimos la URI completa de la peticion HTTP
        forms_elem = interaction_metadata.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FORMS)
        await self.get_complete_request_uri(forms_elem)

        # Luego, conseguimos los headers
        await self.get_headers(forms_elem)

        # Finalmente, ya podemos realizar la peticion HTTP
        http_response = await self.send_http_request(await self.get_method_name(forms_elem), msg)
        if http_response:
            return await self.get_response_content(http_response)
        return None


    async def receive_msg_from_asset(self):
        pass

    # --------------------
    # Other useful methods
    # --------------------
    async def check_interaction_metadata(self, interaction_metadata):
        # TODO de momento solo se comprueba que el SMC de metadatos ofrecido esta dentro del SMC 'InteractionMetadata'
        parent_elem = interaction_metadata.parent
        while not parent_elem.check_semantic_id_exist(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_INTERACTION_METADATA):
            if parent_elem.check_semantic_id_exist('https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Submodel'):
                return False
            else:
                parent_elem = parent_elem.parent
        return True

    async def get_complete_request_uri(self, forms_elem):
        href_elem = forms_elem.get_sm_element_by_semantic_id(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_HREF)
        if ('http://' in href_elem.value) or ('https://' in href_elem.value):
            self.request_uri = href_elem.value
        else:
            _logger.aclinfo("BASE {}, HREF {}, TITLE {}, HEADERS {}".format(self.base, href_elem, self.interface_title, self.request_headers))
            _logger.aclinfo("BASE VALUE {}, HREF VALUE {}".format(self.base.value, href_elem.value))
            self.request_uri = self.base.value + href_elem.value

    async def get_headers(self, forms_elem):
        headers_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_HEADERS)
        request_headers = {}
        for header_smc in headers_elem:
            field_name = header_smc.get_sm_element_by_semantic_id(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_NAME).value
            field_value = header_smc.get_sm_element_by_semantic_id(HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_FIELD_VALUE).value
            request_headers[field_name] = field_value
        if len(request_headers) != 0:
            self.request_headers.update(request_headers)

    async def get_method_name(self, forms_elem):
        method_name_elem = forms_elem.get_sm_element_by_semantic_id(
            HTTPAssetInterfaceSemantics.SEMANTICID_HTTP_INTERFACE_METHOD_NAME)
        return method_name_elem.value

    async def send_http_request(self, request_method, msg):
        if request_method == 'GET':
            return requests.get(url=self.request_uri, headers=self.request_headers, params=msg)
        elif request_method == 'DELETE':
            # TODO a probar
            return requests.delete(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif request_method == 'HEAD':
            # TODO a probar
            return requests.head(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif request_method == 'PATCH':
            # TODO a probar
            return requests.patch(url=self.request_uri, headers=self.request_headers, params=self.request_params)
        elif request_method == 'POST':
            return requests.post(url=self.request_uri, headers=self.request_headers, data=msg)
        elif request_method == 'PUT':
            # TODO a probar
            return requests.put(url=self.request_uri, headers=self.request_headers, params=self.request_params)

    async def get_response_content(self, http_response):
        if 'Accept' in self.request_headers:
            if self.request_headers['Accept'] == 'application/json':
                response_content_json = json.loads(http_response.text)
                return response_content_json['data']
            if self.request_headers['Accept'] == 'text/plain':
                return str(http_response.text)
            if self.request_headers['Accept'] == 'text/html':
                aas_xml_bytes = http_response.text.encode('utf-8')  # fromstring cannot handle strings with an encoding
                response_content_xml = etree.fromstring(aas_xml_bytes)
                # TODO sin probar
                return 'UNTESTED'
        else:
            return None

class HTTPAssetInterfaceSemantics:

    SEMANTICID_HTTP_INTERFACE_TITLE = 'https://www.w3.org/2019/wot/td#title'
    SEMANTICID_HTTP_INTERFACE_BASE = 'https://www.w3.org/2019/wot/td#baseURI'
    SEMANTICID_HTTP_INTERFACE_CONTENT_TYPE = 'https://www.w3.org/2019/wot/hypermedia#forContentType'

    SEMANTICID_HTTP_INTERFACE_ENDPOINT_METADATA = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata'
    SEMANTICID_HTTP_INTERFACE_INTERACTION_METADATA = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata'


    SEMANTICID_HTTP_INTERFACE_PROPERTY = 'https://www.w3.org/2019/wot/td#PropertyAffordance'
    SEMANTICID_HTTP_INTERFACE_ACTION = 'https://www.w3.org/2019/wot/td#ActionAffordance'

    SEMANTICID_HTTP_INTERFACE_FORMS = 'https://www.w3.org/2019/wot/td#hasForm'
    SEMANTICID_HTTP_INTERFACE_HREF = 'https://www.w3.org/2019/wot/hypermedia#hasTarget'
    SEMANTICID_HTTP_INTERFACE_METHOD_NAME = 'https://www.w3.org/2011/http#methodName'
    SEMANTICID_HTTP_INTERFACE_HEADERS = 'https://www.w3.org/2011/http#headers'
    SEMANTICID_HTTP_INTERFACE_FIELD_NAME = 'https://www.w3.org/2011/http#fieldName'
    SEMANTICID_HTTP_INTERFACE_FIELD_VALUE = 'https://www.w3.org/2011/http#fieldValue'

