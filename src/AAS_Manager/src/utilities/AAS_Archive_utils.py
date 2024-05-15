# File to save useful methods for accessing the AAS Archive
import calendar
import configparser
import json
import os
import time

from utilities.AASarchiveInfo import AASarchiveInfo


# svcRequests = "/aas_archive/interactions/ManagerToCore.json"
# svcResponses = "/aas_archive/interactions/CoreToManager.json"
# logFilePath = "/aas_archive/log/ServiceHistory.log"
#
#
# assetRelatedSvcPath = '/aas_archive/services/assetRelatedSvc'
# aasInfrastructureSvcPath = '/aas_archive/services/aasInfrastructureSvc'
# aasServicesPath = '/aas_archive/services/aasServices'
# submodelServicesPath = '/aas_archive/services/submodelServices'

# ------------------------
# Methods related to files
# ------------------------
def createStatusFile():
    """This method creates the status file of the AAS Manager and sets it to "initializing"."""
    config = configparser.ConfigParser()
    config['INFORMATION'] = {'name': 'AAS_Manager', 'status': 'Initializing',
                             'timestamp': str(calendar.timegm(time.gmtime()))}
    with (open(AASarchiveInfo.statusFilePath, 'x') as statusFile):
        config.write(statusFile)
        statusFile.close()


def createInteractionFiles():
    """This method creates the necessary interaction files to exchange information between AAS Core and AAS Manager."""

    # First interaction folders are created
    os.mkdir(AASarchiveInfo.coreInteractionsFolderPath)
    os.mkdir(AASarchiveInfo.managerInteractionsFolderPath)

    # Then the interaction files are added in each folder
    with (open(AASarchiveInfo.coreInteractionsFolderPath + AASarchiveInfo.svcRequestFileSubPath,
               'x') as coreRequestsFile,
          open(AASarchiveInfo.coreInteractionsFolderPath + AASarchiveInfo.svcResponseFileSubPath,
               'x') as coreResponsesFile,
          open(AASarchiveInfo.managerInteractionsFolderPath + AASarchiveInfo.svcRequestFileSubPath,
               'x') as managerRequestsFile,
          open(AASarchiveInfo.managerInteractionsFolderPath + AASarchiveInfo.svcResponseFileSubPath,
               'x') as managerResponsesFile):
        coreRequestsFile.write('{"serviceRequests": []}')
        coreRequestsFile.close()

        managerRequestsFile.write('{"serviceRequests": []}')
        managerRequestsFile.close()

        coreResponsesFile.write('{"serviceResponses": []}')
        coreResponsesFile.close()

        managerResponsesFile.write('{"serviceResponses": []}')
        managerResponsesFile.close()


def createLogFiles():
    """This method creates the necessary log files to save services information."""

    # First the log folder is created
    os.mkdir(AASarchiveInfo.logFolderPath)
    # The folder for services log is also created
    os.mkdir(AASarchiveInfo.svcLogFolderPath)

    # Then the log files are added in each folder
    allSvcLogFileNames = [AASarchiveInfo.assetRelatedSvcLogFileName, AASarchiveInfo.aasInfrastructureSvcLogFileName,
                          AASarchiveInfo.aasServicesLogFileName, AASarchiveInfo.submodelServicesLogFileName]
    for logFileName in allSvcLogFileNames:
        with open(AASarchiveInfo.svcLogFolderPath + '/' + logFileName, 'x') as logFile:
            logFile.write('[]')
            logFile.close()


def changeStatus(newStatus):
    """This method updated the status of an AAS Manager instance.

    Parameters
    ----------
    :param newStatus: the new status of the AAS Manager instance.
    """
    config = configparser.RawConfigParser()
    config.read(AASarchiveInfo.statusFilePath)
    config.set('INFORMATION', 'status', newStatus)
    config.set('INFORMATION', 'timestamp', str(calendar.timegm(time.gmtime())))


def fileToJSON(filePath):
    """This method gets the content of a JSON file."""
    f = open(filePath)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)
        return None
    return content


def updateFile(filePath, content):
    """This method updates the content of a JSON file."""
    with open(filePath, "w") as outfile:
        json.dump(content, outfile)


def XMLToFile(filePath, XML_content):
    """This method writes the content of a XML in a file."""
    with open(filePath, 'wb') as sm_file:
        sm_file.write(XML_content)

