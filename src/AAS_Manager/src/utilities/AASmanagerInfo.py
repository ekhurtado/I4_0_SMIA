from copy import copy

from spade.template import Template

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

<<<<<<< HEAD
=======
    NEG_STANDARD_ACL_TEMPLATE_CFP = NEG_STANDARD_ACL_TEMPLATE_ONT  # template for CFP messages
    NEG_STANDARD_ACL_TEMPLATE_CFP.set_metadata("performative", "CallForProposal")
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE.set_metadata("performative", "Propose")
    NEG_STANDARD_ACL_TEMPLATE_FAILURE = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_FAILURE.set_metadata("performative", "Failure")
    NEG_STANDARD_ACL_TEMPLATE_INFORM = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_INFORM.set_metadata("performative", "Inform")
    # The template for the negotiation is the combination of the different possibilities
    NEG_STANDARD_ACL_TEMPLATE = (
                NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_PROPOSE | NEG_STANDARD_ACL_TEMPLATE_FAILURE | NEG_STANDARD_ACL_TEMPLATE_INFORM)
>>>>>>> bef2e4cd69b773fced98c40691a08b0385784d8c
