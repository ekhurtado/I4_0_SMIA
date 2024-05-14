import time

from flask import Flask, request
from utilities import AAS_Archive_utils, Submodels_utils, ConfigMap_utils
from utilities.AASarchive import AASarchive

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
    """Method for handling requests for Asset Related Services."""
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")
            global interactionID

            svcInteractionID = interactionID

            # Create the valid JSON structure to save in svcRequests.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                                    svcID=request.json['serviceID'],
                                                                    svcType=request.json['serviceType'],
                                                                    svcData=request.json['serviceData'])
            # Save the JSON in svcRequests.json
            AAS_Archive_utils.addNewSvcRequest(AASarchive.assetRelatedSvcPath, svcRequestJSON)

            # Increment the interactionID
            interactionID = interactionID + 1

            # Wait until the service is completed
            # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
            #  haber una espera hasta que se complete el servicio
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.getSvcResponse(AASarchive.assetRelatedSvcPath, svcInteractionID)
                if svcResponse is not None:
                    print(svcResponse)
                    # Set the service as completed
                    svcCompleted = True
                    # Write the information in the log file
                    AAS_Archive_utils.saveSvcInfoInLogFile(AASarchive.assetRelatedSvcPath,
                                                           AASarchive.assetRelatedSvcLogFileName, svcInteractionID)
                    # Return message to the sender
                    return "Service completed! Response: " + str(svcResponse)

                # Waits 2 seconds
                time.sleep(2)
        case _:
            print("Performative not available.")

    return "OK"

@app.route('/AASInfrastructureService/', methods=['POST'])
def aasInfrastructureSvcRequests():
    """Method for handling requests for AAS Infrastructure Services."""
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")
            global interactionID

            svcInteractionID = interactionID

            # Create the valid JSON structure to save in svcRequests.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                                    svcID=request.json['serviceID'],
                                                                    svcType=request.json['serviceType'],
                                                                    svcData=request.json['serviceData'])
            # Save the JSON in svcRequests.json
            AAS_Archive_utils.addNewSvcRequest(AASarchive.aasInfrastructureSvcPath, svcRequestJSON)

            # Increment the interactionID
            interactionID = interactionID + 1

            # Wait until the service is completed
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.getSvcResponse(AASarchive.aasInfrastructureSvcPath, svcInteractionID)
                if svcResponse is not None:
                    print(svcResponse)
                    # Set the service as completed
                    svcCompleted = True
                    # Write the information in the log file
                    AAS_Archive_utils.saveSvcInfoInLogFile(AASarchive.aasInfrastructureSvcPath,
                                                           AASarchive.aasInfrastructureSvcLogFileName, svcInteractionID)
                    # Return message to the sender
                    return "Service completed! Response: " + str(svcResponse)

                # Waits 2 seconds
                time.sleep(2)
        case _:
            print("Performative not available.")

    return "OK"


@app.route('/AASservice/', methods=['POST'])
def aasServiceRequests():
    """Method for handling requests for AAS Services."""
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")
            global interactionID

            svcInteractionID = interactionID

            # Create the valid JSON structure to save in svcRequests.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                                    svcID=request.json['serviceID'],
                                                                    svcType=request.json['serviceType'],
                                                                    svcData=request.json['serviceData'])
            # Save the JSON in svcRequests.json
            AAS_Archive_utils.addNewSvcRequest(AASarchive.aasServicesPath, svcRequestJSON)

            # Increment the interactionID
            interactionID = interactionID + 1

            # Wait until the service is completed
            # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
            #  haber una espera hasta que se complete el servicio
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.getSvcResponse(AASarchive.aasServicesPath, svcInteractionID)
                if svcResponse is not None:
                    print(svcResponse)
                    # Set the service as completed
                    svcCompleted = True
                    # Write the information in the log file
                    AAS_Archive_utils.saveSvcInfoInLogFile(AASarchive.aasServicesPath,
                                                           AASarchive.aasServicesLogFileName, svcInteractionID)
                    # Return message to the sender
                    return "Service completed! Response: " + str(svcResponse)

                # Waits 2 seconds
                time.sleep(2)
        case _:
            print("Performative not available.")

    return "OK"

@app.route('/SubmodelService/', methods=['POST'])
def submodelSvcRequests():
    """Method for handling requests for Submodel Services."""
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")
            global interactionID

            svcInteractionID = interactionID

            # Create the valid JSON structure to save in svcRequests.json
            svcRequestJSON = AAS_Archive_utils.createSvcRequestJSON(interactionID=svcInteractionID,
                                                                    svcID=request.json['serviceID'],
                                                                    svcType=request.json['serviceType'],
                                                                    svcData=request.json['serviceData'])
            # Save the JSON in svcRequests.json
            AAS_Archive_utils.addNewSvcRequest(AASarchive.submodelServicesPath, svcRequestJSON)

            # Increment the interactionID
            interactionID = interactionID + 1

            # Wait until the service is completed
            # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
            #  haber una espera hasta que se complete el servicio
            svcCompleted = False
            while not svcCompleted:
                print(str(request.json['serviceID']) + "service not completed yet.")
                svcResponse = AAS_Archive_utils.getSvcResponse(AASarchive.submodelServicesPath, svcInteractionID)
                if svcResponse is not None:
                    print(svcResponse)
                    # Set the service as completed
                    svcCompleted = True
                    # Write the information in the log file
                    AAS_Archive_utils.saveSvcInfoInLogFile(AASarchive.submodelServicesPath,
                                                           AASarchive.submodelServicesLogFileName, svcInteractionID)
                    # Return message to the sender
                    return "Service completed! Response: " + str(svcResponse)

                # Waits 2 seconds
                time.sleep(2)
        case _:
            print("Performative not available.")

    return "OK"


def initializeAASarchive():
    """ This method initializes the system of the I4.0 Component, performing the necessary actions to let the AAS Archive
     in the initial conditions to start the main program."""
    # Create the interaction files
    AAS_Archive_utils.createInteractionFiles()

    # Create log file
    AAS_Archive_utils.createLogFiles()

    # Create submodels folder
    Submodels_utils.createSubModelFolder()

def initializeSubModels():
    """ This method initializes the submodels of the I4.0 Component, obtaining all the information from the ConfigMap
    associated to the component, in order to create the necessary XML submodel files and store them in the AAS Archive."""

    # First, the selected submodels are obtained
    selectedSubModelNames = ConfigMap_utils.getSubModelNames()

    # TODO: faltaria comprobar entre los submodelos seleccionados cuales son propios de todos los AASs (los que seran
    #  los propios del AAS Manager). El usuario podra proponer submodelos y tambien se escribira en el ConfigMap su
    #  informacion, pero sera el AAS Core (desarrollado por el usuario) el encargado de generar el XML (como tambien de
    #  actualizarlo, leerlo...), ya que es el usuario el que conoce su estructura

    # Create submodels files for each one
    Submodels_utils.createSubModelFiles(selectedSubModelNames)


if __name__ == '__main__':
    print("Initializing AAS Manager...")
    # The interactionID is started at 0
    interactionID = 0

    # Before starting the AAS Manager, it will execute the required initialization of the system
    initializeAASarchive()
    initializeSubModels()

    # Run application
    app.run(host="0.0.0.0", port=7000)

