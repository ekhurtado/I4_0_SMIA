import json
import os
import time

from flask import Flask, request
from utilities import AAS_Archive_utils, Submodels_utils

interactionID = 0

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    print(request)

    if request.method == 'GET':
        # Handle GET requests
        print("GET type request")
    elif request.method == 'POST':
        # Handle POST requests
        print("POST type request")
    return "OK"


@app.route('/AssetRelatedService/', methods=['POST'])
def assetRelatedSvcRequests():
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")
            global interactionID

            svcInteractionID = interactionID

            # Create the valid JSON structure to save in ManagerToCore.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                                    serviceID=request.json['serviceID'],
                                                                    serviceType=request.json['serviceType'],
                                                                    serviceData=request.json['serviceData'])
            # Save the JSON in ManagerToCore.json
            AAS_Archive_utils.addNewSvcRequest(svcRequestJSON)

            # Increment the interactionID
            interactionID = interactionID + 1

            # Wait until the service is completed
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.checkSvcResponse(interactionID=svcInteractionID)
                if svcResponse is not None:
                    print(svcResponse)
                    # Set the service as completed
                    svcCompleted = True
                    # Write the information in the log file
                    AAS_Archive_utils.saveSvcInfoInLogFile(svcInteractionID)
                    # Return message to the sender
                    return "Service completed! Response: " + str(svcResponse)

                # Waits 2 seconds
                time.sleep(2)
        case _:
            print("Performative not available.")

    return "OK"


def initializeSystem():
    # Create the interaction files
    AAS_Archive_utils.createInteractionFiles()

    # Create configuration files from ConfigMap
    Submodels_utils.createSubModels()

    # Create log file
    AAS_Archive_utils.createLogFile()


if __name__ == '__main__':
    print("Initializing AAS Manager...")
    interactionID = 0

    # Before starting the AAS Manager, it will execute the required initialization of the system
    initializeSystem()

    # Run application
    app.run(host="0.0.0.0", port=7000)

