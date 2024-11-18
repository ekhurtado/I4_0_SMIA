from owlready2 import OneOf


class CapabilitySkillOntologyUtils:
    """This class contains all information about the proposal of the ontology based on Capability-Skill model. This
    information groups the required semanticIDs or the qualifiers to analyze AAS models."""

    @staticmethod
    def get_possible_values_of_datatype(datatype):
        """
        This method returns all possible values of an OWL data type. If the data type does not have the equivalent
        'OneOf', so the values do not need to be constrained and validated, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            list: possible values of datatype in form of a list of strings.
        """
        possible_values = []
        if datatype.equivalent_to:  # Comprobar si hay clases equivalentes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.append(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

    # Types of Capabilities
    MANUFACTURING_CAPABILITY_TYPE = 'ManufacturingCapability'
    ASSET_CAPABILITY_TYPE = 'AssetCapability'
    AGENT_CAPABILITY_TYPE = 'AgentCapability'
    CAPABILITY_TYPE_POSSIBLE_VALUES = [MANUFACTURING_CAPABILITY_TYPE, ASSET_CAPABILITY_TYPE, AGENT_CAPABILITY_TYPE]

    # SemanticIDs of Capabilities
    SEMANTICID_MANUFACTURING_CAPABILITY = 'urn:ehu:gcis:capabilityskillontology:1:1:manufacturingcapability'
    SEMANTICID_ASSET_CAPABILITY = 'urn:ehu:gcis:capabilityskillontology:1:1:assetcapability'
    SEMANTICID_AGENT_CAPABILITY = 'urn:ehu:gcis:capabilityskillontology:1:1:agentcapability'
    SEMANTICID_CAPABILITY_CONSTRAINT = 'urn:ehu:gcis:capabilityskillontology:1:1:capabilityconstraint'
    SEMANTICID_CAPABILITY_PROPERTY = 'urn:ehu:gcis:capabilityskillontology:1:1:capabilityproperty'

    # SemanticIDs of Skills
    SEMANTICID_MANUFACTURING_SKILL = 'urn:ehu:gcis:capabilityskillontology:1:1:manufacturingskill'
    SEMANTICID_SKILL_INTERFACE = 'urn:ehu:gcis:capabilityskillontology:1:1:skillinterface'
    SEMANTICID_SKILL_PARAMETER = 'urn:ehu:gcis:capabilityskillontology:1:1:skillparameter'
    SEMANTICID_SKILL_STATE_MACHINE = 'urn:ehu:gcis:capabilityskillontology:1:1:skillstatemachine'

    # SemanticIDs of Relationships
    SEMANTICID_REL_CAPABILITY_SKILL = 'urn:ehu:gcis:capabilityskillontology:1:1:capabilityrealizedby'
    SEMANTICID_REL_CAPABILITY_CAPABILITY_CONTRAINT = 'urn:ehu:gcis:capabilityskillontology:1:1:capabilityrestrictedby'
    SEMANTICID_REL_SKILL_SKILL_INTERFACE = 'urn:ehu:gcis:capabilityskillontology:1:1:skillaccesiblethrough'
    SEMANTICID_REL_SKILL_SKILL_PARAMETER = 'urn:ehu:gcis:capabilityskillontology:1:1:skillhasparameter'
    SEMANTICID_REL_SKILL_SKILL_STATE_MACHINE = 'urn:ehu:gcis:capabilityskillontology:1:1:skillbehavioursconformsto'
    SEMANTICID_REL_SKILL_PARAMETER_SKILL_INTERFACE = 'urn:ehu:gcis:capabilityskillontology:1:1:skillparameterexposedthrough'


    # Qualifiers for Capabilities
    QUALIFIER_CAPABILITY_TYPE = 'ExpressionSemantic'
    QUALIFIER_CAPABILITY_POSSIBLE_VALUES = ['REQUIREMENT', 'OFFER', 'ASSURANCE']

    # Qualifiers for Skills
    QUALIFIER_SKILL_TYPE = 'SkillImplementationType'
    QUALIFIER_SKILL_POSSIBLE_VALUES = ['STATE', 'TRIGGER', 'OPERATION', 'FUNCTIONBLOCK']

    # Qualifiers for Feasibility Checking
    QUALIFIER_FEASIBILITY_CHECKING_TYPE = 'FeasibilityCheckingCondition'
    QUALIFIER_FEASIBILITY_CHECKING_POSSIBLE_VALUES = ['PRECONDITION', 'INVARIANT', 'POSTCONDITION']

    # IDs for Negotiation AgentCapability
    CONCEPT_DESCRIPTION_ID_NEGOTIATION_CRITERIA = 'urn:ehu:gcis:conceptdescriptions:1:1:negotiationcriteria'


class CapabilitySkillOntologyInfo:
    """
    This class contains information related to the ontology of Capability-Skill: namespaces, OWL file...
    """
    CSS_BASE_NAMESPACE = 'http://www.w3id.org/hsu-aut/css#'
    CSS_SMIA_NAMESPACE = 'http://www.w3id.org/upv-ehu/gcis/css-smia#'


class CapabilitySkillACLInfo:
    """
    This subclass of CapabilitySkillOntology contains information about the structure of the message that are sent
    between DTs in relation to Capability-Skill model.
    """

    # Required Capability information
    REQUIRED_CAPABILITY_NAME = 'capabilityName'
    REQUIRED_CAPABILITY_TYPE = 'capabilityType'
    REQUIRED_CAPABILITY_CONSTRAINTS = 'capabilityConstraints'
    REQUIRED_SKILL_INFO = 'skillInfo'
    REQUIRED_SKILL_NAME = 'skillName'
    REQUIRED_SKILL_ELEMENT_TYPE = 'smeType'
    REQUIRED_SKILL_PARAMETERS = 'skillParameters'
    REQUIRED_SKILL_INPUT_PARAMETERS = 'inputs'
    REQUIRED_SKILL_OUTPUT_PARAMETERS = 'outputs'
    # TODO pensar si harian falta mas


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
