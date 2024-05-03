# File to save useful methods for accessing the AAS Archive
import calendar
import configparser
from datetime import datetime
import json
import os
import time

# svcRequests = "examples/ManagerToCore.json"
# svcResponses = "examples/CoreToManager.json"
# logFilePath = "examples/ServiceHistory.log"

svcRequests = "/aas_archive/interactions/ManagerToCore.json"
svcResponses = "/aas_archive/interactions/CoreToManager.json"
logFilePath = "/aas_archive/log/ServiceHistory.log"


# ------------------------
# Methods related to files
# ------------------------
def createInteractionFiles():

    # First the folder is created
    os.mkdir("/aas_archive/interactions")

    # Then the content is added
    with open(svcRequests, 'x') as requestsFile, open(svcResponses, 'x') as responsesFile:
        requestsFile.write('{"serviceRequests": []}')
        responsesFile.write('{"serviceResponses": []}')

        requestsFile.close()
        responsesFile.close()

def createLogFile():
    # First the folder is created
    os.mkdir("/aas_archive/log")

    # Then the content is added
    with open(logFilePath, 'x') as logFile:
        logFile.write('[]')
        logFile.close()


def fileToJSON(filePath):
    f = open(filePath)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:", e)
        return None
    return content


def updateFile(filePath, content):
    with open(filePath, "w") as outfile:
        json.dump(content, outfile)


# ---------------------------
# Methods related to requests
# ---------------------------
def createSvcRequestJSON(interactionID, serviceID, serviceType, serviceData):
    svcRequestJSON = {"interactionID": interactionID,
                      "serviceID": serviceID,
                      "serviceType": serviceType,
                      "serviceData": serviceData
                      }
    svcRequestJSON['serviceData']['timestamp'] = calendar.timegm(time.gmtime())
    return svcRequestJSON


def addNewSvcRequest(newRequestJSON):
    svcRequestsJSON = fileToJSON(svcRequests)
    if svcRequestsJSON == None:
        svcRequestsJSON = {'serviceRequests': [newRequestJSON]}
    else:
        svcRequestsJSON['serviceRequests'].append(newRequestJSON)

    updateFile(svcRequests, svcRequestsJSON)

def getSvcRequestInfo(interactionID):
    svcRequestsJSON = fileToJSON(svcRequests)
    for i in svcRequestsJSON['serviceRequests']:
        if i['interactionID'] == interactionID:
            return i
    return None

# ----------------------------
# Methods related to responses
# ----------------------------
def checkSvcResponse(interactionID):
    svcResponsesJSON = fileToJSON(svcResponses)
    for i in svcResponsesJSON['serviceResponses']:
        if i['interactionID'] == interactionID:
            return i
    return None

# ----------------------------
# Methods related to responses
# ----------------------------
def saveSvcInfoInLogFile(interactionID):
    # Get the information about the request and response
    svcResponseInfo = checkSvcResponse(interactionID)
    svcRequestInfo = getSvcRequestInfo(interactionID)

    # Create the JSON structure
    logStructure = {
        'level': 'INFO',
        'interactionID': interactionID,
        'serviceStatus': svcResponseInfo['serviceStatus'],
        'serviceInfo': {
            'serviceID': svcRequestInfo['serviceID'],
            'serviceType': svcRequestInfo['serviceType'],
            'requestTimestamp': str(datetime.fromtimestamp(svcRequestInfo['serviceData']['timestamp'])),
            'responseTimestamp': str(datetime.fromtimestamp(svcResponseInfo['serviceData']['timestamp']))
        }
    }
    # If some data has been requested, added to the structura
    requestedData = svcRequestInfo['serviceData']['requestedData']
    if requestedData is not None:
        svcDataJSON = {'requestedData': requestedData, 'dataValue': svcResponseInfo['serviceData'][requestedData]}
        logStructure['serviceInfo']['serviceData'] = svcDataJSON

    # Get the content of LOG file
    logFileJSON = fileToJSON(logFilePath)
    # Add the structure in the file
    logFileJSON.append(logStructure)
    updateFile(filePath=logFilePath, content=logFileJSON)
    print("Service information related to interaction " + str(interactionID) + " added in log file.")