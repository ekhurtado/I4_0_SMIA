import logging
import ntpath
import os

from SpiffWorkflow.bpmn.specs.defaults import EndEvent, ExclusiveGateway
from SpiffWorkflow.bpmn.specs.defaults import ServiceTask
from SpiffWorkflow.specs import StartTask
from aiohttp import web

from smia_pe.utilities.smia_bpmn_utils import SMIABPMNUtils

_logger = logging.getLogger(__name__)




class GUIControllers:
    """This class contains all the controller to be added to SMIA in order to manage the operator actions."""

    def __init__(self, agent_object):
        self.myagent = agent_object


    @staticmethod
    async def hello_controller(request):
        """
        Generic controller during the request of SMIA GUI webpages via HTTP GET call.
        """
        return {"status": "OK"}

    async def smia_pe_gui_get_controller(self, request):
        """
        The controller during the request of SMIA PE Dashboard.
        """
        # The BPMN process parser is analyzed, in order to extract useful information
        GUIFeatures.analyze_bpmn_workflow(self.myagent)
        return {"status": "success"}

    async def smia_pe_gui_bpmn_dot_controller(self, request):
        """
        The controller during the request of SMIA PE Dashboard.
        """
        # The BPMN process parser is analyzed, in order to extract useful information
        return GUIFeatures.to_graphviz(self.myagent)
        # return web.Response(text=GUIFeatures.to_graphviz(self.myagent), content_type="text/plain")

    async def smia_pe_gui_post_controller(self, request):
        """
        The controller during the request of SMIA PE Dashboard.
        """
        data = await request.json()
        bpmn_execution_change = data.get('BPMNExecutionChange', None)   # None if it is missing
        workflow_repeat_change = data.get('WorkflowRepeatChange', None)   # None if it is missing

        if bpmn_execution_change is not None:
            if bpmn_execution_change == 'Continue':
                self.myagent.bpmn_execution_status = True
            if bpmn_execution_change == 'Stop':
                self.myagent.bpmn_execution_status = False

        if workflow_repeat_change is not None:
            # The repeat toggle only applies to the next workflow cycle
            if workflow_repeat_change == 'Enable':
                self.myagent.workflow_repeat = True
            if workflow_repeat_change == 'Disable':
                self.myagent.workflow_repeat = False

        # TODO Think more buttons for SMIA PE
        return {'status': 'success'}
        # return web.json_response({'status': 'success'})
        # return {"status": "success", "reason": "success reason"}

