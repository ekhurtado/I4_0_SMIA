class AASarchiveInfo:
    """This class contains all information about the AAS Archive paths."""

    # Paths related to interactions between Manager and Core
    INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions'
    CORE_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/core'
    MANAGER_INTERACTIONS_FOLDER_PATH = '/aas_archive/interactions/manager'

    # Subpath of interaction files
    SVC_REQUEST_FILE_SUBPATH = '/svcRequests.json'
    SVC_RESPONSE_FILE_SUBPATH = '/svcResponses.json'

    # ConfigMap files
    CONFIG_MAP_PATH = '/aas_archive/config'
    CM_AAS_PROPERTIES_FILENAME = 'aas.properties'
    CM_ASSET_PROPERTIES_FILENAME = 'asset.properties'
    CM_SM_PROPERTIES_FILENAME = 'submodels.properties'

    # Status file
    MANAGER_STATUS_FILE_PATH = '/aas_archive/status/aas_manager.json'
    CORE_STATUS_FILE_PATH = '/aas_archive/status/aas_core.json'