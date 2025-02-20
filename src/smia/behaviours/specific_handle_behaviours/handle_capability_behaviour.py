import json
import logging

import basyx.aas.model
from spade.behaviour import OneShotBehaviour

from smia import GeneralUtils
from smia.logic import inter_aas_interactions_utils
from smia.logic.exceptions import CapabilityRequestExecutionError, CapabilityCheckingError, RequestDataError, \
    AssetConnectionError, OntologyReadingError, AASModelReadingError
from smia.css_ontology.css_ontology_utils import CapabilitySkillACLInfo
from smia.utilities import smia_archive_utils
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
        This method handle capability requests to the DT.
        """

        # TODO, para este paso, se podrian almacenar las capacidades que se han verificado ya cuando se recibe el
        #  Query-If (se supone que otro agente debería mandar en CallForProposal despues del Query-If, pero para
        #  añadirle una validacion extra) Esto podria hacerse con el thread (el Query-If y CFP estarían en la misma
        #  negociacion?). Otra opcion es siempre ejecutar aas_model.capability_checking_from_acl_request()
        cap_name = None
        try:
            # First, the data received is checked to ensure that it contains all the necessary information.
            await self.check_received_capability_request_data()

            # The instances of capability, skill and skill interface are obtained depending on the received data
            cap_ontology_instance, skill_ontology_instance, skill_interface_ontology_instance = \
                await self.get_ontology_instances()
            cap_name = cap_ontology_instance.name

            # Before executing the capability, the capability checking should be also performed to ensure that SMIA
            # can perform it.
            result, reason = await self.execute_capability_checking()
            if not result:
                raise CapabilityRequestExecutionError(
                    cap_name,f"The capability {cap_name} cannot be executed because the capability checking "
                             f"result is invalid. Reason: {reason}.", self)

            # Once all the data has been checked and obtained, the capability can be executed
            cap_execution_result = await self.execute_capability(cap_ontology_instance, skill_ontology_instance,
                                                                 skill_interface_ontology_instance)

            # When the skill has finished, the request is answered
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'result': cap_execution_result})

            _logger.info("Management of the capability {} finished.".format(cap_name))

            # The information will be stored in the log
            execution_info = {'capName': cap_name, 'capType': str(cap_ontology_instance.is_a),
                              'result': str(cap_execution_result), 'taskType': 'CapabilityRequest'}
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.svc_req_data, execution_info,
                                                           self.svc_req_data['serviceType'])

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
        # TODO modificar el codigo para usar la ontologia (sigue con el enfoque antiguo)
        cap_name = None
        try:
            # First, the data received is checked to ensure that it contains all the necessary information.
            await self.check_received_capability_request_data()     # TODO de momento se analiza igual que las Capability requests (mas adelante pensar como son los mensajes ACL para CapabilityRequest y CapabilityChecking)

            # Then, the capability checking process can be executed
            result, reason = await self.execute_capability_checking()

            # When the checking has finished, the request is answered
            cap_name = self.svc_req_data['serviceData']['serviceParams'][CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
            cap_ontology_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)
            await self.send_response_msg_to_sender(FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                                                   {'result': result, 'reason': reason})

            _logger.info("Checking of the capability {} finished with result {}.".format(cap_name, result))

            # The information will be stored in the log
            execution_info = {'capName': cap_name, 'capType': str(cap_ontology_instance.is_a),
                              'result': str(result), 'reason': reason, 'taskType': 'CapabilityChecking'}
            smia_archive_utils.save_completed_svc_log_info(self.requested_timestamp,
                                                           GeneralUtils.get_current_timestamp(),
                                                           self.svc_req_data, execution_info,
                                                           self.svc_req_data['serviceType'])

        except (RequestDataError, AASModelReadingError) as cap_checking_error:
            if isinstance(cap_checking_error, RequestDataError):
                if 'JSON schema' in cap_checking_error.message:
                    cap_name = ''
            cap_checking_error = CapabilityCheckingError(cap_name, cap_checking_error.__class__.__name__ +
                                                                ': ' + cap_checking_error.message, self)
            await cap_checking_error.handle_capability_checking_error()
            return  # killing a behaviour does not cancel its current run loop

    async def handle_inform(self):
        """
        This method handles AAS Services. These services serve for the management of asset-related information through
        a set of infrastructure services provided by the AAS itself. These include Submodel Registry Services (to list
        and register submodels), Meta-information Management Services (including Classification Services, to check if the
        interface complies with the specifications; Contextualization Services, to check if they belong together in a
        context to build a common function; and Restriction of Use Services, divided between access control and usage
        control) and Exposure and Discovery Services (to search for submodels or asset related services).

        """
        _logger.info('CSS-related INFORM performative message: ' + str(self.svc_req_data))


    # Internal logic methods
    # ----------------------
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
            ontology='CapabilityResponse',
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
                # It is checked that the necessary parameter data have been added (in this case only the input
                # parameters will be necessary).
                skill_params = skill_instance.get_associated_skill_parameter_instances()
                for param in skill_params:
                    if param.is_skill_parameter_type(['INPUT', 'INOUTPUT']):
                        # If there is a parameter of type INPUT or INOUTPUT the value of the parameter need to be
                        # specified in the request message
                        if CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES not in received_cap_data:
                            raise RequestDataError("The received request is invalid due to missing #{} field in the "
                                                   "request message because the requested skill need value for an input"
                                                   " parameter ({}).".format(
                                CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES, param.name))
                        if param.name not in received_cap_data[CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES].keys():
                            raise RequestDataError("The received request is invalid due to missing #{} field in the "
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
        # The constraints of the given capability are also checked
        constraint_instances = cap_ontology_instance.get_associated_constraint_instances()
        if constraint_instances is not None:
            if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS not in received_cap_data:
                raise RequestDataError("The received request is invalid because the #{} field is missing in the "
                                       "request message, and the given capability {} has constraints defined.".format(
                    CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS, cap_name))
            for constraint in constraint_instances:
                if constraint.name not in received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS].keys():
                    raise RequestDataError("The received request is invalid due to missing #{} field in the"
                                           "request message because the requested capability need value for this "
                                           "constraint ({}).".format(
                        CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS, constraint.name))
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

    async def execute_capability_checking(self):
        """
        This method executes the process of checking the requested capability to ensure that this SMIA can perform it.

        Returns:
            bool: result of the capability checking
        """
        # First, the ontology instance of the capability is obtained
        received_cap_data = self.svc_req_data['serviceData']['serviceParams']
        cap_name = received_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME]
        cap_ontology_instance = await self.myagent.css_ontology.get_ontology_instance_by_name(cap_name)

        # The associated constraints and received values for them are also obtained
        constraint_instance_list = cap_ontology_instance.get_associated_constraint_instances()
        received_constraint_data = self.svc_req_data['serviceData']['serviceParams'][
            CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS]

        # At this point, the data received has already been verified, so that the values of the constraints can be
        # checked directly.
        for constraint_instance in constraint_instance_list:
            aas_cap_constraint_elem = await self.myagent.aas_model.get_object_by_reference(
                constraint_instance.get_aas_sme_ref())
            result = aas_cap_constraint_elem.check_constraint(received_constraint_data[constraint_instance.name])
            if not result:
                return False, 'The constraint {} with data {} is not valid'.format(constraint_instance.name,
                                                                                   received_constraint_data[constraint_instance.name])
        # If all capability constraint are valid, the checking valid
        # TODO PENSAR MAS VALIDACIONES DURANTE EL CAPABILITY CHECKING
        return True, ''

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

        parent_submodel = aas_skill_interface_elem.get_parent_submodel()
        if parent_submodel.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL):
            # In this case, the capability need to be executed through an asset service
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
        else:
            # In this case, the capability need to be executed through an agent service
            # TODO FALTA COMPROBAR QUE FUNCIONA
            try:
                received_skill_input_data = self.svc_req_data['serviceData']['serviceParams'][
                    CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS_VALUES]
                skill_execution_result = await self.myagent.agent_services.execute_agent_service_by_id(
                    aas_skill_interface_elem.id_short, **received_skill_input_data)
            except (KeyError, ValueError) as e:
                raise CapabilityRequestExecutionError(cap_instance.name, "The requested capability {} cannot be "
                                                      "executed because the agent service {} cannot be successfully "
                                                      "executed.".format(cap_instance.name,
                                                      aas_skill_interface_elem.id_short), self)

        return skill_execution_result

