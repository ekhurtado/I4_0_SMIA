"""This class contains methods related to service management. It contains all type of services proposed in the
Functional View of RAMI 4.0."""
import time

from logic import Interactions_utils
from utilities.AAS_archive_info import AASarchiveInfo


def handle_asset_related_svc(svc_interaction_id, svc_data):
    """This method handles Asset Related Services. These services are part of I4.0 Application Component (application
    relevant).

    Parameters
    ----------
    :param svc_interaction_id : the identifier of the interaction.
    :param svc_data : the information of the data in JSON format.
    """
    # Create the valid JSON structure to save in svcRequests.json
    svc_request_json = Interactions_utils.create_svc_request_json(interaction_id=svc_interaction_id,
                                                                  svc_id=svc_data['serviceID'],
                                                                  svc_type=svc_data['serviceType'],
                                                                  svc_data=svc_data['serviceData'])
    # Save the JSON in svcRequests.json
    Interactions_utils.add_new_svc_request(svc_request_json)

    # Wait until the service is completed
    # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
    #  haber una espera hasta que se complete el servicio
    while True:
        print(str(svc_data['serviceID']) + "service not completed yet.")
        svc_response = Interactions_utils.get_svc_response_info(svc_interaction_id)
        if svc_response is not None:
            print(svc_response)
            # Set the service as completed
            # Write the information in the log file
            Interactions_utils.save_svc_info_in_log_file('Manager',
                                                         AASarchiveInfo.ASSET_RELATED_SVC_LOG_FILENAME,
                                                         svc_interaction_id)
            # Return message to the sender
            return "Service completed! Response: " + str(svc_response)

        # Waits 2 seconds
        time.sleep(2)


def handle_aas_infrastructure_svc(svc_interaction_id, svc_data):
    """This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services
    (Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an AAS, but
    by the platform (computational infrastructure). These include the AAS Create Service (for creating AASs with unique
    identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery Services (for searching
    for AASs).

    Parameters
    ----------
    :param svc_interaction_id : the identifier of the interaction.
    :param svc_data : the information of the data in JSON format.
    """
    pass


def handle_aas_services(svc_interaction_id, svc_data):
    """This method handles AAS Services. These services serve for the management of asset-related information through
    a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
    and register submodels), Meta-information Management Services (including Classification Services, to check if the
    interface complies with the specifications; Contextualization Services, to check if they belong together in a
    context to build a common function; and Restriction of Use Services, divided between access control and usage
    control) and Exposure and Discovery Services (to search for submodels or asset related services).

    Parameters
    ----------
    :param svc_interaction_id : the identifier of the interaction.
    :param svc_data : the information of the data in JSON format.
    """
    return None


def handle_submodel_services(svc_interaction_id, svc_data):
    """This method handles Submodel Services. These services are part of I4.0 Application Component (application
    relevant).

    Parameters
    ----------
    :param svc_interaction_id : the identifier of the interaction.
    :param svc_data : the information of the data in JSON format.
    """
    return None
