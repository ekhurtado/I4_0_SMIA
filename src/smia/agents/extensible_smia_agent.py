import asyncio
import logging

import basyx.aas.model
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, TimeoutBehaviour, PeriodicBehaviour, FSMBehaviour

from smia import AASModelUtils
from smia.agents.smia_agent import SMIAAgent
from smia.assetconnection.asset_connection import AssetConnection
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class ExtensibleSMIAAgent(SMIAAgent):
    """
    This agent offers some extension mechanisms to add own code to the base :term:`SMIA` agent.
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.extended_agent_capabilities = []

    # TODO The features that shall be offered are:
    #  1. define and add new connections to the asset (i.e., new communication protocols)
    #  2. define and add new agent capabilities to increase its intelligence and autonomy.
    #  3. define and add new agent services

    def add_new_agent_capability(self, behaviour_class):
        """
        This method adds a new :term:`agent capability <Capability>` to SMIA to increase its intelligence and autonomy.
        The new capability is added as a SPADE behavior instance. If it is not a valid behavior (within the types
        offered by :term`SPADE`), it cannot be added.

        Args:
            behaviour_class: SPADE behaviour class instance.
        """
        if isinstance(behaviour_class, (CyclicBehaviour, PeriodicBehaviour, OneShotBehaviour, TimeoutBehaviour,
                                        FSMBehaviour)):
            self.extended_agent_capabilities.append(behaviour_class)
            _logger.info("Added a new agent capability to SMIA: {}".format(behaviour_class))
        else:
            _logger.warning("The new agent capability [{}] cannot be added because it is not a SPADE behavior "
                            "class.".format(behaviour_class))

    def add_new_agent_service(self, service_id, service_method):
        """
        This method adds a new agent service to SMIA to increase its intelligence and autonomy. The new service is added
         as a Python method that will be called when the service is requested.

        Args:
            service_id (str): identifier of the new service (id or idShort of the related AAS SubmodelElement).
            service_method: Python method that will be called when the service is requested.
        """
        if (service_id is None) or (service_method is None):
            _logger.warning("The new agent service cannot be added because the service identifier or method were not "
                            "provided.")
        else:
            asyncio.run(self.agent_services.save_agent_service(service_id, service_method))
            _logger.info("Added a new agent service to SMIA: {}".format(service_id))

    def add_new_asset_connection(self, aas_interface_id_short, asset_connection_class):
        """
        This method adds a new asset connection to SMIA. The new connection is added by the instance class inherited
        from the official SMIA generic class named 'AssetConnection' and the associated AAS interface element. To
        correctly perform the addition, make sure that the given instance is inherited from this class and that the
        idShort represents the valid AAS SubmodelElement of the related interface within the
        'AssetInterfacesDescription' submodel .

        Args:
            aas_interface_id_short (str): identifier of the related AAS interface element in the form of idshort of the SubmodelElement.
            asset_connection_class: instance class to be added as a new asset connection (inheriting from 'AssetConnection').
        """
        if not isinstance(asset_connection_class, AssetConnection):
            _logger.warning("The new asset connection [{}] cannot be added because it does not inherit from the "
                            "official SMIA class 'AssetConnection'.".format(asset_connection_class))
            return
        if aas_interface_id_short is None:
            _logger.warning("The new asset connection [{}] cannot be added because the idShort of the related AAS "
                            "interface element was not provided.".format(asset_connection_class))
            return

        async def check_and_save_asset_connection():
            object_store = AASModelUtils.read_aas_model_object_store()
            await self.aas_model.set_aas_model_object_store(object_store)
            aid_submodel = await self.aas_model.get_submodel_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
            if (aid_submodel is None) or (not isinstance(aid_submodel, basyx.aas.model.Submodel)):
                _logger.warning("The standardized submodel 'AssetInterfacesDescription' does not exist in the AAS "
                                "model.".format(asset_connection_class))
                return
            try:
                aas_interface_elem = aid_submodel.get_referable(aas_interface_id_short)
                aas_interface_elem_ref = basyx.aas.model.ModelReference.from_referable(aas_interface_elem)

                # At this point, all checks have been passed, so the new asset connection can be added.
                await self.save_asset_connection_class(aas_interface_elem_ref, asset_connection_class)
                self.conns = {aas_interface_elem_ref: asset_connection_class}
            except KeyError as e:
                _logger.warning(e)
                _logger.warning("The new asset connection [{}] cannot be added because the idShort of the related AAS "
                                "interface element is not valid.".format(asset_connection_class))
                return

        asyncio.run(check_and_save_asset_connection())
        _logger.info("Added a new asset connection to SMIA: {}".format(aas_interface_id_short))

