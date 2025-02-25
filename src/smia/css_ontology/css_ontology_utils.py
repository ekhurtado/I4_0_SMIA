import logging

from basyx.aas.adapter import aasx
from owlready2 import OneOf

from smia import SMIAGeneralInfo
from smia.logic.exceptions import OntologyReadingError, CriticalError
from smia.utilities import properties_file_utils, smia_archive_utils

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
        ontology_property = properties_file_utils.get_ontology_general_property("inside-aasx")
        if (ontology_property == '#') or (ontology_property.lower() in ('yes', 'true', 't', '1')):
            # The ontology file will be checked if the ontology file is inside the AASX package if the initialization
            # properties file is not added ('inside-aasx' property is '#') or is added and set as such.
            aas_model_serialization_format = properties_file_utils.get_aas_general_property('model.serialization')
            if aas_model_serialization_format == '.aasx':
                try:
                    with aasx.AASXReader(properties_file_utils.get_aas_model_filepath()) as aasx_reader:
                        for part_name, content_type in aasx_reader.reader.list_parts():
                            # All parts of the AASX package are analyzed
                            # if '.owl' in part_name:
                            if any(ext in part_name for ext in ['.owl', '.rdf', '.owx']):
                                ontology_zip_file = aasx_reader.reader.open_part(part_name)
                                ontology_file_bytes = ontology_zip_file.read()
                                return properties_file_utils.create_ontology_file(ontology_file_bytes)
                        else:
                            # If the ontology file is not inside the AASX and is not defined in the initialization
                            # properties file, an OWL file will be looked for inside the SMIA Archive.
                            _logger.info("The ontology OWL file is not found within the AASX package, so it will be "
                                         "searched for within the SMIA Archive.")
                            ontology_file_path = smia_archive_utils.get_file_by_extension(
                                SMIAGeneralInfo.CONFIGURATION_FOLDER_PATH, '.owl')
                            if ontology_file_path is None:
                                raise CriticalError("Failed to read ontology file inside the AASX package (FileNotFound)"
                                                    " and inside the SMIA Archive.")
                            else:
                                return ontology_file_path

                except ValueError as e:
                    raise CriticalError("Failed to read AAS model: invalid file.")
            else:
                # The serialization format must be AASX. However, it will be checked if the ontology file defined in
                # the properties file is valid.
                _logger.warning("The properties file may not be well defined. The ontology file is set as is within "
                                "AASX, but the serialization format of the AAS model is not AASX.")
                # It will try with the file path defined in the properties file, if it does not exist, it will crash
                # during the loading of the ontology
                return properties_file_utils.get_defined_ontology_filepath()
        else:
            return properties_file_utils.get_defined_ontology_filepath()

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
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.add(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

    @staticmethod
    def check_and_get_xsd_datatypes(datatype):
        """
        This method checks whether the given OWL data type is one of those defined in XSD and, if true, returns the
        associated data type. If false, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            object: value of datatype defined in XSD (None if it is not found).
        """
        if datatype.equivalent_to:  # Check for equivalent classes
            for equivalent in datatype.equivalent_to:
                if equivalent == str:
                    return str
            return None

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
    def get_aas_classes_from_object_property(object_property_class):
        """
        This method gets the AAS class related to the of the ontology classes of a given Object Property. If the
        attribute of the AAS class does not exist, it raises an exception.

        Args:
            object_property_class (ObjectPropertyClass): class object of the ObjectProperty.

        Returns:
            object, object: AAS class value of the domain and range ontology classes.
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
            raise OntologyReadingError("The domain or range of object property object {} does not have associated "
                                           "AAS model classes defined".format(object_property_class))

    # Types of Capabilities
    MANUFACTURING_CAPABILITY_TYPE = 'ManufacturingCapability'
    ASSET_CAPABILITY_TYPE = 'AssetCapability'
    AGENT_CAPABILITY_TYPE = 'AgentCapability'
    CAPABILITY_TYPE_POSSIBLE_VALUES = [MANUFACTURING_CAPABILITY_TYPE, ASSET_CAPABILITY_TYPE, AGENT_CAPABILITY_TYPE]

    # SemanticIDs of Capabilities
    # TODO ESTA LA DEJO PORQUE NO SE HA UTILIZADO TODAVIA EN LA ONTOLOGIA, PERO TAMBIEN HAY QUE ELIMINARLA
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
    from smia.aas_model import extended_submodel

    CSS_ONTOLOGY_AAS_MODEL_LINK = {
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI: extended_submodel.ExtendedCapability,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_CAPABILITY_CONSTRAINT_IRI: extended_submodel.ExtendedCapabilityConstraint,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI: extended_submodel.ExtendedSkill,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_INTERFACE_IRI: extended_submodel.ExtendedSkillInterface,
        CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_PARAMETER_IRI: extended_submodel.ExtendedSkillParameter,
        # CSS_ONTOLOGY_SKILL_STATE_MACHINE_IRI: '',     # TODO todavia no se ha usado
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
    REQUIRED_SKILL_PARAMETERS_VALUES = 'skillParameterValues'
    REQUIRED_SKILL_INPUT_PARAMETERS = 'inputs'
    REQUIRED_SKILL_OUTPUT_PARAMETERS = 'outputs'
    REQUIRED_SKILL_INTERFACE_NAME = 'skillInterfaceName'
    # TODO pensar si harian falta mas


