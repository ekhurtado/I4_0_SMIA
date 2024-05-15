class AASarchiveInfo:
    """This class will contain all information about the AAS Archive"""

    # Paths related to interactions between Manager and Core
    interactionsFolderPath = '/aas_archive/interactions'
    coreInteractionsFolderPath = '/aas_archive/interactions/core'
    managerInteractionsFolderPath = '/aas_archive/interactions/manager'

    # Subpath of interaction files
    svcRequestFileSubPath = '/svcRequests.json'
    svcResponseFileSubPath = '/svcResponses.json'

    # Paths for log files
    logFolderPath = '/aas_archive/log'
    svcLogFolderPath = '/aas_archive/log/services'
    assetRelatedSvcLogFileName = 'assetRelatedSvcHistory.log'
    aasInfrastructureSvcLogFileName = 'aasInfrastructureSvcHistory.log'
    aasServicesLogFileName = 'aasServicesHistory.log'
    submodelServicesLogFileName = 'submodelServicesHistory.log'

    # ConfigMap files
    configMapPath = '/aas_archive/config'
    cmSMPropertiesFileName = 'submodels.properties'

    # Submodel files
    subModelFolderPath = '/aas_archive/submodels'
    technicalDataSMFileName = 'Technical_data_SM.xml'
    configurationSMFileName = 'Configuration_SM.xml'

    # Status file
    statusFilePath = '/aas_archive/status/aas_manager.properties'
