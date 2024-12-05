class FIPAACLInfo:
    """
    This class contains the values related to FIPA-ACL standard.
    """

    # Performative values
    FIPA_ACL_PERFORMATIVE_CFP = 'CallForProposal'
    FIPA_ACL_PERFORMATIVE_INFORM = 'Inform'
    FIPA_ACL_PERFORMATIVE_REQUEST = 'Request'
    FIPA_ACL_PERFORMATIVE_PROPOSE = 'Propose'
    FIPA_ACL_PERFORMATIVE_FAILURE = 'Failure'
    FIPA_ACL_PERFORMATIVE_QUERY_IF = 'Query-If'
    # TODO add more if they are needed
    # TODO se han añadido estos pero todavia no se utilizan:
    FIPA_ACL_PERFORMATIVE_ACCEPT_PROPOSAL = 'AcceptProposal'
    FIPA_ACL_PERFORMATIVE_REJECT_PROPOSAL = 'RejectProposal'
    FIPA_ACL_PERFORMATIVE_AGREE = 'Agree'
    FIPA_ACL_PERFORMATIVE_CONFIRM = 'Confirm'
    FIPA_ACL_PERFORMATIVE_NOT_UNDERSTOOD = 'NotUnderstood'
    FIPA_ACL_PERFORMATIVE_REFUSE = 'Refuse'

    # Ontology values
    FIPA_ACL_ONTOLOGY_SVC_REQUEST = 'SvcRequest'
    FIPA_ACL_ONTOLOGY_SVC_RESPONSE = 'SvcResponse'
    FIPA_ACL_ONTOLOGY_CAPABILITY_REQUEST = 'CapabilityRequest'
    FIPA_ACL_ONTOLOGY_CAPABILITY_CHECKING = 'CapabilityChecking'
    FIPA_ACL_ONTOLOGY_CAPABILITY_RESPONSE = 'CapabilityResponse'
    FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION = 'Negotiation'


class ACLJSONSchemas:
    """This class contains all the JSON schemas related to ACL messages sent between SMIA agents."""

    JSON_SCHEMA_SUBMODEL_SERVICE_REQUEST = {
        "type": "object",
        "properties": {
            "ModelReference": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "value": {"type": "string"}
                            },
                            "required": ["type", "value"]
                        }
                    }
                },
                "required": ["keys"]
            },
            "ExternalReference": {
                "type": "string"
            }
        },
        "oneOf": [
            {"required": ["ModelReference"]},
            {"required": ["ExternalReference"]}
        ]
    }

    JSON_SCHEMA_CAPABILITY_REQUEST = {
        "type": "object",
        "properties": {
            "capabilityName": {"type": "string"},
            "skillName": {"type": "string"},
            "skillParameterValues": {
              "type": "object",
              "additionalProperties": {
                "type": "string"
              }
            },
            "skillInterfaceName": {"type": "string"}
        },
        "required": ["capabilityName"]
    }
