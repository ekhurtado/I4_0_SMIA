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
    neg_standard_acl_template_cfp = GeneralUtils.create_acl_template(performative='CallForProposal',
                                                                     ontology='negotiation')
    neg_standard_acl_template_propose = GeneralUtils.create_acl_template(performative='Propose',
                                                                     ontology='negotiation')
    neg_standard_acl_template_failure = GeneralUtils.create_acl_template(performative='Failure',
                                                                         ontology='negotiation')
    neg_standard_acl_template_inform = GeneralUtils.create_acl_template(performative='Inform',
                                                                         ontology='negotiation')
    NEG_STANDARD_ACL_TEMPLATE = (neg_standard_acl_template_cfp | neg_standard_acl_template_propose
                                 | neg_standard_acl_template_failure | neg_standard_acl_template_inform)

