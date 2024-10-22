import asyncio

import basyx.aas.model.submodel
from basyx.aas.util import traversal


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

