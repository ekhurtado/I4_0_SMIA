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
        pass

    @abc.abstractmethod
    async def connect_with_asset(self):
        pass

    @abc.abstractmethod
    async def send_msg_to_asset(self, interaction_metadata, msg):
        pass

    @abc.abstractmethod
    async def receive_msg_from_asset(self):
        pass
