package utilities;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;

public class AAS_ArchiveUtils {


    // ------------------------
    // Methods related to files
    // ------------------------
    public static void createStatusFile() {
        JSONObject statusFileJSON = new JSONObject();
        statusFileJSON.put("name", "AAS_Core");
        statusFileJSON.put("status", "Initializing");
        statusFileJSON.put("timestamp", System.currentTimeMillis() / 1000);

        updateFile(AAS_ArchiveInfo.coreStatusFilePath, statusFileJSON);
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

    public static JSONObject createSvcCompletedResponse(JSONObject requestJSON, String serviceRequestedData) {
        JSONObject completedResponseJSON = new JSONObject();
        completedResponseJSON.put("interactionID", requestJSON.get("interactionID"));
        completedResponseJSON.put("thread", requestJSON.get("thread"));
        completedResponseJSON.put("serviceID", requestJSON.get("serviceID"));
        completedResponseJSON.put("serviceType", requestJSON.get("serviceType"));

        JSONObject serviceDataJSON = new JSONObject();
        serviceDataJSON.put("serviceStatus", "Completed");
        serviceDataJSON.put("serviceCategory", "service-response");
        serviceDataJSON.put("timestamp", System.currentTimeMillis() / 1000);   // Add the timestamp in seconds

        if (serviceRequestedData != null) {
            String requestedDataName = (String) ((JSONObject) ((JSONObject) requestJSON.get("serviceData")).get("serviceParams")).get("requestedData");
            JSONObject requestedDataJSON = new JSONObject();
            requestedDataJSON.put(requestedDataName, serviceRequestedData);
            serviceDataJSON.put("serviceParams", requestedDataJSON);
        }
        completedResponseJSON.put("serviceData", serviceDataJSON);
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
