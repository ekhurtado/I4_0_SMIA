import asyncio

from spade.agent import Agent
import logging

from states.StateRunning import StateRunning
from states.StateStopping import StateStopping
from utilities.AASmanagerInfo import AASmanagerInfo
from behaviours.AASFSMBehaviour import AASFSMBehaviour
from states.StateBooting import StateBooting

_logger = logging.getLogger(__name__)


class AASManagerAgent(Agent):
    """
    This is the top level in the hierarchy of SPADE Agents. It extends the own class Agent of SPADE. The AAS Manager
    Agent will be the generic and from which all other types of AAS Managers will start.
    """

    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)

        # Objects for storing the information related to ACL services are initialized
        self.acl_messages_id = 0  # It is reset
        self.acl_svc_requests = {}
        self.acl_svc_responses = {}

        # Objects for storing the information related to AAS Manager-Core interactions are initialized
        self.interaction_id_num = 0  # The interactionId number is reset
        self.interaction_id = 'manager-' + str(self.agent.interaction_id_num)  # The complete interactionId
        self.interaction_requests = {}
        self.interaction_responses = {}

        # The Lock object is used to manage the access to global agent attributes (request and response dictionaries,
        # interaction id number...)
        self.lock = asyncio.Lock()

    async def setup(self):
        """
        This method performs the common setup of all types of Managers. It defines the Finite State Machine (FSM) of
        the general AAS Manager Agent.
        """

        # First, the FSMBehaviour is instantiated
        fsm_behaviour = AASFSMBehaviour()

        # A common AAS Manager has three states
        fsm_behaviour.add_state(name=AASmanagerInfo.BOOTING_STATE_NAME, state=StateBooting(), initial=True)
        fsm_behaviour.add_state(name=AASmanagerInfo.RUNNING_STATE_NAME, state=StateRunning())
        fsm_behaviour.add_state(name=AASmanagerInfo.STOPPING_STATE_NAME, state=StateStopping())

        # Transitions are defined to determine from which state to which other state you are allowed to move to.
        fsm_behaviour.add_transition(source=AASmanagerInfo.BOOTING_STATE_NAME, dest=AASmanagerInfo.RUNNING_STATE_NAME)
        fsm_behaviour.add_transition(source=AASmanagerInfo.RUNNING_STATE_NAME, dest=AASmanagerInfo.STOPPING_STATE_NAME)

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

    async def save_new_interaction_request(self, request_data):
        """
        This method adds a new Intra AAS interaction Request to the global requests dictionary of the AAS Manager for
        this type of interaction.

        Args:
            request_data (dict): all the information of the ACL Service Request in JSON format.
        """
        async with self.lock:  # safe access to a shared object of the agent
            self.interaction_requests[self.get_interaction_id()] = request_data

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
