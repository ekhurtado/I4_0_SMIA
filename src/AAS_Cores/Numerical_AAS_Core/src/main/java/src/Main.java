package src;

import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.json.simple.JSONObject;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import src.functionalities.AssetRelatedServices;
import utilities.AAS_ArchiveUtils;
import utilities.InteractionsUtils;
import utilities.KafkaInfo;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Objects;

public class Main {

    private static Main instance;

    // Logger object
    static final Logger LOGGER = LogManager.getLogger(Main.class.getName());

    private String aasManagerStatus;

    // Number of each type of request
    private int numberOfARSvcRequests;  // ARSvc = Asset Related Service
    private int numberOfAASIsvcRequests;  // AASIsvc = AAS Infrastructure Service
    private int numberOfAASsvcRequests;  // AASsvc = AAS Service
    private int numberOfSMsvcRequests;  // SMsvc = Submodel Service
    private ArrayList<String> serviceRecord;

    private Main() {
        numberOfARSvcRequests = 0;
        numberOfAASIsvcRequests = 0;
        numberOfAASsvcRequests = 0;
        numberOfSMsvcRequests = 0;
        serviceRecord = new ArrayList<>();
        aasManagerStatus = "Unknown";
    }

    public static Main getInstance() {
        if (instance == null) {
            instance = new Main();
        }
        return instance;
    }

    public String executeARSvcFunctionality(String serviceID, JSONObject serviceData) {
        System.out.println("Executing the functionality asociated to the Asset service: " + serviceID);
        String data = null;
        JSONObject serviceParams = (JSONObject) serviceData.get("serviceParams");
        switch (serviceID) {
            case "getAssetData":
                switch ((String) serviceParams.get("requestedData")) {
                    case "battery":
                        data = String.valueOf(AssetRelatedServices.getAssetBattery());
                        break;
                    case "specifications":
                        data = AssetRelatedServices.getAssetSpecifications();
                        break;
                    default:
                        System.out.println("Request data is not available.");
                }
                break;

            case "setAssetData":
                System.out.println("Setting asset data...");
                break;
            case "getAssetModel":
                data = AssetRelatedServices.getAssetModel();
                break;
            case "getNegotiationValue":
                data = AssetRelatedServices.getNegotiationValue(serviceData);
            default:
                System.out.println("This service ID is not available.");
                break;
        }
        System.out.println("Functionality executed.");
        return data; // Si la funcionalidad no tiene que devolver nada, devuelve null
    }

    public static void main(String[] args) throws InterruptedException {

        System.out.println("Initializing AAS Core...");
        LOGGER.info("Initializing AAS Core...");
        Main aas_core = Main.getInstance();

        // First, the AAS Core has to set its initial status
        // TODO this code is for the interaction through JSON (it has to be removed)
//        AAS_ArchiveUtils.createStatusFile();

        // This AAS core does not require an initialization process
//        AAS_ArchiveUtils.changeStatus("InitializationReady");
        // TODO test if it is working with Kafka
        System.out.println("Sending message through Kafka...");
        JSONObject msg_data = new JSONObject();
        msg_data.put("status", "InitializationReady");
        String result = InteractionsUtils.sendInteractionMsgToManager("core-status", msg_data);
        if (!result.equals("OK")) {
            System.err.println("Interaction AAS Manager-Core not working");
        }

        // Then, it waits until the AAS Manager is ready


        // TODO test if it is working with Kafka
        KafkaConsumer kafkaConsumerPartitionManager = InteractionsUtils.createInteractionKafkaConsumer();
//        kafkaConsumerPartitionManager.subscribe(Collections.singletonList(KafkaInfo.KAFKA_TOPIC));

        while (true) {
            final ConsumerRecords<String, String> consumerRecords =
                    kafkaConsumerPartitionManager.poll(Duration.ofMillis(10000));

            System.out.println("Consumer record:");
            System.out.println(consumerRecords.toString());

            consumerRecords.forEach(record -> {
                System.out.println("Mensaje recibido:");
//                System.out.println(record.toString());

                System.out.println("KEY: " + record.key());
                System.out.println("VALUE: " + record.value());
//                System.out.println("PARTITION:" + record.partition());
//                System.out.println("OFFSET:" + record.offset());
//
//                System.out.printf("Consumer Record:(%s, %s, %d, %d)\n",
//                        record.key(), record.value(),
//                        record.partition(), record.offset());

                // The next service request information if JSON format is in the value of the message
                System.out.println("Intentando pasar de string a JSON...");
                JSONObject nextRequestJSON;
                try {
                    JSONParser jsonParser = new JSONParser();
                    nextRequestJSON = (JSONObject) jsonParser.parse(record.value());
                } catch (ParseException e) {
                    throw new RuntimeException(e);
                }
                System.out.println(nextRequestJSON.toString());
//                System.out.println(nextRequestJSON.toJSONString());
//                System.out.println(nextRequestJSON.get("dato1"));

                // If the message received is about the status of the AAS Manager, the information in the AAS Core will
                // be updated.
                if (nextRequestJSON.containsKey("status")) {
                    System.out.println("New status of the AAS Manager: " + nextRequestJSON.get("status"));
                    aas_core.aasManagerStatus = (String) nextRequestJSON.get("status");
                    if (!aas_core.aasManagerStatus.equals("Initializing"))
                        System.out.println("AAS Manager has initialized, so the AAS Core can go to running state.");

                } else {

                    // Only if the AAS Manager is ready the AAS Core will work
                    if (!aas_core.aasManagerStatus.equals("Initializing") && !aas_core.aasManagerStatus.equals("idle")) {

                        switch ((String) Objects.requireNonNull(nextRequestJSON).get("serviceType")) {
                            case "AssetRelatedService":
                                String serviceResponseData = aas_core.executeARSvcFunctionality((String) nextRequestJSON.get("serviceID"), (JSONObject) nextRequestJSON.get("serviceData"));

                                // Prepare the response
                                System.out.println("Creating the service response object...");
                                JSONObject responseFinalJSON = AAS_ArchiveUtils.createSvcCompletedResponse(nextRequestJSON, serviceResponseData);
                                // Update response JSON
                                // TODO this code is for the interaction through JSON (it has to be removed)
//                        AAS_ArchiveUtils.updateSvcCompleteResponse(responseFinalJSON);

                                // TODO test if it is working with Kafka
                                System.out.println("Response JSON: " + responseFinalJSON.toJSONString());
                                InteractionsUtils.sendInteractionMsgToManager("core-service-response", responseFinalJSON);

                                // Update number of requests
                                aas_core.numberOfARSvcRequests += 1;
                                break;
                            case "AASInfrastructureService":
                                // Update number of requests
                                aas_core.numberOfAASIsvcRequests += 1;
                                break;
                            case "AASservice":
                                // Update number of requests
                                aas_core.numberOfAASsvcRequests += 1;
                                break;
                            case "SubmodelService":
                                // Update number of requests
                                aas_core.numberOfSMsvcRequests += 1;
                                break;
                            default:
                                System.out.println("Service not available.");
                        }

                        System.out.println("Requested service completed.");

//                  aas_core.serviceRecord.add(String.valueOf(nextRequestJSON.get("interactionID")));
                    }
                }
            });

            kafkaConsumerPartitionManager.commitAsync();
        }

    }
}
