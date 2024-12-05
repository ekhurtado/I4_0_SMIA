import json
import logging

import basyx.aas.model
from basyx.aas import model
from spade.behaviour import OneShotBehaviour

from logic import IntraAASInteractions_utils, negotiation_utils, inter_aas_interactions_utils
from logic.exceptions import RequestDataError, ServiceRequestExecutionError, AASModelReadingError
from logic.services_utils import SubmodelServicesUtils
from utilities.fipa_acl_info import FIPAACLInfo, ACLJSONSchemas

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

        # First, the performative of the request is obtained
        # TODO NUEVO ENFOQUE (usando performative)
        match self.svc_req_data['performative']:
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:  # TODO actualizar dentro de todo el codigo los usos de performativas y ontologias de FIPA-ACL
                await self.handle_request()
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF:
                await self.handle_query_if()
            # TODO PensarOtros
            case _:
                _logger.error("Performative not available for service management.")
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
                _logger.assetinfo("The service with interaction id [" + await self.myagent.get_interaction_id() +
                                        "] to the AAS Core has been requested")

                # In this case, the service request is completed, since it needs the cooperation of the AAS Core.
                # When the response arrives, another behaviour is responsible for checking whether the service has been
                # fully performed
                # The information about the interaction request is also stored in the global variables of the agent
                await self.myagent.save_interaction_request(interaction_id=current_interaction_id,
                                                            request_data=interaction_request_json)

                _logger.assetinfo("interaction_requests shared object updated by " + str(self.__class__.__name__)
                     + " responsible for interaction [" + current_interaction_id + "]. Action: request data added")

                # Finally, it has to increment the interaction id as new requests has been made
                await self.myagent.increase_interaction_id_num()    # TODO pensar muy bien donde aumentarlo (quizas dentro del propio send_interaction_msg_to_core de Interaction_utils? para no olvidarlo)
                _logger.assetinfo("interaction_id shared object updated by " + str(self.__class__.__name__)
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


    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_request(self):
        """
        This method handle capability requests to the DT.
        """
        # The type is analyzed to perform the appropriate service
        match self.svc_req_data['serviceType']:
            case "AssetRelatedService":
                await self.handle_asset_related_svc()   # TODO
            case "AASInfrastructureService":
                await self.handle_aas_infrastructure_svc()   # TODO
            case "AASservice":
                await self.handle_aas_services()   # TODO
            case "SubmodelService":
                await self.handle_submodel_service_request()
            case _:
                _logger.error("Service type not available.")

    async def handle_query_if(self):
        """This method handle Query-If service requests. This request is received when the DT is asked about information
         related to a service."""
        pass
        # TODO FALTA POR HACER

    # -----------------------------------
    # Methods to handle specific services
    # -----------------------------------
    async def handle_submodel_service_request(self):
        """
        This method handles a Submodel Service request. These services are part of I4.0 Application Component (
        application relevant).
        """
        # The submodel service will be executed using a ModelReference or an ExternalReference, depending on the
        # requested element. This information is in serviceParams TODO (de momento en serviceParams, ya veremos mas adelante)
        try:
            # First, the received data is checked and validated
            await inter_aas_interactions_utils.check_received_request_data(
                self.svc_req_data, ACLJSONSchemas.JSON_SCHEMA_SUBMODEL_SERVICE_REQUEST)

            # If the data is valid, the SubmodelElement is obtained from the AAS model. For this purpose, the
            # appropriate BaSyx object must be created
            ref_object = None
            if 'ModelReference' in self.svc_req_data['serviceData']['serviceParams']:
                keys = ()
                last_type = None
                for key in self.svc_req_data['serviceData']['serviceParams']['ModelReference']['keys']:
                    basyx_key_type = await SubmodelServicesUtils.get_key_type_by_string(key['type'])
                    keys += (model.Key(basyx_key_type, key['value']),)
                    last_type = basyx_key_type
                ref_object = basyx.aas.model.ModelReference(
                    key=keys, type_=await SubmodelServicesUtils.get_model_type_by_key_type(last_type))

            elif 'ExternalReference' in self.svc_req_data['serviceData']['serviceParams']:
                ref_object = model.ExternalReference((model.Key(
                    type_=model.KeyTypes.GLOBAL_REFERENCE,
                    value=self.svc_req_data['serviceData']['serviceParams']['ExternalReference']),))
            # When the appropriate Reference object is created, the requested SubmodelElement can be obtained
            requested_sme = await self.myagent.aas_model.get_object_by_reference(ref_object)

            # When the AAS object has been obtained, the request is answered
            sme_info = str(requested_sme)   # TODO de momento simplemente lo devolvemos en string (para mas adelante pensar si desarrollar un metodo que devuelva toda la informacion)
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'requested_object': sme_info})
            _logger.info("Management of the service with thread {} finished.".format(self.svc_req_data['thread']))

        except (RequestDataError, ServiceRequestExecutionError, AASModelReadingError) as svc_request_error:
            # todo
            if isinstance(svc_request_error, RequestDataError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 svc_request_error.message, self)
            if isinstance(svc_request_error, AASModelReadingError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 "{}. Reason: {}".format(svc_request_error.message,
                                                                                         svc_request_error.reason), self)
            await svc_request_error.handle_service_execution_error()
            return  # killing a behaviour does not cancel its current run loop



    async def send_response_msg_to_sender(self, performative, service_params):
        """
        This method creates and sends a FIPA-ACL message with the given serviceParams and performative.

        Args:
            performative (str): performative according to FIPA-ACL standard.
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_aas_interactions_utils.create_inter_aas_response_msg(
            receiver=self.svc_req_data['sender'],
            thread=self.svc_req_data['thread'],
            performative=performative,
            service_id=self.svc_req_data['serviceID'],
            service_type=self.svc_req_data['serviceType'],
            service_params=json.dumps(service_params)
        )
        await self.send(acl_msg)