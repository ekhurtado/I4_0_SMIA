

class AASarchive:
    """This class will contain all information about the AAS Archive"""

    # Path to the files of all type of services
    svcFolderPath = '/aas_archive/services'
    assetRelatedSvcPath = '/aas_archive/services/assetRelatedSvc'
    aasInfrastructureSvcPath = '/aas_archive/services/aasInfrastructureSvc'
    aasServicesPath = '/aas_archive/services/aasServices'
    submodelServicesPath = '/aas_archive/services/submodelServices'

    # Subpath of interaction files
    svcRequestFileSubPath = '/interactions/svcRequests.json'
    svcResponseFileSubPath = '/interactions/svcResponses.json'

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