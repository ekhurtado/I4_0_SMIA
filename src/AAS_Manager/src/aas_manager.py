import time
from flask import Flask, request

from logic import Services_utils
from utilities import AAS_Archive_utils, Submodels_utils
from utilities.ConfigMap_utils import ConfigMap_utils

interaction_id = 0

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


@app.route('/Service/', methods=['POST'])
def service_requests():
    """Method for handling requests for Asset Related Services."""
    print(request.data)
    performative = request.json['performative']

    match performative:
        case "CallForProposal":
            print("Call for proposal request.")

            global interaction_id

            match request.json['serviceType']:
                case "AssetRelatedService":
                    Services_utils.handle_asset_related_svc(interaction_id, request.json)
                case "AASInfrastructureServices":
                    Services_utils.handle_aas_infrastructure_svc(interaction_id, request.json)
                case "AASservices":
                    Services_utils.handle_aas_services(interaction_id, request.json)
                case "SubmodelServices":
                    Services_utils.handle_submodel_services(interaction_id, request.json)
                case _:
                    print("Service type not available.")

            # Increment the interactionID
            interaction_id = interaction_id + 1
        case _:
            print("Performative not available.")

    return "OK"


def initialize_aas_archive():
    """ This method initializes the system of the I4.0 Component, performing the necessary actions to let the
    AAS Archive in the initial conditions to start the main program."""
    # Create the status file
    AAS_Archive_utils.create_status_file()

    # Create the interaction files
    AAS_Archive_utils.create_interaction_files()

    # Create log file
    AAS_Archive_utils.create_log_files()

    print("AAS Archive initialized.")


def initialize_submodels():
    """ This method initializes the submodels of the I4.0 Component, obtaining all the information from the ConfigMap
    associated to the component, in order to create the necessary XML submodel files and store them in the AAS Archive.
    """

    # First, the selected submodels are obtained
    selected_submodel_names = ConfigMap_utils.get_submodel_names()

    # TODO: faltaria comprobar entre los submodelos seleccionados cuales son propios de todos los AASs (los que seran
    #  los propios del AAS Manager). El usuario podra proponer submodelos y tambien se escribira en el ConfigMap su
    #  informacion, pero sera el AAS Core (desarrollado por el usuario) el encargado de generar el XML (como tambien de
    #  actualizarlo, leerlo...), ya que es el usuario el que conoce su estructura

    # Create submodels files for each one
    Submodels_utils.create_submodel_files(selected_submodel_names)


if __name__ == '__main__':
    print("Initializing AAS Manager...")
    # The interactionID is started at 0
    interaction_id = 0

    time.sleep(10)

    # Before starting the AAS Manager, it will execute the required initialization of the system
    initialize_aas_archive()
    initialize_submodels()

    # Set that AAS Manager is ready
    AAS_Archive_utils.change_status('InitializationReady')

    # Wait until the AAS Core has initialized
    AAS_Archive_utils.check_core_initialization()

    # Run application
    app.run(host="0.0.0.0", port=7000)
