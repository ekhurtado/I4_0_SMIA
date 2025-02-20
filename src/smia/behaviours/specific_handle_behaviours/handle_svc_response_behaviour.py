import logging

from spade.behaviour import OneShotBehaviour

_logger = logging.getLogger(__name__)


class HandleSvcResponseBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles all the service responses that the SMIA has received. This
    response can arrive from an FIPA-ACL message or from the AAS Core as an interaction message. This is a
    OneShotBehaviour because it handles an individual service response and then kills itself.
    """

    # TODO PENSAR SI ELIMINAR ESTA CLASE Y AGRUPAR TANTO Requests como Responses en 'HandleSvcBehaviour', ya que para
    #  CSS solo hay CapabilityBehaviour. Dentro de esta se podria analizar la performativa (como ya se hace), para ver
    #  si es una peticion o una respuesta
    def __init__(self, agent_object, svc_resp_interaction_type, svc_resp_data):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
            svc_resp_interaction_type (str): the type of the service response interaction (:term:`Inter AAS Interaction`
            or :term:`Intra AAS Interaction`)
            svc_resp_data (dict): all the information about the service response
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.svc_resp_interaction_type = svc_resp_interaction_type
        self.svc_resp_data = svc_resp_data

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleSvcResponseBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # TODO hay que pensar bien como identificar las peticiones de servicios y sus respuestas. En las interacciones
        #  Manager-Core tenemos el interactionID, con lo que es muy facil mapear la respuesta con su peticion. En
        #  cambio, si esa interaccion viene dada por una peticion anterior en ACL, hay que pensar como relacionar todas
        #  estar interacciones. Una solucion puede ser el atributo thread que propone FIP-ACL (o conversation ID). En
        #  este caso, el thread se enviara en todos los mensajes ACL, y este tambien se puede añadir en las
        #  interacciones Manager-Core. De esta forma, si una peticion de ACL exige una peticion de interaccion
        #  Manager-Core, en esta segunda se añadirá el mismo thread, de modo que podremos relacionar todas las
        #  peticiones-respuestas del mismo thread. Un servicio solo se completará del todo si todas las peticiones de
        #   ese thread tienen su respuesta

        # First, the service type of the request is obtained
        match self.svc_resp_data['serviceType']:
            case "AssetRelatedService":
                await self.handle_asset_related_service_response()
            case "AASInfrastructureServices":
                await self.handle_aas_infrastructure_svc_response()
            case "AASservices":
                await self.handle_aas_services_response()
            case "SubmodelServices":
                await self.handle_submodel_service_response()
            case _:
                _logger.error("Service type not available.")

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_asset_related_service_response(self):
        """
        This method handles Asset Related Services. These services are part of I4.0 Application Component (application
        relevant).
        """
        # TODO pensar como se gestionaria este caso. Uno que se me ocurre es que llega el ganador de una negociacion
        #  solicitada por el Core.
        _logger.info("Asset Related Service response.")
        match self.svc_resp_data['serviceID']:
            case 'negotiationResult':
                _logger.info("The result of the negotiation is due to a previous start negotiation request from "
                             "the AAS Core.")
            case 'ACLmessageResult':
                _logger.info("The Inter AAS response is due to a previous Intra AAS request from the AAS Core")
            case _:
                _logger.info("The serviceID is not one of the defaults, so the response is due to a previous "
                             "Intra AAS request from the AAS Core (the serviceID is the one that is related "
                             "with the service requested).")
                # The serviceID is updated as it is not one of the defaults
                self.svc_resp_data['serviceID'] = 'svcRequestResult'
        # TODO


    async def handle_aas_infrastructure_svc_response(self):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services (
        Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an
        AAS, but by the platform (computational infrastructure). These include the AAS Create Service (for creating
        AASs with unique identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery
        Services (for searching for AASs).

        """
        _logger.info('AAS Infrastructure Service response: ' + str(self.svc_resp_data))

    async def handle_aas_services_response(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info('AAS Service response: ' + str(self.svc_resp_data))

    async def handle_submodel_service_response(self):
        """
        This method handles Submodel Services. These services are part of I4.0 Application Component (application
        relevant).

        """
        # TODO, en este caso tendra que comprobar que submodelo esta asociado a la peticion de servicio. Si el submodelo
        #  es propio del SMIA, podra acceder directamente y, por tanto, este behaviour sera capaz de realizar el
        #  servicio completamente. Si es un submodelo del AAS Core, tendra que solicitarselo
        _logger.info('Submodel Service response: '  + str(self.svc_resp_data))
