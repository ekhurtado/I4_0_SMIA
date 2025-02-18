import asyncio
import copy
import json
import logging
from collections import OrderedDict
from datetime import datetime

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from smia import GeneralUtils
from smia.css_ontology.css_ontology_utils import CapabilitySkillACLInfo
from smia.utilities.fipa_acl_info import ServiceTypes, FIPAACLInfo
from smia.utilities.smia_info import SMIAInteractionInfo
from operator_gui_logic import GUIFeatures, GUIControllers

_logger = logging.getLogger(__name__)

class OperatorGUIBehaviour(OneShotBehaviour):
    """The behavior for the Operator only needs to add the web interface to the SMIA SPADE agent and the GUI related
    resources (HTML web pages and drivers)."""

    async def run(self) -> None:

        # First, the dictionary is initialized to add the menu entries that are required in runtime. The name of the
        # SMIA SPADE agent is also initialized to be used in the added HTMLs templates
        self.agent.web_menu_entries = OrderedDict()
        # self.agent.agent_name = str(self.agent.jid).split('@')[0]  # tambien se puede lograr mediante agent.jid.localpart
        self.agent.build_avatar_url = GUIFeatures.build_avatar_url

        # The dictionaries to build operator HTML webpage are also initialized
        self.agent.loaded_statistics = {'AASmodels': 0, 'AvailableSMIAs': 0,
                                          'Capabilities': 0, 'Skills': 0}
        self.agent.css_elems_info = {}
        self.agent.skills_info = {}
        self.agent.available_smia_selection = []
        self.agent.request_exec_info = {}

        _logger.info("SMIA SPADE web interface required resources initialized.")

        # The SMIA icon is added as the avatar of the GUI
        await GUIFeatures.add_custom_favicon(self.agent)
        _logger.info("Added SMIA Favicon to the web interface.")

        # The controllers class is also created offering the agent object
        self.operator_gui_controllers = GUIControllers(self.agent)

        # Then, the required HTML webpages are added to the SMIA SPADE web module
        self.agent.web.add_get('/smia_operator', self.operator_gui_controllers.hello_controller,
                               '/htmls/smia_operator.html')
        self.agent.web.add_get("/smia_operator/load", self.operator_gui_controllers.operator_load_controller, None)
        self.agent.web.add_post("/smia_operator/select", self.operator_gui_controllers.operator_select_controller, None)
        self.agent.web.add_post('/smia_operator/submit', self.operator_gui_controllers.operator_request_controller,
                                '/htmls/smia_operator_submit.html')

        # The new webpages need also to be added in the manu of the web interface
        # await GUIFeatures.add_new_menu_entry(self.agent,'System view', '/system_view', 'fa fa-eye')
        self.agent.web.add_menu_entry("SMIA operator", "/smia_operator", "fa fa-user-cog")

        _logger.info("Added new web pages to the web interface.")

        # TODO se ha añadido el Sen ACL del GUIAgent para realizar la prueba, hay que desarrollar los HTMLs para el
        #  operario y añadirlos

        # The behaviour to receive all FIPA-ACL message is also added to SMIA SPADE agent
        operator_recv_behav = OperatorReceiveBehaviour()
        self.agent.add_behaviour(operator_recv_behav)

        # Once all the configuration is done, the web interface is enabled in the SMIA SPADE agent
        self.agent.web.start(hostname="0.0.0.0", port="10000")
        _logger.info("Started SMIA SPADE web interface.")

class OperatorReceiveBehaviour(CyclicBehaviour):

    async def on_start(self) -> None:
        # The required global dictionaries are added to the agent
        self.agent.received_msgs = []
        self.agent.waiting_behavs = {}

    async def run(self) -> None:
        msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
        if msg:
            _logger.aclinfo("FIPA-ACL Message received from {} with performative {} and content: {}".format(
                msg.sender, msg.get_metadata('performative'), msg.body))
            self.agent.received_msgs.append(msg)
            if msg.thread in self.agent.waiting_behavs:
                _logger.info("There is a behaviour waiting for this message.")
                await self.unlock_behaviour(msg.thread, self.agent.waiting_behavs[msg.thread], msg)


    async def unlock_behaviour(self, thread, behav_name, msg):
        for behaviour in self.agent.behaviours:
            behav_class_name = str(behaviour.__class__.__name__)
            if behav_class_name == behav_name:
                if behaviour.thread == thread:
                    # Once the exact behaviour has been found, its execution is unlocked and the ACL message is offered
                    behaviour.receive_msg = msg
                    behaviour.receive_msg_event.set()
                    # The Event object is unset so that it can be used again.
                    behaviour.receive_msg_event.clear()

                    # The behaviour is also remove from the global dictionary
                    self.agent.waiting_behavs.pop(thread)
                    break


