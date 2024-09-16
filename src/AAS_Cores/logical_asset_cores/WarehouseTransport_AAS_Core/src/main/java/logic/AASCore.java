package logic;

import information.AAS_ArchiveInfo;
import org.apache.commons.lang3.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.simple.JSONObject;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Properties;

public class AASCore {
    /**
     * This class contains all the information about the AAS Core.
     */

    private static AASCore instance;

    public static final Logger LOGGER = LogManager.getLogger(AASCore.class);

    private String aasID;

    private String aasCoreStatus;
    private String aasManagerStatus;

    private int interactionIdNum;

    private HashMap<String,JSONObject> serviceRequestsRecord;
    private HashMap<String,JSONObject> serviceResponsesRecord;
    private ArrayList<String> transportAASIDList;
    private ArrayList<String> warehouseAASIDList;

    private String applicationToExecute;

    private AASCore() {
        aasID = null;

        aasCoreStatus = "Starting";
        aasManagerStatus = "Unknown";
        interactionIdNum = 0;

        serviceRequestsRecord = new HashMap<>();
        serviceResponsesRecord = new HashMap<>();

        transportAASIDList = new ArrayList<>();
        warehouseAASIDList = new ArrayList<>();

        applicationToExecute = "";

        System.setProperty("log4j.configurationFile", "log4j2.xml");
//        System.setProperty("log4j.configurationFile", ClassLoader.getSystemClassLoader().getResource("log4j2.xml").getPath());

    }

    public static AASCore getInstance() {
        if (instance == null) {
            instance = new AASCore();
        }
        return instance;
    }

    public synchronized void unlockLogic() {
        notify(); // Notify any waiting threads that the value has been updated
    }

    public synchronized void lockLogic() throws InterruptedException {
        wait(); // Wait until notified that the value has been updated
    }

    // Methods related to attributes
    // -----------------------------

    // GET METHODS
    public String getAASID() {
        return aasID;
    }

    public String getInteractionID() {
        return "core-" + interactionIdNum;
    }

    public String getStatus() {
        return aasCoreStatus;
    }

    public String getManagerStatus() {
        return aasManagerStatus;
    }

    public String getAppToExecute() {
        return applicationToExecute;
    }

    public ArrayList<String> getTransportAASIDList() {
        return transportAASIDList;
    }

    public String getTransportAASIDListAsString() {
        return StringUtils.join(transportAASIDList, ",");
    }

    public JSONObject getServiceRequestRecord(String thread) {
        return serviceRequestsRecord.get(thread);
    }

    public JSONObject getServiceResponseRecord(String thread) {
        return serviceResponsesRecord.get(thread);
    }

    // SET METHODS
    public void setStatus(String newStatus) {
        aasCoreStatus = newStatus;
    }

    public void setManagerStatus(String newManagerStatus) {
        aasManagerStatus = newManagerStatus;
    }

    public void increaseInteractionIDNum() {
        interactionIdNum += 1;
    }

    public void addNewServiceRequestRecord(JSONObject requestData) {
        serviceRequestsRecord.put((String) requestData.get("thread"), requestData);
    }

    public void addNewServiceResponseRecord(JSONObject responseData) {
        serviceResponsesRecord.put((String) responseData.get("thread"), responseData);
    }

    // Methods related to the logic of the AAS Core
    // -------------------------------------------
    public void initializeAASCore() {
        /**
         * This method performs the initialization tasks of this AAS Core. It has been decided to add some useful
         * information in the ConfigMap of the I4.0 SMIA deployment, to make it easy to change for testing. This
         * information includes the application selected to be run and the other AASs available in the I4.0 system
         * (because for now there is no infrastructure service to get information about the available AASs).
         */

        Properties prop = new Properties();
//        URL filePath = ClassLoader.getSystemClassLoader().getResource("aas.properties");  // TODO for local tests
//        System.out.println(fileURL.getPath());
//        try (InputStream inputStream = fileURL.openStream()) {
        String filePath = AAS_ArchiveInfo.configFolderPath + '/' + AAS_ArchiveInfo.aasPropertiesFileName;
        try (InputStream inputStream = new FileInputStream(filePath)) {

            // Loading the properties.
            prop.load(inputStream);

            // Getting properties for the application to execute
            aasID = prop.getProperty("logicalID");

            String appToExecute = prop.getProperty("applicationToExecute");
            AASCore.LOGGER.info("The application selected to be executed is: " + appToExecute);
            applicationToExecute = appToExecute;

            String transportAASIDs = prop.getProperty("transport-aas-ids");
            transportAASIDList.addAll(Arrays.asList(transportAASIDs.split(",")));

            String warehouseAASIDs = prop.getProperty("warehouse-aas-ids");
            warehouseAASIDList.addAll(Arrays.asList(warehouseAASIDs.split(",")));

            AASCore.LOGGER.info("All information obtained from the properties file.");

        } catch (IOException ex) {
            AASCore.LOGGER.error("Problem occurs when reading file !");
            ex.printStackTrace();
        }

    }
}
