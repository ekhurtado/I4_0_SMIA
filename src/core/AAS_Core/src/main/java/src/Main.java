package src;

import org.json.simple.JSONObject;
import src.functionalities.AssetServices;
import utilities.AAS_Archive_utils;

public class Main {

    private static Main instance;
    private Main() {

    }

    public static Main getInstance() {
        if (instance == null) {
            instance = new Main();
        }
        return instance;
    }

    public String executeFunctionality(String serviceID, JSONObject serviceData) {
        System.out.println("Executing the functionality asociated to the Asset service: " + serviceID);
        switch (serviceID) {
            case "getAssetData":
                String data = null;
                switch ((String) serviceData.get("requestedData")) {
                    case "battery":
                        data = String.valueOf(AssetServices.getAssetBattery());
                    case "model":
                        data = AssetServices.getAssetModel();
                    case "specifications":
                        data = AssetServices.getAssetSpecifications();
                    default:
                        System.out.println("Requestes data is not available.");
                }
                return data;
            case "setAssetData":
                System.out.println("Setting asset data...");
        }
        return null; // Si la funcionalidad no tiene que devolver nada, devuelve null
    }

    public static void main(String[] args) throws InterruptedException {

        System.out.println("Initializing AAS Core...");
        Main aas_core = Main.getInstance();

        // Get the next service request
        JSONObject nextRequestJSON = null;
        while (nextRequestJSON == null) {
            System.out.println("No request yet.");
            Thread.sleep(2000); // pausa de 2s
            nextRequestJSON = AAS_Archive_utils.getNextSvcRequest();
        }

        System.out.println("Service requested.");
        // Set the service state as in progress
        AAS_Archive_utils.setResponseServiceState((String) nextRequestJSON.get("interactionID"), "In Progress");
        // Perform the request
        String serviceData = null;
        switch ((String) nextRequestJSON.get("serviceType")) {
            case "AssetService":
                serviceData = aas_core.executeFunctionality((String) nextRequestJSON.get("serviceID"), (JSONObject) nextRequestJSON.get("serviceData"));
            default:
                System.out.println("Service not available.");
        }

        // Prepare the response
        JSONObject responseFinalJSON = AAS_Archive_utils.getSvcCompletedResponse(nextRequestJSON, serviceData);
        // Update response JSON
        AAS_Archive_utils.updateSvcCompleteResponse(responseFinalJSON);
    }
}
