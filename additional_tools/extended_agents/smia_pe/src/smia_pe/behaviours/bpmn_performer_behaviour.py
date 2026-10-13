import asyncio
import logging

from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.specs.defaults import ServiceTask

from smia import CriticalError, GeneralUtils
from smia.logic import inter_smia_interactions_utils, acl_smia_messages_utils
from smia.utilities.aas_related_services_info import AASRelatedServicesInfo
from smia.utilities.fipa_acl_info import FIPAACLInfo, ACLSMIAOntologyInfo, ACLSMIAJSONSchemas
from spade.behaviour import CyclicBehaviour

from smia_pe.utilities.smia_bpmn_info import SMIABPMNInfo
from smia_pe.utilities.smia_bpmn_utils import SMIABPMNUtils
from smia_pe.utilities.smia_pe_aas_model_utils import SMIAPEModelUtils

_logger = logging.getLogger(__name__)

class BPMNPerformerBehaviour(CyclicBehaviour):
# class BPMNPerformerBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour that handles the execution of a CSS-driven BPMN flexible production plan.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        # The object to store the content of the associated BPMN file
        self.bpmn_file_bytes = None

        # This event object will allow waiting for the response of an ACL request message from SMIA PE to other SMIA
        # instances (when requesting data, requesting capabilities execution...). Since this behaviour is OneShot, when
        # it needs to wait for a response it will be blocked with this object. When the ACL response arrived, the
        # ReceiveACLBehaviour will unlock this behaviour, offering the response message content
        self.acl_request_event = asyncio.Event()
        # This object will be used to obtain the response message content. When the ReceiveACLBehaviour receives a
        # message, it will add the content with the thread of the message {'threadValue': 'ACLcontent'}
        self.acl_messages_responses = {}

        # Process configuration defined in BPMN
        self.bpmn_config_initialized = False
        self.myagent.workflow_repeat = SMIABPMNInfo.DEFAULT_WORKFLOW_REPEAT
        self.myagent.negotiation_criterion = SMIABPMNInfo.DEFAULT_NEGOTIATION_CRITERION

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("BPMNPerformerBehaviour starting...")

        self.bpmn_start_time = GeneralUtils.get_current_timer_nanosecs()

        # The variable for execution information about the SMIA PE is initialized
        self.myagent.smia_pe_info = {'Status': 'Starting', 'StartTime': GeneralUtils.get_current_date_time(),
                                     'ISMInteractions': 0, 'Interactions': 0, 'ReceivedACLmsg': 0,
                                     'InteractionsDict': []}

        # The BPMN file content is obtained in bytes
        _logger.info("Obtaining the BPMN file content...")
        self.bpmn_file_bytes = SMIAPEModelUtils.get_bpmn_file_bytes_from_aas()
        if self.bpmn_file_bytes is None:
            CriticalError("BPMN file not found, so the SMIA PE cannot start.")
        _logger.info("The BPMN file content for this SMIA PE obtained and stored.")

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'analysis', 'title':
            'Obtaining BPMN file ...', 'message': 'The BPMN file has been obtained from the AAS model.'})

        _logger.info("SMIA PE will wait 15 seconds for other instances to complete their initializations..")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # This behavior analyzes and performs a BPMN production plan based on CSS. The behavior is OneShot so it will
        # perform the plan and terminate itself. When requests need to be made to other SMIA instances it will remain
        # blocked until the response for this message arrives. A complementary Cyclic behavior has been developed to
        # receive all messages and unblock this behavior to continue with the production plan.

        # If the workflow must not repeat, only the first Cyclic iteration executes it.
        # bpmn_config_initialized is set in the first iteration
        if self.bpmn_config_initialized and not self.myagent.workflow_repeat:
            _logger.info("WORKFLOW_REPEAT is False and the workflow has already been executed, "
                         "so further executions are skipped.")
            await asyncio.sleep(5)
            return

        # First, the BPMN parser is created, the SMIA namespace is added and the BPMN file content is loaded
        bpmn_parser = BpmnParser()
        bpmn_parser.namespaces['smia'] = SMIABPMNInfo.BPMN_SMIA_NAMESPACE
        bpmn_parser.add_bpmn_str(self.bpmn_file_bytes)

        # Let's get the parser of the process related to the production plan and all the values of the required
        # SMIA attributes
        process_parser = SMIABPMNUtils.get_process_parser(bpmn_parser)
        SMIABPMNUtils.add_smia_attributes_values(process_parser)
        self.process_parser = process_parser

        # The complete process parser is also saved in the agent object
        self.myagent.bpmn_process_parser = self.process_parser

        # The workflow-level configuration is resolved once at startup (env var predominates
        # over the smia: process attribute). Later Cyclic iterations must not overwrite GUI toggles.
        if not self.bpmn_config_initialized:
            self.myagent.bpmn_execution_status = SMIABPMNUtils.get_process_smia_config(
                process_parser, SMIABPMNInfo.PROCESS_WORKFLOW_AUTOSTART_ATTRIBUTE,
                SMIABPMNInfo.WORKFLOW_AUTOSTART_ENV_VAR,
                SMIABPMNInfo.DEFAULT_WORKFLOW_AUTOSTART, bool)
            self.myagent.workflow_repeat = SMIABPMNUtils.get_process_smia_config(
                process_parser, SMIABPMNInfo.PROCESS_WORKFLOW_REPEAT_ATTRIBUTE,
                SMIABPMNInfo.WORKFLOW_REPEAT_ENV_VAR,
                SMIABPMNInfo.DEFAULT_WORKFLOW_REPEAT, bool)
            self.myagent.negotiation_criterion = SMIABPMNUtils.get_process_smia_config(
                process_parser, SMIABPMNInfo.PROCESS_NEGOTIATION_CRITERION_ATTRIBUTE,
                SMIABPMNInfo.NEGOTIATION_CRITERION_ENV_VAR,
                SMIABPMNInfo.DEFAULT_NEGOTIATION_CRITERION, str)
            self.bpmn_config_initialized = True
            _logger.info(f"Workflow config resolved: autostart=[{self.myagent.bpmn_execution_status}], "
                         f"repeat=[{self.myagent.workflow_repeat}], negotiation_criterion="
                         f"[{self.myagent.negotiation_criterion}].")

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'analysis', 'title':
            'Obtaining SMIA attributes from BPMN file ...', 'message': 'All CSS-related information has been obtained '
                                                                       'from the SMIA-BPMN workflow..'})

        setattr(process_parser.get_spec().start.outputs[0], 'current_exec_elem', True)
        # To finalize the initialization of the BPMN file, the SMIA instances associated to the specified assets need
        # to be obtained
        await self.get_smia_instances_of_specified_assets()

        # When the BPMN file has been initialized, it can be started to execute
        await self.execute_workflow()


    async def get_smia_instances_of_specified_assets(self):
        """
        This method gets all the SMIA instances identifiers of the specified capabilities where the asset has been
        specified.
        """
        for spec_name, spec_instance in self.process_parser.get_spec().task_specs.items():
            if isinstance(spec_instance, ServiceTask):
                if spec_instance.smia_asset is not None:
                    # In this case the asset has been specified so it will need to request an AAS Infrastructure Service
                    # to get the SMIA identifier associated to this asset identifier
                    _logger.info("Obtaining the SMIA instance identifier for asset "
                                 "[{}].".format(spec_instance.smia_asset))
                    spec_instance.smia_instance = await self.get_smia_instance_id_by_asset_id(spec_instance.smia_asset)

    async def execute_workflow(self):
        """
        This method executes the BPMN workflow.
        """
        # Let's start from the beginning
        current_elem = self.process_parser.get_spec().start

        # The element is set as the current execution step
        setattr(current_elem, 'current_exec_elem', True)

        while current_elem is not None:
            # The element is set as the current execution step
            setattr(current_elem, 'current_exec_elem', True)

            # It will only continue executing the workflow if the global variable is set for that (the user can stop
            # the execution through the GUI)
            if self.myagent.bpmn_execution_status:
                # The BPMN element is performed and, when finished, the next one is obtained
                result = await self.execute_bpmn_element(current_elem)
                _logger.aclinfo('----------------------------RESULTADDDDDDOO: {}'.format(result))
                if result is not None and 'reason' in result:
                    # A FAILURE ACL response was received: execution is paused
                    _logger.warning("BPMN workflow aborted due to a received FAILURE ACL message on element "
                                  "[{}].".format(getattr(current_elem, 'bpmn_name', current_elem)))
                    self.myagent.bpmn_execution_status = False
                    continue
                elif getattr(current_elem, 'error_exec_elem', False):
                    # If the execution has completed and an error occurred earlier, it is updated
                    setattr(current_elem, 'error_exec_elem', False)
                current_elem = SMIABPMNUtils.get_next_bpmn_element(self.process_parser, current_elem)
            else:
                _logger.warning("BPMN execution is stopped via the GUI.")

                # A one-second wait will be added between the execution of each step
                await asyncio.sleep(1)

        # When it is arrived to an EndEvent the current_elem is None, so the BPMN is finished
        _logger.assetinfo("BPMN workflow completed successfully.")
        self.myagent.bpmn_info['CompletedWorkflows'] += 1
        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append(
            {'type': 'analysis', 'title': 'SMIA workflow successfully completed',
             'message': 'All the steps of the SMIA-BPMN workflow have been performed.'})


    async def execute_bpmn_element(self, current_bpmn_elem):
        """
        This method executes a specific element of the BPMN workflow.

        Args:
            current_bpmn_elem: BPMN element object.
        """
        # Before executing the BPMN element it is necessary to check if some additional tasks need to be done
        if isinstance(current_bpmn_elem, ServiceTask):
            # Only ServiceTasks can be executed by SMIA PE
            if len(current_bpmn_elem.smia_additional_tasks) > 0:
                await self.execute_additional_tasks_of_bpmn_element(current_bpmn_elem)
            _logger.assetinfo("Executing BPMN element {}".format(current_bpmn_elem.bpmn_name))
            _logger.assetinfo("-----------------> ")

            result = await self.execute_acl_rp_css_protocol(current_bpmn_elem)
            _logger.info("SMIACL request result: {}".format(result))
            return result
        return None

    async def execute_additional_tasks_of_bpmn_element(self, bpmn_element):
        """
        This method executes the additional tasks related to a specific element of the BPMN workflow.

        Args:
            bpmn_element: BPMN element object.
        """
        for task in bpmn_element.smia_additional_tasks:
            if task == SMIABPMNInfo.TASK_REQUEST_DISTRIBUTED_CNP:
                if (hasattr(bpmn_element, 'smia_asset') and bpmn_element.smia_asset is not None and
                        hasattr(bpmn_element, 'smia_instance') and bpmn_element.smia_instance is not None):
                    # In this case the CNP protocol has been performed in a previous step due to a request of a data for
                    # this instance
                    pass
                else:
                    _logger.assetinfo("The capability {} has no asset identifier specified, so it will be obtained through "
                                 "the CNP protocol.".format(bpmn_element.smia_capability))
                    smia_instance_candidates = await self.get_smia_instances_id_by_capability(bpmn_element.smia_capability)
                    bpmn_element.smia_instance = await self.execute_acl_cnp_protocol(smia_instance_candidates, bpmn_element)
                    # With the winner SMIA instance, it can be obtained the associated asset ID
                    bpmn_element.smia_asset = await self.get_asset_id_by_smia_instance_id(bpmn_element.smia_instance)

            if task == SMIABPMNInfo.TASK_REQUEST_DATA_TO_PREVIOUS:
                for previous_request in bpmn_element.smia_request_to_previous:
                    previous_element = SMIABPMNUtils.get_previous_bpmn_element(self.process_parser, bpmn_element)
                    _logger.assetinfo("A data need to be requested to the SMIA instance {}".format(previous_element.smia_instance))
                    required_data_ref = SMIABPMNUtils.get_required_data_from_bpmn_element(bpmn_element,
                                                                                          previous_request)
                    required_data_value = await self.execute_acl_qp_aas_protocol(previous_element.smia_instance,
                                                                                 AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_VALUE_BY_REF,
                                                                                 required_data_ref)
                    # When the data is obtained, it needs to be added to the BPMN element
                    SMIABPMNUtils.update_bpmn_element_with_requested_data(bpmn_element, previous_request,
                                                                          required_data_value)
            if task == SMIABPMNInfo.TASK_REQUEST_DATA_TO_FOLLOWING:
                for following_request in bpmn_element.smia_request_to_following:
                    following_element = SMIABPMNUtils.get_next_bpmn_element(self.process_parser, bpmn_element)
                    if following_element.smia_asset is None:
                        # It cannot request to the following element because it needs to perform a distributed CNP
                        # protocol to obtain the asset and SMIA identifiers
                        smia_instance_candidates = await self.get_smia_instances_id_by_capability(
                            following_element.smia_capability)
                        following_element.smia_instance = await self.execute_acl_cnp_protocol(smia_instance_candidates,
                                                                                         following_element)
                        # With the winner SMIA instance, it can be obtained the associated asset ID
                        following_element.smia_asset = await self.get_asset_id_by_smia_instance_id(
                            following_element.smia_instance)

                    # Now the following element is specified, so the data can be requested
                    _logger.assetinfo("The data {} need to be requested to the SMIA instance {} related to the following task "
                                 "within the BPMN workflow.".format(following_request, following_element.smia_instance))
                    required_data_ref = SMIABPMNUtils.get_required_data_from_bpmn_element(bpmn_element, following_request)
                    required_data_value = await self.execute_acl_qp_aas_protocol(following_element.smia_instance,
                        AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_VALUE_BY_REF, required_data_ref)
                    # When the data is obtained, it needs to be added to the BPMN element
                    SMIABPMNUtils.update_bpmn_element_with_requested_data(bpmn_element, following_request,
                                                                          required_data_value)

            if task == SMIABPMNInfo.TASK_REQUEST_DATA_TO_TASK:
                for task_request in bpmn_element.smia_request_to_task_by_id:
                    task_element = SMIABPMNUtils.get_bpmn_element_by_id(self.process_parser, task_request['taskID'])
                    if task_element.smia_asset is None:
                        # It cannot request to the following element because it needs to perform a distributed CNP
                        # protocol to obtain the asset and SMIA identifiers
                        smia_instance_candidates = await self.get_smia_instances_id_by_capability(
                            task_element.smia_capability)
                        task_element.smia_instance = await self.execute_acl_cnp_protocol(smia_instance_candidates,
                                                                                         task_element)
                        # With the winner SMIA instance, it can be obtained the associated asset ID
                        task_element.smia_asset = await self.get_asset_id_by_smia_instance_id(
                            task_element.smia_instance)

                    # Now the following element is specified, so the data can be requested
                    _logger.assetinfo("The data {} need to be requested to the SMIA instance {} related to the task "
                                 "within the BPMN workflow.".format(task_request, task_element.smia_instance))
                    required_data_ref = SMIABPMNUtils.get_required_data_from_bpmn_element(bpmn_element, task_request)
                    required_data_value = await self.execute_acl_qp_aas_protocol(task_element.smia_instance,
                        AASRelatedServicesInfo.AAS_DISCOVERY_SERVICE_GET_SM_VALUE_BY_REF, required_data_ref)
                    # When the data is obtained, it needs to be added to the BPMN element
                    SMIABPMNUtils.update_bpmn_element_with_requested_data(bpmn_element, task_request,
                                                                          required_data_value)

            if task == SMIABPMNInfo.TASK_CHECK_TIMEOUT:
                # At this point it is set as False. During the execution of the BPMN element will be set a True if the
                # timeout is reached
                bpmn_element.smia_timeout_reached = False

    # Methods related to interactions with other SMIA instances
    # ---------------------------------------------------------
    async def send_acl_and_wait(self, acl_msg):
        """
        This method sends an ACL message and waits to the response.

        Args:
            acl_msg (spade.message.Message): the SPADE message object to be sent.
        """
        await self.send(acl_msg)
        # To warn that it is waiting for a value for a given thread, the thread will be added to the response object
        # with a null value
        self.acl_messages_responses[acl_msg.thread] = None
        # Now the behaviour will wait until the response message arrive to the Receiver Behaviour and unlocks the Event
        await self.acl_request_event.wait()
        # If the behaviour continues from this line, it means that the response has arrived, so the Event is cleared
        self.acl_request_event.clear()
        # The response content will be available in the 'acl_messages_responses' of the behaviour
        return self.acl_messages_responses[acl_msg.thread]

    async def create_acl_message_to_smia_ism(self, msg_body):
        """
        This method creates an ACL message to request an AAS Infrastructure Service to the SMIA ISM.

        Args:
            msg_body: body of the ACL message.

        Returns:
            spade.message.Message: SPADE-ACL-SMIA message object
        """
        return await inter_smia_interactions_utils.create_acl_smia_message(
            f"{AASRelatedServicesInfo.SMIA_ISM_ID}@"
            f"{await acl_smia_messages_utils.get_xmpp_server_from_jid(self.myagent.jid)}",
            await acl_smia_messages_utils.create_random_thread(self.myagent), FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST,
            ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE, protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL,
            msg_body=msg_body)

    async def get_smia_instance_id_by_asset_id(self, asset_id):
        """
        This method gets the SMIA instance identifier associated to a given asset ID.

        Args:
            asset_id (str): identifier of the asset

        Returns:
            str: identifier of the associated SMIA instance.
        """
        # In order to obtain the data, an AAS Infrastructure Service need to be requested to SMIA ISM
        request_acl_msg = await self.create_acl_message_to_smia_ism(await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
            serviceID='GetSMIAInstanceIDByAssetID', serviceType='DiscoveryService', serviceParams=asset_id))
        _logger.aclinfo("FIPA-RP with an AAS Infrastructure Service initiated with SMIA ISM to obtain the SMIA instance"
                        " identifier for asset {}".format(asset_id))

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Obtaining SMIA instance associated to a specific asset ...', 'message': 'The FIPA-RP protocol has been '
            'performed to SMIA ISM to obtain the SMIA instance for the asset {}'.format(asset_id)})
        self.myagent.smia_pe_info['ISMInteractions'] += 1

        await self.send_acl_and_wait(request_acl_msg)

        # When the data has been received, it will be obtained from the global dictionary and will be returned
        return acl_smia_messages_utils.get_parsed_body_from_acl_msg(self.acl_messages_responses[request_acl_msg.thread])

    async def get_asset_id_by_smia_instance_id(self, smia_instance_id):
        """
        This method gets the asset identifier associated to a given SMIA instance.

        Args:
            smia_instance_id (str): identifier of the SMIA instance

        Returns:
            str: identifier of the associated asset.
        """
        # In order to obtain the data, an AAS Infrastructure Service need to be requested to SMIA ISM
        request_acl_msg = await self.create_acl_message_to_smia_ism(await acl_smia_messages_utils.
                                                                    generate_json_from_schema(
            ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
            serviceID='GetAssetIDBySMIAInstanceID', serviceType='DiscoveryService', serviceParams=smia_instance_id))
        _logger.aclinfo("FIPA-RP with an AAS Infrastructure Service initiated with SMIA ISM to obtain the asset "
                        "identifier for the SMIA instance {}".format(smia_instance_id))

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Obtaining asset identifier associated to a specific SMIA instance ...', 'message':
            'The FIPA-RP protocol has been performed to SMIA ISM to obtain the asset identifier for the SMIA instance '
            '{}'.format(smia_instance_id)})
        self.myagent.smia_pe_info['ISMInteractions'] += 1

        await self.send_acl_and_wait(request_acl_msg)
        # When the data has been received, it will be obtained from the global dictionary and will be returned
        return acl_smia_messages_utils.get_parsed_body_from_acl_msg(self.acl_messages_responses[request_acl_msg.thread])

    async def get_smia_instances_id_by_capability(self, capability_iri):
        """
        This method gets the SMIA instances identifiers that have associated a given capability.

        Args:
            capability_iri (str): identifier of the capability (IRI).

        Returns:
            list: identifiers of the associated SMIA instances.
        """
        # First, it will obtain all the asset identifiers associated to the given capability
        request_assets_acl_msg = await self.create_acl_message_to_smia_ism(await acl_smia_messages_utils.
            generate_json_from_schema(ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
            serviceID=AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_ALL_ASSET_BY_CAPABILITY,
            serviceType=AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY, serviceParams=capability_iri))
        _logger.aclinfo("FIPA-RP with an AAS Infrastructure Service initiated with SMIA ISM to obtain the all the "
                        "assets associated to the capability {}".format(capability_iri))

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Obtaining assets associated to a specific capability ...', 'message': 'The FIPA-RP protocol has been '
            'performed to SMIA ISM to obtain the assets identifiers associated to the capability with IRI {}'.format(
            capability_iri)})
        self.myagent.smia_pe_info['ISMInteractions'] += 1

        await self.send_acl_and_wait(request_assets_acl_msg)
        # When the assets have been received, it will be obtained from the global dictionary
        assets_id_list = acl_smia_messages_utils.get_parsed_body_from_acl_msg(
            self.acl_messages_responses[request_assets_acl_msg.thread])
        # For each asset, its associated SMIA instance ID will be obtained. It may have already been obtained, so check
        # whether the BPMN instances already have the value
        smia_instances_id_list = []
        for asset_id in assets_id_list:
            smia_instance_id = SMIABPMNUtils.get_bpmn_element_smia_instance_by_asset_id(self.process_parser, asset_id)
            if smia_instance_id is None:
                # In this case it must be requested to the SMIA ISM, in order to obtain from the SMIA KB
                request_smia_id_acl_msg = await self.create_acl_message_to_smia_ism(
                    {'serviceID': AASRelatedServicesInfo.AAS_INFRASTRUCTURE_DISCOVERY_SERVICE_GET_SMIA_BY_ASSET,
                     'serviceType': AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY,
                     'serviceParams': asset_id})

                # The information to be displayed in the GUI is also added
                self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
                    'Obtaining SMIA instance associated to a specific asset ...', 'message':
                    'The FIPA-RP protocol has been performed to SMIA ISM to obtain the SMIA instance associated to the '
                    'asset {}'.format(asset_id)})
                self.myagent.smia_pe_info['ISMInteractions'] += 1

                await self.send_acl_and_wait(request_smia_id_acl_msg)
                # When the data have been received it is added to the list
                smia_instance_id = acl_smia_messages_utils.get_parsed_body_from_acl_msg(
                    self.acl_messages_responses[request_smia_id_acl_msg.thread])
            smia_instances_id_list.append(smia_instance_id)
        return smia_instances_id_list


    async def execute_acl_qp_aas_protocol(self, smia_instance_id, aas_service_id, requested_aas_ref):
        """
        This method executes the FIPA-ACL QP interaction protocol (Query Protocol), to query an AAS element to a given
        SMIA instance.

        Args:
            smia_instance_id (str): identifier of SMIA instance to be the requested.
            aas_service_id (str): identifier of AAS service to be the requested.
            requested_aas_ref (str): reference of the AAS element to be queried.

        Returns:
            object: returns the queried AAS element content.
        """

        query_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            smia_instance_id, await acl_smia_messages_utils.create_random_thread(self.myagent),
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_QUERY_REF, ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_SERVICE,
            protocol=FIPAACLInfo.FIPA_ACL_QUERY_PROTOCOL, msg_body=await acl_smia_messages_utils.generate_json_from_schema(
                ACLSMIAJSONSchemas.JSON_SCHEMA_AAS_SERVICE,
                serviceID=aas_service_id, serviceType=AASRelatedServicesInfo.AAS_SERVICE_TYPE_DISCOVERY,
                serviceParams=requested_aas_ref))
        _logger.aclinfo("FIPA-QP initiated with {} to obtain the AAS element {}".format(smia_instance_id, requested_aas_ref))

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Obtaining AAS information through FIPA-QP protocol ...', 'message': 'The FIPA-QP protocol has been '
            'performed to obtain the AAS information with reference {}'.format(requested_aas_ref)})
        self.myagent.smia_pe_info['Interactions'] += 1

        await self.send_acl_and_wait(query_acl_msg)
        # When the data has been received, it will be obtained from the global dictionary and will be returned
        return acl_smia_messages_utils.get_parsed_body_from_acl_msg(self.acl_messages_responses[query_acl_msg.thread])

    async def execute_acl_cnp_protocol(self, smia_instance_ids, bpmn_element):
        """
        This method executes the FIPA-ACL CNP interaction protocol (Contract Net Protocol), to obtain the best option among several.

        Args:
            smia_instance_ids (list): list with all the identifiers of SMIA instances to be the participants of the protocol.
            bpmn_element: BPMN element.

        Returns:
            str, str: returns the asset identifier and the SMIA instance identifier of the best option.
        """

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Performing FIPA-CNP protocol ...', 'message':
            'The FIPA-CNP protocol has been performed to obtain the best SMIA instance between {} to realize the '
            'capability with IRI {}'.format(smia_instance_ids, bpmn_element.smia_capability)})

        # The FIPA-CNP message will be sent with CFP performative and same thread for all receivers
        # The negotiation criterion is a workflow-level config (env > BPMN > default), resolved once at startup
        neg_criterion = getattr(self.myagent, 'negotiation_criterion',
                                SMIABPMNInfo.DEFAULT_NEGOTIATION_CRITERION)
        cfp_thread = await acl_smia_messages_utils.create_random_thread(self.myagent)
        for smia_instance_id in smia_instance_ids:
            cfp_acl_message = await inter_smia_interactions_utils.create_acl_smia_message(
                smia_instance_id, cfp_thread, FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP,
                ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE, protocol=FIPAACLInfo.FIPA_ACL_CONTRACT_NET_PROTOCOL,
                msg_body=await acl_smia_messages_utils.generate_json_from_schema(
                    ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE, capabilityIRI=bpmn_element.smia_capability,
                    skillIRI=bpmn_element.smia_skill, constraints=bpmn_element.smia_constraints,
                    skillParams=bpmn_element.smia_skill_parameters,
                    negCriterion=neg_criterion,
                    negRequester=str(self.myagent.jid), negTargets=smia_instance_ids))
            await self.send(cfp_acl_message)

            self.myagent.smia_pe_info['Interactions'] += 1

        _logger.aclinfo("FIPA-CNP initiated with SMIA candidates {} to perform capability {}".format(
            smia_instance_ids, bpmn_element.smia_capability))
        # When all messages have been sent, it will wait to the winner response
        self.acl_messages_responses[cfp_thread] = None
        await self.acl_request_event.wait()
        self.acl_request_event.clear()

        # In this case, the sender of the message is the winner, so it will return its identifier
        return acl_smia_messages_utils.get_sender_from_acl_msg(self.acl_messages_responses[cfp_thread])


    async def execute_acl_rp_css_protocol(self, bpmn_element):
        """
        This method executes the FIPA-ACL RP interaction protocol (Request Protocol), to request the execution of
        an CSS-based capability.

        Args:
            bpmn_element: BPMN element.

        Returns:
            object: returns the response content.
        """
        request_css_acl_msg = await inter_smia_interactions_utils.create_acl_smia_message(
            bpmn_element.smia_instance, await acl_smia_messages_utils.create_random_thread(self.myagent),
            FIPAACLInfo.FIPA_ACL_PERFORMATIVE_REQUEST, ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE,
            protocol=FIPAACLInfo.FIPA_ACL_REQUEST_PROTOCOL, msg_body=await acl_smia_messages_utils.generate_json_from_schema(
                ACLSMIAJSONSchemas.JSON_SCHEMA_CSS_SERVICE, capabilityIRI=bpmn_element.smia_capability,
                skillIRI=bpmn_element.smia_skill, constraints=bpmn_element.smia_constraints,
                skillParams=bpmn_element.smia_skill_parameters))
        _logger.aclinfo("FIPA-RP initiated to request CSS execution: SMIA [{}] -> capability "
                     "[{}]".format(bpmn_element.smia_instance, bpmn_element.smia_capability))
        if SMIABPMNInfo.TASK_CHECK_TIMEOUT in bpmn_element.smia_additional_tasks:

            # The information to be displayed in the GUI is also added
            self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'analysis', 'title':
                'A CSS-related execution need timeout checking ...', 'message': 'A timeout of {} seconds will be checked'
                ' for execution of the capability with IRI {} on the SMIA instance {}'.format(
                bpmn_element.timeout_value, bpmn_element.smia_capability, bpmn_element.smia_instance)})

            # In this case, the method for managing the timeout need to be performed in parallel to the CSS request
            asyncio.create_task(SMIABPMNUtils.perform_bpmn_timeout_check(self.myagent, request_css_acl_msg.thread,
                                                                         bpmn_element.timeout_value))

        # The information to be displayed in the GUI is also added
        self.myagent.smia_pe_info['InteractionsDict'].append({'type': 'acl_send', 'title':
            'Requesting a CSS-related execution through FIPA-RP protocol ...', 'message': 'The FIPA-QP protocol has been '
            'performed to request the execution of the capability with IRI {} to the SMIA instance {}'.format(
            bpmn_element.smia_capability, bpmn_element.smia_instance)})
        self.myagent.smia_pe_info['Interactions'] += 1

        await self.send_acl_and_wait(request_css_acl_msg)

        # It will be checked whether the timeout has been reached
        if (isinstance(self.acl_messages_responses[request_css_acl_msg.thread], str) and
                self.acl_messages_responses[request_css_acl_msg.thread] == 'ERROR: TIMEOUT REACHED'):
            bpmn_element.smia_timeout_reached = True
            return
        # When the data has been received, it will be obtained from the global dictionary and will be returned
        return acl_smia_messages_utils.get_parsed_body_from_acl_msg(
            self.acl_messages_responses[request_css_acl_msg.thread])
