from smia.utilities.fipa_acl_info import FIPAACLInfo
from smia.utilities.general_utils import GeneralUtils


class SMIAInteractionInfo:
    """This class contains the information about the SMIA interactions."""

    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    # TODO finalizar con el plantilla estandar final decidida para la comunicacion entre agentes
    SVC_STANDARD_ACL_TEMPLATE_CFP = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    SVC_STANDARD_ACL_TEMPLATE_INFORM = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    SVC_STANDARD_ACL_TEMPLATE_REQUEST = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    SVC_STANDARD_ACL_TEMPLATE_QUERY_IF = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    # TODO OJO! De momento añado las plantillas de capacidades tambien, pero la idea es hacer dos behaviour diferentes
    CAP_STANDARD_ACL_TEMPLATE_REQUEST = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_CAPABILITY_REQUEST)
    CAP_STANDARD_ACL_TEMPLATE_QUERY_IF = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_CAPABILITY_CHECKING)
    # The template for the service requests is the combination of the different possibilities
    SVC_STANDARD_ACL_TEMPLATE = (SVC_STANDARD_ACL_TEMPLATE_CFP | SVC_STANDARD_ACL_TEMPLATE_INFORM
                                 | SVC_STANDARD_ACL_TEMPLATE_REQUEST | SVC_STANDARD_ACL_TEMPLATE_QUERY_IF
                                 | CAP_STANDARD_ACL_TEMPLATE_REQUEST | CAP_STANDARD_ACL_TEMPLATE_QUERY_IF  # TODO OJO, estos son los dos las capacidades
                                 )

    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    NEG_STANDARD_ACL_TEMPLATE_CFP = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_FAILURE = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_INFORM = GeneralUtils.create_acl_template(
        performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    # The template for the negotiations is the combination of the different possibilities
    NEG_STANDARD_ACL_TEMPLATE = (NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_FAILURE |
                                 NEG_STANDARD_ACL_TEMPLATE_INFORM)


class AssetInterfacesInfo:
    """This class contains the information related to Asset Interfaces submodel (AssetInterfacesDescription submodel of
    IDTA)."""

    # SemanticIDs of Asset Interfaces
    SEMANTICID_INTERFACES_SUBMODEL = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Submodel'
    SEMANTICID_INTERFACE = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface'
    SEMANTICID_ENDPOINT_METADATA = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata'
    SEMANTICID_INTERACTION_METADATA = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata'
    SEMANTICID_VALUE_SEMANTICS = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/valueSemantics'

    # SemanticIDs of W3 2011
    SUPPL_SEMANTICID_HTTP = 'http://www.w3.org/2011/http'
    SEMANTICID_INTERFACE_INTERACTION_TYPE = 'https://www.w3.org/1999/02/22-rdf-syntax-ns#type'

    # SemanticIDs of Web of Things (WoT) ontology
    SEMANTICID_INTERFACE_TITLE = 'https://www.w3.org/2019/wot/td#title'
    SEMANTICID_INTERFACE_BASE = 'https://www.w3.org/2019/wot/td#baseURI'
    SEMANTICID_INTERFACE_CONTENT_TYPE = 'https://www.w3.org/2019/wot/hypermedia#forContentType'

    SEMANTICID_INTERFACE_SECURITY_DEFINITIONS = 'https://www.w3.org/2019/wot/td#definesSecurityScheme'
    SEMANTICID_INTERFACE_NO_SECURITY_SCHEME = 'https://www.w3.org/2019/wot/security#NoSecurityScheme'

    SEMANTICID_INTERFACE_PROPERTY = 'https://www.w3.org/2019/wot/td#PropertyAffordance'
    SEMANTICID_INTERFACE_ACTION = 'https://www.w3.org/2019/wot/td#ActionAffordance'

    SEMANTICID_INTERFACE_FORMS = 'https://www.w3.org/2019/wot/td#hasForm'
    SEMANTICID_INTERFACE_HREF = 'https://www.w3.org/2019/wot/hypermedia#hasTarget'

    # TODO NUEVO
    SEMANTICID_INTERFACE_INTERACTION_DATA_QUERY = 'https://admin-shell.io/idta/AssetInterfacesDescription/1/0/dataQuery'  # TODO CUIDADO, ESTE ES NUEVO, PENSAR COMO SERIA. Se ha pensado asociar este ID con un apartado de la interfaz donde se añadirá el query para extraer la informacion de la respuesta del activo (esta query debera ir en relacion con el tipo de contenido, p.e. JSONata o JSONPath para respuestas JSON)
