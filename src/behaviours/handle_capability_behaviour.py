import json
import logging

from spade.behaviour import OneShotBehaviour

from logic import inter_aas_interactions_utils
from logic.exceptions import CapabilityRequestExecutionError
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
            case FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP:  # TODO actualizar dentro de todo el codigo los usos de performativas y ontologias de FIPA-ACL
                await self.handle_call_for_proposal()
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
    async def handle_call_for_proposal(self):
        """
        This method handle CallForProposal requests for the Capability.
        """
        if self.svc_req_data['serviceID'] == 'capabilityRequest':
            # First, the capability to be performed will be obtained from the internal AAS model
            # TODO, para este paso, se podrian almacenar las capacidades que se han verificado ya cuando se recibe el
            #  Query-If (se supone que otro agente debería mandar en CallForProposal despues del Query-If, pero para
            #  añadirle una validacion extra) Esto podria hacerse con el thread (el Query-If y CFP estarían en la misma
            #  negociacion?). Otra opcion es siempre ejecutar aas_model.capability_checking_from_acl_request()
            required_cap_data = self.svc_req_data['serviceData']['serviceParams']

            # The data received is checked to ensure that it contains all the necessary information.
            await self.check_received_cap_data(required_cap_data)

            required_cap_type = required_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_TYPE]
            capability_elem = await self.myagent.aas_model.get_capability_by_id_short(
                cap_type=required_cap_type,
                cap_id_short=required_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME])
            if required_cap_type == CapabilitySkillOntology.ASSET_CAPABILITY_TYPE:
                # In this case, the asset skill has to be executed through skill interface
                _logger.interactioninfo("The Capability requested is of AssetCapability type.")
                # TODO, habria que tener en cuenta que puede ser asincrono, asi que quizas un wait hasta que el asset
                #  connection reciba la respuesta. Al final hay que pensar parecido a como se hacia con interactionID,
                #  pero en  este caos no tenemos peticion respuesta interna

                # TODO De momento el AssetConnection se establece al leer el AAS Model, pero, si queremos ofrecer mas de
                #  una interfaz simultánea, habría que especificarla justo antes de realizar la conexión con el activo

                # TODO BORRAR (es solo para pruebas, esta como el AAS Core de ROS, usando un fichero JSON como intermediario para el gateway)

                # skill_elem =  self.myagent.aas_model.get_skill_data_by_capability(capability_elem, 'skillObject')
                skill_interface_elem = await self.myagent.aas_model.get_skill_data_by_capability(capability_elem,
                                                                                                 'skillInterface')

                # SkillInterface will be an SME action inside the AssetInterfacesDescription submodel. The interface
                # will be already configured from the agent Booting state, so it will be possible to execute the
                # AssetConnection sending method passing the SkillInterface to it. The AssetConnection will collect the
                # necessary information from the SkillInterface (from the SubmodelElement). The asset connection message
                # sending method will wait for the response, as well as the CapabilityHandleBehaviour.
                skill_execution_result = ''
                asset_connection_ref = skill_interface_elem.get_parent_ref_by_semantic_id(
                    AssetInterfacesInfo.SEMANTICID_INTERFACE)
                if asset_connection_ref:
                    # Once the Asset Connection reference is obtained, the associated class can be used to connect with
                    # the asset
                    asset_connection_class = await self.myagent.get_asset_connection_class(asset_connection_ref)

                    # The skill inputs parameters has to be obtained
                    required_skill_parameters = required_cap_data[
                        CapabilitySkillACLInfo.REQUIRED_SKILL_INFO][CapabilitySkillACLInfo.REQUIRED_SKILL_PARAMETERS]
                    required_skill_input_parameters = None
                    if CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS in required_skill_parameters:
                        required_skill_input_parameters = required_skill_parameters[
                            CapabilitySkillACLInfo.REQUIRED_SKILL_INPUT_PARAMETERS]
                    if CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS in required_skill_parameters:
                        # TODO analizar que pasaria si hay output parameters
                        required_skill_output_parameters = required_skill_parameters[
                            CapabilitySkillACLInfo.REQUIRED_SKILL_OUTPUT_PARAMETERS]

                    _logger.interactioninfo("The Asset connection of the Skill Interface has been obtained.")
                    _logger.interactioninfo(
                        "Executing skill of the capability through a request of an asset service...")
                    skill_execution_result = await asset_connection_class.send_msg_to_asset(skill_interface_elem,
                                                                                            required_skill_input_parameters)
                    if skill_execution_result:
                        _logger.interactioninfo("Skill of the capability successfully executed.")

                        # Se comprueba si la capacidad requerida tiene postcondiciones
                        constraints_values = required_cap_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS]
                        await self.myagent.aas_model.skill_feasibility_checking_post_conditions(capability_elem,
                                                                                                constraints_values)

                    else:
                        _logger.warning("Failed to execute the skill of the capability correctly.")

                else:
                    _logger.warning("The capability required has invalid skill interface.")
                    skill_execution_result = 'NotExecuted'

                # When the skill has finished, the request is answered
                await self.send_response_inform_to_sender({'result': skill_execution_result})
                _logger.info("Management of the capability {} finished.".format(capability_elem))

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
            required_capability_data = self.svc_req_data['serviceData']['serviceParams']
            # It will be checked if the DT can perform the required capability
            result = await self.myagent.aas_model.capability_checking_from_acl_request(required_capability_data)
            await self.send_response_inform_to_sender({'result': result})
            _logger.info("The Capability [{}] has been checked, with result: {}.".format(
                required_capability_data[CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME], result))
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

    async def send_response_inform_to_sender(self, service_params):
        """
        This method creates and sends and INFORM FIPA-ACL message with the given serviceParams.

        Args:
            service_params (dict): JSON with the serviceParams to be sent in the message.
        """
        acl_msg = inter_aas_interactions_utils.create_inter_aas_response_msg(
            receiver=self.svc_req_data['sender'],
            thread=self.svc_req_data['thread'],
            performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
            service_id=self.svc_req_data['serviceID'],
            service_type=self.svc_req_data['serviceType'],
            service_params=json.dumps(service_params)
        )
        await self.send(acl_msg)

    async def check_received_cap_data(self, received_cap_data):
        """
        This method checks if the received

        Args:
            received_cap_data (dict): JSON with the received information about the requested capability.

        Returns:
            bool: the result of the check.
        """
        # TODO hacer ahora
        try:
            if CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME not in received_cap_data:
                raise CapabilityRequestExecutionError("The capability cannot be executed due to missing {} field in request "
                                                      "message.".format(CapabilitySkillACLInfo.REQUIRED_CAPABILITY_NAME),
                                                      self.svc_req_data['sender'], self.svc_req_data['thread'],
                                                      self.svc_req_data['serviceID'], self)
            pass
        except CapabilityRequestExecutionError as cap_exec_error:
            await cap_exec_error.handle_capability_execution_error()
