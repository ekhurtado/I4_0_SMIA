import asyncio
import logging
import sys

import basyx.aas.adapter.json
import basyx.aas.adapter.xml
from basyx.aas import model
from basyx.aas.model import ModelReference
from spade.behaviour import OneShotBehaviour
from tqdm.asyncio import tqdm

from smia.aas_model import extended_submodel
from smia.aas_model.aas_model_utils import AASModelUtils
from smia.aas_model.extended_submodel import ExtendedSkill, ExtendedSkillInterface, ExtendedComplexSkillInterface, \
    ExtendedComplexSkill, ExtendedSimpleSkill, ExtendedSimpleSkillInterface
from smia.assetconnection.http_asset_connection import HTTPAssetConnection
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils, CapabilitySkillOntologyInfo, \
    CSSModelAASModelInfo
from smia.utilities.smia_info import AssetInterfacesInfo
from smia.logic.exceptions import AASModelReadingError, AASModelOntologyError, \
    OntologyReadingError, OntologyInstanceCreationError

_logger = logging.getLogger(__name__)


class InitAASModelBehaviour(OneShotBehaviour):
    """
    This class implements the behaviour responsible for reading the AAS model to obtain all submodels, submodel elements
     and concept descriptions. The necessary checks are performed to ensure the valid  initial conditions to start the
     running state of the DT. The AAS model is defined in the ConfigMap associated to the deployed container and in
     order to successfully read the definition in any serialization format (JSON or XML), BaSyx Python SDK will be used.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the SMIA agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        self.progress_bar = None

        # The counters for all type of analyzed elements are initialized
        self.analyzed_capabilities = []
        self.analyzed_capability_constraints = []
        self.analyzed_skills = []
        self.analyzed_skill_interfaces = []
        self.analyzed_skill_params = []
        self.analyzed_asset_connections = []
        self.errors_found = []

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        # Depending on the serialization format, the required BaSyx read method shall be executed. This will store all
        # the received elements of the model in the corresponding global object of the agent.
        object_store = AASModelUtils.read_aas_model_object_store()
        await self.myagent.aas_model.set_aas_model_object_store(object_store)

        # First, the initial general analysis is performed on the AAS model.
        await self.myagent.aas_model.execute_general_analysis(self.myagent)

        # A progress bar is used for showing how the AAS model is being read.
        await self.create_progress_bar_object()

        # When the object store is created, the required values and information is obtained from the AAS model
        _logger.info("Reading the AAS model to get all defined ontology elements...")
        await self.get_and_save_ontology_classes_information()

        await asyncio.sleep(.5)
        _logger.info("Reading the AAS model to get all relationships between ontology elements...")
        await self.get_and_save_ontology_relationships_information()

        # After the AAS model has been analyzed, the AssetConnection class can be specified
        _logger.info("Reading the AAS model to get all asset connections...")
        await self.get_and_configure_asset_connections()

        # The progress bar is closed
        self.progress_bar.close()
        await asyncio.sleep(1)

        # The final results of the analysis are shown
        await self.print_analysis_result()

        _logger.info("AAS model initialized.")
        self.exit_code = 0

    async def get_and_save_ontology_classes_information(self):
        """
        This method stores all the information related to the class elements defined in the ontology. Since the data is
         defined in the AAS model, it will be used to check whether the required data defined in the ontology has been
          added in the AAS model. If the elements are valid, they will be created their associated ontology instance and
          the AAS SubmodelElement will be associated to these instances.
        """
        for ontology_class_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS:
            await self.check_and_create_instances_by_iri(ontology_class_iri)

    async def get_and_save_ontology_relationships_information(self):
        """
        This method stores all the information related to the relationships between elements defined in the ontology.
        Since the data is defined in the AAS model, it will be used to check whether the linked elements have their
        associated ontology instance (created just before the execution of this method).
        """
        for ontology_relationship_iri in CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS:
            await self.check_and_create_relationship_by_iri(ontology_relationship_iri)

        # Skills that are of type Operation SubmodelElement are a special case, because their OperationVariables are
        # related SkillParameters, but there is no relation between them.
        await self.check_and_create_operation_relationships()

    async def check_and_create_instances_by_iri(self, ontology_class_iri):
        """
        This method checks the relationship between two elements and, if it is valid, it creates it (it connects the
        related ontology instances through the appropriate ObjectProperty).

        Args:
            ontology_class_iri (str): identifier in form of IRI for the element within the CSS ontology.
        """
        sme_list = None
        try:
            sme_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(ontology_class_iri)
        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")

        for submodel_elem in sme_list:
            await self.add_step_progress_bar()

            try:
                # For each SubmodelElement an instance within the CSS ontology is created
                await self.create_ontology_instance_from_sme_element(submodel_elem, ontology_class_iri)
                # created_instance = await self.myagent.css_ontology.create_ontology_object_instance(ontology_class,
                #                                                                                    submodel_elem.id_short)

                # The submodel element will be converted from the Basyx class to the extended one (of the SMIA approach)
                await self.convert_sme_class_to_extended_by_iri(submodel_elem, ontology_class_iri)

                # The element is saved as analyzed
                await self.add_new_analyzed_element(submodel_elem)

            except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
                if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                    _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
                else:
                    _logger.warning("Check the CSS ontology definition.")
                self.errors_found.append(submodel_elem.id_short)

    async def create_ontology_instance_from_sme_element(self, sme_elem, ontology_iri):
        """
        This method creates the ontology instance from the AAS Submodel Element.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model with all configured data.
            ontology_iri (str): IRI of the ontology class of the instance to be created.
        """
        try:
            ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(ontology_iri)
            if ontology_class is None:
                raise OntologyReadingError('The ontology class with IRI {} does not exist in the given OWL ontology. '
                                           'Check the ontology file.')
            # The class is used as constructor to build the instance of the CSS ontology
            created_instance = await self.myagent.css_ontology.create_ontology_object_instance(ontology_class,
                                                                                               sme_elem.id_short)
            # TODO de momento se crean las instancias de las ontologias con el id_short, pero habria que pensar si el
            #  id_short puede repetirse (el id_short es único dentro del submodelo)
            await self.add_ontology_required_information(sme_elem, created_instance)

        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError, OntologyInstanceCreationError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")
            self.errors_found.append(sme_elem.id_short)

    @staticmethod
    async def add_ontology_required_information(aas_model_elem, ontology_instance):
        """
        This method adds the required information defined in the ontology to the given instance. All information is
        obtained from given the AAS Submodel Element.

        Args:
            aas_model_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model with all configured data.
            ontology_instance (ThingClass): instance class on which the information will be added.
        """
        # The ontology may state that it is required to add some attributes
        ontology_required_value_iris = ontology_instance.get_data_properties_iris()
        for required_value_iri in ontology_required_value_iris:
            required_value = aas_model_elem.get_qualifier_value_by_semantic_id(required_value_iri)
            required_value_name = ontology_instance.get_data_property_name_by_iri(required_value_iri)
            ontology_instance.set_data_property_value(required_value_name, required_value)
        # The Submodel Element is also added to be available to the ontology instance object in form of a reference
        ontology_instance.set_aas_sme_ref(ModelReference.from_referable(aas_model_elem))

    @staticmethod
    async def convert_sme_class_to_extended_by_iri(sme_elem, ontology_iri):
        """
        This method converts the class of a SubmodelElement to the Extended class, in order to add the required method
        to be used during the execution of the software. The extended class is obtained from from the CSS ontology utils
         class using the IRI of the ontology class.

        Args:
            sme_elem (basyx.aas.model.SubmodelElement): SubmodelElement of the AAS model to be modified.
            ontology_iri (iri): ontology class IRI.
        """
        current_class = sme_elem.__class__
        new_class = CSSModelAASModelInfo.CSS_ONTOLOGY_AAS_MODEL_LINK[ontology_iri]
        # TODO comprobar si con el nuevo metodo de extension en 'add_old_sme_class' se evita el problema del Simple y Complex de skill e interfaz
        if new_class is ExtendedSkill:
            # In this case there are two types of classes (Simple and Complex)
            if sme_elem.check_if_element_is_structural():
                sme_elem.__class__ = ExtendedComplexSkill
            else:
                sme_elem.__class__ = ExtendedSimpleSkill
        elif new_class is ExtendedSkillInterface:
            # In this case there are two types of classes (Simple and Complex)
            if sme_elem.check_if_element_is_structural():
                sme_elem.__class__ = ExtendedComplexSkillInterface
            else:
                sme_elem.__class__ = ExtendedSimpleSkillInterface
        else:
            sme_elem.__class__ = new_class
        # The old class new to be added to the Extended class
        sme_elem.add_old_sme_class(current_class)

    async def check_and_create_relationship_by_iri(self, relationship_iri):
        """
        This method checks the relationship between two elements and, if it is valid, it creates it (it connects the
        related ontology instances through the appropriate ObjectProperty).

        Args:
            relationship_iri (str): identifier in form of IRI for the relationship within the CSS ontology.
        """
        rels_list, rel_ontology_class, domain_aas_class, range_aas_class = None, None, None, None
        try:
            rels_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
                relationship_iri, basyx.aas.model.RelationshipElement)
            rel_ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(relationship_iri)
            # The required AAS classes for the elements within this relationship is obtained from the CSS ontology
            domain_aas_class, range_aas_class = CapabilitySkillOntologyUtils.get_aas_classes_from_object_property(
                rel_ontology_class)
        except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
            if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
            else:
                _logger.warning("Check the CSS ontology definition.")

        domain_aas_elem, range_aas_elem = None, None
        for rel in rels_list:
            await self.add_step_progress_bar()

            # First, the elements of capability and skill are determined (no matter in which order of the
            # relationship they are listed).
            try:
                domain_aas_elem, range_aas_elem = await self.myagent.aas_model.get_elements_from_relationship(
                    rel, domain_aas_class, range_aas_class)
                # It is checked if the capability and the skill have the required semanticIDs within the ontology
                # if not domain_aas_elem.check_semantic_id_exist(domain_class_iri):
                domain_aas_elem.get_semantic_id_of_css_ontology()
                range_aas_elem.get_semantic_id_of_css_ontology()

                # When both are checked, if the ontology instances exist the link is set in the ontology
                await self.myagent.css_ontology.add_object_property_to_instances_by_names(rel_ontology_class.name,
                                                                                          domain_aas_elem.id_short,
                                                                                          range_aas_elem.id_short)

            except (AASModelReadingError, AASModelOntologyError, OntologyReadingError) as e:
                if isinstance(e, AASModelReadingError) or isinstance(e, AASModelOntologyError):
                    _logger.warning("Check the AAS Model {}. Reason of the fail: {}.".format(e.sme_class, e.reason))
                else:
                    _logger.warning("Check the CSS ontology definition.")
                if None not in (domain_aas_elem, range_aas_elem):
                    self.errors_found.append("{} ({},{})".format(rel.id_short, domain_aas_elem.id_short,
                                                                 range_aas_elem.id_short))
                else:
                    self.errors_found.append("{} ({},{})".format(rel.id_short, domain_aas_class, range_aas_class))

    async def check_and_create_operation_relationships(self):
        """
        This method checks the relationship between OperationVariables and their related Operation SubmodelElement and,
        if they are included in the CSS ontology (by semanticIDs), the related ontology instances are linked through
        the appropriate ObjectProperty.
        """
        skill_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI)
        rel_ontology_class = await self.myagent.css_ontology.get_ontology_class_by_iri(
            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_HASPARAMETER_IRI)
        for skill in skill_list:
            if isinstance(skill, model.Operation):
                variable = None
                try:
                    if rel_ontology_class is None:
                        raise OntologyReadingError('The class for the relationship with IRI {} does not exist in the '
                                                   'given ontology. Check the OWL ontology file.'.format(
                            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_PROP_HASPARAMETER_IRI))
                    if skill.check_semantic_id_exist(CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_IRI):
                        operation_variables = skill.get_operation_variables_by_semantic_id(
                            CapabilitySkillOntologyInfo.CSS_ONTOLOGY_SKILL_PARAMETER_IRI)
                        for variable in operation_variables:
                            # When both are checked, if the ontology instances exist the link is set in the ontology
                            await self.myagent.css_ontology.add_object_property_to_instances_by_names(
                                rel_ontology_class.name, skill.id_short, variable.id_short)
                except OntologyReadingError as error:
                    _logger.warning("Check the CSS ontology definition.")
                    if None not in (skill, variable):
                        self.errors_found.append("{} ({},{})".format('hasParameter', skill.id_short,
                                                                     variable.id_short))
                    else:
                        self.errors_found.append("{} ({},{})".format('hasParameter', 'Operation', 'OperationVariable'))


    async def get_and_configure_asset_connections(self):
        """
        This method gets all Asset Interfaces Descriptions in the AAS model, configures each case with associated
        'AssetConnection' class and saves the information in the global variable of the agent for all asset connections.
        """
        # TODO PROXIMO PASO: hay que modificicar la variable global para assetconnection del agente ya que se debe
        #  habilitar añadir mas de un AssetConnection. Para ello, se analizara el Submodelo "AssetInterfacesDescription"
        #  y se recogerá cada SMC dentro de el, el cual determinara una interfaz diferente. Por cada interfaz,
        #  dependiendo del tipo (HTTP, OPC UA...) se generará una clase AssetConnection. Esta deberá tener, por una
        #  parte, la referencia al SMC del modelo AAS. Utilizando esta referencia, leera toda la informacion de ese
        #  submodelo y configurará la interfaz (p.e. añadiendo los datos del endpoint), para dejar la interfaz lista
        #  para ser usada (se hará referencia a los SMEs dentro de "InteractionMetada" del submodelo de la interfaz,
        #  que es donde estan los datapoints)
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning("AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to "
                            "be connected to the asset.")
            return
        for interface_elem in asset_interfaces_submodel.submodel_element:
            await self.add_step_progress_bar()

            if interface_elem.check_semantic_id_exist(AssetInterfacesInfo.SEMANTICID_INTERFACE) is False:
                _logger.warning("There is a submodel element inside the interfaces submodel with invalid semanticID.")
                continue
            # Dependiendo del tipo de interfaz se generara una clase u otra (de momento solo HTTP)
            if interface_elem.check_suppl_semantic_id_exist(AssetInterfacesInfo.SUPPL_SEMANTICID_HTTP):
                # Hay una interfaz de tipo HTTP
                http_connection_class = HTTPAssetConnection()
                await http_connection_class.configure_connection_by_aas_model(interface_elem)
                interface_model_ref = ModelReference.from_referable(interface_elem)
                await self.myagent.save_asset_connection_class(interface_model_ref, http_connection_class)
            if interface_elem.check_suppl_semantic_id_exist('id de opc ua'):
                # TODO Hay una interfaz de tipo OPC CUA
                pass

            self.analyzed_asset_connections.append(interface_elem.id_short)

        _logger.info("All asset connections defined in the AAS model have been configured and saved.")

    async def print_analysis_result(self):
        """
        This method simply prints the result of the complete analysis of the AAS model.
        """
        _logger.info("AAS model analysis results. \n\t- Analyzed capabilities: {}\n\t- Analyzed capability "
                     "constraints: {}\n\t- Analyzed skills: {}\n\t- Analyzed skill interfaces: {}\n\t- Analyzed skill "
                     "parameters: {}\n\t- Analyzed asset connections: {}\n\t\x1b[91m- Errors found: {}\x1b[0m".format(
                      self.analyzed_capabilities, self.analyzed_capability_constraints, self.analyzed_skills,
                      self.analyzed_skill_interfaces, self.analyzed_skill_params, self.analyzed_asset_connections,
                      self.errors_found))

        for analyzed_dict in [self.analyzed_capabilities, self.analyzed_capability_constraints, self.analyzed_skills,
                     self.analyzed_skill_interfaces, self.analyzed_skill_params, self.analyzed_asset_connections]:
            if len(analyzed_dict) > 0 and set(analyzed_dict).issubset(self.errors_found):
                _logger.error("All elements of an ontology class have been detected as errors, so check the AAS model "
                              "or the OWL ontology file.")

    async def create_progress_bar_object(self):
        """
        This method creates the object for showing by console the progress of the analysis of the AAS model in form of
        a progress bar. The object is
        """
        # The iterations during the analysis of the AAS model will be the number of steps in the progress bar
        # The iteration number will be the sum of the possible Asset Connections and the Capability-Skill relationships.
        ontology_elements_semantic_ids = CapabilitySkillOntologyInfo.CSS_ONTOLOGY_THING_CLASSES_IRIS + \
                                         CapabilitySkillOntologyInfo.CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS
        ontology_elements_list = await self.myagent.aas_model.get_submodel_elements_by_semantic_id_list(
            ontology_elements_semantic_ids)
        asset_interfaces_submodel = await self.myagent.aas_model.get_submodel_by_semantic_id(
            AssetInterfacesInfo.SEMANTICID_INTERFACES_SUBMODEL)
        if not asset_interfaces_submodel:
            _logger.warning(
                "AssetInterfacesSubmodel submodel is not defined. Make sure that this DT does not need to be"
                " connected to the asset.")
            asset_interfaces_submodel = type('obj', (object,), {
                'submodel_element': []})  # This is a solution to not brake the next commmand
        total_iterations = len(asset_interfaces_submodel.submodel_element) + len(ontology_elements_list)
        # with logging_redirect_tqdm():
        self.progress_bar = tqdm(total=total_iterations, desc='Analyzing AAS model', file=sys.stdout, ncols=75,
                                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} ontology submodel elements \n')

    async def add_step_progress_bar(self):
        """
        This method adds a new step in the progress bar to show the status of the AAS model analysis.
        """
        # Add a new step in the progress bar
        self.progress_bar.update(1)
        await asyncio.sleep(.2)  # Simulate some processing time

    async def add_new_analyzed_element(self, aas_elem):
        """
        This method adds the new analyzed element in the corresponding list of class variables.

        Args:
            aas_elem (basyx.aas.model.SubmodelElement): analyzed SubmodelElement,
        """
        if isinstance(aas_elem, extended_submodel.ExtendedCapability):
            self.analyzed_capabilities.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedSkill):
            self.analyzed_skills.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedSkillInterface):
            self.analyzed_skill_interfaces.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedSkillParameter):
            self.analyzed_skill_params.append(aas_elem.id_short)
        elif isinstance(aas_elem, extended_submodel.ExtendedCapabilityConstraint):
            self.analyzed_capability_constraints.append(aas_elem.id_short)
