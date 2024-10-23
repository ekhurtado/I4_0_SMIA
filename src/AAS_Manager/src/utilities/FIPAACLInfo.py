class FIPAACLInfo:
    """
    This class contains the values related to FIPA-ACL standard.
    """

    # Performative values
    FIPA_ACL_PERFORMATIVE_CFP = 'CallForProposal'
    FIPA_ACL_PERFORMATIVE_INFORM = 'Inform'
    FIPA_ACL_PERFORMATIVE_PROPOSE = 'Propose'
    FIPA_ACL_PERFORMATIVE_FAILURE = 'Failure'
    FIPA_ACL_PERFORMATIVE_QUERY_IF = 'Query-If'
    # TODO add more if they are needed

    # Ontology values
    FIPA_ACL_ONTOLOGY_SVC_REQUEST = 'SvcRequest'
    FIPA_ACL_ONTOLOGY_SVC_RESPONSE = 'SvcResponse'
    FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION = 'Negotiation'