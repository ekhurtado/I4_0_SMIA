package utilities;

import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import java.util.Collections;
import java.util.Properties;

public class InteractionsUtils {


    // ------------------------
    // Methods related to files
    // ------------------------
    public static KafkaConsumer createInteractionKafkaConsumer() {

        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaInfo.KAFKA_SERVER_IP + ":9092");
        props.put(ConsumerConfig.CLIENT_ID_CONFIG, "i4-0-smia-core");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

        KafkaConsumer<String, String> kafkaConsumerPartitionManager = new KafkaConsumer<>(props);
        kafkaConsumerPartitionManager.assign(Collections.singletonList(
                new TopicPartition(KafkaInfo.KAFKA_TOPIC, KafkaInfo.MANAGER_TOPIC_PARTITION)));
        return kafkaConsumerPartitionManager;
    }

    public static String sendInteractionMsgToManager(String msg_key, JSONObject msg_data) {

        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaInfo.KAFKA_SERVER_IP + ":9092");
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "i4-0-smia-core");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

        KafkaProducer<String, String> kafkaProducerPartitionCore = new KafkaProducer<>(props);
        ProducerRecord<String, String> record = new ProducerRecord<>(KafkaInfo.KAFKA_TOPIC,
                KafkaInfo.CORE_TOPIC_PARTITION, msg_key, msg_data.toString());
        kafkaProducerPartitionCore.send(record);
        kafkaProducerPartitionCore.flush();

        return "OK";
    }

    public static void changeStatus(String newStatus) {
        JSONObject statusFileJSON = fileToJSON(AAS_ArchiveInfo.coreStatusFilePath);
        statusFileJSON.put("status", newStatus);
        updateFile(AAS_ArchiveInfo.coreStatusFilePath, statusFileJSON);
    }

    public static String getManagerStatus() {
        JSONParser parser = new JSONParser();
        try (Reader reader = new FileReader(AAS_ArchiveInfo.managerStatusFilePath)) {
            JSONObject statusFileJSON = (JSONObject) parser.parse(reader);
            return statusFileJSON.get("status").toString();
        }  catch (FileNotFoundException e) {
            return null;
        } catch (IOException | ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public static JSONObject fileToJSON(String filePath) {
        JSONParser parser = new JSONParser();
        try (Reader reader = new FileReader(filePath)) {
            return (JSONObject) parser.parse(reader);
        } catch (IOException | ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public static void updateFile(String filePath, JSONObject content) {
        try (FileWriter file = new FileWriter(filePath)) {
            file.write(content.toJSONString());
            file.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    // -----------------------------------
    // Methods related to service requests
    // -----------------------------------
    public static JSONObject getNextSvcRequest() {
        /**
         * This method gets the next service request that has not be realized. To achieve that it analyzes the service
         * requests of AAS Manager, and check if there is an response for each request in the AAS Core, because if
         * there is not, it means that the request has to be performed. Returns the JSON object of the new request or
         * null if no request has been made.
         * @return JSON object with the information of the new service. NULL if it no request has been made.
         */

        // For each service, check if there is an response for each request, because if there is not, it means that the
        // request has to be performed
        JSONArray requestsArray = (JSONArray) fileToJSON(AAS_ArchiveInfo.managerInteractionsFolderPath + AAS_ArchiveInfo.svcRequestFileSubPath).get("serviceRequests");
        for (Object obj: requestsArray) {
            JSONObject reqObj = (JSONObject) obj;
            if (getResponseServiceJSON(((Long) reqObj.get("interactionID")).intValue()) == null)
                return reqObj;
        }
        return null;
    }

    // ------------------------------------
    // Methods related to service responses
    // ------------------------------------
    public static void setResponseServiceState(int interactionID, String newState) {
        // Conseguimos el JSON del servicio en el archivo de respuestas
        JSONObject serviceJSON = getResponseServiceJSON(interactionID);
        if (serviceJSON == null) {
            serviceJSON = new JSONObject();
            serviceJSON.put("interactionID", interactionID);
        }
        serviceJSON.put("serviceStatus", newState);
        updateSvcResponse(serviceJSON);
    }

    // ---------------------------------------
    // Methods related to responses (by AAS Core)
    //----------------------------------------
    private static void updateSvcResponse(JSONObject serviceJSON) {
        JSONArray responsesArray = (JSONArray) fileToJSON(AAS_ArchiveInfo.coreInteractionsFolderPath + AAS_ArchiveInfo.svcResponseFileSubPath).get("serviceResponses");
        responsesArray.add(serviceJSON);
        JSONObject updatedContent = new JSONObject();
        updatedContent.put("serviceResponses", responsesArray);
        updateFile(AAS_ArchiveInfo.coreInteractionsFolderPath + AAS_ArchiveInfo.svcResponseFileSubPath, updatedContent);
    }

    private static JSONObject getResponseServiceJSON(int interactionID) {
        JSONArray responsesArray = (JSONArray) fileToJSON(AAS_ArchiveInfo.coreInteractionsFolderPath + AAS_ArchiveInfo.svcResponseFileSubPath).get("serviceResponses");
        for (Object o: responsesArray) {
            JSONObject svcJSON = (JSONObject) o;
            if (interactionID == ((Long) svcJSON.get("interactionID")).intValue())
                return svcJSON;
        }
        return null;
    }

    public static JSONObject createSvcCompletedResponse(JSONObject requestJSON, String serviceData) {
        JSONObject completedResponseJSON = new JSONObject();
        completedResponseJSON.put("interactionID", requestJSON.get("interactionID"));
        completedResponseJSON.put("serviceID", requestJSON.get("serviceID"));
        completedResponseJSON.put("serviceType", requestJSON.get("serviceType"));
        completedResponseJSON.put("serviceStatus", "Completed");
        if (serviceData != null) {
            JSONObject serviceDataJSON = new JSONObject();
            String requestedData = (String) ((JSONObject) requestJSON.get("serviceData")).get("requestedData");
            serviceDataJSON.put(requestedData, serviceData);
            serviceDataJSON.put("timestamp", System.currentTimeMillis() / 1000);   // Add the timestamp in seconds
            completedResponseJSON.put("serviceData", serviceDataJSON);
        }
        return completedResponseJSON;
    }

    public static void updateSvcCompleteResponse(JSONObject responseFinalJSON) {
        String svcResponsesFilePath = AAS_ArchiveInfo.coreInteractionsFolderPath + AAS_ArchiveInfo.svcResponseFileSubPath;
        System.out.println(fileToJSON(svcResponsesFilePath).toJSONString());
        JSONArray responsesArray = (JSONArray) fileToJSON(svcResponsesFilePath).get("serviceResponses");
        if (responsesArray == null)
            responsesArray = new JSONArray();
        responsesArray.add(responseFinalJSON);
        JSONObject updatedResponseContent = new JSONObject();
        updatedResponseContent.put("serviceResponses", responsesArray);
        updateFile(svcResponsesFilePath, updatedResponseContent);
    }
}
