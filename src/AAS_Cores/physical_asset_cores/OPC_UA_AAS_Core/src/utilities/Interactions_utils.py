"""
File to group useful methods related to interactions between AAS Manager and AAS Core.
"""
import calendar
import json
import time

from kafka import KafkaConsumer, TopicPartition, KafkaProducer
from kafka.errors import KafkaError

from utilities.AASArchive_utils import file_to_json, update_json_file
from utilities.AASarchiveInfo import AASarchiveInfo
from utilities.KafkaInfo import KafkaInfo


def get_next_svc_request():
    print("Obtaining the next service request from AAS Manager.")
    svc_requests_file_path = AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    if len(svc_requests_json['serviceRequests']) != 0:
        return svc_requests_json['serviceRequests'][len(svc_requests_json['serviceRequests']) - 1]
    else:
        return None


def delete_svc_request(svc_request_object):
    print("Deleting the service request with ID " + str(svc_request_object['interactionID']) + " from AAS Archive.")
    svc_requests_file_path = AASarchiveInfo.MANAGER_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_REQUEST_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    for i in range(len(svc_requests_json['serviceRequests'])):
        if svc_requests_json['serviceRequests'][i]["interactionID"] == svc_request_object['interactionID']:
            svc_requests_json['serviceRequests'].pop(i)
            break
    update_json_file(svc_requests_file_path, svc_requests_json)

def create_response_json_object(svc_request_info, svc_params = None):

    response_json =  {
        'interactionID': svc_request_info['interactionID'],
        'thread': svc_request_info['thread'],
        'serviceType': svc_request_info['serviceType'],
        'serviceID': svc_request_info['serviceID'],
        'serviceData': {
            'serviceStatus': 'Completed',
            'serviceCategory': 'service-response',
            'timestamp': calendar.timegm(time.gmtime())
        }
    }
    if svc_params is not None:
        response_json['serviceData']['serviceParams'] = svc_params
    return response_json

def add_new_svc_response(new_response_json):
    """
    This method adds a new service response to the related service interaction file of the core and updates it
    in the AAS Archive.

    Args:
        new_response_json: The service requests content in JSON format.
    """

    # Get the content of the service requests interaction file
    svc_requests_file_path = AASarchiveInfo.CORE_INTERACTIONS_FOLDER_PATH + AASarchiveInfo.SVC_RESPONSE_FILE_SUBPATH
    svc_requests_json = file_to_json(svc_requests_file_path)
    if svc_requests_json is None:
        svc_requests_json = {'serviceResponses': [new_response_json]}
    else:
        svc_requests_json['serviceResponses'].append(new_response_json)

    update_json_file(svc_requests_file_path, svc_requests_json)

# ---------------------
# Kafka related methods (Intra AAS interaction platform)
# ---------------------
def send_interaction_msg_to_manager(client_id, msg_key, msg_data):
    """
    This method sends a Kafka interaction message to the AAS Manager. To this end, the AAS Core will publish messages
    in its partition, where the AAS Core will be listening.

    Args:
        client_id (str): the id of the client of the Kafka producer.
        msg_key (str): the key of the Kafka message.
        msg_data: the data of the Kafka message.

    Returns:
        str: shipment status
    """
    # First, the Kafka producer is created
    kafka_producer = KafkaProducer(bootstrap_servers=[KafkaInfo.KAFKA_SERVER_IP + ':9092'],
                                   client_id=client_id,
                                   value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                   key_serializer=str.encode,
                                   )
    print("Kafka producer created. Sending message to AAS Manager through topic " + KafkaInfo.KAFKA_TOPIC +
          " and partition " + str(KafkaInfo.CORE_TOPIC_PARTITION) + "...")
    result = kafka_producer.send(KafkaInfo.KAFKA_TOPIC, value=msg_data, key=msg_key,
                                 partition=KafkaInfo.CORE_TOPIC_PARTITION)
    print("Message sent to topic " + KafkaInfo.KAFKA_TOPIC)
    print(str(result))
    try:
        record_metadata = result.get(timeout=10)
        print("Kafka producer has sent the message. Producer closing...")
        kafka_producer.close()
        return "OK"
    except KafkaError as e:
        print("ERROR")
        print(e)
        kafka_producer.close()
        return None


def create_interaction_kafka_consumer(client_id):
    """
    This method creates the Kafka consumer for subscribing to AAS Manager partition in the topic of the AAS.
    Args:
        client_id (str): the id of the client of the Kafka consumer.

    Returns:
        KafkaConsumer: the object of the Kafka consumer.
    """

    kafka_consumer_manager_partition = KafkaConsumer(bootstrap_servers=[KafkaInfo.KAFKA_SERVER_IP + ':9092'],
                                                     client_id=client_id,
                                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                                     enable_auto_commit=True,
                                                     group_id='i4-0-smia-cores'
                                                     )
    kafka_consumer_manager_partition.assign([TopicPartition(KafkaInfo.KAFKA_TOPIC, KafkaInfo.MANAGER_TOPIC_PARTITION)])

    return kafka_consumer_manager_partition
