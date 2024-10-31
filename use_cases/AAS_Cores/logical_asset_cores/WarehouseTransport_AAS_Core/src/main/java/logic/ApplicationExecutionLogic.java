package logic;

import org.json.simple.JSONObject;
import utilities.InteractionUtils;

public class ApplicationExecutionLogic extends Thread {

    @Override
    public void run() {
        // First, the AAS Manager status will be checked to ensure that it is ready
        AASCore.LOGGER.info("ApplicationExecutionLogic waiting until the AAS Manager finishes its initialization state.");
        try {
            AASCore.getInstance().lockLogic();  // Wait until the InteractionHandlingLogic gets the status information
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        AASCore.LOGGER.info("The AAS Manager has finished its booting state, so the application can be executed");

        // At this point the AAS Manager is ready
        AASCore aasCore = AASCore.getInstance();
        switch (aasCore.getAppToExecute()) {
            case "collection":
                // This application will send the best transport robot (through a negotiation) to collect a product from
                // the warehouse
                executeCollectionApp();
                break;
            case "delivery":
                // This application will send the best transport robot (through a negotiation) to deliver a product to
                // the warehouse
                executeDeliveryApp();
                break;
            default:
                AASCore.LOGGER.warn("Application not available");
        }
    }

    private void checkAASManagerStatus() throws InterruptedException {
        // TODO old version
        while (true) {
            AASCore.LOGGER.info("Thread ApplicationExecutionLogic... ");
            AASCore aasCore = AASCore.getInstance();
            AASCore.LOGGER.info("Trying to get attribute of AAS Core class");
            String aasManagerCurrentStatus = aasCore.getManagerStatus();
            if (aasManagerCurrentStatus.equals("Initializing") || aasManagerCurrentStatus.equals("idle")) {
                AASCore.LOGGER.info("The AAS Manager has not initialized yet, it is not ready. Waiting for 2 seconds " +
                        "and trying again...");
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            } else {
                AASCore.LOGGER.info("The AAS Manager is ready, so the application can start.");
                break;
            }
        }
    }

    private static void executeCollectionApp() {
        AASCore.LOGGER.info("Executing collection application...");
        // TODO (pensar si comparten partes con la app de delivery, para reutilizar metodos (p.e. pedir negociacion))
    }


    private static void executeDeliveryApp() {
        AASCore.LOGGER.info("Executing delivery application...");
        // TODO primero, manda negociar a transportes. Espera hasta recibir al ganador, cuando lo tiene, le pide que
        //  lleve el producto al warehouse. Cuando lo haya hecho, le dice a la maquina del warehouse que lo almacene
        // Recordad que los IDs de los AASs se han añadido en el ConfigMap, estan en la clase AASCore

        AASCore.LOGGER.info("Starting delivery application...");
        AASCore aasCore = AASCore.getInstance();

        // First,  a negotiation request will be sent to all transport robots to obtain the best option. The criteria
        // will be the battery
        AASCore.LOGGER.info("Requesting the negotiation to all transport AASs to obtain the transport with the best " +
                "level of battery...");
        JSONObject serviceParams = new JSONObject();
        serviceParams.put("criteria", "battery");
        // The target list in a String separated by ',' is obtained
        serviceParams.put("targets", aasCore.getTransportAASIDListAsString());
        JSONObject negotiationInteractionRequestJSON = InteractionUtils.createInteractionObjectForManagerRequest(
                "AssetRelatedService", "startNegotiation", serviceParams);
        InteractionUtils.sendInteractionRequestToManager(negotiationInteractionRequestJSON);
        // Since the interaction is asynchronous because the response of the negotiation with the winner ID can be
        // received at any time by the AAS Core, this thread will be waiting until this happens.
        AASCore.LOGGER.info("ApplicationExecutionLogic waiting until the negotiation winner has been received.");
        try {
            AASCore.getInstance().lockLogic();  // Wait until the InteractionHandlingLogic gets the status information
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        AASCore.LOGGER.info("The winner of the negotiation has already been received, so the application logic can continue.");

        // Once the negotiation winner has received, the service request to perform the transport will be sent to the
        // winner through an Intra AAS interaction request
        AASCore.LOGGER.info("Requesting the transport service to move the product to the warehouse...");
        // First, it has to get the winner from the responses data of the AAS Core
        JSONObject responseJSON = aasCore.getServiceResponseRecord((String) negotiationInteractionRequestJSON.get("thread"));
        String winnerJID = (String) ((JSONObject)((JSONObject) responseJSON.get("serviceData")).get("serviceParams")).get("winner");
        serviceParams = new JSONObject();
        serviceParams.put("receiver", winnerJID);
        serviceParams.put("serviceID", "delivery");
        JSONObject transportInteractionRequestJSON = InteractionUtils.createInteractionObjectForManagerRequest(
                "AssetRelatedService", "sendInterAASsvcRequest", serviceParams);
        InteractionUtils.sendInteractionRequestToManager(transportInteractionRequestJSON);
        // In this case it must also wait to receive confirmation that the service has been performed
        AASCore.LOGGER.info("ApplicationExecutionLogic waiting to receive confirmation that the transport service " +
                "has been realized.");
        try {
            aasCore.lockLogic();  // Wait until the InteractionHandlingLogic gets the status information
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        AASCore.LOGGER.info("The transport has already been received, so the application logic can continue.");
        // Before performing the next step, it will be checked whether the service has been completed
        responseJSON = aasCore.getServiceResponseRecord((String) transportInteractionRequestJSON.get("thread"));
        if (!((JSONObject) responseJSON.get("serviceData")).get("serviceStatus").equals("Completed")) {
            AASCore.LOGGER.error("The transport service has not been completed.");
            return;     // TODO pensar si añadir excepciones para cuando la aplicacion no sale bien
        }

        // Now, the last part of the application can be performed: the storage of the product in the warehouse
        AASCore.LOGGER.info("Requesting the service to store the product in the warehouse...");
        serviceParams = new JSONObject();
        serviceParams.put("receiver", aasCore.getWarehouseAASID());
        serviceParams.put("serviceID", "storeProduct");
        serviceParams.put("target", "INTRODUCE:22"); // TODO para pruebas se ha puesto fijo, si no, se debe seleccionar donde se quiere almacenar
        JSONObject storageInteractionRequestJSON = InteractionUtils.createInteractionObjectForManagerRequest(
                "AssetRelatedService", "sendInterAASsvcRequest", serviceParams);
        InteractionUtils.sendInteractionRequestToManager(storageInteractionRequestJSON);
        // It will wait to receive confirmation that the service has been performed
        AASCore.LOGGER.info("ApplicationExecutionLogic waiting to receive confirmation that the storage service " +
                "has been realized.");
        try {
            aasCore.lockLogic();  // Wait until the InteractionHandlingLogic gets the status information
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        // Before finishing the application, it will be checked whether the service has been completed
        responseJSON = aasCore.getServiceResponseRecord((String) storageInteractionRequestJSON.get("thread"));
        if (!((JSONObject) responseJSON.get("serviceData")).get("serviceStatus").equals("Completed")) {
            AASCore.LOGGER.error("The storage service has not been completed.");
            return;     // TODO pensar si añadir excepciones para cuando la aplicacion no sale bien
        }
        AASCore.LOGGER.info("The product has been stored in the warehouse, so the application has been " +
                "successfully completed.");

    }
}