class OperatorRequestBehaviour(OneShotBehaviour):
    """
    This behaviour handles the CSS-related requests through FIPA-ACL messages.
    """

    def __init__(self, agent_object, req_data):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
            req_data (dict): all the information about the CSS-related request
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object
        self.request_data = req_data

        self.receive_msg_event = asyncio.Event()        # In order to wait for specific incoming messages
        self.receive_msg = None

        self.thread = req_data['thread']
        self.smia_id_list = req_data['formData'].getall('smia_id[]', [])
        self.asset_id_list = req_data['formData'].getall('asset_id[]', [])
        self.selected = req_data['formData'].getall('checkbox[]', [])
        self.capability = req_data['formData'].get('capability', None)  # Default if missing
        self.constraints = req_data['formData'].get('constraints', None)
        self.skill = req_data['formData'].get('skill', None)
        self.skill_params = req_data['formData'].get('skillParams', None)
        self.form_data = req_data['formData']

        # Group data by row index
        self.processed_data = []
        self.selected_smia_ids = []
        for idx, smia_id in enumerate(self.smia_id_list):
            if smia_id in self.selected:
                self.processed_data.append({
                    "smiaID": smia_id,
                    "assetID": self.asset_id_list[idx],
                })
                self.selected_smia_ids.append(smia_id + '@' + str(self.myagent.jid.domain))

    async def run(self) -> None:

        try:
            # The ACL message template is created
            msg = Message(thread=self.thread)
            msg_body_json = {'serviceID': 'capabilityRequest',
                             'serviceType': ServiceTypes.ASSET_RELATED_SERVICE,
                             'serviceData': {'serviceCategory': 'service-request',
                                             'serviceParams': {
                                                 'capabilityName': self.capability, 'skillName': self.skill
                                             }}
                             }
            if self.skill_params is not None:
                skill_params_dict = {}
                for param in set(eval(self.skill_params)):
                    param_value = self.form_data.get(param, None)
                    if param_value is None:
                        _logger.warning("The value of the {} parameter is missing, it is possible that the capability "
                                        "cannot be executed.".format(param))
                    skill_params_dict[param] = param_value
                msg_body_json['serviceData']['serviceParams']['skillParameterValues'] = skill_params_dict

            if self.constraints is not None:
                msg_body_json['serviceData']['serviceParams'][
                    CapabilitySkillACLInfo.REQUIRED_CAPABILITY_CONSTRAINTS] = eval(self.constraints)

            # The information of the CSS-related request is added in the agent dictionary for the HTML result page
            self.myagent.request_exec_info['InteractionsDict'].append(
                {'type': 'analysis', 'title': 'Analyzing operator selection ...', 'capability': self.capability,
                 'skill': self.skill, 'constraints': self.constraints, 'smia_ids': self.selected_smia_ids})

            # The JSON for the message body is added to message object
            msg.body = json.dumps(msg_body_json)
            smia_id = self.selected_smia_ids[0]

            if len(self.processed_data) > 1:
                _logger.info("There are multiple SMIAs to be requested: negotiation is required")

                # The negotiation request is made by performative CallForProposal (CFP)
                general_thread = str(self.thread)
                self.thread = msg.thread + '-neg'   # It needs to be updated in order to receive later the associated response msg
                # msg.thread = self.thread
                msg.metadata = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_CFP.metadata
                # The negotiation request ACL message is prepared (with skill for using RAM that every SMIA has)
                neg_body_json = copy.deepcopy(msg_body_json)
                neg_body_json['serviceData']['serviceParams'].update(
                    {'neg_requester_jid': str(self.myagent.jid), 'targets': (','.join(self.selected_smia_ids)),
                     'capabilityName': 'Negotiation', 'skillName': 'NegotiationBasedOnRAM'})

                # The updated JSON for the message body is added to message object
                msg.body = json.dumps(neg_body_json)

                for smia_id in self.selected_smia_ids:
                    # The CFP message is sent to each SMIA participant of the negotiation
                    msg.to = smia_id
                    _logger.aclinfo("Sending Negotiation request to {}...".format(smia_id))
                    neg_msg = OperatorRequestBehaviour.create_acl_msg(
                        smia_id, self.thread, SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_CFP.metadata, neg_body_json)
                    await self.send(neg_msg)
                    # await self.send(msg)
                    _logger.aclinfo("Message sent to {}!".format(msg.to))

                    self.myagent.request_exec_info['Interactions'] += 1

                # The information about the negotiation request is added in the dictionary for the HTML result page
                self.myagent.request_exec_info['InteractionsDict'].append(
                    {'type': 'acl_send', 'title': 'Requesting negotiation betweeen selected SMIAs ...',
                     'message': 'As several SMIAs have been selected, all of them {} have been asked to negotiate with '
                                'each other in order to obtain the best option.'.format(self.selected_smia_ids)})

                # The behaviour need to wait to the response message of negotiation winner
                self.myagent.waiting_behavs[self.thread] = self.__class__.__name__
                _logger.info('The behaviour will wait for the winner of the negotiation...')
                await self.receive_msg_event.wait()

                # The request for negotiation has been answered
                self.thread = msg.thread

                # The SMIA id to request the capability is updated to create correctly the next ACL message
                smia_id = eval(json.loads(self.receive_msg.body)['serviceData']['serviceParams'])['winner']

                # The information about the negotiation response is added in the dictionary for the HTML result page
                response_info = {'type': 'acl_recv', 'title': 'Obtaining negotiation winner ...'}
                if self.receive_msg.get_metadata('performative') == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE:
                    response_info.update({'response_type': 'failure', 'response_title':
                        'The negotiation process has not been completed.', 'response_msg':
                        str(json.loads(self.receive_msg.body)['serviceData']['serviceParams'])})
                else:
                    response_info.update({'response_type': 'success', 'response_title':
                        'The negotiation process has been completed.', 'response_msg':
                        'The SMIA winner of the negotiation is: {}.'.format(smia_id)})
                self.myagent.request_exec_info['InteractionsDict'].append(response_info)

            if ((self.capability != 'Negotiation') or
                    (self.capability == 'Negotiation' and len(self.processed_data) == 1)):  # TODO CUIDADO SI SE CAMBIA EL NOMBRE DE NEGOTIATION
                # If the capacity is not Negotiation and there are several SMIA, a request for negotiation had to be made
                # and the winner has been received, so the capacity will have to be requested from the winner. If there is
                # only one SMIA, the capacity will be requested directly.

                if self.capability == 'Negotiation':
                    # In this particular case, the negotiation request is made via the performative CallForProposal
                    msg_metadata = SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE_CFP.metadata
                    msg_body_json['serviceData']['serviceParams'].update({'neg_requester_jid': str(self.myagent.jid),
                                                                          'targets': smia_id})
                else:
                    msg_metadata = SMIAInteractionInfo.CAP_STANDARD_ACL_TEMPLATE_REQUEST.metadata

                # msg.body = json.dumps(msg_body_json)
                msg = OperatorRequestBehaviour.create_acl_msg(smia_id, self.thread, msg_metadata, msg_body_json)

                _logger.info("The selected capability to be executed is [{}].".format(self.capability))
                # The information about the CSS-related request is added in the dictionary for the HTML result page
                self.myagent.request_exec_info['InteractionsDict'].append(
                    {'type': 'acl_send', 'title': 'Requesting CSS-related capability execution ...',
                     'message': 'The SMIA with ID [{}] has been requested to execute the capability [{}].'.format(
                         smia_id, self.capability)})

                # msg.to = smia_id
                _logger.aclinfo("Sending {} capability request to {}...".format(self.capability, smia_id))
                await self.send(msg)
                _logger.aclinfo("Message sent to {}!".format(msg.to))
                self.myagent.request_exec_info['Interactions'] += 1

                # The behaviour need to wait to the response message
                self.myagent.waiting_behavs[self.thread] =  self.__class__.__name__
                _logger.info('The behaviour will wait for the response of the CSS-related request...')
                await self.receive_msg_event.wait()

                # The information about the CSS-related response is added in the agent dictionary for HTML result page
                response_info = {'type': 'acl_recv', 'title': 'Obtaining CSS-related capability execution result ...',
                                 'response_msg': str(json.loads(self.receive_msg.body)['serviceData']['serviceParams'])}
                if self.receive_msg.get_metadata('performative') == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_FAILURE:
                    response_info.update({'response_type': 'failure', 'response_title':
                        'The CSS-related execution has not been completed.'})
                else:
                    response_info.update({'response_type': 'success', 'response_title':
                        'The CSS-related execution has been completed.'})

                self.myagent.request_exec_info['InteractionsDict'].append(response_info)

            # As the CSS-related request has finished, the time information is added in the agent dictionary
            end_time = GeneralUtils.get_current_date_time()
            duration = (datetime.fromisoformat(str(end_time)) -
                        datetime.fromisoformat(str(self.myagent.request_exec_info['StartTime']))).total_seconds()
            self.myagent.request_exec_info.update({'EndTime': end_time, 'Duration': duration})

        except Exception as e:
            _logger.error("An exception occurred during an CSS-related request!")
            _logger.error(e)
            # The information about the error is added in the dictionary for the HTML result page
            self.myagent.request_exec_info['InteractionsDict'].append(
                {'type': 'exception', 'title': 'An error ocurred during the CSS-related request.', 'message': str(e)})


    @staticmethod
    def create_acl_msg(receiver_jid, thread, metadata, body_json):
        """
        This method creates an FIPA-ACL SPADE message.

        Args:
            receiver_jid (str): the JID of the SMIA agent receiver.
            thread (str): thread of the message.
            metadata: metadata of the message.
            body_json (dict): the body of the message in JSON format.

        Returns:
            spade.message.Message: the SPADE message object.
        """
        msg = Message(to=receiver_jid, thread=thread)
        msg.metadata = metadata
        msg.body = json.dumps(body_json)
        return msg