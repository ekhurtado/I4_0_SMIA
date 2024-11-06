import abc
from enum import Enum, unique


class AssetConnection(metaclass=abc.ABCMeta):
    """
    This class is an abstract class for all AssetConnections.
    TODO desarrollarlo mas
    """

    @unique
    class ArchitectureStyle(Enum):
        PUBSUB = 0
        CLIENTSERVER = 1
        NOTAPPLICABLE = 2

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.architecture_style: AssetConnection.ArchitectureStyle = AssetConnection.ArchitectureStyle.NOTAPPLICABLE

    @abc.abstractmethod
    async def configure_connection_by_aas_model(self, interface_aas_elem):
        """
        This method configures de Asset Connection using the interface element defined in the AAS model.

        Args:
            interface_aas_elem (basyx.aas.model.SubmodelElement): element of the AAS model with the asset interface information.
        """
        pass

    @abc.abstractmethod
    async def check_asset_connection(self):
        pass

    @abc.abstractmethod
    async def connect_with_asset(self):
        pass

    @abc.abstractmethod
    async def execute_skill_by_asset_service(self, interaction_metadata, skill_params_exposure_elems, skill_input_params= None, skill_output_params=None):
        """
        This method sends a message to the asset and returns the response. The connection of the interface of the asset
        is already configured in 'configure_connection_by_aas_model' method, but the interaction metadata is provided
        in form of a Python object of AAS model (SubmodelElement).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElement): element of the AAS model with all metadata for the interaction with the asset.
            skill_params_exposure_elems (list(basyx.aas.model.SubmodelElement)): submodel elements that exposes all skill parameters.
            skill_input_params (dict): skill input parameters in form of JSON object (None if the skill does not have inputs).
            skill_output_params (dict): skill output parameters in form of JSON object (None if the skill does not have outputs).

        Returns:
            object: response information defined in the interaction metadata.
        """
        pass

    @abc.abstractmethod
    async def execute_asset_service(self, interaction_metadata, service_data=None):
        """
        This method sends a message to the asset and returns the response. The connection of the interface of the asset
        is already configured in 'configure_connection_by_aas_model' method, but the interaction metadata is provided
        in form of a Python object of AAS model (SubmodelElement).

        Args:
            interaction_metadata (basyx.aas.model.SubmodelElement): element of the AAS model with all metadata for the interaction with the asset.
            service_data: object with the data of the service

        Returns:
            object: response information defined in the interaction metadata.
        """
        pass

    @abc.abstractmethod
    async def receive_msg_from_asset(self):
        pass
