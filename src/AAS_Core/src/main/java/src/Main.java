package src;

import org.json.simple.JSONObject;
import src.functionalities.AssetServices;
import utilities.AAS_Archive_utils;

import java.util.ArrayList;

public class Main {

    private static Main instance;

    private int numberOfRequests;
    private ArrayList<String> serviceRecord;

    private Main() {
        numberOfRequests = 0;
        serviceRecord = new ArrayList<>();
    }

    public static Main getInstance() {
        if (instance == null) {
            instance = new Main();
        }
        return instance;
    }

    public String executeFunctionality(String serviceID, JSONObject serviceData) {
        System.out.println("Executing the functionality asociated to the Asset service: " + serviceID);
        String data = null;
        switch (serviceID) {
            case "getAssetData":
                switch ((String) serviceData.get("requestedData")) {
                    case "battery":
                        data = String.valueOf(AssetServices.getAssetBattery());
                        break;
                    case "specifications":
                        data = AssetServices.getAssetSpecifications();
                        break;
                    default:
                        System.out.println("Requestes data is not available.");
                }
                break;

            case "setAssetData":
                System.out.println("Setting asset data...");
                break;
            case "getAssetModel":
                data = AssetServices.getAssetModel();
                break;
        }
        return data; // Si la funcionalidad no tiene que devolver nada, devuelve null
    }

    public static void main(String[] args) throws InterruptedException {

        System.out.println("Initializing AAS Core...");
        Main aas_core = Main.getInstance();

        while (true) {
            // Check if a new request has been made
            boolean newRequest = AAS_Archive_utils.checkNewRequests(aas_core.numberOfRequests);
            if (newRequest) {
                // Get the new request information
                JSONObject nextRequestJSON = AAS_Archive_utils.getNextSvcRequest(aas_core.serviceRecord);
                System.out.println("Service requested.");

                // Perform the request
                String serviceData = null;
                switch ((String) nextRequestJSON.get("serviceType")) {
                    case "AssetService":
                        serviceData = aas_core.executeFunctionality((String) nextRequestJSON.get("serviceID"), (JSONObject) nextRequestJSON.get("serviceData"));
                        break;
                    default:
                        System.out.println("Service not available.");
                }

                // Prepare the response
                JSONObject responseFinalJSON = AAS_Archive_utils.getSvcCompletedResponse(nextRequestJSON, serviceData);
                // Update response JSON
                AAS_Archive_utils.updateSvcCompleteResponse(responseFinalJSON);

                // Update number of requests
                aas_core.numberOfRequests += 1;
                aas_core.serviceRecord.add(String.valueOf(nextRequestJSON.get("interactionID")));
            } else {
                System.out.println("No request yet.");
                Thread.sleep(5000); // waits for 5s
            }
        }
    }
}
