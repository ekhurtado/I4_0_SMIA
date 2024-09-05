import json
import logging
import time

from spade.behaviour import CyclicBehaviour

from behaviours.SvcRequestHandlingBehaviour import SvcRequestHandlingBehaviour
from logic import Services_utils, Interactions_utils
from utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


class SvcACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the AAS Manager will receive from the
    others standardized AAS Manager in the I4.0 System.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("ACLHandlingBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # TODO modificar el concepto de como gestionar los servicios. En este behaviour (llamemosle a partir de ahora
            #  SvcRequestsHanldingBehaviour) se gestionarán todas las peticiones de servicios via ACL, pero no gestionará
            #  cada servicio individualmente. Por cada servicio añadira otro behaviour al agente (llamemosle
            #  'SvcHandlingBehaviour') y este sí será el encargado de gestionar ese servicio en concreto. De esta forma,
            #  conseguimos que los servicios se gestionen "en paralelo" (aunque no es 100% paralelo según van llegando
            #  peticiones de servicios se van generando behaviours, así que se van gestionando todos a la vez). Gracias
            #  a esta forma cada behaviour individual es capaz de gestionar mas facilmente su servicio (analizar si
            #  tarda mucho en realizarse, guardar en el log cuando finalice toda la informacion que la tendra en su
            #  propia clase, etc.). Cada behaviour individual será el que se eliminará del agente en cuanto el servicio
            #  se haya completado (self.kill())

            # TODO ACTUALIZACION: de momento se va a seguir esta idea, y por cada peticion de servicio se va a crear un
            #  behaviour (SvcRequestHandlingBehaviour). Este se creará tanto con peticiones via ACL como peticiones via
            #  Interaction (solicitadas por el AAS Core), ya que en ambos casos es una solicitud de un servicio al AAS
            #  Manager. Este dentro del behaviour decidirá los pasos a seguir para llevar a cabo ese servicio (solicitar
            #  algo por interaccion, o por ACL a otro Manager...). Para respuestas a peticiones de servicio se generará
            #  otro behaviour diferente

            # An ACL message has been received by the agent
            _logger.aclinfo("         + Message received on AAS Manager Agent (ACLHandlingBehaviour)")
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # TODO por ACL entiendo que también pueden llegar respuestas de servicios, no solo solicitudes,
            #  asi que habria que modificar esto
            service_category = msg_json_body['serviceData']['serviceCategory']

            if service_category == 'service-request':
                # A new service request is added to the global dictionary of ACL requests of the agent
                self.myagent.

                # A new behaviour is added to the SPADE agent to handle this specific service request
                svc_req_handling_behav = SvcRequestHandlingBehaviour(self.agent, msg_json_body)
                self.myagent.add_behaviour(svc_req_handling_behav)


        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (ACLHandlingBehaviour)")

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_asset_related_svc(self, svc_data):
        """
        This method handles Asset Related Services. These services are part of I4.0 Application Component (application
        relevant).

        Args:
            svc_data (dict): the information of the data in JSON format.
        """
        # First of all, the service request will be made to the AAS Core

        # Create the valid JSON structure to save in svcRequests.json
        svc_request_json = Interactions_utils.create_svc_request_json(interaction_id=self.agent.interaction_id,
                                                                      svc_id=svc_data['serviceID'],
                                                                      svc_type=svc_data['serviceType'],
                                                                      svc_data=svc_data['serviceData'])
        # TODO this code is for the interaction through JSON (it has to be removed)
        # # Save the JSON in svcRequests.json
        # Interactions_utils.add_new_svc_request(svc_request_json)

        # TODO test if it is working with Kafka
        request_result = await Interactions_utils.send_interaction_msg_to_core(client_id='i4-0-smia-manager',
                                                                         msg_key='manager-service-request',
                                                                         msg_data=svc_request_json)
        if request_result is not "OK":
            _logger.error("The AAS Manager-Core interaction is not working: " + str(request_result))
        else:
            _logger.aclinfo("The service with interaction id [" +str(self.agent.interaction_id)+
                         "] to the AAS Core has been requested")
            self.agent.interaction_id += 1  # increment the interaction id as new requests has been made

        # Wait until the service is completed
        # TODO esto cuando se desarrolle el AAS Manager en un agente no se realizara de esta manera. No debera
        #  haber una espera hasta que se complete el servicio
        # TODO this code is for the interaction through JSON (it has to be removed)
        # while True:
        #     _logger.info(str(svc_data['serviceID']) + " service not completed yet.")
        #     svc_response = Interactions_utils.get_svc_response_info(current_interaction_id)
        #     if svc_response is not None:
        #         print(svc_response)
        #         # Set the service as completed
        #         # Write the information in the log file
        #         Interactions_utils.save_svc_info_in_log_file('Manager',
        #                                                      AASarchiveInfo.ASSET_RELATED_SVC_LOG_FILENAME,
        #                                                      current_interaction_id)
        #         # Return message to the sender
        #         _logger.info("Service completed! Response: " + str(svc_response))
        #         break
        #     time.sleep(2)

    async def handle_aas_infrastructure_svc(self, svc_data):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services
        (Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an AAS, but
        by the platform (computational infrastructure). These include the AAS Create Service (for creating AASs with unique
        identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery Services (for searching
        for AASs).

        Args:
            svc_interaction_id (int): the identifier of the interaction.
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))

    async def handle_aas_services(self, svc_data):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        Args:
            svc_interaction_id (int): the identifier of the interaction.
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))

    async def handle_submodel_services(self, svc_data):
        """
        This method handles Submodel Services. These services are part of I4.0 Application Component (application
        relevant).

        Args:
            svc_interaction_id (int): the identifier of the interaction.
            svc_data (dict): the information of the data in JSON format.
        """
        _logger.info(str(self.agent.interaction_id) + str(svc_data))
