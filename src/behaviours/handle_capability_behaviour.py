import json
import logging

import basyx.aas.model
from spade.behaviour import OneShotBehaviour

from logic import inter_aas_interactions_utils
from logic.exceptions import CapabilityRequestExecutionError, CapabilityCheckingError, CapabilityDataError
from utilities.capability_skill_ontology import CapabilitySkillACLInfo, CapabilitySkillOntology, AssetInterfacesInfo
from utilities.fipa_acl_info import FIPAACLInfo

_logger = logging.getLogger(__name__)


class HandleCapabilityBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles a request related to the capabilities of the Digital Twin.
    TODO (segun se vaya desarrollando extenderlo mas)
    """

    def __init__(self, agent_object, svc_req_data):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
            svc_req_data (dict): all the information about the service request
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.svc_req_data = svc_req_data

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("HandleCapabilityBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # First, the performative of request is obtained and, depending on it, different actions will be taken
        match self.svc_req_data['performative']:
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST:  # TODO actualizar dentro de todo el codigo los usos de performativas y ontologias de FIPA-ACL
                await self.handle_request()
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_IF:
                await self.handle_query_if()
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM:
                await self.handle_inform()
            case "PensarOtro":  # TODO
                pass
            case _:
                _logger.error("Performative not available for capability management.")
        self.exit_code = 0

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_request(self):
        """
        This method handle CallForProposal requests for the Capability.
        """
        if self.svc_req_data['serviceID'] == 'capabilityRequest':
            # First, the capability to be performed will be obtained from the internal AAS model
            # TODO, para este paso, se podrian almacenar las capacidades que se han verificado ya cuando se recibe el
            #  Query-If (se supone que otro agente debería mandar en CallForProposal despues del Query-If, pero para
            #  añadirle una validacion extra) Esto podria hacerse con el thread (el Query-If y CFP estarían en la misma
            #  negociacion?). Otra opcion es siempre ejecutar aas_model.capability_checking_from_acl_request()
            received_cap_data = self.svc_req_data['serviceData']['serviceParams']

            try:

                # The data received is checked to ensure that it contains all the necessary information.
                await self.check_received_cap_data()

                # The capability checking should be also performed to ensure that the DT can perform it
                # TODO PENSAR COMO REALIZAR EL CAPABILITY CHECKING YA QUE LA INFORMACION RECIBIDA AL SOLICITAR UN CAPABILITY CHECKING O REQUEST NO ES LA MISMA (p.e. en request estan los datos de los parametros)
                # await self.myagent.aas_model.capability_checking_from_acl_request(received_cap_data)

                # TODO CAMBIAR REQUIRED POR RECEIVED
                received_cap_type = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE]
                capability_elem = await self.myagent.aas_model.get_capability_by_id_short(
                    cap_type=received_cap_type,
                    cap_id_short=received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME])
                # if received_cap_type == CapabilitySkillOntology.ASSET_CAPABILITY_TYPE:
                #     # In this case, the asset skill has to be executed through skill interface
                #     _logger.interactioninfo("The Capability requested is of AssetCapability type.")
                # TODO, habria que tener en cuenta que puede ser asincrono, asi que quizas un wait hasta que el asset
                #  connection reciba la respuesta. Al final hay que pensar parecido a como se hacia con interactionID,
                #  pero en  este caos no tenemos peticion respuesta interna

                # TODO De momento el AssetConnection se establece al leer el AAS Model, pero, si queremos ofrecer mas de
                #  una interfaz simultánea, habría que especificarla justo antes de realizar la conexión con el activo

                # First, the skill interface elem need to be obtained.
                skill_elem = await self.myagent.aas_model.get_skill_data_by_capability(capability_elem,
                                                                                       'skillObject')
                # There are two situations: the 'skillaccesiblethrough' relationship of the skill points to a submodel
                # element within AssetInterfacesSubmodel, so the skill interface element can be obtained directly.
                skill_interface_elem = await self.myagent.aas_model.get_skill_data_by_capability(capability_elem,
                                                                                                 'skillInterface')
                # In the second situation the 'skillaccesiblethrough' relationship of the skill points to a
                # ConceptDescription. In this case there are different skill interfaces, depending on the values of
                # skill parameters, which are defined in the ConceptDescription.
                if isinstance(skill_interface_elem, basyx.aas.model.ConceptDescription):
                    # To obtain the appropriate skill interface, first the received value that determines the skill
                    # interface is located. The value need to be part of a skill parameter and the semanticID is its
                    # valueId attribute
                    skill_parameter_id_short = skill_elem.get_variable_value_id(skill_interface_elem.id)
                    # Since the id_short of the parameter is the same key as the received value, the value can be get
                    skill_parameter_value = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INFO][
                        CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS][CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS][skill_parameter_id_short]
                    skill_parameter_value_semantic_id = await self.myagent.aas_model.get_concept_description_pair_value_id_by_value_name(
                        skill_interface_elem.id, skill_parameter_value)
                    skill_interface_elem = await self.myagent.aas_model.get_asset_interface_interaction_metadata_by_value_semantic_id(
                        skill_parameter_value_semantic_id)

                # SkillInterface will be an SME action inside the AssetInterfacesDescription submodel. The interface
                # will be already configured from the agent Booting state, so it will be possible to execute the
                # AssetConnection sending method passing the SkillInterface to it. The AssetConnection will collect the
                # necessary information from the SkillInterface (from the SubmodelElement). The asset connection message
                # sending method will wait for the response, as well as the CapabilityHandleBehaviour.
                skill_execution_result = ''
                asset_connection_ref = skill_interface_elem.get_parent_ref_by_semantic_id(
                    AssetInterfacesInfo.SEMANTICID_INTERFACE)
                if asset_connection_ref:
                    # Once the Asset Connection reference is obtained, the associated class can be used to
                    # connect with the asset
                    asset_connection_class = await self.myagent.get_asset_connection_class(asset_connection_ref)

                    # If the skill has parameters, they have to be obtained from the received data
                    received_skill_input_parameters = None
                    received_skill_output_parameters = None
                    skill_params_exposures = None
                    # TODO como de momento el skill elem es Operation, tiene los parametros dentro del elemento
                    if len(skill_elem.input_variable) != 0 or len(skill_elem.output_variable) != 0:
                        # TODO HACER AHORA UN CHECKING DE LOS DATOS RECIBIDOS SOBRE LA SKILL EN UN METODO A PARTE (
                        #  usando el submodel element de la skill se comprueba si tiene input parameter, y despues si
                        #  existe en los datos recibidos. Asi con todos (inout, output, skill interface, sme type...))
                        if CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS not in received_cap_data[
                            CapabilitySkillACLInfo.REQUIRED_SKILL_INFO]:
                            _logger.warning("The skill of the Capability requested needs input parameters and these have not been added to the request data.")
                            CapabilityRequestExecutionError(received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME],
                                                            "The skill of the Capability requested needs input parameters and these have not been added to the request data.", self)

                        # The exposure element within the skill interface need to be obtained from each skill parameter
                        skill_params_exposures = await self.myagent.aas_model.get_skill_parameters_exposure_interface_elements(skill_elem)

                    # The required data is obtained from the received information
                    received_skill_parameters = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INFO][
                        CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]

                    if len(skill_elem.input_variable) != 0:
                        # The skill has input parameters, they have to be obtained
                        if CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS in received_skill_parameters:
                            received_skill_input_parameters = received_skill_parameters[
                                CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS]
                    if len(skill_elem.output_variable) != 0:
                        # The skill has output parameters, they have to be obtained
                        if CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS in received_skill_parameters:
                            received_skill_output_parameters = received_skill_parameters[
                                CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS]
                            # TODO analizar que pasaria si hay output parameters

                    _logger.interactioninfo("The Asset connection of the Skill Interface has been obtained.")
                    _logger.interactioninfo(
                        "Executing skill of the capability through a request of an asset service...")
                    skill_execution_result = await asset_connection_class.execute_skill_by_asset_service(
                        interaction_metadata=skill_interface_elem,
                        skill_params_exposure_elems=skill_params_exposures,
                        skill_input_params=received_skill_input_parameters,
                        skill_output_params=received_skill_output_parameters)
                    if skill_execution_result:
                        _logger.interactioninfo("Skill of the capability successfully executed.")

                        # Se comprueba si la capacidad requerida tiene postcondiciones
                        constraints_values = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS]
                        await self.myagent.aas_model.skill_feasibility_checking_post_conditions(capability_elem,
                                                                                                constraints_values)

                    else:
                        _logger.warning("Failed to execute the skill of the capability correctly.")

                else:
                    _logger.warning("The capability required has invalid skill interface.")
                    skill_execution_result = 'NotExecuted'

                # When the skill has finished, the request is answered
                await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                       {'result': skill_execution_result})
                _logger.info("Management of the capability {} finished.".format(capability_elem))
            except (CapabilityDataError, CapabilityCheckingError, CapabilityRequestExecutionError) as cap_request_error:    # TODO pensar si hay mas (p.e. AssetConnectionError)
                if isinstance(cap_request_error, CapabilityDataError):
                    if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME in received_cap_data:
                        cap_request_error = CapabilityRequestExecutionError(
                            received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], cap_request_error.message, self)
                    else:
                        cap_request_error = CapabilityRequestExecutionError('', cap_request_error.message, self)
                if isinstance(cap_request_error, CapabilityCheckingError):
                    cap_request_error = CapabilityRequestExecutionError(cap_request_error.cap_name, cap_request_error.reason, self)

                await cap_request_error.handle_capability_execution_error()
                return  # killing a behaviour does not cancel its current run loop
        else:
            pass
            # TODO pensar que situaciones habria

    async def handle_query_if(self):
        """
        This method handle Query-If requests for the Capability. This request is received when the DT is asked about
        information related to a capability.

        """
        if self.svc_req_data['serviceID'] == 'capabilityChecking':
            # The DT has been asked if it has a given capability.
            # First, the information about the required capability is obtained
            required_cap_data = self.svc_req_data['serviceData']['serviceParams']

            # It will be checked if the DT can perform the required capability
            try:
                # First, the received data is checked
                await self.check_received_cap_data()

                # Then, the capability checking process can be executed
                result = await self.myagent.aas_model.capability_checking_from_acl_request(required_cap_data)
            except (CapabilityDataError, CapabilityCheckingError) as cap_checking_error:
                if isinstance(cap_checking_error, CapabilityDataError):
                    if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME in required_cap_data:
                        cap_checking_error = CapabilityCheckingError(
                            required_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], cap_checking_error.message)
                    else:
                        cap_checking_error = CapabilityCheckingError('', cap_checking_error.message)

                cap_checking_error.add_behav_class(self)
                await cap_checking_error.handle_capability_checking_error()
                return  # killing a behaviour does not cancel its current run loop

            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, {'result': result})
            _logger.info("The Capability [{}] has been checked, with result: {}.".format(
                required_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], result))
        else:
            # TODO pensar otras categorias para capabilities
            pass

    async def handle_inform(self):
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


    async def check_received_cap_data(self):
        """
        This method checks if the received

        Returns:
            bool: the result of the check.
        """
        # try:
        #     if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME not in received_cap_data:
        #         raise CapabilityRequestExecutionError("The received capability data is invalid due to missing #{} "
        #                                               "field in request message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME),
        #                                               self)
        #     elif CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE not in received_cap_data:
        #         raise CapabilityRequestExecutionError("The received capability data is invalid due to missing #{} field in "
        #                                               "request message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE),
        #                                               self)
        #     elif CapabilitySkillACLInfo.REQUIRED_SKILL_INFO not in received_cap_data:
        #         raise CapabilityRequestExecutionError("The received capability data is invalid due to missing #{} field in "
        #                                               "request message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_INFO),
        #                                               self)
        #     # TODO analizar si faltan mas fields obligatorios
        #     return True
        # except CapabilityRequestExecutionError as cap_exec_error:
        #     await cap_exec_error.handle_capability_execution_error()
        #     return False
        received_cap_data = self.svc_req_data['serviceData']['serviceParams']
        if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME not in received_cap_data:
            raise CapabilityDataError("The received capability data is invalid due to missing #{} field in request "
                                      "message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME))
        elif CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE not in received_cap_data:
            raise CapabilityDataError("The received capability data is invalid due to missing #{} field in request "
                                      "message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE))
        elif CapabilitySkillACLInfo.REQUIRED_SKILL_INFO not in received_cap_data:
            raise CapabilityDataError("The received capability data is invalid due to missing #{} field in request "
                                      "message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_INFO))
