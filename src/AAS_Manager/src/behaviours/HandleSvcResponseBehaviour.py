import json
import logging

from spade.behaviour import OneShotBehaviour

from logic import InterAASInteractions_utils, Negotiation_utils
from utilities import AAS_Archive_utils
from utilities.GeneralUtils import GeneralUtils

_logger = logging.getLogger(__name__)


class HandleSvcResponseBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles all the service responses that the AAS Manager has received. This
    response can arrive from an FIPA-ACL message or from the AAS Core as an interaction message. This is a
    OneShotBehaviour because it handles an individual service response and then kills itself.
    """

    def __init__(self, agent_object, svc_resp_interaction_type, svc_resp_data):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
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
        # TODO este tipo de servicios supongo que siempre se solicitaran via Kafka, pero aun asi pongo el if
        if self.svc_resp_interaction_type == 'Intra AAS interaction':

            # If a response of this type has arrived, it means that a previous interaction request has been made to the
            # AAS Core, so the first step is to match the response and its request information
            svc_interaction_id = self.svc_resp_data['interactionID']
            if await self.myagent.get_interaction_request(interaction_id=svc_interaction_id) is None:
                _logger.error("The interaction message response with id " + svc_interaction_id +
                              " has not its request information")
                return

            # Since the request has been performed, it is removed from the global dictionary
            await self.myagent.remove_interaction_request(interaction_id=svc_interaction_id)
            _logger.interactioninfo("interaction_requests shared object updated by " + str(self.__class__.__name__) +
                                    " responsible for interaction [" + svc_interaction_id + "]. Action: request data removed")

            # The information if stored in the global dictionary for the responses
            await self.myagent.save_interaction_response(interaction_id=svc_interaction_id,
                                                         response_data=self.svc_resp_data)
            _logger.interactioninfo("interaction_responses shared object updated by " + str(self.__class__.__name__) +
                                    " responsible for interaction [" + svc_interaction_id + "]. Action: response data added")

            # It is also stored in the log of the AAS archive
            AAS_Archive_utils.save_svc_log_info(self.svc_resp_data, 'AssetRelatedService')
            _logger.info("Information of service with id " + str(svc_interaction_id) +
                         " has saved correctly in the log of the AAS Archive")

            # It has to be checked if this service is part of a previous service request (part of a complex
            # conversation). For this purpose, the attribute 'thread' will be used.
            inter_aas_req = await self.myagent.get_acl_svc_request(thread=self.svc_resp_data['thread'])
            if inter_aas_req is not None:
                # In this case, there is a previous Inter AAS interaction, so it must perform the appropriate actions
                # according to the ontology.
                # TODO mirar si es parte de una negociacion, en cuyo caso tendria que buscar entre los behaviours del
                #  agente y cambiar el valor del neg_value (no enviar un ACL)
                match inter_aas_req['ontology']:
                    case "SvcRequest":
                        # In this case, the previous interaction has been an Inter AAS servie request, so the response
                        # to that request must be sent through FIPA-ACL to the requesting AAS.
                        inter_aas_response = InterAASInteractions_utils.create_inter_aas_response_object(inter_aas_req,
                                                                                                         self.svc_resp_data)

                        acl_msg = GeneralUtils.create_acl_msg(receiver=inter_aas_req['sender'],
                                                              thread=self.svc_resp_data['thread'],
                                                              performative=inter_aas_req['performative'],
                                                              ontology=inter_aas_req['ontology'],
                                                              body=json.dumps(inter_aas_response))
                        await self.send(acl_msg)
                        _logger.aclinfo("ACL Service response sent to request with thread ["
                                        + self.svc_resp_data['thread'] + "]")

                        # Since the Inter AAS interaction request has also been made, it is removed from the global
                        # dictionary
                        await self.myagent.remove_acl_svc_request(self.svc_resp_data['thread'])
                        _logger.aclinfo("acl_svc_requests shared object updated by " + str(self.__class__.__name__) +
                                        " responsible for interaction [" + svc_interaction_id +
                                        "]. Action: request data removed")

                        # The information if stored in the global dictionary for the Inter AAS interaction responses
                        await self.myagent.save_acl_svc_response(thread=self.svc_resp_data['thread'],
                                                                 response_data=inter_aas_response)
                        _logger.aclinfo("acl_svc_responses shared object updated by " + str(self.__class__.__name__) +
                                        " responsible for interaction [" + svc_interaction_id +
                                        "]. Action: response data added")

                    case _:
                        _logger.warning("Ontology not available.")
            else:
                # In this case, there is no previous Inter AAS Interaction request
                if self.svc_resp_data['serviceID'] == 'getNegotiationValue':
                    # In this case, the Intra AAS interaction has been part of a negotiation, so it has to notify to
                    # the associate handling behaviour, which is in charge of this exact negotiation
                    # If the negotiation value has been requested, this value must be saved in the behaviour
                    # class as an attribute
                    Negotiation_utils.add_value_and_unlock_neg_handling_behaviour(
                        agent=self.myagent,
                        thread=self.svc_resp_data['thread'],
                        neg_value=self.svc_resp_data['serviceData']['serviceParams']['value'])
                else:
                    print(self.svc_resp_data['serviceID'])
                    # TODO desarrollarlo para otros casos con solo Intra AAS Interaction

        elif self.svc_resp_interaction_type == 'Inter AAS interaction':
            # TODO pensar como se gestionaria este caso
            print("Asset Related Service requested through Inter AAS interaction")

    async def handle_aas_infrastructure_svc(self):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services (
        Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an
        AAS, but by the platform (computational infrastructure). These include the AAS Create Service (for creating
        AASs with unique identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery
        Services (for searching for AASs).

        """
        _logger.info(str(self.myagent.get_interaction_id()) + str(self.svc_resp_data))

    async def handle_aas_services(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info(await self.myagent.get_interaction_id() + str(self.svc_resp_data))

    async def handle_submodel_services(self):
        """
        This method handles Submodel Services. These services are part of I4.0 Application Component (application
        relevant).

        """
        # TODO, en este caso tendra que comprobar que submodelo esta asociado a la peticion de servicio. Si el submodelo
        #  es propio del AAS Manager, podra acceder directamente y, por tanto, este behaviour sera capaz de realizar el
        #  servicio completamente. Si es un submodelo del AAS Core, tendra que solicitarselo
        _logger.info(await self.myagent.get_interaction_id() + str(self.svc_resp_data))
