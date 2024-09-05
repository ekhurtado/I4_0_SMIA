import json
import logging
import time

from spade.behaviour import CyclicBehaviour

from logic import Services_utils, Interactions_utils
from utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


class InteractionHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the interaction messages that the AAS Manager will receive
    from the AAS Core.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("InteractionHandlingBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # First of all, the Kafka consumer is created, who will receive the messages.
        kafka_consumer_core_partition = Interactions_utils.create_interaction_kafka_consumer('i4-0-smia-manager')
        await kafka_consumer_core_partition.start()

        _logger.info("The AAS Manager is listening for interaction messages from the AAS Core...")
        try:
            async for msg in kafka_consumer_core_partition:
                _logger.interactioninfo("New AAS Core message!")
                _logger.interactioninfo("   |__ msg: " + str(msg))

                # We get the key (as it is in bytes, we transform it into string) and the body of Kafka's message
                msg_key = msg.key.decode("utf-8")
                msg_json_value = msg.value

                match msg_key:
                    case 'core-status':
                        _logger.interactioninfo("The AAS Manager has received an update of the AAS Core status.")
                        # TODO
                    case 'core-service-request':
                        _logger.interactioninfo("The AAS Manager has received a service request from the AAS Core.")
                        # TODO
                    case 'core-service-response':
                        _logger.interactioninfo("The AAS Manager has received a service response from the AAS Core.")
                        _logger.interactioninfo("The service with id " + str(msg_json_value['interactionID']) +
                                     " has been answered from the AAS Core to the AAS Manager. Data of the response: "
                                     + str(msg_json_value))
        finally:
            _logger.info("Finalizing Kafka Consumer...")
            await kafka_consumer_core_partition.stop()

