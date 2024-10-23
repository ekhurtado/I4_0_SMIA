import asyncio
import logging
import basyx.aas.model.submodel
from basyx.aas.util import traversal

from utilities.CapabilitySkillOntology import CapabilitySkillOntology

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
            generator(basyx.aas.model.RelationshipElement): generator with all Relationship SubmodelElements.
        """
        for aas_object in self.aas_model_object_store:
            if isinstance(aas_object, basyx.aas.model.Submodel):
                for submodel_element in traversal.walk_submodel(aas_object):
                    if isinstance(submodel_element, basyx.aas.model.RelationshipElement):
                        for semantic_id in traversal.walk_semantic_ids_recursive(submodel_element):
                            for reference in semantic_id.key:
                                if str(reference) == rel_semantic_id_external_ref:
                                    yield submodel_element

    # ---------------------------------------------------------------
    # Methods related to Capability-Skill ontology and AAS meta-model
    # ---------------------------------------------------------------
    async def get_capability_associated_constraints(self, capability_elem):
        """
        This method gets the constraints associated to a capability.

        Args:
            capability_elem (basyx.aas.model.Capability): capability Python object.

        Returns:
            generator: generator with all constraints of the selected capability in form of Python objects.
        """
        rels_cap_constraints = self.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_CAPABILITY_CAPABILITY_CONTRAINT)
        for rel in rels_cap_constraints:
            first_elem = self.get_object_by_reference(rel.first)
            second_elem = self.get_object_by_reference(rel.second)
            if first_elem == capability_elem:
                yield second_elem
            elif second_elem == capability_elem:
                yield first_elem

    async def get_skill_interface_element(self, skill_elem):
        """
        This method gets the interfaces associated to a skill.

        Args:
            skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

        Returns:
            generator: the interface of the selected skill in form of Python object.
        """
        rels_skill_interfaces = self.get_relationship_elements_by_semantic_id(
            CapabilitySkillOntology.SEMANTICID_REL_SKILL_SKILL_INTERFACE)
        for rel in rels_skill_interfaces:
            first_elem = self.get_element_with_reference(rel.first)
            second_elem = self.get_element_with_reference(rel.second)
            if first_elem == skill_elem:
                return second_elem
            elif second_elem == skill_elem:
                return first_elem
