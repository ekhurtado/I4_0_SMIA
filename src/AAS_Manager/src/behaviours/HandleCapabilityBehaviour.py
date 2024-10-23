import json
import logging

from spade.behaviour import OneShotBehaviour

from logic import IntraAASInteractions_utils, Negotiation_utils, InterAASInteractions_utils
from utilities.FIPAACLInfo import FIPAACLInfo
from utilities.GeneralUtils import GeneralUtils

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
            case "PensarOtro": # TODO
                pass
            case _:
                _logger.error("Performative not available for capability management.")

    # ------------------------------------------
    # Methods to handle of all types of services
    # ------------------------------------------
    async def handle_call_for_proposal(self):
        """
        This method handle CallForProposal requests for the Capability.
        """
        # TODO por hacer
        pass

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
            acl_msg = InterAASInteractions_utils.create_inter_aas_response_msg(
                receiver=self.svc_req_data['sender'],
                thread=self.svc_req_data['thread'],
                performative=FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM,
                service_id=self.svc_req_data['serviceID'],
                service_type=self.svc_req_data['serviceType'],
                service_params= json.dumps({'result': result})
            )
            await self.send(acl_msg)
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
