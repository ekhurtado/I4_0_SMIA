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
    svc_standard_acl_template_cfp = GeneralUtils.create_acl_template(performative='CallForProposal',
                                                                     ontology='SvcRequest')
    svc_standard_acl_template_inform = GeneralUtils.create_acl_template(performative='Inform',
                                                                     ontology='SvcRequest')
    # The template for the service requests is the combination of the different possibilities
    SVC_STANDARD_ACL_TEMPLATE = (svc_standard_acl_template_cfp | svc_standard_acl_template_inform)


    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    NEG_STANDARD_ACL_TEMPLATE_CFP = GeneralUtils.create_acl_template(performative='CallForProposal',
                                                                     ontology='negotiation')
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE = GeneralUtils.create_acl_template(performative='Propose',
                                                                     ontology='negotiation')
    NEG_STANDARD_ACL_TEMPLATE_FAILURE = GeneralUtils.create_acl_template(performative='Failure',
                                                                         ontology='negotiation')
    NEG_STANDARD_ACL_TEMPLATE_INFORM = GeneralUtils.create_acl_template(performative='Inform',
                                                                         ontology='negotiation')
    NEG_STANDARD_ACL_TEMPLATE = (NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_PROPOSE
                                 | NEG_STANDARD_ACL_TEMPLATE_FAILURE | NEG_STANDARD_ACL_TEMPLATE_INFORM)

