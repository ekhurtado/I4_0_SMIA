package information;

public class AAS_ArchiveInfo {
    /**
     * This class will contain all information about the AAS Archive.
     */

    // Paths related to interactions between AAS Core and AAS Manager
    public static final String coreInteractionsFolderPath = "/aas_archive/interactions/core";
    public static final String managerInteractionsFolderPath = "/aas_archive/interactions/manager";

    // Subpath of interaction files
    public static final String svcRequestFileSubPath = "/svcRequests.json";
    public static final String svcResponseFileSubPath = "/svcResponses.json";


    // Status file
    public static final String coreStatusFilePath = "/aas_archive/status/aas_core.json";
    public static final String managerStatusFilePath = "/aas_archive/status/aas_manager.json";

    // Config file
    public static final String configFolderPath = "/aas_archive/config";
    public static final String aasPropertiesFileName = "aas.properties";

}