class GUIFeatures:
    """This class contains the methods related to SPADE web interface customization."""
    # FAVICON_PATH = './htmls/static/SMIA_favicon.ico' # TODO BORRAR
    FAVICON_PATH = '/htmls/static/SMIA_favicon.ico'

    @staticmethod
    async def add_new_menu_entry(agent, entry_name, entry_url, entry_icon):
        """
        This method adds a new entry to the SPADE web interface menu.

        Args:
            agent (smia.agents.smia_agent.SMIAAgent): SMIA SPADE agent object.
            entry_name (str): name of the new entry.
            entry_url (str): url to access the new entry.
            entry_icon (str): icon identifier from Font Awesome collection.
        """
        # The menu entry is added with the SPADE web module
        agent.web.add_menu_entry(entry_name, entry_url, entry_icon)

        # Then, the information is added to the attribute with the dictionary in the agent, so that it is accessible
        # to HTML templates.
        agent.web_menu_entries[entry_name] = {"url": entry_url, "icon": entry_icon}

    @staticmethod
    async def handle_favicon(request):
        """
        This method represents the controller that will handle the requests when the Favicon is requested.

        Args:
            request: request object to get the favicon file.

        Returns:
            web.FileResponse: response to the web browser.
        """
        # favicon_path = os.path.join(GUIFeatures.FAVICON_PATH)
        return web.FileResponse(GUIFeatures.FAVICON_PATH)

    @staticmethod
    async def add_custom_favicon(agent):
        """
        This method adds a custom Favicon to the SMIA GUI.

        Args:
            agent (spade.agent.Agent): SMIA SPADE agent object.
        """
        # The favicon is accessed with an HTTP request to a specific URL, and needs a controller
        agent.web.app.router.add_get('/favicon.ico', GUIFeatures.handle_favicon)
        # The static folder also need to be added to static files view.
        favicon_folder_path = ntpath.split(GUIFeatures.FAVICON_PATH)[0]
        agent.web.app.router.add_static('/static/', path=favicon_folder_path)

    @staticmethod
    def build_avatar_url(jid: str) -> str:
        """
        This method overrides the original SPADE method to use the Favicon as the avatar in SMIA SPADE web interface.
        """
        return '/favicon.ico'

    @staticmethod
    def to_graphviz(agent_object):
        if agent_object.bpmn_graphviz_info == "digraph SMIA_PE_workflow { rankdir=LR; node [fixedsize=true];}":
            graph = ("digraph SMIA_PE_workflow { node [shape=rectangle, fontsize=12, fontname=Helvetica]; "
                     "ranksep=0.75; nodesep=0.5;")
            additional_graph = ""
            if hasattr(agent_object, 'bpmn_process_parser'):
                # Let's also update the process parser elements
                agent_object.bpmn_workflow_elements = []

                process_parser = agent_object.bpmn_process_parser
                # Hacer una lista para ir analizando todos los que se vayan detectando (añadir todos los outputs), ya que da igual que se repitan (o se puede hacer otra lista para los analizados)
                elems_to_analyze = [process_parser.get_spec().start]
                analyzed_elems = []
                while len(elems_to_analyze) > 0:
                    current_elem = elems_to_analyze.pop()
                    if current_elem not in analyzed_elems:
                        if isinstance(current_elem, StartTask):
                            for out_elem in current_elem.outputs: elems_to_analyze.append(out_elem)
                            continue
                        if isinstance(current_elem, EndEvent):
                            current_elem.outputs = []

                        origin = current_elem.bpmn_id
                        origin = origin.replace(" ", "_")
                        if isinstance(current_elem, ExclusiveGateway):
                            for condition, elem_id in current_elem.cond_task_specs:
                                dest = ''
                                if condition.args[0].lower() in ('yes', 'true', 't', '1'):
                                    dest = elem_id.replace(" ", "_") + ' [label=yes]'
                                elif condition.args[0].lower() in ('no', 'false', 'f', '0'):
                                    dest = elem_id.replace(" ", "_") + ' [label=no]'
                                graph += "{0} -> {1};".format(origin, dest)
                        else:
                            for output_elem in current_elem.outputs:
                                dest = output_elem.bpmn_id
                                dest = dest.replace(" ", "_")
                                graph += "{0} -> {1};".format(origin, dest)

                        # The options for each element are also added
                        additional_graph_options = ''
                        if (SMIABPMNUtils.get_bpmn_display_name(current_elem) == 'Start' or
                                isinstance(current_elem, EndEvent)):
                            additional_graph_options += 'label={}, shape=ellipse'.format(
                                SMIABPMNUtils.get_bpmn_display_name(current_elem).replace(" ", "_"))

                        elif isinstance(current_elem, ExclusiveGateway):
                            additional_graph_options += 'label={}, shape=diamond'.format(
                                SMIABPMNUtils.get_bpmn_display_name(current_elem).replace(" ", "_"))
                            # The outputs of the exclusive are added at the same level
                            additional_graph += ('{ rank=same; ' + '; '.join(out.bpmn_id for out in current_elem.outputs)
                                                 + '; }')
                        else:
                            additional_graph_options += 'label={}'.format(SMIABPMNUtils.
                                                                  get_bpmn_display_name(current_elem).replace(" ", "_"))

                            agent_object.bpmn_workflow_elements.append(current_elem)

                        if getattr(current_elem, 'error_exec_elem', False):
                            additional_graph_options += ', style=filled, fillcolor=gold'
                        elif hasattr(current_elem, 'current_exec_elem') and current_elem.current_exec_elem:
                            additional_graph_options += ', style=filled, fillcolor=green'

                        additional_graph += '{} [{}]; '.format(origin, additional_graph_options)
                        for out_elem in current_elem.outputs: elems_to_analyze.append(out_elem)
                        analyzed_elems.append(current_elem)

                        # if isinstance(current_elem, EndEvent):
                        #     break

                graph += additional_graph
                graph += "}"
                return graph
        else:
            return agent_object.bpmn_graphviz_info

    @staticmethod
    def analyze_bpmn_workflow(agent_object):
        """
        This method analyzed the BPMN workflow and extracts all the information,
        """

        if not hasattr(agent_object, 'bpmn_process_parser'):
            # In this case the BPMN behaviour has not yet started
            return
        process_parser = agent_object.bpmn_process_parser
        if agent_object.bpmn_info['ServiceTasks'] != 0:
            # In this case it has been already analyzed
            # TODO PENSAR SI AQUI BUSCAR QUE SE ESTA EJECUTANDO
            return
        current_elem = process_parser.get_spec().start
        while current_elem is not None:
            # The BPMN element is performed and, when finished, the next one is obtained
            GUIFeatures.analyze_bpmn_element(agent_object, current_elem)
            if isinstance(current_elem, EndEvent):
                current_elem = None
                break
            current_elem = current_elem.outputs[0]  # TODO CUIDADO, HAY QUE CAMBIARLO YA QUE EL EXCLUSIVE TIENE DOS

        # When it is arrived to an EndEvent the current_elem is None, so the BPMN can finish
        _logger.info("BPMN workflow analyzed successfully for HTML GUI.")

    @staticmethod
    def analyze_bpmn_element(agent_object, bpmn_element):
        if isinstance(bpmn_element, ServiceTask):
            agent_object.bpmn_info['ServiceTasks'] += 1
            if bpmn_element.smia_capability is not None:
                agent_object.bpmn_info['Capabilities'] += 1
            if bpmn_element.smia_skill is not None:
                agent_object.bpmn_info['Skills'] += 1
            if bpmn_element.smia_asset is not None:
                agent_object.bpmn_info['Assets'] += 1

        if isinstance(bpmn_element, ExclusiveGateway):
            agent_object.bpmn_info['ExclusiveGateways'] += 1

