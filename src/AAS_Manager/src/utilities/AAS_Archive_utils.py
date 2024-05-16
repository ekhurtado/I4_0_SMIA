""" File to save useful methods for accessing the AAS Archive."""
import calendar
import json
import os
import time

from utilities.AASarchiveInfo import AASarchiveInfo


# ------------------------
# Methods related to files
# ------------------------
def createStatusFile():
    """This method creates the status file of the AAS Manager and sets it to "initializing"."""
    initialStatusInfo = {'name': 'AAS_Manager', 'status': 'Initializing',
                             'timestamp': calendar.timegm(time.gmtime())}

    with (open(AASarchiveInfo.managerStatusFilePath, 'x') as statusFile):
        json.dump(initialStatusInfo, statusFile)
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


# -------------------------
# Methods related to status
# -------------------------
def changeStatus(newStatus):
    """This method updated the status of an AAS Manager instance.

    Parameters
    ----------
    :param newStatus: the new status of the AAS Manager instance.
    """
    statusFileJSON = fileToJSON(AASarchiveInfo.managerStatusFilePath)
    statusFileJSON['status'] = newStatus
    statusFileJSON['timestamp'] = calendar.timegm(time.gmtime())
    updateJSONFile(AASarchiveInfo.managerStatusFilePath, statusFileJSON)


def getStatus(entity):
    """This methods gets the status of the requested entity.

    Parameters
    ----------
    :param entity: The entity to get the status for."""
    statusFileJSON = None
    if entity == "Manager":
        statusFileJSON = fileToJSON(AASarchiveInfo.managerStatusFilePath)
    elif entity == "Core":
        statusFileJSON = fileToJSON(AASarchiveInfo.coreStatusFilePath)
    return statusFileJSON['status']

def checkCoreInitialization():
    """This method checks if the core has initialized so the Manager can be started."""
    coreInitialized = False
    while coreInitialized is False:
        if os.path.isfile(AASarchiveInfo.coreStatusFilePath) is True:
            if fileToJSON(AASarchiveInfo.coreStatusFilePath)['status'] is not "Initializing":
                coreInitialized = True
        time.sleep(1)   # waits 1s
    print('AAS Core has initialized, so the AAS Manager is starting.')

# ------------------------
# Methods related to JSON
# ------------------------
def fileToJSON(filePath):
    """This method gets the content of a JSON file.

    Parameters
    ----------
    :param filePath: the path of the JSON file."""
    f = open(filePath)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)
        return None
    return content


def updateJSONFile(filePath, content):
    """This method updates the content of a JSON file.

    Parameters
    ----------
    :param filePath: the path to the JSON file.
    :param content: the content of the JSON file.
    """
    with open(filePath, "w") as outfile:
        json.dump(content, outfile)


# ------------------------
# Methods related to XML
# ------------------------
def XMLToFile(filePath, XML_content):
    """This method writes the content of a XML in a file."""
    with open(filePath, 'wb') as sm_file:
        sm_file.write(XML_content)