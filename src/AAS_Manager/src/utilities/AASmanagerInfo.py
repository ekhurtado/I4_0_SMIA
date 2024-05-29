from spade.template import Template


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
    SVC_STANDARD_ACL_TEMPLATE_ONT = Template()
    SVC_STANDARD_ACL_TEMPLATE_ONT.set_metadata("ontology", "SvcRequest")

    SVC_STANDARD_ACL_TEMPLATE_INFORM = SVC_STANDARD_ACL_TEMPLATE_ONT
    SVC_STANDARD_ACL_TEMPLATE_INFORM.set_metadata("performative", "Inform")
    SVC_STANDARD_ACL_TEMPLATE_CFP = SVC_STANDARD_ACL_TEMPLATE_ONT
    SVC_STANDARD_ACL_TEMPLATE_CFP.set_metadata("performative", "CallForProposal")
    # The template for the service requests is the combination of the different possibilities
    SVC_STANDARD_ACL_TEMPLATE = (SVC_STANDARD_ACL_TEMPLATE_INFORM | SVC_STANDARD_ACL_TEMPLATE_CFP)


    # Object of the standard template for service requests through ACL messages
    # -------------------------------------------------------------------------
    NEG_STANDARD_ACL_TEMPLATE_ONT = Template()  # the basis of the template
    NEG_STANDARD_ACL_TEMPLATE_ONT.set_metadata("ontology", "negotiation")

    NEG_STANDARD_ACL_TEMPLATE_CFP = NEG_STANDARD_ACL_TEMPLATE_ONT   # template for CFP messages
    NEG_STANDARD_ACL_TEMPLATE_CFP.set_metadata("performative", "CallForProposal")
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_PROPOSE.set_metadata("performative", "Propose")
    NEG_STANDARD_ACL_TEMPLATE_FAILURE = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_FAILURE.set_metadata("performative", "Failure")
    NEG_STANDARD_ACL_TEMPLATE_INFORM = NEG_STANDARD_ACL_TEMPLATE_ONT
    NEG_STANDARD_ACL_TEMPLATE_INFORM.set_metadata("performative", "Inform")
    # The template for the negotiation is the combination of the different possibilities
    NEG_STANDARD_ACL_TEMPLATE = (NEG_STANDARD_ACL_TEMPLATE_CFP | NEG_STANDARD_ACL_TEMPLATE_PROPOSE | NEG_STANDARD_ACL_TEMPLATE_FAILURE | NEG_STANDARD_ACL_TEMPLATE_INFORM)