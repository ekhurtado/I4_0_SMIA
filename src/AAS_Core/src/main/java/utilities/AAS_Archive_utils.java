package utilities;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import java.util.ArrayList;
import java.util.Iterator;

public class AAS_Archive_utils {

//    private static final String svcRequests = "/aas_archive/interactions/ManagerToCore.json";
//    private static final String svcResponses = "/aas_archive/interactions/CoreToManager.json";

    // ------------------------
    // Methods related to files
    // ------------------------
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
         * This method gets the next service request that has not be realized. To achieve that it analyzes all service
         * type folder, and, for each service, check if there is an response for each request, because if there is not,
         * it means that the request has to be performed. Returns the JSON object of the new request or null if no
         * request has been made.
         * @return JSON object with the information of the new service. NULL if it no request has been made.
         */
        String[] allSvcFolderPaths = new String[]{AAS_Archive_Info.assetRelatedSvcPath, AAS_Archive_Info.aasInfrastructureSvcPath,
                AAS_Archive_Info.aasServicesPath, AAS_Archive_Info.submodelServicesPath};

        // For each service, check if there is an response for each request, because if there is not, it means that the
        // request has to be performed
        for (String svcFolder: allSvcFolderPaths) {
            JSONArray requestsArray = (JSONArray) fileToJSON(svcFolder + AAS_Archive_Info.svcRequestFileSubPath).get("serviceRequests");
            for (Object obj: requestsArray) {
                JSONObject reqObj = (JSONObject) obj;
                if (getResponseServiceJSON(svcFolder, (String) reqObj.get("interactionID")) != null)
                    return reqObj;
            }
        }
        return null;
    }

    // ------------------------------------
    // Methods related to service responses
    // ------------------------------------
    public static void setResponseServiceState(String svcTypeFolderPath, String interactionID, String newState) {
        // Conseguimos el JSON del servicio en el archivo de respuestas
        JSONObject serviceJSON = getResponseServiceJSON(svcTypeFolderPath, interactionID);
        if (serviceJSON == null) {
            serviceJSON = new JSONObject();
            serviceJSON.put("interactionID", interactionID);
        }
        serviceJSON.put("serviceStatus", newState);
        updateSvcResponse(svcTypeFolderPath, serviceJSON);
    }

    private static void updateSvcResponse(String svcTypeFolderPath, JSONObject serviceJSON) {
        JSONArray responsesArray = (JSONArray) fileToJSON(svcTypeFolderPath + AAS_Archive_Info.svcResponseFileSubPath).get("serviceResponses");
        responsesArray.add(serviceJSON);
        JSONObject updatedContent = new JSONObject();
        updatedContent.put("serviceResponses", responsesArray);
        updateFile(svcTypeFolderPath + AAS_Archive_Info.svcResponseFileSubPath, updatedContent);
    }

    private static JSONObject getResponseServiceJSON(String svcTypeFolderPath, String interactionID) {
        JSONArray responsesArray = (JSONArray) fileToJSON(svcTypeFolderPath + AAS_Archive_Info.svcResponseFileSubPath).get("serviceResponses");
        for (Object o: responsesArray) {
            JSONObject svcJSON = (JSONObject) o;
            if (interactionID.equals((String) svcJSON.get("interactionID")))
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

    public static void updateSvcCompleteResponse(String svcTypeFolderPath, JSONObject responseFinalJSON) {
        String svcResponsesFilePath = svcTypeFolderPath + AAS_Archive_Info.svcResponseFileSubPath;
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
