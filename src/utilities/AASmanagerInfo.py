from utilities.FIPAACLInfo import FIPAACLInfo
from utilities.GeneralUtils import GeneralUtils


class AASmanagerInfo:
    """This class contains the general information about the AAS Manager."""

    # Variables related to states of the FSM
    # --------------------------------------
    BOOTING_STATE_NAME = 'BOOTING'
    RUNNING_STATE_NAME = 'RUNNING'
    STOPPING_STATE_NAME = 'STOPPING'
    IDLE_STATE_NAME = 'IDLE'

    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    # TODO finalizar con el plantilla estandar final decidida para la comunicacion entre agentes
    SVC_STANDARD_ACL_TEMPLATE_CFP = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
                                                                     ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    SVC_STANDARD_ACL_TEMPLATE_INFORM = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                                        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    SVC_STANDARD_ACL_TEMPLATE_QUERY_IF = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF,
                                                                        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)
    # The template for the service requests is the combination of the different possibilities
    SVC_STANDARD_ACL_TEMPLATE = (SVC_STANDARD_ACL_TEMPLATE_CFP | SVC_STANDARD_ACL_TEMPLATE_INFORM
                                 | SVC_STANDARD_ACL_TEMPLATE_QUERY_IF)

    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    NEG_STANDARD_ACL_TEMPLATE_CFP = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
                                                                     ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE,
                                                                         ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_FAILURE = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE,
                                                                         ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE_INFORM = GeneralUtils.create_acl_template(performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                                        ontology=FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION)
    NEG_STANDARD_ACL_TEMPLATE = (NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_PROPOSE
                                 | NEG_STANDARD_ACL_TEMPLATE_FAILURE | NEG_STANDARD_ACL_TEMPLATE_INFORM)
