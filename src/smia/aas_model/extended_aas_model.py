import asyncio
import logging
import basyx.aas.model.submodel
from basyx.aas.util import traversal
from smia.aas_model.aas_model_utils import AASModelInfo

from smia.logic.exceptions import CapabilityCheckingError, AASModelReadingError, OntologyReadingError
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils, CapabilitySkillACLInfo, \
    CapabilitySkillOntologyInfo
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class ExtendedAASModel:
    """This class contains methods related to the AAS model stored in Python objects. These methods are useful when
    using the AAS model in the SMIA approach."""

    aas_model_object_store = None  #: Storage with all Python object obtained from the AAS model
    capabilities_skills_dict = None  #: Dictionary with all information related to Capability-Skill model obtained from the AAS model

    lock = None  #: Asyncio Lock object for secure access to shared AAS model objects

    def __init__(self):

        # The object to store all Python objects obtained from the AAS model are initialized
        self.aas_model_object_store = None

        # Also, the object to store all information related to Capabilities and Skills is initialized. To this end, the
        # dictionary is divided in capabilities related to the agent (DT) and capabilities related to the asset.
        self.capabilities_skills_dict = {'AgentCapabilities': {}, 'AssetCapabilities': {}}

        # The Lock object is used to manage the access to global agent attributes (request and response dictionaries,
        # interaction id number...)
        self.lock = asyncio.Lock()

    # -----------------------------------------
    # Methods related to AAS model object store
    # -----------------------------------------
    async def set_aas_model_object_store(self, object_store):
        """
        This method updates the object store for the AAS model.

        Args:
            object_store (basyx.aas.model.DictObjectStore): object to store all Python elements of the AAS model.

        """
        async with self.lock:
            self.aas_model_object_store = object_store

    async def get_aas_model_object_store(self):
        """
        This method returns the object store for the AAS model.

        Returns:
            basyx.aas.model.DictObjectStore: object with all Python elements of the AAS model.

        """
        async with self.lock:
            return self.aas_model_object_store

    # ---------------
    # General methods
    # ---------------
    async def execute_general_analysis(self, smia_agent):
        """
        This method performs the general analysis on the AAS model to check if it is a valid AAS model for SMIA
        software, and provides information to the user via console or log file.

        Args:
            smia_agent(spade.agent.Agent): SMIA SPADE agent object.
        """
        # If standardized submodels are added is checked
        asset_interfaces_submodel = await self.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning("AssetInterfacesSubmodel submodel is not defined. Make sure that this SMIA does not need to "
                            "be connected to the asset via any communication protocols.")
        software_nameplate_submodel = await self.get_submodel_by_semantic_id(
            AASModelInfo.SEMANTICID_SOFTWARE_NAMEPLATE_SUBMODEL)
        if not software_nameplate_submodel:
            _logger.warning("SoftwareNameplate submodel is not defined. This can lead to errors during SMIA runtime.")
        else:
            # Checks if the instance name defined in the AAS matches the one defined in the agent during start-up.
            for software_nameplate_instance in software_nameplate_submodel.submodel_element:
                aas_smia_instance_name = software_nameplate_instance.get_sm_element_by_semantic_id(AASModelInfo.SEMANTICID_SOFTWARE_NAMEPLATE_INSTANCE_NAME)
                if aas_smia_instance_name is not None:
                    if aas_smia_instance_name.value != smia_agent.jid.localpart:
                        _logger.warning(
                            "The SMIA instance name defined in the SoftwareNameplate submodel [{}] and the identifier "
                            "used to start the agent [{}] do not match. This can result in errors during SMIA runtime."
                            "".format(aas_smia_instance_name.value, smia_agent.jid.localpart))
        # TODO Add more checks


    # -------------------------------------------
    # Methods related to capability skills object
    # -------------------------------------------
    async def set_capabilities_skills_object(self, cap_skills_object):
        """
        This method updates the object that contains with all the information about Capabilities and Skills of the DT
        and the asset.

        Args:
            cap_skills_object (dict): object with all the information about Capabilities and Skills of the DT and the asset.

        """
        async with self.lock:
            self.capabilities_skills_dict = cap_skills_object

    async def get_capabilities_skills_object(self):
        """
        This method returns the object with all the information about Capabilities and Skills of the DT and the asset.

        Returns:
            dict: all the information about Capabilities and Skills of the DT and the asset in JSON format.

        """
        async with self.lock:
            return self.capabilities_skills_dict

    async def save_capability_skill_information(self, capability_type, cap_skill_info):
        """
        This method saves the information of a capability and its associated skill in the global dictionary. It
        distinguishes between AgentCapabilities and AssetCapabilities.

        Args:
            capability_type (str): type of the capability (AgentCapabilities or AssetCapabilities).
            cap_skill_info (dict): information in form of a JSON object.
        """
        if capability_type not in CapabilitySkillOntologyUtils.CAPABILITY_TYPE_POSSIBLE_VALUES:
            _logger.error("The capability type is not valid. The information cannot be saved.")
            return
        async with self.lock:
            try:
                if capability_type == CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE:
                    self.capabilities_skills_dict['AgentCapabilities'] = cap_skill_info
                if capability_type == CapabilitySkillOntologyUtils.ASSET_CAPABILITY_TYPE:
                    self.capabilities_skills_dict['AssetCapabilities'] = cap_skill_info
            except KeyError:
                _logger.error("The capability type is not valid. The information cannot be saved.")

    async def get_capability_dict_by_type(self, cap_type):
        """
        This method returns the capability dictionary related to the given capability type.

        Args:
            cap_type(str): type of the capability (AgentCapabilities or AssetCapabilities).

        Returns:
            dict: dictionary will the information of all capabilities of the given type.
        """
        async with self.lock:
            if cap_type == CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE:
                return self.capabilities_skills_dict['AgentCapabilities']
            if cap_type == CapabilitySkillOntologyUtils.ASSET_CAPABILITY_TYPE:
                return self.capabilities_skills_dict['AssetCapabilities']
            return {}

    # -----------------------------------------
    # General methods related to AAS meta-model
    # -----------------------------------------
    async def get_object_by_reference(self, reference):
        """
        This method gets the AAS meta-model Python object using the reference, distinguishing between ExternalReference
         and ModelReference.

        Args:
            reference (basyx.aas.model.Reference): reference object related to desired element

        Returns:
            object: Python object of the desired element associated to the reference.
        """
        try:
            if isinstance(reference, basyx.aas.model.ExternalReference):
                for key in reference.key:
                    return self.aas_model_object_store.get_identifiable(key.value)
            elif isinstance(reference, basyx.aas.model.ModelReference):
                return reference.resolve(self.aas_model_object_store)
        except KeyError as e:
            _logger.error(e)
            raise AASModelReadingError("The object within the AAS model with reference {} does not "
                                       "exist".format(reference), sme_class=None, reason='AASModelObjectNotExist')

    async def get_submodel_elements_by_semantic_id(self, semantic_id_external_ref, sme_class=None):
        """
        This method gets all SubmodelElements by the semantic id in form of an external reference. The SubmodelElements
        to obtain can be filtered by the meta-model class.

        Args:
            semantic_id_external_ref (str): semantic id in form of an external reference
            sme_class (basyx.aas.model.SubmodelElement): Submodel Element class of the elements to be found (None if no
             filtering is required).

        Returns:
            list(basyx.aas.model.SubmodelElement): list with all SubmodelElements of the given class.
        """
        if sme_class is None:
            sme_class = basyx.aas.model.SubmodelElement
        rels_elements = []
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(aas_object):
                    if isinstance(submodel_element, sme_class):
                        if submodel_element.check_semantic_id_exist(semantic_id_external_ref):
                            rels_elements.append(submodel_element)
                        if isinstance(submodel_element, basyx.aas.model.Operation):
                            # In case of Operation, OperationVariables need to be analyzed
                            rels_elements.extend(submodel_element.get_operation_variables_by_semantic_id(
                                semantic_id_external_ref))
        return rels_elements

    async def get_submodel_elements_by_semantic_id_list(self, semantic_id_external_refs, sme_class=None):
        """
        This method obtains all the SubmodelElements that have any of the given semantic identifiers (in form of an
        external references). The SubmodelElements to obtain can be filtered by the meta-model class.

        Args:
            semantic_id_external_refs (list(str)): semantic identifiers in form of a list of external references
            sme_class (basyx.aas.model.SubmodelElement): Submodel Element class of the elements to be found (None if no
             filtering is required).

        Returns:
            list(basyx.aas.model.SubmodelElement): list with all SubmodelElements of the given class.
        """
        if sme_class is None:
            sme_class = basyx.aas.model.SubmodelElement
        rels_elements = []
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(aas_object):
                    if isinstance(submodel_element, sme_class):
                        for semantic_id in semantic_id_external_refs:
                            if submodel_element.check_semantic_id_exist(semantic_id):
                                rels_elements.append(submodel_element)
                            if isinstance(submodel_element, basyx.aas.model.Operation):
                                # In case of Operation, OperationVariables need to be analyzed
                                rels_elements.extend(submodel_element.get_operation_variables_by_semantic_id(
                                    semantic_id))
        return rels_elements

    async def get_submodel_by_semantic_id(self, sm_semantic_id):
        """
        This method gets the Submodel object using its semantic identifier.

        Args:
            sm_semantic_id (str): semantic identifier of the Submodel.

        Returns:
            basyx.aas.model.Submodel: Submodel in form of a Python object.
        """
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel) and aas_object.semantic_id is not None:
                for reference in aas_object.semantic_id.key:
                    if reference.value == sm_semantic_id:
                        return aas_object

    async def check_element_exist_in_namespaceset_by_id_short(self, namespaceset_elem, elem_id_short):
        """
        This method checks if an element exists in the NamespaceSet using its id_short.

        Args:
            namespaceset_elem (basyx.aas.model.NamespaceSet): NamespaceSet element
            elem_id_short (str): id_short of the element.

        Returns:
            bool: result of the check
        """
        for namespace_elem in namespaceset_elem:
            if namespace_elem.id_short == elem_id_short:
                return True
        return False

    async def get_concept_description_pair_value_id_by_value_name(self, concept_description_id, value_name):
        """
        This method gets the value_id of a pair within a Concept Description using the value name.

        Args:
            concept_description_id (str): globally unique identifier of the Concept Description.
            value_name (str): name of the value inside the pair to find.

        Returns:
            str: value_id of the pair that contains the provided value name.
        """
        concept_description = self.aas_model_object_store.get_identifiable(concept_description_id)
        if concept_description:
            # First, it is checked the embedded_data_specifications (the specification of the data inside the element).
            if concept_description.embedded_data_specifications:
                # Vamos a comprobar que tenga valueList (en esa variable se añaden los posibles valores para una propiedad)
                for embedded_data_spec in concept_description.embedded_data_specifications:
                    if isinstance(embedded_data_spec.data_specification_content,
                                  basyx.aas.model.DataSpecificationIEC61360):
                        if embedded_data_spec.data_specification_content.value_list:
                            value_list = embedded_data_spec.data_specification_content.value_list
                            for value_elem in value_list:
                                if value_elem.value == value_name:
                                    # As it is another ConceptDescription, it is a ExternalReference (first key)
                                    return value_elem.value_id.key[0].value

        _logger.error("Concept Description with id [{}] not found.".format(concept_description_id))
        return None

    # ---------------------------------------------------------------
    # Methods related to Capability-Skill ontology and AAS meta-model
    # ---------------------------------------------------------------
    async def get_capability_by_id_short(self, cap_type, cap_id_short):
        """
        This method gets the capability object with all its information using its id_short attribute and the type of
        the Capability.

        Args:
            cap_type (str): type of the capability (AgentCapabilities or AssetCapabilities).
            cap_id_short (str): id_short of the Capability to find.

        Returns:
            basyx.aas.model.Capability: Python object of capability to find (None if the Capability does not exist)
        """
        for cap_elem, cap_info in (await self.get_capability_dict_by_type(cap_type)).items():
            if cap_elem.id_short == cap_id_short:
                return cap_elem
        return None

    async def get_cap_skill_elem_from_relationship(self, rel_element):
        """
        This method returns the Capability and Skill objects from the Relationship element, no matter in which order
        they are specified.

        Args:
            rel_element (basyx.aas.model.RelationshipElement): Python object of the RelationshipElement.

        Returns:
            basyx.aas.model.Capability, basyx.aas.model.SubmodelElement: capability and skill SME in Python
            reference objects.
        """
        first_rel_elem = await self.get_object_by_reference(rel_element.first)
        second_rel_elem = await self.get_object_by_reference(rel_element.second)
        if isinstance(first_rel_elem, basyx.aas.model.Capability):
            return first_rel_elem, second_rel_elem
        elif isinstance(second_rel_elem, basyx.aas.model.Capability):
            return second_rel_elem, first_rel_elem
        else:
            _logger.error(
                "This method has been used incorrectly. This Relationship does not have a Capability element.")
            return None, None

    async def get_elements_from_relationship(self, rel_element, first_elem_class=None, second_elem_class=None):
        """
        This method returns the objects of a given Relationship element taking into account the type of class that is
        required for the objects referenced within the relationship. The objects will be returned in the order
        specified by the classes, no matter in which order they are defined in the AAS model (in the case of not
        specifying any class, it is returned in the original order).

        Args:
            rel_element (basyx.aas.model.RelationshipElement): Python object of the RelationshipElement.
            first_elem_class (basyx.aas.model.SubmodelElement): Class required for the first element returned.
            second_elem_class (basyx.aas.model.SubmodelElement): Class required for the second element returned.

        Returns:
            basyx.aas.model.SubmodelElement, basyx.aas.model.SubmodelElement: SME Python objects with the required format.
        """
        # Using the references within the relationship, both SubmodelElement are obtained
        first_rel_elem = await self.get_object_by_reference(rel_element.first)
        second_rel_elem = await self.get_object_by_reference(rel_element.second)
        if first_rel_elem is None or second_rel_elem is None:
            raise AASModelReadingError("Elements of the relationship {} does not exist in the AAS model"
                                       "".format(rel_element.id_short), sme_class=rel_element,
                                       reason="Relationship referenced element invalid")
        if None in (first_rel_elem, second_rel_elem):
            # If no one is required, it simply returns the elements
            return first_rel_elem, second_rel_elem
        if None not in (first_rel_elem, second_rel_elem):
            # If both are required, both have to be checked
            if (first_elem_class is None) or (second_elem_class is None):
                raise OntologyReadingError('The classes of the relation {} do not exist. Check the OWL ontology '
                                           'file.'.format(rel_element.id_short))
            if isinstance(first_rel_elem, first_elem_class) and isinstance(second_rel_elem, second_elem_class):
                return first_rel_elem, second_rel_elem
            elif isinstance(first_rel_elem, second_elem_class) and isinstance(second_rel_elem, first_elem_class):
                return second_rel_elem, first_rel_elem
            else:
                raise AASModelReadingError("Elements of the relationship {} are not exist of the required classes {}, "
                                           "{}".format(rel_element.id_short, first_elem_class, second_elem_class)
                                           , sme_class=rel_element, reason="Relationship referenced element invalid")
        if first_elem_class is not None:
            if isinstance(first_rel_elem, first_elem_class):
                return first_rel_elem, second_rel_elem
            elif isinstance(second_rel_elem, first_elem_class):
                return second_rel_elem, first_rel_elem
            else:
                raise AASModelReadingError("The element {} within the relationship {} is not of the required class "
                                           "{}".format(first_rel_elem, rel_element.id_short, first_elem_class),
                                           sme_class=rel_element, reason="Relationship referenced element invalid")
        if second_elem_class is not None:
            if isinstance(first_rel_elem, second_elem_class):
                return second_rel_elem, first_rel_elem
            elif isinstance(second_rel_elem, second_elem_class):
                return first_rel_elem, second_rel_elem
            else:
                raise AASModelReadingError("The element {} within the relationship {} is not of the required class "
                                           "{}".format(second_rel_elem, rel_element.id_short, second_elem_class),
                                           sme_class=rel_element, reason="Relationship referenced element invalid")

    async def get_capability_associated_constraints(self, capability_elem):
        """
        This method gets the constraints associated to a capability.

        Args:
            capability_elem (basyx.aas.model.Capability): capability Python object.

        Returns:
            list: list with all constraints of the selected capability in form of Python objects.
        """
        cap_constraints = []
        rels_cap_constraints = await self.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI, basyx.aas.model.RelationshipElement)
        for rel in rels_cap_constraints:
            first_elem = await self.get_object_by_reference(rel.first)
            second_elem = await self.get_object_by_reference(rel.second)
            if first_elem == capability_elem:
                cap_constraints.append(second_elem)
            elif second_elem == capability_elem:
                cap_constraints.append(first_elem)
        return cap_constraints

    async def get_capability_associated_constraints_by_qualifier_data(self, capability_elem, qualifier_type,
                                                                      qualifier_value):
        """
        This method gets the constraints associated to a capability that have specific qualifier data.

        Args:
            capability_elem (basyx.aas.model.Capability): capability Python object.
            qualifier_type (str): type of the qualifier
            qualifier_value (str): value of the qualifier

        Returns:
            list: list with all constraints of the selected capability in form of Python objects.
        """
        all_constraints = await self.get_capability_associated_constraints(capability_elem)
        for constraint in all_constraints:
            if constraint.qualifier:
                for qualifier in constraint.qualifier:
                    if (qualifier.type == qualifier_type) and (qualifier.value == qualifier_value):
                        return constraint
        return None

    async def get_skill_interface_by_skill_elem(self, skill_elem):
        """
        This method gets the interfaces associated to a skill.

        Args:
            skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

        Returns:
            (basyx.aas.model.SubmodelElement): the interface of the selected skill in form of Python object (None if it does not exist).
        """
        rels_skill_interfaces = await self.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI, basyx.aas.model.RelationshipElement)
        for rel in rels_skill_interfaces:
            first_elem = await self.get_object_by_reference(rel.first)
            second_elem = await self.get_object_by_reference(rel.second)
            if first_elem == skill_elem:
                return second_elem
            elif second_elem == skill_elem:
                return first_elem
        return None

    async def get_asset_interface_interaction_metadata_by_value_semantic_id(self, value_semantic_id):
        """
        This method reads the AssetInterfacesDescription submodel and returns an Interaction Metadata by a given value
        semanticID. This is how in this approach it is established that an attribute is of asset data type.

        Args:
            value_semantic_id (str): semanticID of the value of the Interaction Metadata.

        Returns:
            basyx.aas.model.SubmodelElementCollection: SubmodelElement of the required Interaction Metadata (None if the semanticID does not exist)
        """
        asset_interfaces_submodel = await self.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        for interface_smc in asset_interfaces_submodel.submodel_element:
            interaction_metadata = interface_smc.get_sm_element_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERACTION_METADATA)
            for element_type_smc in interaction_metadata:
                # InteractionMetadata has properties, actions or events
                for element_smc in element_type_smc:
                    # The valueSemantic SubmodelElement is obtained
                    value_semantics = element_smc.get_sm_element_by_semantic_id(
                        AssetInterfacesInfo.SEMANTICID_VALUE_SEMANTICS)
                    if value_semantics:
                        for reference in value_semantics.value.key:
                            if reference.value == value_semantic_id:
                                return element_smc
        return None

    async def get_skill_parameters_exposure_interface_elem(self, skill_elem):
        """
        This method gets the exposure element within the skill interface linked to the parameters of the given skill.

        Args:
            skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

        Returns:
            basyx.aas.model.SubmodelElement: exposure submodel element of skill parameters.
        """
        # The exposure elements can be obtained with the related relationship semanticID
        rels_params_exposed = await self.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyUtils.SEMANTICID_REL_SKILL_PARAMETER_SKILL_INTERFACE, basyx.aas.model.RelationshipElement)
        for rel in rels_params_exposed:
            first_elem = await self.get_object_by_reference(rel.first)
            second_elem = await self.get_object_by_reference(rel.second)
            if first_elem == skill_elem:
                 return  second_elem
            elif second_elem == skill_elem:
                return first_elem
        return None

    async def skill_feasibility_checking_post_conditions(self, capability_elem, constraints_data):
        """
        This method checks the feasibility of a Capability element in relation with its post-conditions.

        Args:
            capability_elem (basyx.aas.model.Capability): capability Python object.
            constraints_data (dict): JSON object with the data of the constraints (with required values)
        """
        # First, the postcondition constraints are obtained
        post_condition_constraints = await self.get_capability_associated_constraints_by_qualifier_data(capability_elem,
                                                                                                        CapabilitySkillOntologyUtils.QUALIFIER_FEASIBILITY_CHECKING_TYPE,
                                                                                                        'POSTCONDITION')
        if post_condition_constraints:
            # TODO habra que pensar como analizar las post condiciones
            pass
