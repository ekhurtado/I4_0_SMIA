import logging

from basyx.aas.adapter import aasx
from owlready2 import OneOf

from logic.exceptions import OntologyReadingError, CriticalError
from utilities import configmap_utils

_logger = logging.getLogger(__name__)

class CapabilitySkillOntologyUtils:
    """This class contains all information about the proposal of the ontology based on Capability-Skill model. This
    information groups the required semanticIDs or the qualifiers to analyze AAS models."""

    @staticmethod
    def get_ontology_file_path():
        """
        This method gets the valid file path of the ontology file. The file is obtained from the AASX package or from
        the configuration folder inside the SMIA Archive, depending on the definition in the properties file.

        Returns:
            str: file path to the ontology file.
        """
        if configmap_utils.get_ontology_general_property("inside-aasx").lower() in ('yes', 'true', 't', '1'):
            aas_model_serialization_format = configmap_utils.get_aas_general_property('model.serialization')
            if aas_model_serialization_format == 'AASX':
                try:
                    with aasx.AASXReader(configmap_utils.get_aas_model_filepath()) as aasx_reader:
                        for part_name, content_type in aasx_reader.reader.list_parts():
                            # All parts of the AASX package are analyzed
                            # if '.owl' in part_name:
                            if any(ext in part_name for ext in ['.owl', '.rdf', '.owx']):
                                ontology_zip_file = aasx_reader.reader.open_part(part_name)
                                ontology_file_bytes = ontology_zip_file.read()
                                return configmap_utils.create_ontology_file(ontology_file_bytes)
                        else:
                            raise CriticalError("Failed to read ontology file inside the AASX package (FileNotFound).")
                except ValueError as e:
                    raise CriticalError("Failed to read AAS model: invalid file.")
            else:
                # The serialization format must be AASX. However, it will be checked if the ontology file defined in
                # the properties file is valid.
                _logger.warning("The properties file may not be well defined. The ontology file is set as is within "
                                "AASX, but the serialization format of the AAS model is not AASX.")
                # It will try with the file path defined in the properties file, if it does not exist, it will crash
                # during the loading of the ontology
                return configmap_utils.get_defined_ontology_filepath()
        else:
            return configmap_utils.get_defined_ontology_filepath()

    @staticmethod
    def get_possible_values_of_datatype(datatype):
        """
        This method returns all possible values of an OWL data type. If the data type does not have the equivalent
        'OneOf', so the values do not need to be constrained and validated, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            set: possible values of datatype in form of a list of strings.
        """
        possible_values = set()
        if datatype.equivalent_to:  # Comprobar si hay clases equivalentes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.add(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

    @staticmethod
    def check_whether_part_of_domain(owl_instance, domain):
        """
        This method checks whether a given instance class is part of a given domain.

        Args:
            owl_instance (ThingClass): instance of the OWL class to be checked.
            domain (CallbackList): list of all classes within the given domain.

        Returns:
            bool: result of the check.
        """
        for domain_class in domain:
            for owl_class in owl_instance.is_a:
                if owl_class == domain_class or domain_class in owl_class.ancestors():
                    return True
        return False

    @staticmethod
    def get_attribute_from_classes_in_object_property(object_property_class, attribute_name):
        """
        This method gets the required attribute of the ontology classes of a given Object Property. If the attribute
        does not exist, it raises an exception.

        Args:
            object_property_class (ObjectPropertyClass): class object of the ObjectProperty.
            attribute_name (str): the attribute to get from the class object within the given object property.

        Returns:
            object, object: attribute value of the domain and range ontology classes.
        """
        if object_property_class is None:
            raise OntologyReadingError("The object property object {} is None".format(object_property_class))
        if len(object_property_class.domain) == 0 or len(object_property_class.range) == 0:
            raise OntologyReadingError("The domain or range of object property {} are "
                                       "empty".format(object_property_class))
        try:
            for domain_class in object_property_class.domain:
                if hasattr(domain_class, 'get_associated_aas_class'):
                    domain_aas_class = domain_class.get_associated_aas_class()
                    break
            else:
                # In this case no domain class is of the defined CSS model of the SMIA approach.
                raise OntologyReadingError("The domain of object property object {} does not have any associated "
                                           "AAS model classes defined".format(object_property_class))
            for range_class in object_property_class.range:
                if hasattr(range_class, 'get_associated_aas_class'):
                    range_aas_class = range_class.get_associated_aas_class()
                    break
            else:
                # In this case no range class is of the defined CSS model of the SMIA approach.
                raise OntologyReadingError("The range of object property object {} does not have any associated "
                                           "AAS model classes defined".format(object_property_class))
            return domain_aas_class, range_aas_class
        except KeyError as e:
            # TODO
            pass

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
    CSS_ONTOLOGY_BASE_NAMESPACE = 'http://www.w3id.org/hsu-aut/css#'
    CSS_ONTOLOGY_SMIA_NAMESPACE = 'http://www.w3id.org/upv-ehu/gcis/css-smia#'

    # SemanticIDs (IRIs) of Capabilities
    CSS_ONTOLOGY_CAPABILITY_IRI = 'http://www.w3id.org/hsu-aut/css#Capability'
    CSS_ONTOLOGY_AGENT_CAPABILITY_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#AgentCapability'
    CSS_ONTOLOGY_ASSET_CAPABILITY_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability'
    CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI = 'http://www.w3id.org/hsu-aut/css#CapabilityConstraint'

    # SemanticIDs (IRIs) of Skills
    CSS_ONTOLOGY_SKILL_IRI = 'http://www.w3id.org/hsu-aut/css#Skill'
    CSS_ONTOLOGY_SKILL_INTERFACE_IRI = 'http://www.w3id.org/hsu-aut/css#SkillInterface'
    CSS_ONTOLOGY_SKILL_PARAMETER_IRI = 'http://www.w3id.org/hsu-aut/css#SkillParameter'
    CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI = 'http://www.w3id.org/hsu-aut/css#StateMachine'

    # SemanticIDs (IRIs) of Object Properties (relationship between classes)
    CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI = 'http://www.w3id.org/hsu-aut/css#isRealizedBy'
    CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI = 'http://www.w3id.org/hsu-aut/css#isRestrictedBy'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI = 'http://www.w3id.org/hsu-aut/css#accessibleThrough'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_ASSET_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#accessibleThroughAssetService'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_AGENT_IRI = 'http://www.w3id.org/upv-ehu/gcis/css-smia#accessibleThroughAgentService'
    CSS_ONTOLOGY_PROP_HASPARAMETER_IRI = 'http://www.w3id.org/hsu-aut/css#hasParameter'
    CSS_ONTOLOGY_PROP_BEHAVIOURSCONFORMSTO_IRI = 'http://www.w3id.org/hsu-aut/css#behaviorConformsTo'

    CSS_ONTOLOGY_THING_CLASSES_IRIS = [CSS_ONTOLOGY_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_AGENT_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_ASSET_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI,
                                       CSS_ONTOLOGY_SKILL_IRI,
                                       CSS_ONTOLOGY_SKILL_INTERFACE_IRI,
                                       CSS_ONTOLOGY_SKILL_PARAMETER_IRI,
                                       CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI,
                                       ]

    CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS = [CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI,
                                           CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_ASSET_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_AGENT_IRI,
                                           CSS_ONTOLOGY_PROP_HASPARAMETER_IRI,
                                           CSS_ONTOLOGY_PROP_BEHAVIOURSCONFORMSTO_IRI
                                           ]


class CSSModelAASModelInfo:
    """
    This class contains information about the relation between the Capability-Skill-Service model and the AAS model.
    """
    from aas_model import extended_submodel


    # TODO HACER AHORA GENERAR TAMBIEN UNA LISTA CON LAS CLASES DE LA ONTOLOGIA Y LAS CLASES 'Extended' del AAS asociadas
    CSS_ONTOLOGY_AAS_MODEL_LINK = {
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI: extended_submodel.ExtendedCapabilityConstraint,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI: extended_submodel.ExtendedSkill,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI: extended_submodel.ExtendedSkillInterface,
        # CSS_ONTOLOGY_SKILL_PARAMETER_IRI: '',
        # CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI: '',
    }


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

