from utilities.fipa_acl_info import FIPAACLInfo
from utilities.general_utils import GeneralUtils


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
    NEG_STANDARD_ACL_TEMPLATE = (NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_PROPOSE
                                 | NEG_STANDARD_ACL_TEMPLATE_FAILURE | NEG_STANDARD_ACL_TEMPLATE_INFORM)
