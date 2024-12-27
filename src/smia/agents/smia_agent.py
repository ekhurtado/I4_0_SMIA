import asyncio

import basyx.aas.model
from spade.agent import Agent
import logging

from smia.aas_model.extended_aas_model import ExtendedAASModel
from smia.css_ontology.capability_skill_ontology import CapabilitySkillOntology
from smia.logic.agent_services import AgentServices
from smia.logic.exceptions import AASModelReadingError
from smia.states.state_running import StateRunning
from smia.states.state_stopping import StateStopping
from smia.utilities import configmap_utils
from smia.utilities.general_utils import SMIAGeneralInfo
from smia.behaviours.aas_fsm_behaviour import AASFSMBehaviour
from smia.states.state_booting import StateBooting
from smia.utilities.general_utils import GeneralUtils

_logger = logging.getLogger(__name__)


class SMIAAgent(Agent):
    """
    This is the top level in the hierarchy of SPADE Agents. It extends the own class Agent of SPADE. The SMIA
    Agent will be the generic and from which all other types of AAS Managers will start.
    """

    acl_svc_requests = {}   #: Dictionary to save FIPA-ACL service requests
    acl_svc_responses = {}   #: Dictionary to save FIPA-ACL service responses
    interaction_id_num = 0  #: Identifier for Intra AAS interaction, created by the AAS Manager
    interaction_requests = {}  #: Dictionary to save Intra AAS interaction requests
    interaction_responses = {}  #: Dictionary to save Intra AAS interaction responses
    negotiations_data = {}  #: Dictionary to save negotiations related information
    aas_model = None  #: Object with the extended AAS model
    css_ontology = None  #: Object with the Capability-Skill-Service ontology
    asset_connections = None  #: Class with the Asset Connection methods
    agent_services = None   #: Class with the all services of the Agent
    lock = None  #: Asyncio Lock object for secure access to shared SMIA objects

    def __init__(self, jid: str = None, password: str = None, verify_security: bool = False):
    # def __init__(self, jid: str = None, password: str = None, port: int = 5222, verify_security: bool = False):     # For v4.0.0 and more

        # The AAS_ID will be set in the associated ConfigMap, within the general-information of the AAS
        if jid is None:
            jid = configmap_utils.get_dt_general_property('agentID')
        if '@' not in jid:
            # The XMPP server of the MAS will also be set in the associated ConfiMap
            xmpp_server = configmap_utils.get_dt_general_property('xmpp-server')

            # Build the agent jid and password
            jid = jid + '@' + xmpp_server
        if password is None:
            password = configmap_utils.get_dt_general_property('password')

        super().__init__(jid, password, verify_security)
        # super().__init__(jid, password, port, verify_security)      # For v4.0.0 and more

        # The banner of the program is printed
        GeneralUtils.print_smia_banner()

        self.initialize_smia_attributes()


    def initialize_smia_attributes(self):
        """
        This method initializes all the attributes of the AAS Manager
        """
        # Objects to store the information related to ACL services are initialized
        self.acl_messages_id = 0  # It is reset
        self.acl_svc_requests = {}
        self.acl_svc_responses = {}

        # Objects to store the information related to AAS Manager-Core interactions are initialized
        self.interaction_id_num = 0  # The interactionId number is reset
        self.interaction_id = 'manager-' + str(self.interaction_id_num)  # The complete interactionId
        self.interaction_requests = {}
        self.interaction_responses = {}

        # Object to store the information related to negotiations is initialized
        self.negotiations_data = {}

        # The object with the CSS ontology and useful methods is initialized
        self.css_ontology = CapabilitySkillOntology()

        # The object with the Extended AAS model and useful methods is initialized
        self.aas_model = ExtendedAASModel()

        # The object with the AssetConnection class is initialized. At this point, as a empty JSON
        self.asset_connections = {}

        # The class with all AgentServices is initialized
        self.agent_services = AgentServices(self)

        # The Lock object is used to manage the access to global agent attributes (request and response dictionaries,
        # interaction id number...)
        self.lock = asyncio.Lock()

    async def setup(self):
        """
        This method performs the common setup of all types of Managers. It defines the Finite State Machine (FSM) of
        the general AAS Manager Agent.
        """
        _logger.info(f"Setting up {self.jid} SMIA...")

        # First, the FSMBehaviour is instantiated
        fsm_behaviour = AASFSMBehaviour()

        # TODO HACER AHORA PENSAR SI TIENE ESTADO IDLE SMIA GENERICO (en SMIAResource esta definido con IDLE)

        # A common AAS Manager has three states
        fsm_behaviour.add_state(name=SMIAGeneralInfo.BOOTING_STATE_NAME, state=StateBooting(), initial=True)
        fsm_behaviour.add_state(name=SMIAGeneralInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=SMIAGeneralInfo.STOPPING_STATE_NAME, state=StateStopping())

        # Transitions are defined to determine from which state to which other state you are allowed to move to.
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.BOOTING_STATE_NAME, dest=SMIAGeneralInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=SMIAGeneralInfo.RUNNING_STATE_NAME, dest=SMIAGeneralInfo.STOPPING_STATE_NAME)

        # The FSM behaviour is added to the agent
        self.add_behaviour(fsm_behaviour)
        _logger.info(f"{self.jid} setup finished correctly.")

    # ----------------------------------------------
    # Methods related to shared objects of the agent
    # ----------------------------------------------
    async def get_interaction_id(self):
        """
        This method returns the identifier of the AAS Intra interactions of the AAS Manager.

        Returns:
            str: identifier of the interaction id.
        """
        async with self.lock:
            return 'manager-' + str(self.interaction_id_num)

    async def increase_interaction_id_num(self):
        """
        This method increases the interaction id number for the AAS Intra interactions between the AAS Manager and the
        AAS Core.
        """
        async with self.lock:
            self.interaction_id_num += 1

    async def save_new_acl_svc_request(self, thread, request_data):
        """
        This method adds a new ACL Service Request to the global acl service requests dictionary of the AAS Manager.

        Args:
            thread (str): thread of the ACL Service Request.
            request_data (dict): all the information of the ACL Service Request in JSON format.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.acl_svc_requests[thread] = request_data

    async def save_acl_svc_response(self, thread, response_data):
        """
        This method adds a specific Inter AAS interaction response to the global responses dictionary of the AAS Manager
        for this type of interaction.

        Args:
            thread (str): thread of the ACL Service response.
            response_data (dict): all the information of the ACL Service response in JSON format.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.acl_svc_responses[thread] = response_data

    async def remove_acl_svc_request(self, thread):
        """
        This method removes an ACL Service Request from the global acl service requests dictionary of the AAS Manager.

        Args:
            thread (str): thread of the ACL Service Request.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.acl_svc_requests.pop(thread, None)

    async def get_acl_svc_request(self, thread):
        """
        This method gets the information of an ACL Service Request from the global acl service requests dictionary of
        the AAS Manager using the thread.
        Args:
            thread (str): thread of the ACL Service Request.

        Returns:
            dict: all information of the ACL Service Request in JSON format (null if the thread does not exist).
        """
        async with self.lock:  # safe access to a shared object of the agent
            if thread in self.acl_svc_requests:
                return self.acl_svc_requests[thread]
            else:
                return None

    async def save_interaction_request(self, interaction_id, request_data):
        """
        This method adds a specific Intra AAS interaction Request to the global requests dictionary of the AAS Manager
        for this type of interaction using a specific interaction id.

        Args:
            interaction_id (str): interaction identifier of the Intra AAS interaction request.
            request_data (dict): all the information of the Intra AAS interaction Request in JSON format.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.interaction_requests[interaction_id] = request_data

    async def save_interaction_response(self, interaction_id, response_data):
        """
        This method adds a specific Intra AAS interaction response to the global responses dictionary of the AAS Manager
        for this type of interaction.

        Args:
            interaction_id (str): identifier of the Intra AAS interaction response.
            response_data (dict): all the information of the ACL Service response in JSON format.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.interaction_responses[interaction_id] = response_data

    async def remove_interaction_request(self, interaction_id):
        """
        This method removes an Intra AAS interaction Request from the global requests dictionary of the AAS Manager for
        this type of interaction.

        Args:
            interaction_id (str): interaction identifier of the Intra AAS interaction Request.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.interaction_requests.pop(interaction_id, None)

    async def get_interaction_request(self, interaction_id):
        """
        This method gets the information of an Intra AAS Interaction Request from the global acl service requests
        dictionary of the AAS Manager using the interaction identifier.
        Args:
            interaction_id (str): interaction identifier of the Intra AAS interaction Request.

        Returns:
            dict: all information of the Intra AAS Interaction Request in JSON format (null if the thread does not exist).
        """
        async with self.lock:  # safe access to a shared object of the agent
            if interaction_id in self.interaction_requests:
                return self.interaction_requests[interaction_id]
            else:
                return None

    async def save_negotiation_data(self, thread, neg_data):
        """
        This method saves the information of a specific negotiation in which the AAS Manager has participated. The data
        is stored in the global object for all negotiations of the AAS Manager.

        Args:
            thread (str): thread of the negotiation
            neg_data (dict): all the information of the specific negotiation
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.negotiations_data[thread] = neg_data

    async def add_new_asset_connection(self, interface_reference, asset_connection):
        """
        This method adds a new asset connection to the global variable of the agent.

        Args:
            interface_reference (str): reference of the interface of the AssetConnection
            asset_connection: class with all information about the AssetConnection
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.asset_connections[interface_reference] = asset_connection

    async def get_asset_connection_class_by_ref(self, asset_connection_ref):
        """
        This method gets the asset connection class using its reference.

        Args:
            asset_connection_ref (basyx.aas.model.ModelReference): reference of the asset connection

        Returns:
            assetconnection.asset_connection: class of the asset connection
        """
        async with self.lock:  # safe access to a shared object of the agent
            for conn_ref, conn_class in self.asset_connections.items():
                if conn_ref == asset_connection_ref:
                    return conn_class
            raise AASModelReadingError("There is not asset connection class linked to {}".format(asset_connection_ref),
                                       asset_connection_ref, "MissingAssetConnectionClass")

    async def get_all_asset_connections(self):
        """
        This method returns all asset connections of the agent.

        Returns:
            dict: dictionary wil all asset connections
        """
        async with self.lock:  # safe access to a shared object of the agent
            return self.asset_connections