# File to save useful methods for accessing the AAS Archive
import calendar
import configparser
import json
import os
import time

# svcRequests = "examples/ManagerToCore.json"
# svcResponses = "examples/CoreToManager.json"

svcRequests = "/aas_archive/interactions/ManagerToCore.json"
svcResponses = "/aas_archive/interactions/CoreToManager.json"


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


# ----------------------------
# Methods related to responses
# ----------------------------
def checkSvcResponse(interactionID):
    svcResponsesJSON = fileToJSON(svcResponses)
    for i in svcResponsesJSON['serviceResponses']:
        if i['interactionID'] == interactionID:
            return i
    return None
