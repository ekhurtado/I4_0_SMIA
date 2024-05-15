package utilities;

public class AAS_Archive_Info {
    /**
     * This class will contain all information about the AAS Archive.
     */

    // Paths related to interactions between AAS Core and AAS Manager
    public static final String interactionsFolderPath = "/aas_archive/interactions";
    public static final String coreInteractionsFolderPath = "/aas_archive/interactions/core";
    public static final String managerInteractionsFolderPath = "/aas_archive/interactions/manager";

    // Subpath of interaction files
    public static final String svcRequestFileSubPath = "/svcRequests.json";
    public static final String svcResponseFileSubPath = "/svcResponses.json";

    // Paths to the files of all type of services
//    public static final String svcFolderPath = "/aas_archive/services";
//    public static final String assetRelatedSvcPath = "/aas_archive/services/assetRelatedSvc";
//    public static final String aasInfrastructureSvcPath = "/aas_archive/services/aasInfrastructureSvc";
//    public static final String aasServicesPath = "/aas_archive/services/aasServices";
//    public static final String submodelServicesPath = "/aas_archive/services/submodelServices";


    // Status file
    public static final String coreStatusFilePath = "/aas_archive/status/aas_core.json";
    public static final String managerStatusFilePath = "/aas_archive/status/aas_manager.json";

}
