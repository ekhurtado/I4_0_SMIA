package utilities;

import information.KafkaInfo;
import logic.AASCore;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.json.simple.JSONObject;

import java.util.Collections;
import java.util.Properties;

public class InteractionUtils {
    /**
     * This class contains the methods related to AAS Manager-Core interactions.
     */

    // ------------------------
    // Methods related to Kafka
    // ------------------------
    public static KafkaConsumer createInteractionKafkaConsumer() {

        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaInfo.KAFKA_SERVER_IP + ":9092");
        props.put(ConsumerConfig.CLIENT_ID_CONFIG, "i4-0-smia-core");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "i4-0-smia-cores");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");  // Start reading at the earliest offset
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");

        KafkaConsumer<String, String> kafkaConsumerPartitionManager = new KafkaConsumer<>(props);
        kafkaConsumerPartitionManager.assign(Collections.singletonList(
                new TopicPartition(KafkaInfo.KAFKA_TOPIC, KafkaInfo.MANAGER_TOPIC_PARTITION)));
        return kafkaConsumerPartitionManager;
    }

    public static String sendInteractionMsgToManager(String msg_key, JSONObject msg_data) {

        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaInfo.KAFKA_SERVER_IP + ":9092");
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "i4-0-smia-core");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        KafkaProducer<String, String> kafkaProducerPartitionCore = new KafkaProducer<>(props);
        AASCore.LOGGER.info("Kafka Producer created");

        ProducerRecord<String, String> record = new ProducerRecord<>(KafkaInfo.KAFKA_TOPIC,
                KafkaInfo.CORE_TOPIC_PARTITION, msg_key, msg_data.toString());
        kafkaProducerPartitionCore.send(record);
        kafkaProducerPartitionCore.flush();
        AASCore.LOGGER.info("Kafka message sent!");
        kafkaProducerPartitionCore.close();

        return "OK";
    }

    public static void sendAASCoreStatusToManager(String currentState) {
        AASCore.LOGGER.info("Sending current state [{}] to the AAS Manager through Kafka...", currentState);
        JSONObject msg_data = new JSONObject();
        msg_data.put("status", currentState);
        String result = sendInteractionMsgToManager("core-status", msg_data);
        if (!result.equals("OK")) {
            System.err.println("Interaction AAS Manager-Core not working");
        }
    }

    public static void sendInteractionRequestToManager(JSONObject msg_data) {
        AASCore.LOGGER.info("Sending Intra AAS interaction request to the AAS Manager through Kafka...");
        String result = sendInteractionMsgToManager("core-service-request", msg_data);
        if (!result.equals("OK")) {
            System.err.println("Interaction AAS Manager-Core not working");
        }
        // After the request has been made, the interaction_id is increased
        AASCore.getInstance().increaseInteractionIDNum();
    }

    public static JSONObject createInteractionObjectForManagerRequest(String serviceType, String serviceID, JSONObject serviceParams) {
        JSONObject interactionJSON = new JSONObject();
        interactionJSON.put("interactionID", AASCore.getInstance().getInteractionID());
        interactionJSON.put("thread", createThread());
        interactionJSON.put("serviceType", serviceType);
        interactionJSON.put("serviceID", serviceID);

        JSONObject serviceDataJSON = new JSONObject();
        serviceDataJSON.put("serviceCategory", "service-request");
        serviceDataJSON.put("timestamp", System.currentTimeMillis() / 1000);
        if (serviceParams != null)
            serviceDataJSON.put("serviceParams", serviceParams);
        interactionJSON.put("serviceData", serviceDataJSON);

        return interactionJSON;
    }

    public static String createThread() {
        String randomString = RandomStringUtils.random(5, true, true);
        return AASCore.getInstance().getAASID() + "-" + randomString;
    }

}
