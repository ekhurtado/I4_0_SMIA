package utilities;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;

public class AAS_Archive_utils {

//    private static final String svcRequests = "/aas_archive/interactions/ManagerToCore.json";
    private static final String svcRequests = "C:\\Users\\839073\\OneDrive - UPV EHU\\Tesis doctoral\\TesisEkaitzHurtado\\Ideas Ekaitz\\Componente I4.0\\Recursos\\ManagerToCore.json";
    private static final String svcResponses = "/aas_archive/interactions/CoreToManager.json";

    // ------------------------
    // Methods related to files
    // ------------------------
    public static JSONObject fileToJSON(String filePath) {
        JSONParser parser = new JSONParser();
        try (Reader reader = new FileReader(svcRequests)) {
            return (JSONObject) parser.parse(reader);
        } catch (IOException | ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public static void updateFile(String filePath, JSONObject content) {
        try (FileWriter file = new FileWriter(filePath)) {
            file.write(content.toJSONString());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // -----------------------------------
    // Methods related to service requests
    // -----------------------------------
    public static JSONObject getNextSvcRequest() {
        JSONArray requestsArray = (JSONArray) fileToJSON(svcRequests).get("serviceRequests");
        System.out.println(requestsArray.toString());

        if (requestsArray.isEmpty())
            return null;
        else {
            return (JSONObject) requestsArray.get(0);
        }
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

    public static JSONObject getSvcCompletedResponse(JSONObject nextRequestJSON, String serviceData) {
        // TODO
        return null;
    }

    public static void updateSvcCompleteResponse(JSONObject responseFinalJSON) {
        // TODO
    }
}
