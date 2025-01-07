"""This class groups the methods related to the Intra AAS interactions between the Manager and the Core."""

import json
import logging
from datetime import datetime

from aiokafka import AIOKafkaConsumer, TopicPartition

from smia.utilities.general_utils import SMIAGeneralInfo, GeneralUtils
from smia.utilities.smia_archive_utils import file_to_json, update_json_file
from smia.utilities.kafka_info import KafkaInfo

_logger = logging.getLogger(__name__)


# ----------------------------
# Methods related to responses
# ----------------------------
def save_svc_info_in_log_file(requested_entity, svc_type_log_file_name, interaction_id_num):
    """
    This method saves the information of a service request in the associated log file.

    Args:
        requested_entity (str): The entity that has requested the service, to know in which interaction files to search.
        svc_type_log_file_name (str): The log file name of the service type.
        interaction_id_num (int): Identifier of the interaction.
    """

    # Get the information about the request and response
    svc_request_info, svc_response_info = None  # TODO falta pensar como conseguirlo, ya no hay interactionID

    # Create the JSON structure
    log_structure = {
        'level': 'INFO',
        'interactionID': interaction_id_num,
        'serviceStatus': svc_response_info['serviceStatus'],
        'serviceInfo': {
            'serviceID': svc_request_info['serviceID'],
            'serviceType': svc_request_info['serviceType'],
            'requestTimestamp': str(datetime.fromtimestamp(svc_request_info['serviceData']['timestamp'])),
            'responseTimestamp': str(datetime.fromtimestamp(svc_response_info['serviceData']['timestamp']))
        }
    }
    # If some data has been requested, added to the structura
    if 'requestedData' in svc_request_info['serviceData'].keys():
        requested_data_name = svc_request_info['serviceData']['requestedData']
        svc_data_json = {'requestedData': requested_data_name,
                         'dataValue': svc_response_info['serviceData'][requested_data_name]}
        log_structure['serviceInfo']['serviceData'] = svc_data_json

    # Get the content of LOG file
    log_file_json = file_to_json(SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + svc_type_log_file_name)

    # Add the structure in the file
    log_file_json.append(log_structure)
    update_json_file(file_path=SMIAGeneralInfo.SVC_LOG_FOLDER_PATH + '/' + svc_type_log_file_name, content=log_file_json)
    _logger.info("Service information related to interaction " + str(interaction_id_num) + " added in log file.")


# ------------------------
# Methods related to Kafka
# ------------------------
def create_interaction_kafka_consumer(client_id):
    """
    This method creates the Kafka consumer for subscribing to AAS Core partition in the topic of the AAS.
    Args:
        client_id (str): the id of the client of the Kafka consumer.

    Returns:
        AIOKafkaConsumer: the object of the Kafka consumer.
    """

    kafka_consumer_core_partition = AIOKafkaConsumer(bootstrap_servers=[KafkaInfo.KAFKA_SERVER_IP + ':9092'],
                                                     client_id=client_id,
                                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                                     enable_auto_commit=True,
                                                     group_id='i4-0-smia-managers'
                                                     )
    kafka_consumer_core_partition.assign([TopicPartition(KafkaInfo.KAFKA_TOPIC, KafkaInfo.CORE_TOPIC_PARTITION)])

    return kafka_consumer_core_partition
