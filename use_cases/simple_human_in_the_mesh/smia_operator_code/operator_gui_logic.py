import asyncio
import logging
import ntpath
import os
import random
import string

import basyx
from aiohttp import web
from basyx.aas import model
from basyx.aas.adapter import aasx

from smia import SMIAGeneralInfo, GeneralUtils
from smia.aas_model.aas_model_utils import AASModelInfo
from smia.behaviours.init_aas_model_behaviour import InitAASModelBehaviour
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyInfo, CapabilitySkillOntologyUtils

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

                    # For each AASX, the JID and assetID of the associated SMIA need to be obtained
                    smia_jid = await GUIFeatures.get_smia_jid_from_aas_store(self.myagent, aas_object_store)
                    self.myagent.loaded_smias[file.name]['SMIA_JID'] = smia_jid

                    asset_id = await GUIFeatures.get_asset_id_from_aas_store(aas_object_store)
                    self.myagent.loaded_smias[file.name]['AssetID'] = asset_id

                    _logger.info("Analyzed SMIA AAS model of {}".format(file.name))

        # Now, the obtained information is analyzed in order to obtain data to display in SMIA Operator HTML
        self.myagent.loaded_statistics = {'AASmodels': len(self.myagent.loaded_smias), 'AvailableSMIAs': 0,
                                          'Capabilities': 0, 'Skills': 0}
        analyzed_elems = {'Capabilities': [], 'Skills': []}
        css_elems_info = {}
        for file_name, info_dict in self.myagent.loaded_smias.items():
            if info_dict['SMIA_JID'] is not None:
                self.myagent.loaded_statistics['AvailableSMIAs'] += 1
            for rel, aas_elems in info_dict.items():
                if not isinstance(rel, str):
                    if CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI == rel.iri:
                        for capability, skills in aas_elems.items():
                            cap_info = {'capName': capability.id_short, 'skills': [], 'capConstraints': set(),
                                        'capDescription': '', 'capType': 'Unknown', 'AASmodel': set()}
                            if (capability.description is not None) and ('en' in capability.description):
                                cap_info['capDescription'] = capability.description.get('en')
                            if capability.check_semantic_id_exist(
                                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_AGENT_CAPABILITY_IRI):
                                cap_info['capType'] = 'AgentCapability'
                            elif capability.check_semantic_id_exist(
                                    CapabilitySkillOntologyInfo.CSS_ONTOLOGY_ASSET_CAPABILITY_IRI):
                                cap_info['capType'] = 'AssetCapability'

                            for related_skill in skills:
                                if related_skill.id_short not in analyzed_elems['Skills']:
                                    analyzed_elems['Skills'].append(related_skill.id_short)
                                    self.myagent.loaded_statistics['Skills'] += 1
                                cap_info['skills'].append(related_skill.id_short)

                                if isinstance(related_skill, basyx.aas.model.Operation):
                                    # In this case the Skill parameters are the inoutput variables of the AAS elem
                                    param_set = set()
                                    for param in related_skill.input_variable:
                                        param_set.add(param.id_short)
                                    if related_skill not in self.myagent.skills_info:
                                        self.myagent.skills_info[related_skill] = param_set
                                    else:
                                        self.myagent.skills_info[related_skill].update(param_set)

                            if capability.id_short not in analyzed_elems['Capabilities']:
                                analyzed_elems['Capabilities'].append(capability.id_short)
                                self.myagent.loaded_statistics['Capabilities'] += 1

                                css_elems_info[capability.id_short] = cap_info
                            else:
                                for related_skill in cap_info['skills']:
                                    if related_skill not in css_elems_info[capability.id_short]['skills']:
                                        css_elems_info[capability.id_short]['skills'].append(related_skill)

                            css_elems_info[capability.id_short]['AASmodel'].add(file_name)
                    if CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_ISRESTRICTEDBY_IRI == rel.iri:
                        for capability, constraints in aas_elems.items():
                            const_info = set()
                            for const in constraints:
                                const_info.add(const.id_short)
                            if capability.id_short not in css_elems_info:
                                css_elems_info[capability.id_short] = {'capConstraints': const_info}
                            else:
                                css_elems_info[capability.id_short]['capConstraints'].update(const_info)
                    if CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_HASPARAMETER_IRI == rel.iri:
                        for skill, skill_param in aas_elems.items():
                            if skill not in css_elems_info['skillData']:
                                param_set = set()
                                param_set.add(skill_param)
                                self.myagent.skills_info[skill] = param_set
                            else:
                                self.myagent.skills_info[skill].add(skill_param)

        # Once all data is analyzed, it is saved in the agent dictionary
        self.myagent.css_elems_info = css_elems_info

        return {"status": "success", "reason": "success reason"}
        # return {"status": "error", "reason": "error reason"}

    async def operator_select_controller(self, request):

        data = await request.json()
        available_smia_selection = []
        for cap_name, cap_info in self.myagent.css_elems_info.items():
            if cap_name == data['Capability']:
                # At this point, the restrictions (if any) are valid
                for aas_model in cap_info['AASmodel']:
                    available_smia = {'SMIAsInfo': {
                        'SMIA_JID' : await self.get_smia_attrib_by_file_name(aas_model,'SMIA_JID'),
                        'AssetID' : await self.get_smia_attrib_by_file_name(aas_model,'AssetID')}
                    }
                    available_smia.update(data)

                    # The skill parameters are also added (if any)
                    for skill_elem, skill_params in self.myagent.skills_info.items():
                        if skill_elem.id_short == data['Skill'] and len(skill_params) > 0:
                            available_smia['skillParameters'] = skill_params

                    if 'CapConstraints' not in data:
                        _logger.info("The selected capability does not have constraints, so the SMIA can perform it.")
                        available_smia_selection.append(available_smia)
                    else:
                        # Constraints need to be validated.
                        _logger.info("The constraints need to be validated for this SMIA: {}.".format(aas_model))
                        for constr_name, constr_value in data['CapConstraints'].items():
                            # Constraint AAS elem is obtained
                            aas_constr_elem = await self.get_aas_elem_of_model_by_id_short(aas_model, constr_name)
                            try:
                                # The ExtendedCapabilityConstraint class is used to automatically check the constraint
                                if not aas_constr_elem.check_constraint(float(constr_value)):
                                    _logger.info("The constraint {} with value {} is invalid".format(constr_name, constr_value))
                                    break
                            except Exception as e:
                                err_msg = ("An error occurred checking the constraint {} with value {}. Reason: {}"
                                           .format(constr_name, constr_value, e))
                                _logger.warning(err_msg)
                                return {"status": "error", "reason": err_msg}
                        else:
                            # The loop ran without breaking, so the constraints are valid
                            _logger.info("All constraints are valid")
                            available_smia_selection.append(available_smia)

        self.myagent.available_smia_selection = available_smia_selection
        return {"status": "success", "reason": "success reason"}

    async def operator_request_controller(self, request):

        from operator_gui_behaviours import OperatorRequestBehaviour    # local import to avoid circular import errors

        data = await request.post()
        self.myagent.request_exec_info = {'StartTime': GeneralUtils.get_current_date_time(), 'Status': 'Started',
                                          'Interactions': 0}

        # Extract arrays for each field
        smia_id_list = data.getall('smia_id[]', [])
        asset_id_list = data.getall('asset_id[]', [])
        selected = data.getall('checkbox[]', [])
        capability = data.get('capability', None)   # Default if missing
        constraints = data.get('constraints', None)
        skill = data.get('skill', None)
        skill_params = data.get('skillParams', None)

        if skill_params is not None:
            for param in set(eval(skill_params)):
                param_value = data.get(param, None)
                print("Param {} with value {}".format(param, param_value))

        # Group data by row index
        processed_data = []
        selected_smia_ids = []
        for idx, smia_id in enumerate(smia_id_list):
            if smia_id in selected:
                processed_data.append({
                    "smiaID": smia_id,
                    "assetID": asset_id_list[idx],
                })
                selected_smia_ids.append(smia_id)
        print("Requested SMIAs: {}".format(processed_data))
        print("Requested data: {}".format({'Cap': capability, 'Skill': skill, 'Constraints': constraints}))


        request_data = {
            'thread': 'Operator-request-'+ ''.join(random.choices(string.ascii_letters + string.digits, k=4)),
            'formData': data
        }
        capability_request_behav = OperatorRequestBehaviour(self.myagent, request_data)
        self.myagent.add_behaviour(capability_request_behav)

        # Wait until the behaviour has finished (the request has been sent)
        await capability_request_behav.join()

        # return web.json_response({'status': 'OK'})
        return {'status': 'OK'}

    async def get_smia_attrib_by_file_name(self, file_name, smia_attrib):
        for smia_file, smia_info in self.myagent.loaded_smias.items():
            if smia_file == file_name:
                if smia_attrib in smia_info:
                    return smia_info[smia_attrib]
                else:
                    return None
        return None

    async def get_aas_elem_of_model_by_id_short(self, file_name, id_short):
        for smia_file, smia_info in self.myagent.loaded_smias.items():
            if smia_file != file_name:
                continue
            for rel, aas_elems in smia_info.items():
                if not isinstance(rel, str):
                    for elem_domain, elems_range in aas_elems.items():
                        if elem_domain.id_short == id_short:
                            return elem_domain
                        for elem in elems_range:
                            if elem.id_short == id_short:
                                return elem
        return None

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
                return aas_smia_instance_name.value
        _logger.warning("The SoftwareNameplate submodel is defined within the AAS model, but the instance name is not. "
                        "This SMIA cannot be loaded into the SMIA operator.")
        await agent_object.aas_model.set_aas_model_object_store(operator_aas_model_store)
        return None

    @staticmethod
    async def get_asset_id_from_aas_store(aas_model_store):
        """
        This method gets the SMIA JID value from the AAS model store. The SMIA approach establishes that this information need to be added within the '' standardized submodel.

        Args:
            agent_object (smia.agents.smia_agent.SMIAAgent): SMIA SPADE agent object.
            aas_model_store (basyx.aas.model.DictObjectStore): Python object with the AAS model.

        Returns:
            JID: SMIA JID value.
        """
        # First, the AAS model store is analyzed to found an AAS with the globalAssetID defined
        for aas_elem in aas_model_store:
            if isinstance(aas_elem, basyx.aas.model.AssetAdministrationShell):
                if aas_elem.asset_information is not None:
                    if aas_elem.asset_information.global_asset_id is not None:
                        return aas_elem.asset_information.global_asset_id

        _logger.warning("Asset ID not found for model store {}".format(aas_model_store))
        return None