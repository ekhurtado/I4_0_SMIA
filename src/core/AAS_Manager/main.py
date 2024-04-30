import json
import os

from flask import Flask, request
from utilities import AAS_Archive_utils

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

            # Create the valid JSON structure to save in ManagerToCore.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=interactionID,
                                                                    serviceID=request.json['serviceID'],
                                                                    serviceType=request.json['serviceType'],
                                                                    serviceData=request.json['serviceData'])
            # Save the JSON in ManagerToCore.json
            AAS_Archive_utils.addNewSvcRequest(svcRequestJSON)

            # Wait until the service is completed
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.checkSvcResponse(interactionID=interactionID)
                if svcResponse is not None:
                    print(svcResponse)
                    svcCompleted = True
                    interactionID = interactionID + 1

                    return "Service completed! Response: " + str(svcResponse)
        case _:
            print("Performative not available.")

    return "OK"

if __name__ == '__main__':
    print("Initializing AAS Manager...")
    interactionID = 0
    app.run(host="0.0.0.0", port=7000)
