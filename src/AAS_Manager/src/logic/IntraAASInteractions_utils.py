"""This class groups the methods related to the Intra AAS interactions between the Manager and the Core."""

import calendar
import json
import logging
from datetime import datetime
import time

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, TopicPartition

from utilities.AASarchiveInfo import AASarchiveInfo
from utilities.AAS_Archive_utils import file_to_json, update_json_file
from utilities.GeneralUtils import GeneralUtils
from utilities.KafkaInfo import KafkaInfo

_logger = logging.getLogger(__name__)


# --------------------------------------------
# Methods related to requests (by AAS Manager)
# --------------------------------------------
def create_svc_request_interaction_json(interaction_id, request_data):
    """
    This method creates a service request JSON object for an :term:`Intra AAS Interaction`.

    Args:
        interaction_id (int): Identifier ID of the interaction. It is composed by the entity
        that is requesting the service and an incremental value that represent the number of requested services by this entity.
        request_data (dict): All the information of the request of the service in JSON format.

    Returns:
        dict: a JSON object with the service request information.
    """
    svc_request_json = {"interactionID": interaction_id,
                        "thread": request_data['thread'],
                        "serviceID": request_data['serviceID'],
                        "serviceType": request_data['serviceType'],
                        "serviceData": request_data['serviceData']
                        }

    svc_request_json['serviceData']['timestamp'] = GeneralUtils.get_current_timestamp()
    return svc_request_json


def add_new_svc_request(new_request_json):
    """
    This method adds a new service request to the related service interaction file of the manager and updates it
    in the AAS Archive.

    Args:
        new_request_json: The service requests content in JSON format.
    """

    # Get the content of the service requests interaction file
    svc_requests_file_path = AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    if svc_requests_json is None:
        svc_requests_json = {'serviceRequests': [new_request_json]}
    else:
        svc_requests_json['serviceRequests'].append(new_request_json)

    update_json_file(svc_requests_file_path, svc_requests_json)


def get_svc_request_info(interaction_id):
    """
    This method gets the information of a service request.

    Args:
        interaction_id (int): Identifier of the interaction.

    Returns:
        dict: the information of the service request in JSON format.
    """
    svc_requests_json = file_to_json(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH +
                                     AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH)
    for i in svc_requests_json['serviceRequests']:
        if i['interactionID'] == interaction_id:
            return i
    return None


# --------------------------------------------
# Methods related to responses (from AAS Core)
# --------------------------------------------
def get_svc_response_info(interaction_id):
    """
    This method gets the information of a response from the AAS Core related to a request made by the AAS Manager.

    Args:
        interaction_id (int): Identifier of the interaction.

    Returns:
        dict: the information of the service request in JSON format.
    """
    svc_responses_json = file_to_json(
        AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH)
    for i in svc_responses_json['serviceResponses']:
        if i['interactionID'] == interaction_id:
            return i
    return None


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
    svc_request_info, svc_response_info = get_svc_info(requested_entity, interaction_id_num)

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
    log_file_json = file_to_json(AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + svc_type_log_file_name)

    # Add the structure in the file
    log_file_json.append(log_structure)
    update_json_file(file_path=AASarchiveInfo.SVC_LOG_FOLDER_PATH + '/' + svc_type_log_file_name, content=log_file_json)
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


async def send_interaction_msg_to_core(client_id, msg_key, msg_data):
    """
    This method sends a Kafka interaction message to the AAS Core. To this end, the AAS Manager will publish messages
    in its partition, where the AAS Core will be listening.

    Args:
        client_id (str): the id of the client of the Kafka producer.
        msg_key (str): the key of the Kafka message.
        msg_data: the data of the Kafka message.

    Returns:
        str: shipment status
    """
    # First, the Kafka producer is created
    kafka_producer = AIOKafkaProducer(bootstrap_servers=[KafkaInfo.KAFKA_SERVER_IP + ':9092'],
                                      client_id=client_id,
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                      key_serializer=str.encode,
                                      )
    await kafka_producer.start()
    try:
        # The AAS Manager only publish messages in its partition, where the AAS Core will be listening.
        await kafka_producer.send_and_wait(KafkaInfo.KAFKA_TOPIC, value=msg_data,
                                           key=msg_key,
                                           partition=KafkaInfo.MANAGER_TOPIC_PARTITION)
        _logger.info("AAS Manager successfully published an interaction message: key [" + msg_key + "],"
                     " data [" + str(msg_data) + "]")
    finally:
        # Wait for all pending messages to be delivered or expire.
        await kafka_producer.stop()
        return "OK"


# -------------
# Other methods
# -------------
def get_svc_info(requested_entity, interaction_id):
    """
    This method obtains the information of the service considering the entity that has requested the service. In the
    entity is Manager it has to search in Manager requests and Core responses, and in the case of being the Core the
    one that has made the request, the opposite.

    Args:
        requested_entity (str): The entity that has requested the service, to know in which interaction files to search.
        interaction_id (int): Identifier of the interaction.

    Returns:
         dict: Information of the service request in JSON format
         dict: Information of the service response in JSON format.
    """

    if requested_entity == "Manager":
        return get_svc_request_info(interaction_id), get_svc_response_info(interaction_id)
    elif requested_entity == "Core":
        # In this case, it has to search in the opposite files (request of Core and response of Manager)
        svc_requests_json = file_to_json(AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH +
                                         AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH)
        svc_request_info = None
        for i in svc_requests_json['serviceRequests']:
            if i['interactionID'] == interaction_id:
                svc_request_info = i
                break

        svc_responses_json = file_to_json(AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH +
                                          AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH)
        svc_response_info = None
        for i in svc_responses_json['serviceResponses']:
            if i['interactionID'] == interaction_id:
                svc_response_info = i
                break

        return svc_request_info, svc_response_info
