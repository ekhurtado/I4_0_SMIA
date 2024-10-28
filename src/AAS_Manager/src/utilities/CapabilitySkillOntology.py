class CapabilitySkillOntology:
    """This class contains all information about the proposal of the ontology based on Capability-Skill model. This
    information groups the required semanticIDs or the qualifiers to analyze AAS models."""

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

    # Qualifiers for Capabilities
    QUALIFIER_CAPABILITY_TYPE = 'ExpressionSemantic'
    QUALIFIER_CAPABILITY_POSSIBLE_VALUES = ['REQUIREMENT', 'OFFER', 'ASSURANCE']

    # Qualifiers for Skills
    QUALIFIER_SKILL_TYPE = 'SkillImplementationType'
    QUALIFIER_SKILL_POSSIBLE_VALUES = ['STATE', 'TRIGGER', 'OPERATION', 'FUNCTIONBLOCK']

    # Qualifiers for Feasibility Checking
    QUALIFIER_FEASIBILITY_CHECKING_TYPE = 'FeasibilityCheckingCondition'
    QUALIFIER_FEASIBILITY_CHECKING_POSSIBLE_VALUES = ['PRECONDITION', 'INVARIANT', 'POSTCONDITION']


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
    REQUIRED_ELEMENT_TYPE = 'smeType'
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

    # SemanticIDs of HTTP Asset Interface
    SUPPL_SEMANTICID_HTTP = 'http://www.w3.org/2011/http'