import json
import logging

import basyx.aas.model
from spade.behaviour import OneShotBehaviour

from smia.logic import inter_aas_interactions_utils
from smia.logic.exceptions import CapabilityRequestExecutionError, CapabilityCheckingError, RequestDataError, \
    AssetConnectionError, OntologyReadingError, AASModelReadingError
from smia.css_ontology.css_ontology_utils import CapabilitySkillACLInfo
from smia.utilities.smia_info import AssetInterfacesInfo
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLJSONSchemas

_logger = logging.getLogger(__name__)


class HandleCapabilityBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles a request related to the capabilities of the Digital Twin.
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
    async def handle_request_old(self):
        """
        This method handle capability requests to the DT.
        """
        if self.svc_req_data[
            'serviceID'] == 'capabilityRequest':  #  TODO CAMBIARLO POR LA ONTOLOGIA DEL MENSAJE ACL (ahi irá el 'CapabilityRequest')
            # First, the capability to be performed will be obtained from the internal AAS model
            # TODO, para este paso, se podrian almacenar las capacidades que se han verificado ya cuando se recibe el
            #  Query-If (se supone que otro agente debería mandar en CallForProposal despues del Query-If, pero para
            #  añadirle una validacion extra) Esto podria hacerse con el thread (el Query-If y CFP estarían en la misma
            #  negociacion?). Otra opcion es siempre ejecutar aas_model.capability_checking_from_acl_request()

            try:
                # The capability checking should be also performed to ensure that the DT can perform it. In this case,
                # the capability checking is performed in separate steps
                # The data received is checked to ensure that it contains all the necessary information.
                await self.check_received_capability_request_data()
                received_cap_data = self.svc_req_data['serviceData']['serviceParams']

                # TODO: CUIDADO a partir de ahora es el codigo antiguo (sin tener en cuenta la ontologia)
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
                asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(asset_connection_ref)
                if not asset_connection_ref:
                    raise CapabilityRequestExecutionError(cap_name, "The capability {} could not be executed because "
                                                                    "the asset connection of its skill interface element was not found.".format(
                        cap_name), self)

                received_skill_input_parameters, received_skill_output_parameters, skill_params_exposures = \
                    await self.get_asset_connection_input_data_by_skill(skill_elem)

                _logger.assetinfo("The Asset connection of the Skill Interface has been obtained.")
                _logger.assetinfo(
                    "Executing skill of the capability through a request of an asset service...")
                skill_execution_result = await asset_connection_class.execute_skill_by_asset_service(
                    interaction_metadata=skill_interface_elem,
                    skill_params_exposure_elem=skill_params_exposures,
                    skill_input_params=received_skill_input_parameters,
                    skill_output_params=received_skill_output_parameters)
                if skill_execution_result:
                    _logger.assetinfo("Skill of the capability successfully executed.")

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
            except (RequestDataError, CapabilityCheckingError, CapabilityRequestExecutionError,
                    AssetConnectionError) as cap_request_error:  # TODO pensar si hay mas (p.e. AssetConnectionError)
                if isinstance(cap_request_error, RequestDataError):
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
                        received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], f"The error "
                                                                                            f"[{cap_request_error.error_type}] has appeared during the asset connection. "
                                                                                            f"Reason: {cap_request_error.reason}.",
                        self)

                await cap_request_error.handle_capability_execution_error()
                return  # killing a behaviour does not cancel its current run loop
        else:
            pass
            # TODO pensar que situaciones habria

    async def handle_request(self):
        """
        This method handle capability requests to the DT.
        """

        # TODO, para este paso, se podrian almacenar las capacidades que se han verificado ya cuando se recibe el
        #  Query-If (se supone que otro agente debería mandar en CallForProposal despues del Query-If, pero para
        #  añadirle una validacion extra) Esto podria hacerse con el thread (el Query-If y CFP estarían en la misma
        #  negociacion?). Otra opcion es siempre ejecutar aas_model.capability_checking_from_acl_request()
        cap_name = None
        try:
            # The capability checking should be also performed to ensure that the DT can perform it. In this case,
            # the capability checking is performed in separate steps
            # First, the data received is checked to ensure that it contains all the necessary information.
            await self.check_received_capability_request_data()

            # The instances of capability, skill and skill interface are obtained depeding on the received data
            cap_ontology_instance, skill_ontology_instance, skill_interface_ontology_instance = \
                await self.get_ontology_instances()

            # Once all the data has been checked and obtained, the capability can be executed
            cap_execution_result = await self.execute_capability(cap_ontology_instance, skill_ontology_instance,
                                                                 skill_interface_ontology_instance)

            # When the skill has finished, the request is answered
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'result': cap_execution_result})

            _logger.info("Management of the capability {} finished.".format(cap_name))

        except (RequestDataError, OntologyReadingError, CapabilityRequestExecutionError,
                AASModelReadingError, AssetConnectionError) as cap_request_error:
            if isinstance(cap_request_error, RequestDataError):
                if 'JSON schema' in cap_request_error.message:
                    cap_name = ''
            if isinstance(cap_request_error, RequestDataError) or isinstance(cap_request_error, OntologyReadingError) \
                    or isinstance(cap_request_error, AASModelReadingError):
                cap_request_error = CapabilityRequestExecutionError(cap_name, cap_request_error.__class__.__name__ +
                                                                    ': ' + cap_request_error.message, self)
            if isinstance(cap_request_error, AssetConnectionError):
                cap_request_error = CapabilityRequestExecutionError(
                    cap_name, f"The error [{cap_request_error.error_type}] has appeared during the asset "
                              f"connection. Reason: {cap_request_error.reason}.", self)

            await cap_request_error.handle_capability_execution_error()
            return  # killing a behaviour does not cancel its current run loop

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
                await self.check_received_capability_request_data()

                # Then, the capability checking process can be executed
                result = await self.myagent.aas_model.capability_checking_from_acl_request(received_cap_data)
            except (RequestDataError, CapabilityCheckingError) as cap_checking_error:
                if isinstance(cap_checking_error, RequestDataError):
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

    async def check_received_capability_request_data(self):
        """
        This method checks whether the data received contains the necessary information to be able to execute
        the capability. If an error occurs, it throws a CapabilityDataError exception.
        """
        # TODO con el nuevo enfoque solo es necesario añadir la capacidad. Las demas son opcionales (skill, interfaz...)
        #  Esto se debe a que una capacidad puede solicitarse sin definir skills (si ninguna tiene parametros, SMIA
        #  ejecutaría la capacidad con una skill aleatoria). Lo que si se va a comprobar es que si se añaden datos
        #  opcionales, sean validos (p.e. que los datos añadidos estén conformes a la ontologia CSS)
        # First, the structure and attributes of the received data are checked and validated
        await inter_aas_interactions_utils.check_received_request_data_structure(
            self.svc_req_data, ACLJSONSchemas.JSON_SCHEMA_CAPABILITY_REQUEST)
        received_cap_data = self.svc_req_data['serviceData']['serviceParams']
        # if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME not in received_cap_data:
        #     raise RequestDataError("The received capability data is invalid due to missing #{} field in request "
        #                               "message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME))
        # else:
        cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
        cap_ontology_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)
        if cap_ontology_instance is None:
            raise RequestDataError("The capability {} does not an instance defined in the ontology of this "
                                   "DT".format(cap_name))
        if CapabilitySkillACLInfo.REQUIRED_SKILL_NAME in received_cap_data:
            skill_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_NAME]
            result, skill_instance = cap_ontology_instance.check_and_get_related_instance_by_instance_name(skill_name)
            if result is False:
                raise RequestDataError("The capability {} and skill {} are not linked in the ontology of this "
                                       "DT, or the skill does not have an instance"
                                       ".".format(cap_name, skill_name))
            if skill_instance.get_associated_skill_parameter_instances() is not None:
                pass  # TODO HACER AHORA: FALTA POR HACER
                # TODO comprobar que se han añadido los datos necesarios de los parametros (en este caso
                #  solo seran necesarios los parametros de entrada)
                skill_params = skill_instance.get_associated_skill_parameter_instances()
                for param in skill_params:
                    if param.is_skill_parameter_type(['INPUT', 'INOUTPUT']):
                        # If there is a parameter of type INPUT or INOUTPUT the value of the parameter need to be
                        # specified in the request message
                        if CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES not in received_cap_data:
                            raise RequestDataError("The received request is invalid due to missing #{} field in the"
                                                   "request message because the requested skill need value for an input"
                                                   " parameter ({}).".format(
                                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES, param.name))
                        if param.name not in received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES].keys():
                            raise RequestDataError("The received request is invalid due to missing #{} field in the"
                                                   "request message because the requested skill need value for an input"
                                                   " parameter ({}).".format(
                                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES, param.name))
            if CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME in received_cap_data:
                # Solo si se ha definido la skill se define la skill interface, sino no tiene significado
                # TODO pensar la frase anterior. Realmente tiene significado o no? Si no se define la skill, podriamos
                #  definir una interfaz que queremos utilizar si o si? En ese caso, habria que buscar una skill con esa
                #  interfaz para ejecutarla
                skill_interface_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME]
                result, instance = skill_instance.check_and_get_related_instance_by_instance_name(skill_interface_name)
                if result is False:
                    raise RequestDataError("The skill {} and skill interface {} are not linked in the ontology of "
                                           "this DT, or the skill interface does not have an instance"
                                           ".".format(skill_name, skill_interface_name))

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
            raise RequestDataError(
                "The received capability data is invalid due to missing #{} field in the skill "
                "information section of the request message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_NAME))
        if CapabilitySkillACLInfo.REQUIRED_SKILL_ELEMENT_TYPE not in received_skill_data:
            raise RequestDataError(
                "The received capability data is invalid due to missing #{} field in the skill "
                "information section of the request message.".format(
                    CapabilitySkillACLInfo.REQUIRED_SKILL_ELEMENT_TYPE))
        # If the skill has parameters, it will be checked if they exist within the received data
        # TODO de momento los skills son solo Operation, pensar como recoger los skill parameters para los demas casos
        if skill_elem.input_variable or skill_elem.output_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS not in received_skill_data:
                raise RequestDataError(
                    "The received capability data is invalid due to missing #{} field in the skill information"
                    " section of the request message.".format(CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS))
        if skill_elem.input_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS not in received_skill_data[
                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]:
                raise RequestDataError(
                    "The received capability data is invalid due to missing #{} field in the skill parameters "
                    "information section of the request message.".format(
                        CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS))
        if skill_elem.output_variable:
            if CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS not in received_skill_data[
                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]:
                raise RequestDataError(
                    "The received capability data is invalid due to missing #{} field in the skill parameters "
                    "information section of the request message.".format(
                        CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS))

    async def get_ontology_instances(self):
        """
        This method gets the ontology instances for the capability, skill and skill interface depending on the received
        data. If the data is invalid or there are no available combination of three instances, it raises an Exception.

        Returns:
            capability_instance (owlready2.ThingClass), skill_instance (owlready2.ThingClass),
            skill_interface_instance (owlready2.ThingClass): ontology instances for capability, skill and skill
            interface.
        """

        received_cap_data = self.svc_req_data['serviceData']['serviceParams']
        cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
        cap_ontology_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)

        # The CSS ontology is used to search for instances
        if CapabilitySkillACLInfo.REQUIRED_SKILL_NAME not in received_cap_data:
            cap_associated_skills = cap_ontology_instance.get_associated_skill_instances()
            if cap_associated_skills is None:
                raise CapabilityRequestExecutionError(cap_name, "The capability {} does not have any associated skill, "
                                                                "so it cannot be executed".format(cap_name), self)
            else:
                # En este caso no se ha determinado una skill en concreto, asi que se comprobará si alguna
                # skill no tiene parametros, por lo que puede ser directamente ejecutada
                for skill in cap_associated_skills:
                    if skill.get_associated_skill_parameter_instances() is None:
                        # En este caso no tiene parametros, por lo que se puede ejecutar directamente
                        if len(list(skill.get_associated_skill_interface_instances())) == 0:
                            # If the skill does not have interfaces, it cannot be executed
                            continue
                        # The first skill interface is obtained to execute the capability
                        return cap_ontology_instance, skill, list(skill.get_associated_skill_interface_instances())[0]
                else:
                    # En este caso todas las skills tienen parametros, asi que hay que solicitarselos al
                    # requester de la ejecución de la capacidad. Se devolverán todas skills con sus
                    # parametros para que vuelva a solicitar la ejecución de la capacidad pero con una skill
                    # especificada y con los valores necesarios de sus parametros
                    raise RequestDataError("To execute the capability {}, the skill and its parameters need to be added"
                                           " in the request message.".format(cap_name))
        else:
            # En este caso se ha especificado una skill, asi que primera se analizara si tiene parametros y
            # si estos se han definido
            result, skill_ontology_instance = (cap_ontology_instance.check_and_get_related_instance_by_instance_name(
                received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_NAME]))
            skill_interface_ontology_instance = None
            if CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME not in received_cap_data:
                # Si no se ha definido una skill interface, se recoge la primera
                skill_interface_ontology_instance = list(skill_ontology_instance.
                                                         get_associated_skill_interface_instances())[0]
                if skill_interface_ontology_instance is None:
                    raise CapabilityRequestExecutionError(cap_name, "The capability requested by the given"
                                                                    " skill cannot be executed because there is no skill "
                                                                    "interface defined.", self)
            else:
                result, skill_interface_ontology_instance = skill_ontology_instance.check_and_get_related_instance_by_instance_name(
                    received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_INTERFACE_NAME])
            return cap_ontology_instance, skill_ontology_instance, skill_interface_ontology_instance

    async def execute_capability(self, cap_instance, skill_instance, skill_interface_instance):
        """
        This method executes a given capability through as an implementation of a given skill through a given skill
        interface. All the data received are instances of the CSS ontology.

        Args:
            cap_instance (owlready2.ThingClass): ontology instance of the capability to execute.
            skill_instance (owlready2.ThingClass): ontology instance of the skill to execute.
            skill_interface_instance (owlready2.ThingClass): ontology instance of the skill interface to use.

        Returns:
            object: result of the capability execution
        """
        aas_cap_elem = await self.myagent.aas_model.get_object_by_reference(cap_instance.get_aas_sme_ref())
        aas_skill_elem = await self.myagent.aas_model.get_object_by_reference(skill_instance.get_aas_sme_ref())
        aas_skill_interface_elem = await self.myagent.aas_model.get_object_by_reference(
            skill_interface_instance.get_aas_sme_ref())
        if None in (aas_cap_elem, aas_skill_elem, aas_skill_interface_elem):
            raise CapabilityRequestExecutionError(cap_instance.name, "The requested capability {} cannot be executed"
                                                                     " because there is no AAS element linked to the ontology "
                                                                     "instances.".format(cap_instance.name), self)
        # The asset interface will be obtained from the skill interface SubmodelElement.
        aas_asset_interface_elem = aas_skill_interface_elem.get_associated_asset_interface()
        # TODO PENSAR COMO SERIA CON UN AGENT SERVICE
        # With the AAS SubmodelElement of the asset interface the related Python class, able to connect to the asset,
        # can be obtained.
        asset_connection_class = await self.myagent.get_asset_connection_class_by_ref(aas_asset_interface_elem)
        _logger.assetinfo("The Asset connection of the Skill Interface has been obtained.")
        # Now the capability can be executed through the Asset Connection class related to the given skill. The required
        # input data can be obtained from the received message, since it has already been verified as containing such data
        # TODO FALTA DESARROLLARLO EN EL METODO DE CHEQUEO DEL MENSAJE
        _logger.assetinfo("Executing skill of the capability through an asset service...")
        received_skill_input_data = self.svc_req_data['serviceData']['serviceParams'][
            CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES]
        skill_execution_result = await asset_connection_class.execute_asset_service(
            interaction_metadata=aas_skill_interface_elem, service_input_data=received_skill_input_data)
        _logger.assetinfo("Skill of the capability successfully executed.")

        # TODO SI LA SKILL TIENE OUTPUT PARAMETERS, HAY QUE RECOGERLOS DEL skill_execution_result. En ese caso, se
        #  sobreescribirá el skill_execution_result con la variable output y su valor (el cual será lo que devolverá el
        #  metodo del asset connnection class)

        return skill_execution_result

    async def get_asset_connection_input_data_by_skill(self, skill_elem):
        """
        This method gets all the input data required in the Asset Connection class by a given skill, in order to
        execute the received capability request.

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