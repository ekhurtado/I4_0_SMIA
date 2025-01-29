import os


class SMIAGeneralInfo:
    """This class contains all general information about the SMIA."""

    # Variables related to states of the FSM
    # --------------------------------------
    BOOTING_STATE_NAME = 'BOOTING'
    RUNNING_STATE_NAME = 'RUNNING'
    STOPPING_STATE_NAME = 'STOPPING'
    IDLE_STATE_NAME = 'IDLE'

    # Path of the SMIA Archive
    SMIA_ARCHIVE_PATH = '/smia_archive'
    if 'KUBERNETES_PORT' not in os.environ: #  If the SMIA DT is run locally, the configuration files are in 'smia_archive' folder of the project
        SMIA_ARCHIVE_PATH = '../smia_archive'

    # Paths related to interactions between Manager and Core
    INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions'
    CORE_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/core'
    MANAGER_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/manager'

    # Subpath of interaction files
    SVC_REQUEST_FILE_SUBPATH = '/svcRequests.json'
    SVC_RESPONSE_FILE_SUBPATH = '/svcResponses.json'

    # Paths for log files
    LOG_FOLDER_PATH = SMIA_ARCHIVE_PATH + '/log'
    SMIA_LOG_FILENAME = 'smia_dt.log'

    SVC_LOG_FOLDER_PATH = LOG_FOLDER_PATH + '/services'
    ERROR_LOG_FOLDER_PATH = LOG_FOLDER_PATH + '/errors'

    ASSET_RELATED_SVC_LOG_FILENAME = 'assetRelatedSvcHistory.log'
    AAS_INFRASTRUCTURE_SVC_LOG_FILENAME = 'aasInfrastructureSvcHistory.log'
    AAS_SERVICES_LOG_FILENAME = 'aasServicesHistory.log'
    SUBMODEL_SERVICES_LOG_FILENAME = 'submodelServicesHistory.log'
    SUBMODEL_CSS_LOG_FILENAME = 'capabilitySkillHistory.log'

    # ConfigMap files
    CONFIGURATION_FOLDER_PATH = SMIA_ARCHIVE_PATH + '/config'
    CONFIGURATION_AAS_FOLDER_PATH = CONFIGURATION_FOLDER_PATH + '/aas'
    CM_GENERAL_PROPERTIES_FILENAME = 'smia-initialization.properties'
    CM_AAS_MODEL_FILENAME = ''
    CM_AAS_PROPERTIES_FILENAME = 'aas.properties'
    CM_ASSET_PROPERTIES_FILENAME = 'asset.properties'
    CM_SM_PROPERTIES_FILENAME = 'submodels.properties'

    # Submodel files
    SUBMODEL_FOLDER_PATH = '/aas_archive/submodels'
    TECHNICAL_DATA_SM_FILENAME = 'Technical_data_SM.xml'
    CONFIGURATION_SM_FILENAME = 'Configuration_SM.xml'

    # Status file
    STATUS_FOLDER_PATH = SMIA_ARCHIVE_PATH + '/status'
    SMIA_STATUS_FILE_NAME = 'smia_dt.json'
    CORE_STATUS_FILE_PATH = '/aas_archive/status/aas_core.json'



