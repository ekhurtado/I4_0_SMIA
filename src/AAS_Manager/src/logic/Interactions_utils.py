"""This class groups the methods related to the interactions between the Manager and the Core"""
import calendar
import configparser
from datetime import datetime
import json
import os
import time

from utilities.AASarchiveInfo import AASarchiveInfo

# --------------------------------------------
# Methods related to requests (by AAS Manager)
# --------------------------------------------
def createSvcRequestJSON(interactionID, svcID, svcType, svcData):
    """This method creates a service request JSON object.

    Parameters
    ----------
    :param interactionID: Identifier of the interaction.
    :param svcID: Identifier of the service
    :param svcType: Type of the service.
    :param svcData: Data of the service in JSON format.

    Returns
    -------
    :return svcRequestJSON: a JSON object with the service request information.
    """
    svcRequestJSON = {"interactionID": interactionID,
                      "serviceID": svcID,
                      "serviceType": svcType,
                      "serviceData": svcData
                      }
    svcRequestJSON['serviceData']['timestamp'] = calendar.timegm(time.gmtime())
    return svcRequestJSON


def addNewSvcRequest(newRequestJSON):
    """This method adds a new service request to the related service interaction file of the manager and updates it in the AAS Archive.

    Parameters
    ----------
    :param newRequestJSON: The service requests content in JSON format.
    """

    # Get the content of the service requests interaction file
    svcRequestsFilePath = AASarchiveInfo.managerInteractionsFolderPath + AASarchiveInfo.svcRequestFileSubPath
    svcRequestsJSON = fileToJSON(svcRequestsFilePath)
    if svcRequestsJSON is None:
        svcRequestsJSON = {'serviceRequests': [newRequestJSON]}
    else:
        svcRequestsJSON['serviceRequests'].append(newRequestJSON)

    updateFile(svcRequestsFilePath, svcRequestsJSON)


def getSvcRequestInfo(interactionID):
    """This method gets the information of a service request.

    Parameters
    ----------
    :param interactionID: Identifier of the interaction.

    Returns
    -------
    :return the information of the service request in JSON format.
    """
    svcRequestsJSON = fileToJSON(AASarchiveInfo.managerInteractionsFolderPath + AASarchiveInfo.svcRequestFileSubPath)
    for i in svcRequestsJSON['serviceRequests']:
        if i['interactionID'] == interactionID:
            return i
    return None


# --------------------------------------------
# Methods related to responses (from AAS Core)
# --------------------------------------------
def getSvcResponseInfo(interactionID):
    """This method gets the information of a response from the AAS Core related to a request made by the AAS Manager.

    Parameters
    ----------
    :param interactionID: Identifier of the interaction.

    Returns
    -------
    :return the information of the service request in JSON format.
    """
    svcResponsesJSON = fileToJSON(AASarchiveInfo.coreInteractionsFolderPath + AASarchiveInfo.svcResponseFileSubPath)
    for i in svcResponsesJSON['serviceResponses']:
        if i['interactionID'] == interactionID:
            return i
    return None


# ----------------------------
# Methods related to responses
# ----------------------------
def saveSvcInfoInLogFile(requestedEntity, svcTypeLogFileName, interactionID):
    """This method saves the information of a service request in the associated log file.

    Parameters
    ----------
    :param requestedEntity: The entity that has requested the service, to know in which interaction files to search.
    :param svcTypeLogFileName: The log file name of the service type.
    :param interactionID: Identifier of the interaction.
    """

    # Get the information about the request and response
    svcResponseInfo, svcRequestInfo = getSvcInfo(requestedEntity, interactionID)

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
    logFileJSON = fileToJSON(AASarchiveInfo.svcLogFolderPath + '/' + svcTypeLogFileName)

    # Add the structure in the file
    logFileJSON.append(logStructure)
    updateFile(filePath=AASarchiveInfo.svcLogFolderPath + '/' + svcTypeLogFileName, content=logFileJSON)
    print("Service information related to interaction " + str(interactionID) + " added in log file.")


# -------------
# Other methods
# -------------
def getSvcInfo(requestedEntity, interactionID):
    """This method obtains the information of the service considering the entity that has requested the service. In the
    entity is Manager it has to search in Manager requests and Core responses, and in the case of being the Core the one
     that has made the request, the opposite.

     Parameters
     ----------
     :param requestedEntity: The entity that has requested the service, to know in which interaction files to search.
     :param interactionID: Identifier of the interaction.

     Returns
     -------
     :returns requestInfo: Information of the service request in JSON format and responseInfo: Information of the
     service response in JSON format.
     """

    if requestedEntity is "Manager":
        return getSvcRequestInfo(interactionID), getSvcResponseInfo(interactionID)
    elif requestedEntity is "Core":
        # In this case, it has to search in the opposite files (request of Core and response of Manager)
        svcRequestsJSON = fileToJSON(
            AASarchiveInfo.managerInteractionsFolderPath + AASarchiveInfo.svcRequestFileSubPath)
        svcRequestInfo = None
        for i in svcRequestsJSON['serviceRequests']:
            if i['interactionID'] == interactionID:
                svcRequestInfo = i
                break

        svcResponsesJSON = fileToJSON(AASarchiveInfo.coreInteractionsFolderPath + AASarchiveInfo.svcResponseFileSubPath)
        svcResponseInfo = None
        for i in svcResponsesJSON['serviceResponses']:
            if i['interactionID'] == interactionID:
                svcResponseInfo = i
                break

        return svcRequestInfo, svcResponseInfo
