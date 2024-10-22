class CapabilitySkillOntology:
    """This class contains all information about the proposal of the ontology based on Capability-Skill model. This
    information groups the required semanticIDs or the qualifiers to analyze AAS models."""

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


