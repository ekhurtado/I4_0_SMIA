import json
import logging

import basyx.aas.model
from spade.behaviour import OneShotBehaviour

from logic import inter_aas_interactions_utils
from logic.exceptions import CapabilityRequestExecutionError, CapabilityCheckingError, CapabilityDataError, \
    AssetConnectionError, OntologyReadingError
from css_ontology.css_ontology_utils import CapabilitySkillACLInfo, AssetInterfacesInfo
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
                # The capability checking should be also performed to ensure that the DT can perform it. In this case,
                # the capability checking is performed in separate steps
                # The data received is checked to ensure that it contains all the necessary information.
                await self.check_received_cap_data()

                # TODO BORRAR: PRUEBA RECOGIENDO LOS DATOS CON CSS ONTOLOGY
                cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
                try:
                    cap_ontology_elem = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)
                    _logger.aclinfo("Capability ontology element found for {}: {}".format(cap_name, cap_ontology_elem))
                    skill_ontology_elems = cap_ontology_elem.isRealizedBy
                    for skill in skill_ontology_elems:
                        _logger.aclinfo("{} is a skill of the capability {}".format(skill.name, cap_ontology_elem.name))
                        for interf in skill.accessibleThroughAssetService:
                            _logger.aclinfo("{} is a skill interface with asset service of the skill {}".format(interf.name, skill.name))
                        for interf in skill.accessibleThroughAgentService:
                            _logger.aclinfo("{} is a skill interface with agent service of the skill {}".format(interf.name, skill.name))
                except OntologyReadingError as e:
                    _logger.error("The capability {} does not exist in the ontology of this DT.".format(cap_name))

                # TODO BORRAR: FIN PRUEBA RECOGIENDO LOS DATOS CON CSS ONTOLOGY

                # First, the skill interface elem need to be obtained. The capability element will be used for this.
                cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
                capability_elem = await self.myagent.aas_model.get_capability_by_id_short(
                    cap_type=received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE],
                    cap_id_short=cap_name)
                skill_elem = await self.myagent.aas_model.get_skill_data_by_capability(capability_elem,
                                                                                       'skillObject')

                # The received skill information must be also checked
                await self.check_received_skill_data(skill_elem)

                # TODO PENSAR QUE HACER CON EL TEMA DEL SKILL INTERFACE (dejarlo como ahora u obligar a que la relación skill con su interfaz sea siempre directa)
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
                    # Since the id_short of the parameter is the same key as the received value, the value can be got
                    skill_parameter_value = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INFO][
                        CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS][
                        CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS][skill_parameter_id_short]
                    skill_parameter_value_semantic_id = await self.myagent.aas_model.get_concept_description_pair_value_id_by_value_name(
                        skill_interface_elem.id, skill_parameter_value)
                    skill_interface_elem = await self.myagent.aas_model.get_asset_interface_interaction_metadata_by_value_semantic_id(
                        skill_parameter_value_semantic_id)

                if not skill_interface_elem:
                    raise CapabilityRequestExecutionError(cap_name, "The capability {} could not be executed because "
                                                                    "its skill interface element was not found.".format(
                        cap_name), self)

                # SkillInterface will be an SME action inside the AssetInterfacesDescription submodel. The interface
                # will be already configured from the agent Booting state, so it will be possible to execute the
                # AssetConnection sending method passing the SkillInterface to it. The AssetConnection will collect the
                # necessary information from the SkillInterface (from the SubmodelElement). The asset connection message
                # sending method will wait for the response, as well as the CapabilityHandleBehaviour.
                asset_connection_ref = skill_interface_elem.get_parent_ref_by_semantic_id(
                    AssetInterfacesInfo.SEMANTICID_INTERFACE)
                # Once the Asset Connection reference is obtained, the associated class can be used to
                # connect with the asset
                asset_connection_class = await self.myagent.get_asset_connection_class(asset_connection_ref)
                if not asset_connection_ref:
                    raise CapabilityRequestExecutionError(cap_name, "The capability {} could not be executed because "
                                                                    "the asset connection of its skill interface element was not found.".format(
                        cap_name), self)

                received_skill_input_parameters, received_skill_output_parameters, skill_params_exposures = \
                    await self.get_asset_connection_skill_data(skill_elem)

                _logger.interactioninfo("The Asset connection of the Skill Interface has been obtained.")
                _logger.interactioninfo(
                    "Executing skill of the capability through a request of an asset service...")
                skill_execution_result = await asset_connection_class.execute_skill_by_asset_service(
                    interaction_metadata=skill_interface_elem,
                    skill_params_exposure_elem=skill_params_exposures,
                    skill_input_params=received_skill_input_parameters,
                    skill_output_params=received_skill_output_parameters)
                if skill_execution_result:
                    _logger.interactioninfo("Skill of the capability successfully executed.")

                    # In case there are output skill parameters, the result will be added to this parameters
                    if received_skill_output_parameters:
                        skill_execution_result = {received_skill_output_parameters: skill_execution_result}
                    else:
                        skill_execution_result = 'Success'

                    # Se comprueba si la capacidad requerida tiene postcondiciones
                    # constraints_values = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS]
                    # await self.myagent.aas_model.skill_feasibility_checking_post_conditions(capability_elem,
                    #                                                                         constraints_values)

                else:
                    _logger.warning("Failed to execute the skill of the capability correctly.")

                # When the skill has finished, the request is answered
                await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                       {'result': skill_execution_result})
                _logger.info("Management of the capability {} finished.".format(capability_elem))
            except (CapabilityDataError, CapabilityCheckingError, CapabilityRequestExecutionError,
                    AssetConnectionError) as cap_request_error:  # TODO pensar si hay mas (p.e. AssetConnectionError)
                if isinstance(cap_request_error, CapabilityDataError):
                    if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME in received_cap_data:
                        cap_request_error = CapabilityRequestExecutionError(
                            received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME],
                            cap_request_error.message, self)
                    else:
                        cap_request_error = CapabilityRequestExecutionError('', cap_request_error.message, self)
                if isinstance(cap_request_error, CapabilityCheckingError):
                    cap_request_error = CapabilityRequestExecutionError(cap_request_error.cap_name,
                                                                        cap_request_error.reason, self)
                if isinstance(cap_request_error, AssetConnectionError):
                    cap_request_error = CapabilityRequestExecutionError(
                        received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME],f"The error "
                            f"[{cap_request_error.error_type}] has appeared during the asset connection. "
                            f"Reason: {cap_request_error.reason}.", self)

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
            # First, the information about the received capability is obtained
            received_cap_data = self.svc_req_data['serviceData']['serviceParams']

            # It will be checked if the DT can perform the received capability
            try:
                # First, the received data is checked
                await self.check_received_cap_data()

                # Then, the capability checking process can be executed
                result = await self.myagent.aas_model.capability_checking_from_acl_request(received_cap_data)
            except (CapabilityDataError, CapabilityCheckingError) as cap_checking_error:
                if isinstance(cap_checking_error, CapabilityDataError):
                    if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME in received_cap_data:
                        cap_checking_error = CapabilityCheckingError(
                            received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME],
                            cap_checking_error.message)
                    else:
                        cap_checking_error = CapabilityCheckingError('', cap_checking_error.message)

                cap_checking_error.add_behav_class(self)
                await cap_checking_error.handle_capability_checking_error()
                return  # killing a behaviour does not cancel its current run loop

            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM, {'result': result})
            _logger.info("The Capability [{}] has been checked, with result: {}.".format(
                received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], result))
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
        This method checks whether the data received contains the necessary information to be able to execute
        the capability.

        Returns:
            bool: the result of the check.
        """
        # TODO PENSAR SI TODOS ESTOS ATRIBUTOS SON NECESARIOS: se ha pensado que quizas se podria solicitar una
        #  capacidad sin necesidad de definir la skill (como se implementa). En este caso, el DT podria elegir
        #  cualquiera de las skills para implementar la capacidad (eso si, habria que ver como recoger los skill
        #  parameters necesarios)
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
        # TODO analizar si faltan mas fields obligatorios
        # If the capability has constraints, it will be checked if they exist within the received data
        cap_elem = await self.myagent.aas_model.get_capability_by_id_short(
            cap_type=received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE],
            cap_id_short=received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME])
        cap_constraints = await self.myagent.aas_model.get_capability_associated_constraints(cap_elem)
        if cap_constraints:
            if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS not in received_cap_data:
                raise CapabilityDataError("The received capability data is invalid due to missing #{} field in request "
                                          "message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS))
            for constraint in cap_constraints:
                if constraint.id_short not in received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS]:
                    raise CapabilityDataError("The received capability data is invalid due to missing #{} constraint in"
                                              " the constraint section of the request message.".format(
                        constraint.id_short))

    async def check_received_skill_data(self, skill_elem):
        """
            This method checks whether the data received contains the necessary information in relation to the skill of the
            received capability request.

            Args:
                skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

            Returns:
                bool: the result of the check.
            """
        received_skill_data = self.svc_req_data['serviceData']['serviceParams'][
            CapabilitySkillACLInfo.REQUIRED_SKILL_INFO]
        if CapabilitySkillACLInfo.REQUIRED_SKILL_NAME not in received_skill_data:
            raise CapabilityDataError(
                "The received capability data is invalid due to missing #{} field in the skill "
                "information section of the request message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_NAME))
        if CapabilitySkillACLInfo.REQUIRED_SKILL_ELEMENT_TYPE not in received_skill_data:
            raise CapabilityDataError(
                "The received capability data is invalid due to missing #{} field in the skill "
                "information section of the request message.".format(
                    CapabilitySkillACLInfo.REQUIRED_SKILL_ELEMENT_TYPE))
        # If the skill has parameters, it will be checked if they exist within the received data
        # TODO de momento los skills son solo Operation, pensar como recoger los skill parameters para los demas casos
        if skill_elem.input_variable or skill_elem.output_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS not in received_skill_data:
                raise CapabilityDataError(
                    "The received capability data is invalid due to missing #{} field in the skill information"
                    " section of the request message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS))
        if skill_elem.input_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS not in received_skill_data[
                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]:
                raise CapabilityDataError(
                    "The received capability data is invalid due to missing #{} field in the skill parameters "
                    "information section of the request message.".format(
                        CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS))
        if skill_elem.output_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS not in received_skill_data[
                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]:
                raise CapabilityDataError(
                    "The received capability data is invalid due to missing #{} field in the skill parameters "
                    "information section of the request message.".format(
                        CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS))

    async def get_asset_connection_skill_data(self, skill_elem):
        """
        This method gets all the information required in the Asset Connection class in order to execute the received
        skill request.

        Args:
            skill_elem (basyx.aas.model.SubmodelElement): skill Python object in form of a SubmodelElement.

        Returns:
            received_skill_input_parameters (dict): information of skill input parameters.
            received_skill_output_parameters (dict): information of skill output parameters.
            skill_params_exposure (basyx.aas.model.SubmodelElement): SubmodelElement within the asset interface submodel that exposes the parameters of the given skill.
        """
        # If the skill has parameters, they have to be obtained from the received data
        received_skill_input_parameters = None
        received_skill_output_parameters = None
        skill_params_exposure = None
        # TODO como de momento el skill elem es Operation (tiene los parametros dentro del elemento)
        if len(skill_elem.input_variable) != 0 or len(skill_elem.output_variable) != 0:
            # The exposure element within the skill interface need to be obtained from each skill parameter
            skill_params_exposure = await self.myagent.aas_model.get_skill_parameters_exposure_interface_elem(
                skill_elem)
        # The received skill parameters is obtained from the received information
        received_cap_data = self.svc_req_data['serviceData']['serviceParams']
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
        return received_skill_input_parameters, received_skill_output_parameters, skill_params_exposure
