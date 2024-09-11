package logic;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.simple.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
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

    private String aasCoreStatus;
    private String aasManagerStatus;

    private int interactionIdNum;

    private HashMap<String,JSONObject> serviceRecord;
    private ArrayList<String> transportAASIDList;
    private ArrayList<String> warehouseAASIDList;

    private String applicationToExecute;

    private AASCore() {
        aasCoreStatus = "Starting";
        aasManagerStatus = "Unknown";
        interactionIdNum = 0;

        serviceRecord = new HashMap<>();
        transportAASIDList = new ArrayList<>();
        warehouseAASIDList = new ArrayList<>();

        applicationToExecute = "";

        System.setProperty("log4j.configurationFile", ClassLoader.getSystemClassLoader().getResource("log4j2.xml").getPath());

    }

    public static AASCore getInstance() {
        if (instance == null) {
            instance = new AASCore();
        }
        return instance;
    }

    // Methods related to attributes
    // -----------------------------
    public void setStatus(String newStatus) {
        aasCoreStatus = newStatus;
    }

    public String getStatus() {
        return aasCoreStatus;
    }

    public void setManagerStatus(String newManagerStatus) {
        aasManagerStatus = newManagerStatus;
    }

    public String getManagerStatus() {
        return aasManagerStatus;
    }

    public String getAppToExecute() {
        return applicationToExecute;
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
        URL filePath = ClassLoader.getSystemClassLoader().getResource("aas.properties");
        System.out.println(filePath.getPath());
        try (InputStream inputStream = filePath.openStream()) {

            // Loading the properties.
            prop.load(inputStream);

            // Getting properties for the application to execute
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
