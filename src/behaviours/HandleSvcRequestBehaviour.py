import logging

from spade.behaviour import OneShotBehaviour

from logic import IntraAASInteractions_utils, negotiation_utils, inter_aas_interactions_utils

_logger = logging.getLogger(__name__)


class HandleSvcRequestBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles all the service requests that the AAS Manager has received. This
    request can arrive from an FIPA-ACL message as a :term:`Inter AAS Interaction` or from the AAS Core as an
    :term:`Intra AAS Interaction` message. This is a OneShotBehaviour because it handles an individual service request
    and then kills itself.
    """

    def __init__(self, agent_object, svc_req_interaction_type, svc_req_data):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
            svc_req_interaction_type (str): the type of the service request interaction (:term:`Inter AAS Interaction`
            or :term:`Intra AAS Interaction`)
            svc_req_data (dict): all the information about the service request
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.svc_req_interaction_type = svc_req_interaction_type
        self.svc_req_data = svc_req_data

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleSvcRequestBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

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

        # First, the service type of the request is obtained
        match self.svc_req_data['serviceType']:
            case "AssetRelatedService":
                await self.handle_asset_related_svc()
            case "AASInfrastructureServices":
                await self.handle_aas_infrastructure_svc()
            case "AASservices":
                await self.handle_aas_services()
            case "SubmodelServices":
                await self.handle_submodel_services()
            case _:
                _logger.error("Service type not available.")

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_asset_related_svc(self):
        """
        This method handles Asset Related Services. These services are part of I4.0 Application Component (application
        relevant).
        """
        if self.svc_req_interaction_type == 'Inter AAS interaction':
            # TODO esto hay que revisarlo. De momento, si llega una peticion por ACL directamente la solicito por Kafka,
            #  ya que es AssetRelatedService. Aun asi, habria que analizar si existe alguna variable o atributo a
            #  revisar para saber qué acción tomar
            # In this type of services an interaction request have to be made to the AAS Core
            # First, the valid JSON structure of the request is generated
            current_interaction_id = await self.myagent.get_interaction_id()
            interaction_request_json = IntraAASInteractions_utils.create_svc_request_interaction_json(
                interaction_id=current_interaction_id,
                request_data=self.svc_req_data)

            # Then, the interaction message is sent to the AAS Core
            request_result = await IntraAASInteractions_utils.send_interaction_msg_to_core(
                client_id='i4-0-smia-manager',
                msg_key='manager-service-request',
                msg_data=interaction_request_json)
            if request_result != "OK":  # TODO Pensar si añadir esto dentro del send_interaction_msg_to_core, al igual que incrementar el interactionID. Es decir, que ese metodo se encargue de enviar el mensaje por Kafka y asegurarse de que no hay problemas, y despues incrementar el id porque ha salido bien
                _logger.error("The AAS Manager-Core interaction is not working: " + str(request_result))
            else:
                _logger.interactioninfo("The service with interaction id [" + await self.myagent.get_interaction_id() +
                                        "] to the AAS Core has been requested")

                # In this case, the service request is completed, since it needs the cooperation of the AAS Core.
                # When the response arrives, another behaviour is responsible for checking whether the service has been
                # fully performed
                # The information about the interaction request is also stored in the global variables of the agent
                await self.myagent.save_interaction_request(interaction_id=current_interaction_id,
                                                            request_data=interaction_request_json)

                _logger.interactioninfo("interaction_requests shared object updated by " + str(self.__class__.__name__)
                     + " responsible for interaction [" + current_interaction_id + "]. Action: request data added")

                # Finally, it has to increment the interaction id as new requests has been made
                await self.myagent.increase_interaction_id_num()    # TODO pensar muy bien donde aumentarlo (quizas dentro del propio send_interaction_msg_to_core de Interaction_utils? para no olvidarlo)
                _logger.interactioninfo("interaction_id shared object updated by " + str(self.__class__.__name__)
                                        + " responsible for interaction [" + current_interaction_id +
                                        "]. Action: interaction_id increased")

        elif self.svc_req_interaction_type == 'Intra AAS interaction':
            # In this type of services an interaction request has received from the AAS Core, so it must analyze the
            # requested service
            _logger.info("Asset Related Service requested through Intra AAS interaction")

            match self.svc_req_data['serviceID']:
                case 'startNegotiation':
                    _logger.info("The AAS Core has requested to start a negotiation. To do so, an Inter AAS Request "
                                 "must be made.")

                    # Create the Inter AAS Interaction required JSON for start a negotiation
                    start_neg_acl_msg = negotiation_utils.create_neg_cfp_msg(
                        thread=self.svc_req_data['thread'],
                        targets=self.svc_req_data['serviceData']['serviceParams']['targets'],
                        neg_requester_jid=str(self.myagent.jid),
                        neg_criteria=self.svc_req_data['serviceData']['serviceParams']['criteria'],
                    )

                    # Send the FIPA-ACL messages to all participants
                    # This PROPOSE FIPA-ACL message is sent to all participants of the negotiation (except for this AAS Manager)
                    print(self.svc_req_data['serviceData']['serviceParams']['targets'])
                    targets_list = self.svc_req_data['serviceData']['serviceParams']['targets'].split(',')
                    for jid_target in targets_list:
                        if jid_target != str(self.agent.jid):
                            start_neg_acl_msg.to = jid_target
                            await self.send(start_neg_acl_msg)
                            _logger.aclinfo("ACL CallForProposal negotiation message sent to " + jid_target +
                                            " on negotiation with thread [" + self.svc_req_data['thread'] + "]")

                    # The information about the interaction request is also stored in the global variables of the agent
                    await self.myagent.save_interaction_request(interaction_id=self.svc_req_data['interactionID'],
                                                                request_data=self.svc_req_data)

                case 'sendInterAASsvcRequest':
                    _logger.info("The AAS Core has requested to send an Inter AAS interaction message to request a "
                                 "service.")

                    # the Inter AAS Interaction message for requesting a service is created
                    service_params = self.svc_req_data['serviceData']['serviceParams']
                    # From serviceParams it has to extract information about the msg ACL and leave the required
                    # serviceParams of the requested service so that it can be executed
                    receiver = service_params.pop('receiver')
                    service_id = service_params.pop('serviceID')
                    svc_request_acl_msg = inter_aas_interactions_utils.create_inter_aas_request_msg(
                        receiver=receiver,
                        thread=self.svc_req_data['thread'],
                        service_id=service_id,
                        service_type=self.svc_req_data['serviceType'],
                        service_params=None if len(service_params) == 0 else service_params
                    )

                    # The ACL message is sent
                    await self.send(svc_request_acl_msg)
                    _logger.aclinfo("ACL Service request sent to " +receiver+ " with thread ["
                                    + self.svc_req_data['thread'] + "]")

                    # The information is stored in the global dictionary for the interaction requests
                    await self.myagent.save_interaction_request(interaction_id=self.svc_req_data['interactionID'],
                                                                request_data=self.svc_req_data)


                case 'sendACLmessage':
                    # TODO add logic to send a FIPA-ACL msg
                    _logger.info("The AAS Core has requested to send a FIPA-ACL message.")
                case _:
                    logging.error("This serviceID is not available for requesting through Intra AAS interaction.")

    async def handle_aas_infrastructure_svc(self):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services
        (Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an AAS, but
        by the platform (computational infrastructure). These include the AAS Create Service (for creating AASs with unique
        identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery Services (for searching
        for AASs).

        """
        _logger.info(await self.myagent.get_interaction_id() + str(self.svc_req_data))

    async def handle_aas_services(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info(await self.myagent.get_interaction_id() + str(self.svc_req_data))

    async def handle_submodel_services(self):
        """
        This method handles Submodel Services. These services are part of I4.0 Application Component (application
        relevant).

        """
        # TODO, en este caso tendra que comprobar que submodelo esta asociado a la peticion de servicio. Si el submodelo
        #  es propio del AAS Manager, podra acceder directamente y, por tanto, este behaviour sera capaz de realizar el
        #  servicio completamente. Si es un submodelo del AAS Core, tendra que solicitarselo
        _logger.info(await self.myagent.get_interaction_id() + str(self.svc_req_data))
