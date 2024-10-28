import asyncio
import logging
import basyx.aas.model.submodel
from basyx.aas.util import traversal

from utilities.CapabilitySkillOntology import CapabilitySkillOntology, CapabilitySkillACLInfo

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
        if capability_type not in CapabilitySkillOntology.CAPABILITY_TYPE_POSSIBLE_VALUES:
            _logger.error("The capability type is not valid. The information cannot be saved.")
            return
        async with self.lock:
            try:
                if capability_type == CapabilitySkillOntology.AGENT_CAPABILITY_TYPE:
                    self.capabilities_skills_dict['AgentCapabilities'] = cap_skill_info
                if capability_type == CapabilitySkillOntology.ASSET_CAPABILITY_TYPE:
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
            if cap_type == CapabilitySkillOntology.AGENT_CAPABILITY_TYPE:
                return self.capabilities_skills_dict['AgentCapabilities']
            if cap_type == CapabilitySkillOntology.ASSET_CAPABILITY_TYPE:
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
        if isinstance(reference, basyx.aas.model.ExternalReference):
            return self.aas_model_object_store.get_identifiable(reference.key)
        elif isinstance(reference, basyx.aas.model.ModelReference):
            return reference.resolve(self.aas_model_object_store)

    async def get_relationship_elements_by_semantic_id(self, rel_semantic_id_external_ref):
        """
        This method gets all Relationship SubmodelElements by the semantic id in form of an external reference.

        Args:
            rel_semantic_id_external_ref (str): semantic id in form of an external reference

        Returns:
            list(basyx.aas.model.RelationshipElement): list with all Relationship SubmodelElements.
        """
        rels_elements = []
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(aas_object):
                    if isinstance(submodel_element, basyx.aas.model.RelationshipElement):
                        for semantic_id in traversal.walk_semantic_ids_recursive(submodel_element):
                            for reference in semantic_id.key:
                                if reference.value == rel_semantic_id_external_ref:
                                    rels_elements.append(submodel_element)
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
                a = aas_object.semantic_id
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
            _logger.error("This method has been used incorrectly. This Relationship does not have a Capability element.")
            return None, None

    async def get_capability_associated_constraints(self, capability_elem):
        """
        This method gets the constraints associated to a capability.

        Args:
            capability_elem (basyx.aas.model.Capability): capability Python object.

        Returns:
            list: list with all constraints of the selected capability in form of Python objects.
        """
        cap_constraints = []
        rels_cap_constraints = await self.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_CAPABILITY_CONTRAINT)
        for rel in rels_cap_constraints:
            first_elem = await self.get_object_by_reference(rel.first)
            second_elem = await self.get_object_by_reference(rel.second)
            if first_elem == capability_elem:
                # yield second_elem
                cap_constraints.append(second_elem)
            elif second_elem == capability_elem:
                # yield first_elem
                cap_constraints.append(first_elem)
        return cap_constraints

    async def check_skill_elem_by_capability(self, cap_type, cap_elem, skill_data):
        """
        This method checks if a skill SubmodelElement is defined associated to a Capability using given skill data.

        Args:
            cap_type (str): type of the capability (AgentCapabilities or AssetCapabilities).
            cap_elem (basyx.aas.model.Capability): capability Python object.
            skill_data (dict): data of the skill.

        Returns:
            bool: result of the check (True if the skill is in the global variable, linked to the capability)
        """
        # First, the skill id_short will be checked
        required_skill_name = skill_data[CapabilitySkillACLInfo.REQUIRED_SKILL_NAME]
        skill_elem = (await self.get_capability_dict_by_type(cap_type))[cap_elem]['skillObject']
        if skill_elem.id_short != required_skill_name:
            _logger.warning("The given skill does not exist in this DT.")
            return False
        # Then, the skill SubmodelElement type will be checked
        required_skill_sme_type = skill_data[CapabilitySkillACLInfo.REQUIRED_ELEMENT_TYPE]
        if skill_elem.__class__.__name__ != required_skill_sme_type:
            _logger.warning("The given skill SubmodelElement type is not the same as the element exists in this DT.")
            return False
        # The skill parameters will be also checked
        # TODO PROXIMO PASO: PENSAR COMO SE HARIA CON VARIOS PARAMETROS (una opcion es definir en el JSON 'inputs' como
        #  listas y que haya que recorrer cada uno de los parametros, tanto de entrada como de salida. Habra que
        #  comprobar que todos existen como elemento Python buscandolos por el id_short. En el caso de que alguno no
        #  esté, el checking falla)
        required_skill_parameters = skill_data[CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]
        if 'input' in required_skill_parameters:
            if await self.check_element_exist_in_namespaceset_by_id_short(skill_elem.input_variable,
                                                                          required_skill_parameters['input']) is False:
            # if required_skill_parameters['input'] != skill_elem.input_variable.id_short:
                _logger.warning("The given skill does not have the same input parameter as the element exists in this DT.")
                return False
        if 'output' in required_skill_parameters:
            if await self.check_element_exist_in_namespaceset_by_id_short(skill_elem.output_variable,
                                                                          required_skill_parameters['output']) is False:
            # if required_skill_parameters['output'] != skill_elem.output_variable.id_short:
                _logger.warning("The given skill does not have the same output parameter as the element exists in this DT.")
                return False
        # When all checks have been passed, the given skill is valid
        return True

    async def get_skill_data_by_capability(self, required_cap_elem, required_data):
        """
        This method gets the Skill SubmodelElement of a given Capability element.
        Args:
            required_cap_elem (basyx.aas.model.Capability): capability Python object.
            required_data (str): required data of the skill elem (Python object or SkillInterface element)

        Returns:
            basyx.aas.model.SubmodelElement: skill SME in form of Python object (None if the Capability does not exist).
        """
        for cap_info_dict in self.capabilities_skills_dict.values():
            for cap_elem, cap_info in cap_info_dict.items():
                if cap_elem == required_cap_elem:
                    return cap_info[required_data]
        return None

    async def get_skill_interface_by_skill_elem(self, skill_elem):
        """
        This method gets the interfaces associated to a skill.

        Args:
            skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

        Returns:
            generator: the interface of the selected skill in form of Python object.
        """
        rels_skill_interfaces = await self.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_SKILL_SKILL_INTERFACE)
        for rel in rels_skill_interfaces:
            first_elem = await self.get_object_by_reference(rel.first)
            second_elem = await self.get_object_by_reference(rel.second)
            if first_elem == skill_elem:
                return second_elem
            elif second_elem == skill_elem:
                return first_elem


    async def capability_checking_from_acl_request(self, required_capability_data):
        """
        This method checks if the DT has a capability required in an ACL message.

        Args:
            required_capability_data (dict): all the information about the required capability

        Returns:
            bool: result of the check (True if the DT can perform the capability)
        """
        required_cap_name = required_capability_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
        required_cap_type = required_capability_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE]
        # It will be checked if the type is among the available options
        if required_cap_type not in CapabilitySkillOntology.CAPABILITY_TYPE_POSSIBLE_VALUES:
            _logger.warning("The required capability does not have a valid type.")
            return False
        # It will be checked if the capability is among the defined in this DT
        capability_elem = await self.get_capability_by_id_short(required_cap_type, required_cap_name)
        if capability_elem is None:
            _logger.warning("A capability has been requested that this DT does not have.")
            return False
        # TODO quedan por analizar las constraints
        # TODO PROXIMO PASO: para analizar las constraint, simplemente se comprobará si el nombre de la constraint se
        #  ha definido en la capacidad requerida (en este paso no se ejecuta la capacidad, por lo que las constraints no se analizan)
        # It will be also checked the skill id_short
        required_skill_data = required_capability_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INFO]
        if await self.check_skill_elem_by_capability(required_cap_type, capability_elem, required_skill_data) is False:
            _logger.warning("A capability has been requested that its skill does not exist in this DT.")
            return False
        # When all checks have been passed, the given skill is valid
        return True


