"""This class contains methods related to service management."""
import time

from logic import Interactions_utils
from utilities.AASarchiveInfo import AASarchiveInfo

def handleAssetRelatedSvc(svcInteractionID, svcData):
    """This method handles service related services.

    Parameters
    ----------
    :param svcInteractionID : the identifier of the interaction.
    :param svcData : the information of the data in JSON format.
    """
    # Create the valid JSON structure to save in svcRequests.json
    svcRequestJSON = Interactions_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                            svcID=svcData['serviceID'],
                                                            svcType=svcData['serviceType'],
                                                            svcData=svcData['serviceData'])
    # Save the JSON in svcRequests.json
    Interactions_utils.addNewSvcRequest(svcRequestJSON)

    # Wait until the service is completed
    # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
    #  haber una espera hasta que se complete el servicio
    svcCompleted = False
    while not svcCompleted:
        print(str(svcData['serviceID']) + "service not completed yet.")
        svcResponse = Interactions_utils.getSvcResponseInfo(svcInteractionID)
        if svcResponse is not None:
            print(svcResponse)
            # Set the service as completed
            svcCompleted = True
            # Write the information in the log file
            Interactions_utils.saveSvcInfoInLogFile('Manager',
                                                   AASarchiveInfo.assetRelatedSvcLogFileName, svcInteractionID)
            # Return message to the sender
            return "Service completed! Response: " + str(svcResponse)

        # Waits 2 seconds
        time.sleep(2)


def handleAASInfrastructureSvc(svcInteractionID, svcData):
    pass


def handleAASservices(svcInteractionID, svcData):
    return None


def handleSubmodelServices(svcInteractionID, svcData):
    return None
