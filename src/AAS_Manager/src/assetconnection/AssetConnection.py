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
    def configure_connection(self, configuration_data):
        pass

    @abc.abstractmethod
    def connect_with_asset(self):
        pass

    @abc.abstractmethod
    def send_msg_to_asset(self, msg):
        pass

    @abc.abstractmethod
    def receive_msg_from_asset(self):
        pass
