import asyncio
import logging
import ntpath
import os
from collections import OrderedDict

import basyx
from aiohttp import web
from basyx.aas import model
from basyx.aas.adapter import aasx
from smia.aas_model.aas_model_utils import AASModelInfo

from smia.behaviours.init_aas_model_behaviour import InitAASModelBehaviour

from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo, CapabilitySkillOntologyUtils

from smia import SMIAGeneralInfo
from spade.behaviour import OneShotBehaviour

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

        # The data to build operator HTML webpage is also initialized
        self.agent.loaded_statistics = {'AASmodels': 0, 'AvailableSMIAs': 0,
                                          'Capabilities': 0, 'Skills': 0}

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
        self.agent.web.add_post('/smia_operator/submit', self.operator_gui_controllers.operator_request_controller,
                                '/htmls/smia_operator_submit.html')

        # The new webpages need also to be added in the manu of the web interface
        # await GUIFeatures.add_new_menu_entry(self.agent,'System view', '/system_view', 'fa fa-eye')
        self.agent.web.add_menu_entry("SMIA operator", "/smia_operator", "fa fa-user-cog")

        _logger.info("Added new web pages to the web interface.")

        # TODO se ha añadido el Sen ACL del GUIAgent para realizar la prueba, hay que desarrollar los HTMLs para el
        #  operario y añadirlos

        # Once all the configuration is done, the web interface is enabled in the SMIA SPADE agent
        self.agent.web.start(hostname="0.0.0.0", port="10000")
        _logger.info("Started SMIA SPADE web interface.")



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

    async def operator_load_controller(self, request):

        # First, the dictionaries where the data will be stored are initialized
        self.myagent.loaded_smias = {}

        # All the available AASX need to be obtained
        _logger.info("Obtaining and analyzing all available SMIAs...")
        for file in os.scandir(SMIAGeneralInfo.CONFIGURATION_AAS_FOLDER_PATH):
            if file.is_file():
                if file.name == SMIAGeneralInfo.CM_AAS_MODEL_FILENAME:
                    _logger.warning("This is the AASX of SMIA operator.")
                else:
                    _logger.info("Analyzing SMIA with AAS model: {}".format(file.name))
                    aas_object_store = await GUIFeatures.read_aasx_file_object_store(file.path)
                    smia_info_dict = await GUIFeatures.analyze_aas_model_store(self.myagent, aas_object_store)
                    self.myagent.loaded_smias[file.name] = smia_info_dict   # TODO pensar si almacenarlo por el JID de esos AASX

                    # For each AASX, the JID of the associated SMIA need to be obtained
                    smia_jid = await GUIFeatures.get_smia_jid_from_aas_store(self.myagent, aas_object_store)
                    self.myagent.loaded_smias[file.name]['SMIA_JID'] = smia_jid
                    _logger.info("Analyzed SMIA AAS model of {}".format(file.name))

        # Now, the obtained information is analyzed in order to obtain data to display in SMIA Operator HTML
        self.myagent.loaded_statistics = {'AASmodels': len(self.myagent.loaded_smias), 'AvailableSMIAs': 0,
                                          'Capabilities': 0, 'Skills': 0}
        analyzed_elems = {'Capabilities': [], 'Skills': []}
        for file_name, info_dict in self.myagent.loaded_smias.items():
            if info_dict['SMIA_JID'] is not None:
                self.myagent.loaded_statistics['AvailableSMIAs'] += 1
            for rel, aas_elems in info_dict.items():
                if rel != 'SMIA_JID' and CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI == rel.iri:
                    for capability, skills in aas_elems.items():
                        if capability.id_short not in analyzed_elems['Capabilities']:
                            analyzed_elems['Capabilities'].append(capability.id_short)
                            self.myagent.loaded_statistics['Capabilities'] += 1
                        for skill in skills:
                            if skill.id_short not in analyzed_elems['Skills']:
                                analyzed_elems['Skills'].append(skill.id_short)
                                self.myagent.loaded_statistics['Skills'] += 1

        return {"status": "success", "reason": "success reason"}
        # return {"status": "error", "reason": "error reason"}

    async def operator_request_controller(self, request):

        data = await request.post()

        # Extract arrays for each field
        smia_id_list = data.getall('smia_id[]', [])
        asset_id_list = data.getall('asset_id[]', [])
        selected = data.getall('checkbox[]', [])
        capability = data.get('capability', None)   # Default if missing
        constraint_name = data.get('constraint_name', None)
        constraint_value = data.get('constraint_value', None)
        skill = data.get('skill', None)

        # Group data by row index
        processed_data = []
        for idx, row_id in enumerate(smia_id_list):
            if row_id in selected:
                processed_data.append({
                    "smiaID": row_id,
                    "assetID": asset_id_list[idx],
                })
        print("Requested SMIAs: {}".format(processed_data))

        # TODO

        if len(processed_data) > 1:
            print("There are multiple SMIAs: negotiation is required")
        else:
            print("There is only one SMIA. Requesting [{}] capability...".format(capability))



        # return web.json_response({'status': 'OK'})
        return {'status': 'OK'}


