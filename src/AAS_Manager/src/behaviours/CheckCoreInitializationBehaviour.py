import json
import logging
import os

from aiokafka import AIOKafkaConsumer, TopicPartition
from spade.behaviour import CyclicBehaviour

from logic import IntraAASInteractions_utils
from utilities.AAS_Archive_utils import file_to_json
from utilities.AASarchiveInfo import AASarchiveInfo
from utilities.KafkaInfo import KafkaInfo

_logger = logging.getLogger(__name__)


class CheckCoreInitializationBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour responsible for check that the AAS Core has been initialized.
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

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # TODO this code is for the interaction through JSON (it has to be removed)
        # # If the file does not exist the behaviour continues to start and check again
        # if os.path.isfile(AASarchiveInfo.CORE_STATUS_FILE_PATH) is True:
        #     core_status_json = file_to_json(AASarchiveInfo.CORE_STATUS_FILE_PATH)
        #     # If the file exists, but the JSON has not been created properly, the AAS Core is not ready yet.
        #     if core_status_json is not None:
        #         if core_status_json['status'] != "Initializing":
        #             # If the status is not "Initializing" the AAS Core is ready, so the behaviour is finished
        #             _logger.info('AAS Core has initialized, so the AAS Manager can be switched to the run state.')
        #             self.kill()

        # TODO check if it is working with Kafka

        #  To check the state of the AAS Core, the AAS Manager will get the
        #  information subscribing to the AAS topic of Kafka, in this case to the partition related to the AAS Core
        kafka_consumer_core_partition = Interactions_utils.create_interaction_kafka_consumer('i4-0-smia-manager')
        await kafka_consumer_core_partition.start()
        _logger.info("Listening for AAS Core messages in topic " + KafkaInfo.KAFKA_TOPIC + " awaiting status "
                                                                                           "information...")

        # Since the status message may arrive before the consumer is created (because the AAS Core has been started
        # before the AAS Manager) the messages have to be read from the beginning.
        await kafka_consumer_core_partition.seek_to_beginning()

        # partitions = kafka_consumer_core_partition.assignment()
        # topic_partitions = [TopicPartition(tp.topic, tp.partition) for tp in partitions]
        # committed_offsets = await kafka_consumer_core_partition.committed(topic_partitions[0])
        # print(topic_partitions[0])
        # print("PRUEBA CONSEGUIR OFFSET")
        # print(committed_offsets)

        try:
            async for msg in kafka_consumer_core_partition:
                _logger.info("New AAS Core message!")
                _logger.info("   |__ msg: " + str(msg))

                # We get the key (as it is in bytes, we transform it into string) and the body of Kafka's message
                msg_key = msg.key.decode("utf-8")
                msg_json_value = msg.value

                if msg_key == 'core-status':
                    print("The AAS Core status information has been received.")
                    if msg_json_value['status'] != "Initializing":
                        # If the status is not "Initializing" the AAS Core is ready, so the behaviour is finished
                        _logger.info('AAS Core has initialized, so the AAS Manager can be switched to the run state.')
                        await kafka_consumer_core_partition.stop()
                        self.kill()
        finally:
            _logger.info("Finalizing Kafka Consumer...")
            await kafka_consumer_core_partition.stop()
