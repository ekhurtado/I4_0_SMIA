package utilities;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import java.util.ArrayList;

public class AAS_Archive_utils {

    private static final String svcRequests = "/aas_archive/interactions/ManagerToCore.json";
    private static final String svcResponses = "/aas_archive/interactions/CoreToManager.json";

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
    public static JSONObject getNextSvcRequest(ArrayList<String> serviceRecord) {
        JSONArray requestsArray = (JSONArray) fileToJSON(svcRequests).get("serviceRequests");
        System.out.println(requestsArray.toString());

        if (requestsArray.isEmpty())
            return null;
        else {
            if (serviceRecord.isEmpty())
                return (JSONObject) requestsArray.get(0);
            for (Object o: requestsArray) {
                JSONObject requestInfo = (JSONObject) o;
                if (!serviceRecord.contains(String.valueOf(requestInfo.get("interactionID"))))
                    return requestInfo;
            }
            return null;
        }
    }

    public static boolean checkNewRequests(int currentNumberOfRequests) {
        JSONArray requestsArray = (JSONArray) fileToJSON(svcRequests).get("serviceRequests");
        return currentNumberOfRequests < requestsArray.size();
    }

    // ------------------------------------
    // Methods related to service responses
    // ------------------------------------
    public static void setResponseServiceState(String interactionID, String newState) {
        // Conseguimos el JSON del servicio en el archivo de respuestas
        JSONObject serviceJSON = getResponseServiceJSON(interactionID);
        if (serviceJSON == null) {
            serviceJSON = new JSONObject();
            serviceJSON.put("interactionID", interactionID);
        }
        serviceJSON.put("serviceStatus", newState);
        updateSvcResponse(serviceJSON);
    }

    private static void updateSvcResponse(JSONObject serviceJSON) {
        JSONArray responsesArray = (JSONArray) fileToJSON(svcResponses).get("serviceResponses");
        responsesArray.add(serviceJSON);
        JSONObject updatedContent = new JSONObject();
        updatedContent.put("serviceResponses", responsesArray);
        updateFile(svcResponses, updatedContent);
    }

    private static JSONObject getResponseServiceJSON(String interactionID) {
        JSONArray responsesArray = (JSONArray) fileToJSON(svcResponses).get("serviceResponses");
        for (Object o: responsesArray) {
            JSONObject svcJSON = (JSONObject) o;
            if (interactionID.equals((String) svcJSON.get("interactionID")))
                return svcJSON;
        }
        return null;
    }

    public static JSONObject getSvcCompletedResponse(JSONObject requestJSON, String serviceData) {
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
        System.out.println(fileToJSON(svcResponses).toJSONString());
        JSONArray responsesArray = (JSONArray) fileToJSON(svcResponses).get("serviceResponses");
        if (responsesArray == null)
            responsesArray = new JSONArray();
        responsesArray.add(responseFinalJSON);
        JSONObject updatedResponseContent = new JSONObject();
        updatedResponseContent.put("serviceResponses", responsesArray);
        updateFile(svcResponses, updatedResponseContent);
    }
}
