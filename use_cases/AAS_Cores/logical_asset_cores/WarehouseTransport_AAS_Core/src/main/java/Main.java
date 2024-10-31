import logic.AASCore;
import logic.ApplicationExecutionLogic;
import logic.InteractionHandlingLogic;
import utilities.InteractionUtils;

public class Main {

    public static void main(String[] args) {
        AASCore.LOGGER.info("Starting the AAS Core related to the Warehouse Transport industrial application...");

        // First, the AAS Core object will be created
        AASCore aasCore = AASCore.getInstance();

        // The AAS Core is initializing, so it will notify to the AAS Manager
        AASCore.LOGGER.info("The AAS Core is initializing...");
        aasCore.setStatus("Initializing");
        InteractionUtils.sendAASCoreStatusToManager(aasCore.getStatus());

        // The AAS Core is initialized
        aasCore.initializeAASCore();
        AASCore.LOGGER.info("The AAS Core has finished its initialization process.");
        aasCore.setStatus("InitializationReady");
        InteractionUtils.sendAASCoreStatusToManager(aasCore.getStatus());

        // When the AAS Core has finished the initialization it will create two parallel threads: one to manage AAS
        // Manager interaction messages and the other for executing the logic of the application
        InteractionHandlingLogic interactionHandling_thread = new InteractionHandlingLogic();
        ApplicationExecutionLogic appHandling_thread = new ApplicationExecutionLogic();
        interactionHandling_thread.start();
        appHandling_thread.start();


    }
}
