class AASGeneralInfo:
    """This class contains all information about the AAS Archive paths."""

    # Paths related to interactions between Manager and Core
    INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions'
    CORE_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/core'
    MANAGER_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/manager'

    # Subpath of interaction files
    SVC_REQUEST_FILE_SUBPATH = '/svcRequests.json'
    SVC_RESPONSE_FILE_SUBPATH = '/svcResponses.json'

    # Paths for log files
    LOG_FOLDER_PATH = '/aas_archive/log'
    AAS_MANAGER_LOG_FILENAME = 'aas_manager.log'
    SVC_LOG_FOLDER_PATH = '/aas_archive/log/services'
    ASSET_RELATED_SVC_LOG_FILENAME = 'assetRelatedSvcHistory.log'
    AAS_INFRASTRUCTURE_SVC_LOG_FILENAME = 'aasInfrastructureSvcHistory.log'
    AAS_SERVICES_LOG_FILENAME = 'aasServicesHistory.log'
    SUBMODEL_SERVICES_LOG_FILENAME = 'submodelServicesHistory.log'

    # ConfigMap files
    CONFIG_MAP_PATH = '/aas_archive/config'
    CM_DT_PROPERTIES_FILENAME = 'dt.properties'
    CM_AAS_PROPERTIES_FILENAME = 'aas.properties'
    CM_ASSET_PROPERTIES_FILENAME = 'asset.properties'
    CM_SM_PROPERTIES_FILENAME = 'submodels.properties'

    # Submodel files
    SUBMODEL_FOLDER_PATH = '/aas_archive/submodels'
    TECHNICAL_DATA_SM_FILENAME = 'Technical_data_SM.xml'
    CONFIGURATION_SM_FILENAME = 'Configuration_SM.xml'

    # Status file
    MANAGER_STATUS_FILE_PATH = '/aas_archive/status/aas_manager.json'
    CORE_STATUS_FILE_PATH = '/aas_archive/status/aas_core.json'
