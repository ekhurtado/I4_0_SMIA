package logic;

public class ApplicationExecutionLogic extends Thread {

    @Override
    public void run() {
        // First, the AAS Manager status will be checked to ensure that it is ready
        checkAASManagerStatus();

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

    private static void checkAASManagerStatus() {
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
        // TODO
    }


    private static void executeDeliveryApp() {
        AASCore.LOGGER.info("Executing delivery application...");
        // TODO primero, manda negociar a transportes. Espera hasta recibir al ganador, cuando lo tiene, le pide que
        //  lleve el producto al warehouse. Cuando lo haya hecho, le dice a la maquina del warehouse que lo almacene
        // Recordad que los IDs de los AASs se han añadido en el ConfigMap, estan en la clase AASCore
    }
}
