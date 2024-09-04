package src;

import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.json.simple.JSONObject;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
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
        switch (serviceID) {
            case "getAssetData":
                switch ((String) serviceData.get("requestedData")) {
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
        JSONObject msg_data = new JSONObject();
        msg_data.put("status", "InitializationReady");
        String result = InteractionsUtils.sendInteractionMsgToManager("core-status", msg_data);
        if (!result.equals("OK")) {
            System.err.println("Interaction AAS Manager-Core not working");
        }

        // Then, it waits until the AAS Manager is ready
        // TODO this code is for the interaction through JSON (it has to be removed)
//        while (Objects.equals(AAS_ArchiveUtils.getManagerStatus(), "Initializing")) {
//            System.out.println("AAS Manager has not yet been initialized.");
//            Thread.sleep(1000); // Waits 1s
//        }


        System.out.println("AAS Manager has initialized, so the AAS Core is starting.");
//        while (true) {
//            // Get the new request information
//            JSONObject nextRequestJSON = AAS_ArchiveUtils.getNextSvcRequest();
//            if (nextRequestJSON != null) {
//                System.out.println("Service requested by the AAS Manager.");
//
//                // Perform the request
//                String serviceData = null;
//                switch ((String) Objects.requireNonNull(nextRequestJSON).get("serviceType")) {
//                    case "AssetRelatedService":
//                        serviceData = aas_core.executeARSvcFunctionality((String) nextRequestJSON.get("serviceID"), (JSONObject) nextRequestJSON.get("serviceData"));
//
//                        // Prepare the response
//                        System.out.println("Creating the service response object...");
//                        JSONObject responseFinalJSON = AAS_ArchiveUtils.createSvcCompletedResponse(nextRequestJSON, serviceData);
//                        // Update response JSON
//                        AAS_ArchiveUtils.updateSvcCompleteResponse(responseFinalJSON);
//
//                        // Update number of requests
//                        aas_core.numberOfARSvcRequests += 1;
//                        break;
//                    case "AASInfrastructureService":
//                        // Update number of requests
//                        aas_core.numberOfAASIsvcRequests += 1;
//                        break;
//                    case "AASservice":
//                        // Update number of requests
//                        aas_core.numberOfAASsvcRequests += 1;
//                        break;
//                    case "SubmodelService":
//                        // Update number of requests
//                        aas_core.numberOfSMsvcRequests += 1;
//                        break;
//                    default:
//                        System.out.println("Service not available.");
//                }
//
//                System.out.println("Requested service completed.");
//
//                aas_core.serviceRecord.add(String.valueOf(nextRequestJSON.get("interactionID")));
//            } else {
//                System.out.println("No service request yet.");
//                Thread.sleep(5000); // waits for 5s
//            }
//        }

        // TODO test if it is working with Kafka
        KafkaConsumer kafkaConsumerPartitionManager = InteractionsUtils.createInteractionKafkaConsumer();
        kafkaConsumerPartitionManager.subscribe(Collections.singletonList(KafkaInfo.KAFKA_TOPIC));

        while (true) {
            final ConsumerRecords<String, String> consumerRecords =
                    kafkaConsumerPartitionManager.poll(Duration.ofMillis(10000));

            System.out.println("Consumer record:");
            System.out.println(consumerRecords.toString());

            consumerRecords.forEach(record -> {
            	System.out.println("Mensaje recibido:");
            	System.out.println(record.toString());

                System.out.printf("Consumer Record:(%d, %s, %d, %d)\n",
                        record.key(), record.value(),
                        record.partition(), record.offset());

                // TODO get the request JSON
                JSONObject nextRequestJSON = new JSONObject();

                // TODO get the service type, id...
                String serviceType = "";
                String serviceID = "";
                JSONObject serviceData = new JSONObject();
                switch (serviceType) {
                    case "AssetRelatedService":
                        String serviceResponseData = aas_core.executeARSvcFunctionality(serviceID, (JSONObject) serviceData);

                        // Prepare the response
                        System.out.println("Creating the service response object...");
                        JSONObject responseFinalJSON = AAS_ArchiveUtils.createSvcCompletedResponse(nextRequestJSON, serviceResponseData);
                        // Update response JSON
                        // TODO this code is for the interaction through JSON (it has to be removed)
//                        AAS_ArchiveUtils.updateSvcCompleteResponse(responseFinalJSON);

                        // TODO test if it is working with Kafka
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

//                aas_core.serviceRecord.add(String.valueOf(nextRequestJSON.get("interactionID")));
            });

            kafkaConsumerPartitionManager.commitAsync();
        }

    }
}
