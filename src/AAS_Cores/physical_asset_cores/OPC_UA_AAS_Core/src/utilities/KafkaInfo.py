class KafkaInfo:
    """This class contains all information about Kafka, which is the communication mechanism for AAS Manager-Core
    interactions."""

    # Kafka broker related information
    KAFKA_SERVER_IP = 'mi-cluster-mensajeria-kafka-bootstrap.kafka-ns'  # TODO think how to pass to AAS Manager (in AAS XML definition???)

    # Kafka topic related information
    KAFKA_TOPIC = 'aas-opcua-test01'  # TODO check if it is the ID of the AAS
    MANAGER_TOPIC_PARTITION = 0
    CORE_TOPIC_PARTITION = 1
