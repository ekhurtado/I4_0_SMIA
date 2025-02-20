import json
import logging

from spade.behaviour import OneShotBehaviour

from smia import GeneralUtils
from smia.aas_model.aas_model_utils import AASModelUtils
from smia.logic import inter_aas_interactions_utils
from smia.logic.exceptions import RequestDataError, ServiceRequestExecutionError, AASModelReadingError, \
    AssetConnectionError
from smia.utilities import smia_archive_utils
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLJSONSchemas, ServiceTypes
from smia.utilities.smia_info import AssetInterfacesInfo

_logger = logging.getLogger(__name__)


class HandleSvcRequestBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles all the service requests that the SMIA has received. This
    request can arrive from an FIPA-ACL message as a :term:`Inter AAS Interaction` or from the AAS Core as an
    :term:`Intra AAS Interaction` message. This is a OneShotBehaviour because it handles an individual service request
    and then kills itself.
    """

    # TODO PENSAR SI AGRUPAR EN ESTA CLASE TANTO Requests como Responses ('HandleSvcBehaviour'), ya que para CSS solo
    #  hay CapabilityBehaviour. Dentro de esta se podria analizar la performativa (como ya se hace), para ver si es una
    #  peticion o una respuesta

    def __init__(self, agent_object, svc_req_data):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
            svc_req_data (dict): all the information about the service request
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.svc_req_data = svc_req_data

        self.requested_timestamp = GeneralUtils.get_current_timestamp()

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
    async def handle_request(self):
        """
        This method handle capability requests to the DT.
        """
        # The type is analyzed to perform the appropriate service
        match self.svc_req_data['serviceType']:
            case ServiceTypes.ASSET_RELATED_SERVICE:
                # await self.handle_asset_related_svc()   # TODO
                await self.handle_asset_related_service_request()
            case ServiceTypes.AAS_INFRASTRUCTURE_SERVICE:
                await self.handle_aas_infrastructure_svc_request()  # TODO
            case ServiceTypes.AAS_SERVICE:
                await self.handle_aas_services_request()  # TODO
            case ServiceTypes.SUBMODEL_SERVICE:
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
    async def handle_asset_related_service_request(self):
        """
        This method handles an Asset Related Service request. These services are part of I4.0 Application Component
        (application relevant).
        """
        # TODO In this case, AssetRelatedService and AssetService are considered equivalent.
        # The asset related service will be executed using a ModelReference to the related SubmodelElement within the
        # AssetInterfacesDefinition submodel. This information is in serviceParams TODO (de momento en serviceParams, ya veremos mas adelante)
        try:
            # First, the received data is checked and validated
            await inter_aas_interactions_utils.check_received_request_data_structure(
                self.svc_req_data, ACLJSONSchemas.JSON_SCHEMA_ASSET_SERVICE_REQUEST)
            service_params = self.svc_req_data['serviceData']['serviceParams']

            # If the received data is valid, the AAS Reference object need to be created
            aas_asset_service_ref = await AASModelUtils.create_aas_reference_object(
                'ModelReference', service_params['ModelReference']['keys'])
            aas_asset_service_elem = await self.myagent.aas_model.get_object_by_reference(aas_asset_service_ref)

            # The asset connection class is also required to execute the asset related service. It is obtained from the
            # AAS asset service Reference object
            aas_asset_interface_ref = aas_asset_service_elem.get_parent_ref_by_semantic_id(
                AssetInterfacesInfo.SEMANTICID_INTERFACE)
            if aas_asset_service_elem is None:
                raise ServiceRequestExecutionError(self.svc_req_data['thread'], "The added ModelReference is not "
                                                                                " inside the AssetInterfacesDescription "
                                                                                "submodel, so it is not an AssetService.",
                                                   self.svc_req_data['serviceType'], self)
            asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(aas_asset_interface_ref)

            # With all necessary information obtained, the asset related service can be executed
            _logger.assetinfo("Executing skill of the capability through an asset service...")
            received_input_data = None
            if 'serviceParameterValues' in service_params:
                received_input_data = service_params['serviceParameterValues']
            asset_service_execution_result = await asset_connection_class.execute_asset_service(
                interaction_metadata=aas_asset_service_elem,
                service_input_data=received_input_data)
            _logger.assetinfo("Skill of the capability successfully executed.")

            # The result will be sent to the requester
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'result': asset_service_execution_result})
            _logger.info("Management of the service with thread {} finished.".format(self.svc_req_data['thread']))

            # The information will be stored in the log
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.svc_req_data, str(asset_service_execution_result),
                                                           self.svc_req_data['serviceType'])

        except (RequestDataError, ServiceRequestExecutionError,
                AASModelReadingError, AssetConnectionError) as svc_request_error:
            if isinstance(svc_request_error, RequestDataError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 svc_request_error.message,
                                                                 self.svc_req_data['serviceType'], self)
            if isinstance(svc_request_error, AASModelReadingError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'], "{}. Reason: "
                                                                                              "{}".format(
                    svc_request_error.message,
                    svc_request_error.reason), self.svc_req_data['serviceType'], self)
            if isinstance(svc_request_error, AssetConnectionError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 f"The error [{svc_request_error.error_type}] has appeared during the asset "
                                                                 f"connection. Reason: {svc_request_error.reason}.",
                                                                 self.svc_req_data['serviceType'], self)
            await svc_request_error.handle_service_execution_error()
            return  # killing a behaviour does not cancel its current run loop

    async def handle_aas_services_request(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info('AAS Service request: ' + str(self.svc_req_data))

    async def handle_aas_infrastructure_svc_request(self):
        """
        This method handles AAS Infrastructure Services. These services are part of I4.0 Infrastructure Services
        (Systemic relevant). They are necessary to create AASs and make them localizable and are not offered by an AAS, but
        by the platform (computational infrastructure). These include the AAS Create Service (for creating AASs with unique
        identifiers), AAS Registry Services (for registering AASs) and AAS Exposure and Discovery Services (for searching
        for AASs).

        """
        _logger.info('AAS Infrastructure Service request: ' + str(self.svc_req_data))

    async def handle_submodel_service_request(self):
        """
        This method handles a Submodel Service request. These services are part of I4.0 Application Component
        (application relevant).
        """
        # The submodel service will be executed using a ModelReference or an ExternalReference, depending on the
        # requested element. This information is in serviceParams TODO (de momento en serviceParams, ya veremos mas adelante)
        try:
            # First, the received data is checked and validated
            await inter_aas_interactions_utils.check_received_request_data_structure(
                self.svc_req_data, ACLJSONSchemas.JSON_SCHEMA_SUBMODEL_SERVICE_REQUEST)

            # If the data is valid, the SubmodelElement is obtained from the AAS model. For this purpose, the
            # appropriate BaSyx object must be created
            ref_object = None
            if 'ModelReference' in self.svc_req_data['serviceData']['serviceParams']:
                ref_object = await AASModelUtils.create_aas_reference_object(
                    'ModelReference',
                    keys_dict=self.svc_req_data['serviceData']['serviceParams']['ModelReference']['keys'])
            elif 'ExternalReference' in self.svc_req_data['serviceData']['serviceParams']:
                ref_object = await AASModelUtils.create_aas_reference_object(
                    'ExternalReference',
                    external_ref=self.svc_req_data['serviceData']['serviceParams']['ExternalReference'])

            # When the appropriate Reference object is created, the requested SubmodelElement can be obtained
            requested_sme = await self.myagent.aas_model.get_object_by_reference(ref_object)

            # When the AAS object has been obtained, the request is answered
            # TODO de momento simplemente lo devolvemos en string (para mas adelante pensar si desarrollar un metodo que
            #  devuelva toda la informacion)
            sme_info = str(requested_sme)
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'requested_object': sme_info})
            _logger.info("Management of the service with thread {} finished.".format(self.svc_req_data['thread']))

            # The information will be stored in the log
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.svc_req_data, str(sme_info),
                                                           self.svc_req_data['serviceType'])

        except (RequestDataError, ServiceRequestExecutionError, AASModelReadingError) as svc_request_error:
            if isinstance(svc_request_error, RequestDataError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 svc_request_error.message,
                                                                 self.svc_req_data['serviceType'], self)
            if isinstance(svc_request_error, AASModelReadingError):
                svc_request_error = ServiceRequestExecutionError(self.svc_req_data['thread'],
                                                                 "{}. Reason: {}".format(svc_request_error.message,
                                                                                         svc_request_error.reason),
                                                                 self.svc_req_data['serviceType'], self)
            await svc_request_error.handle_service_execution_error()
            return  # killing a behaviour does not cancel its current run loop

    async def send_response_msg_to_sender(self, performative, service_params):
        """
        This method creates and sends a FIPA-ACL message with the given serviceParams and performative.

        Args:
            performative (str): performative according to FIPA-ACL standard.
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_aas_interactions_utils.create_inter_smia_response_msg(
            receiver=self.svc_req_data['sender'],
            thread=self.svc_req_data['thread'],
            performative=performative,
            ontology='SvcResponse',
            service_id=self.svc_req_data['serviceID'],
            service_type=self.svc_req_data['serviceType'],
            service_params=json.dumps(service_params)
        )
        await self.send(acl_msg)