class GUIFeatures:
    """This class contains the methods related to SPADE web interface customization."""
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
        favicon_path = os.path.join(GUIFeatures.FAVICON_PATH)
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
    async def read_aasx_file_object_store(aas_file_path):
        """
        This method reads the AAS model of a given file path according to the AASX serialization format.

        Args:
            aas_file_path (str): path to the AAS model file.

        Returns:
            basyx.aas.model.DictObjectStore:  object with all Python elements of the AAS model.
        """
        object_store = None
        aas_model_file = ntpath.split(aas_file_path)[1] or ntpath.basename(ntpath.split(aas_file_path)[0])
        aas_model_file_name, aas_model_file_extension = os.path.splitext(aas_model_file)
        try:
            # The AAS model is read depending on the serialization format (extension of the AAS model file)
            if aas_model_file_extension == '.aasx':
                with aasx.AASXReader(aas_file_path) as reader:
                    # Read all contained AAS objects and all referenced auxiliary files
                    object_store = model.DictObjectStore()
                    suppl_file_store = aasx.DictSupplementaryFileContainer()
                    reader.read_into(object_store=object_store,
                                     file_store=suppl_file_store)
            else:
                _logger.warning("The serialization format of the file {} is not valid.".format(aas_file_path))
        except ValueError as e:
            _logger.error("Failed to read AAS model: invalid file.")
            _logger.error(e)
        if object_store is None or len(object_store) == 0:
            _logger.error("The AAS model is not valid. It is not possible to read and obtain elements of the AAS "
                                "metamodel.")
        else:
            return object_store


    @staticmethod
    async def analyze_aas_model_store(agent_object, aas_model_store):
        """
        This method parses an AAS model store (BaSyx Python object for storing AAS models) to get information such as
        the CSS model.

        Args:
            agent_object (smia.agents.smia_agent.SMIAAgent): SMIA SPADE agent object.
            aas_model_store (basyx.aas.model.DictObjectStore): Python object with the AAS model.

        Returns:
            dict: information about the AAS.
        """

        # First, the AAS model store of SMIA operator is subtracted from it in order to be able to use the Extended AAS Model methods.
        operator_aas_model_store = await agent_object.aas_model.get_aas_model_object_store()
        await agent_object.aas_model.set_aas_model_object_store(aas_model_store)
        ontology_instances_dict = {}
        smia_info_dict = {}

        # First, the ontology instances are obtained
        for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
            try:
                sme_list = await agent_object.aas_model.get_submodel_elements_by_semantic_id(ontology_class_iri)
                for submodel_elem in sme_list:
                    await InitAASModelBehaviour.convert_sme_class_to_extended_by_iri(submodel_elem, ontology_class_iri)
                    ontology_instances_dict[ontology_class_iri] = sme_list
                    await asyncio.sleep(.05)  # Simulate some processing time
            except Exception as e:
                _logger.error("An exception occurred with the ontology class {}. Error: {}".format(ontology_class_iri, e))
        # Then, the ontology instances are related between each other
        for ontology_relationship_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS:
            try:
                rels_list = await agent_object.aas_model.get_submodel_elements_by_semantic_id(
                    ontology_relationship_iri, basyx.aas.model.RelationshipElement)
                rel_ontology_class = await agent_object.css_ontology.get_ontology_class_by_iri(ontology_relationship_iri)
                domain_aas_class, range_aas_class = CapabilitySkillOntologyUtils.get_aas_classes_from_object_property(
                    rel_ontology_class)
                smia_info_dict[rel_ontology_class] = {}     # Initialize the dictionary for each relationship
                for rel in rels_list:
                    domain_aas_elem, range_aas_elem = None, None
                    await asyncio.sleep(.05)
                    try:
                        domain_aas_elem, range_aas_elem = await agent_object.aas_model.get_elements_from_relationship(
                            rel, domain_aas_class, range_aas_class)
                        domain_aas_elem.get_semantic_id_of_css_ontology()
                        range_aas_elem.get_semantic_id_of_css_ontology()

                        # At this point the relationship is valid
                        if domain_aas_elem not in smia_info_dict[rel_ontology_class]:
                            smia_info_dict[rel_ontology_class][domain_aas_elem] = [range_aas_elem]
                        else:
                            smia_info_dict[rel_ontology_class][domain_aas_elem].append(range_aas_elem)
                    except Exception as e:
                        _logger.error("An exception occurred with the ontology relationship {} between [{},{}]. "
                                      "Error: {}".format(ontology_relationship_iri, domain_aas_elem,range_aas_elem, e))
            except Exception as e:
                _logger.error("An exception occurred with the ontology relationship {}. Error: {}".format(ontology_relationship_iri, e))

        # Lastly, the AAS model store of SMIA operator is set again
        await agent_object.aas_model.set_aas_model_object_store(operator_aas_model_store)

        return smia_info_dict

    @staticmethod
    async def get_smia_jid_from_aas_store(agent_object, aas_model_store):
        """
        This method gets the SMIA JID value from the AAS model store. The SMIA approach establishes that this information need to be added within the '' standardized submodel.

        Args:
            agent_object (smia.agents.smia_agent.SMIAAgent): SMIA SPADE agent object.
            aas_model_store (basyx.aas.model.DictObjectStore): Python object with the AAS model.

        Returns:
            JID: SMIA JID value.
        """
        # First, the AAS model store of SMIA operator is subtracted from it in order to be able to use the Extended AAS Model methods.
        operator_aas_model_store = await agent_object.aas_model.get_aas_model_object_store()
        # _logger.aclinfo("Store SMIA operator [{}]".format(await agent_object.aas_model.get_aas_model_object_store()))  # TODO BORRAR
        await agent_object.aas_model.set_aas_model_object_store(aas_model_store)
        software_nameplate_submodel = await agent_object.aas_model.get_submodel_by_semantic_id(
            AASModelInfo.SEMANTICID_SOFTWARE_NAMEPLATE_SUBMODEL)
        if not software_nameplate_submodel:
            _logger.warning("SoftwareNameplate submodel is not defined within AAS model. This SMIA cannot be loaded to SMIA operator.")
            await agent_object.aas_model.set_aas_model_object_store(operator_aas_model_store)
            return None
        # Checks if the instance name is defined (SMIA JID)
        for software_nameplate_instance in software_nameplate_submodel.submodel_element:
            aas_smia_instance_name = software_nameplate_instance.get_sm_element_by_semantic_id(
                AASModelInfo.SEMANTICID_SOFTWARE_NAMEPLATE_INSTANCE_NAME)
            if aas_smia_instance_name is not None:
                await agent_object.aas_model.set_aas_model_object_store(operator_aas_model_store)
                return aas_smia_instance_name
        _logger.warning("The SoftwareNameplate submodel is defined within the AAS model, but the instance name is not. "
                        "This SMIA cannot be loaded into the SMIA operator.")
        await agent_object.aas_model.set_aas_model_object_store(operator_aas_model_store)
        return None