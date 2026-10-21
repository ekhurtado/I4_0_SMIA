# Release Notes

(Release Notes)=

## v1.0.3

This release of Self-configurable Manufacturing Industrial Agents (SMIA) includes improvements to agent's source code, such as significant enhancements of the MQTT and HTTP asset connections, new methods for the extended classes of the Basyx Python SDK and compatibility with different versions of AAS submodels, and improvements to SMIA ecosystem (SMIA PE, the HTTP-based assets simulator and the SMIA Environment Builder tool). The step-by-step tutorial on simulated assets has also been updated, and a new GitHub workflow for smoke testing of SMIA has been added to the repository.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Significantly improved the HTTP asset connection class (``HTTPAssetConnection``):
  - The variables in each response have been changed from global (class variables) to local, to avoid shared state and eliminate race conditions.
  - The response is now read only once within each session.
  - More efficient handling of input data in parameters and the request body (depending on the AAS definition and the type of request).
- Significantly improved the MQTT asset connection (``MQTTAssetConnection``):
  - Added ``subscribe`` and ``unsubscribe`` interaction types.
  - Added a persistent coroutine-safe session with on-demand reconnect.
  - Added fan-out subscribe with retained cache (when ``retain`` is set in the AAS AID submodel).
  - Added refcounted unsubscribe, so that unsubscribing one interaction does not affect other subscriptions.
- Added new methods for the extended classes of the Basyx Python SDK's ``SubmodelElements``:
  - Added the ``get_sm_element_by_semantic_id`` method to the ``Submodel`` and ``SubmodelElementList`` extended classes.
  - Improved the ``get_sm_element_by_semantic_id`` method for the ``SubmodelElementCollection`` extended class (now it uses ``check_semantic_id_exist``).
- Added compatibility with different versions of the ``AssetInterfacesDescription`` submodel (each version has its own ``semanticID``).
  - Implemented by using wildcards during the comparison when searching for AAS elements by ``semanticID``.
- Improved the assets simulator for HTTP-based assets:
  - It now allows registering new assets via the ``/assets/register`` API and via the web interface, by specifying the asset ID and type (using a toggle select).
- Improved SMIA PE extended agent:
  - Now, if a CSS execution error occurs, the task is displayed in yellow in the Graphviz view of the web interface.
  - Now, BPMN execution is not blocked indefinitely when a CSS execution error occurs: it is possible to resume the flow and re-execute the same task. If the attempt is successful, the BPMN continues.
- Added a new GitHub workflow for smoke testing of SMIA (SMIA operational check):
  - Added the workflow definition (``.github/workflows/smia-operation-test.yml``), the smoke check script (``.github/smia_smoke_check.sh``) and Dockerfile templates (``docker/Dockerfile_SMIA_base_template`` and ``docker/Dockerfile_SMIA_full_base_template``).
  - The workflow has been tested and validated (both failure and success cases).

### Major Changes

- Improved the SMIA Environment Builder tool within the ReadTheDocs documentation platform:
  - Added both versions of the Basyx AAS Server (Go and Java): users can now select the version, and the appropriate deployment environment is generated for each case.
  - All production assets now include the proper environment variable to self-register themselves (instances and CSS information) when SMIA-I KB and SMIA ISM are selected as infrastructure components.
- Updated the step-by-step tutorial on simulated assets:
  - Updated the CSS-enriched AAS models (AASX files) of simulated assets with the common ``NegotiationBasedOnAssetData`` skill, to leverage the ability of SMIA PE and SMIA Operator to specify the negotiation criterion to assign assets.
  - Added the ``CSS_AAS_model_base.aasx`` file to GitHub resources, as a valid template for generating the CSS-enriched AAS models of simulated assets.
  - Updated the guide on the documentation platform: removed the instruction to make changes in Docker Compose (the SMIA Environment Builder does them automatically), and the name of the negotiation skill (``NegotiationBasedOnAssetData``) has been corrected.
  - Added information on selecting the Basyx version during the second phase of deployment to the tutorial guide of the ReadTheDocs documentation platform.
- Updated ``.gitignore``: added pycache folders and files
  - All Python cache folders have also been removed from the GitHub repository to keep the source code clean.

### Fixed errors

- Fixed a bug in SMIA (and extended agents) when retrieving the password for the XMPP server via an environment variable.
  - Previously, ``AGENT_PASSWD`` was used instead of ``AGENT_PSSWD``, so the password value could not be obtained; now the correct environment variable is used.
  - The same bug has also been fixed in the SMIA ReadTheDocs documentation platform.
- Fixed the Basyx AAS Server configuration error with new versions: the Mongo configuration must be updated because it now uses Spring Boot 4.
  - This has been fixed in the SMIA Environment Builder tool.
  - Fixed a versioning issue in the Basyx infrastructure (Go version) when generating environments with SMIA Environment Builder. The `aasenvironment` and `basyxconfiguration` components require the same version (`latest` has been replaced with a fixed version to ensure proper operation).
- Fixed minor errors in the ``getting_started`` and ``glossary`` pages of the documentation platform.
- Fixed the section titles of the release notes in the documentation platform: the latest versions did not have the ``v`` prefix. Now all section titles are correctly formatted.

## v1.0.2

This release of Self-configurable Manufacturing Industrial Agents (SMIA) includes improvements to agent's source code, such as a new asset communication protocol (OPC UA) or a new AAS service, and improvements to SMIA ecosystem (SMIA PE, SMIA Operator and the Camunda Modeler plugin). A new step-by-step tutorial with simulated assets and a new extended agent for health supervision is also added to the documentation platform.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

> [!NOTE]
> **Version 1.0.1 skipped**: Version `1.0.1` was skipped due to a packaging issue on PyPI.

### Features

- Added new asset connection protocol to SMIA: ``OPC UA``.
  - Created ``OPCUAAssetConnection`` class with a single persistent client across requests and subscriptions, and local variables per request to prevent errors in concurrent requests.
  - Added its semanticID in ``AssetInterfacesInfo`` and self-generation in ``InitAASModelBehaviour`` during self-configuration.
  - Added new OPC UA protocol to the template for the ``AssetInterfacesDescription`` submodel as additional resource for AASX Package Explorer.
- Added new AAS service for SMIA: ``GetSubmodelElementBySemanticID``. It returns an AAS Submodel or SubmodelElement using the ``semanticID`` (useful when information is needed but the submodel identifier is not available).
- Added new step-by-step guide on ReadTheDocs: evaluating SMIA platform with the assets simulator (part of SMIA ecosystem).
  - Developed the CSS-enriched AAS models (AASX files) for all simulated assets and added to GitHub resources in ``examples/tutorials/SMIA_simulated_assets_guided_tutorial``.
  - Added full guide on ReadTheDocs platform in ``SMIA User Guide/Step-by-step tutorials``: ``Step-by-step tutorial: Simulated assets``.
  - The tutorial consists of three phases: development of CSS-enriched AAS models for simulated assets, deployment of the SMIA platform, and validation of SMIA instances individually via SMIA Operator and collaboratively via SMIA PE (including ``OperationalHealthSupervisor``).
- Developed a new extended agent ``OperationalHealthSupervisor`` for the new step-by-step guide with simulated assets.
  - The purpose of this agent is to monitor the health of simulated assets and, if necessary, request their replenishment.
  - First operational version with multiple approaches for health property acquisition: approach A based on semanticID references and asset services erquests, and approach B based on ``AssetPropertyProvision`` capability requests.
  - Added source code in GitHub within ``examples/tutorials/SMIA_simulated_assets_guided_tutorial``. It includes launcher, internal logic, utilities, Docker files and CSS-enriched AAS model ``SimulatedAssets_OperationalHealthSupervisor.aasx``.
- Added communication guide as SMIA user guide in ReadTheDocs platform, and improved SMIA User Guide page with references to step-by-step tutorials and the ecosystem.
- Improvements to SMIA plugin for Camunda Modeler: a new set of three global attributes has been added for the CSS-enriched BPMN process: ``autostart``, ``repeat`` and ``negotiation criterion``.
  - This allows users to define the criteria for assigning assets when tasks are left without specifying an asset.
- Improved SMIA PE extended agent to configure settings from BPMN process information (``autostart``, ``repeat``, ``negotiation criterion``). If defined as environment variables, their values take precedence over those defined in the BPMN.
  - This allows assets to be assigned based on the criteria defined in the BPMN during the CNP distributed protocol.
- Improved SMIA Operator extended agent: added option to specify the negotiation criterion when multiple SMIA instances are selected, with instant validation that warns when the selected SMIAs do not all support the chosen criterion.

### Major Changes

- Improved OPC UA asset connection efficiency by reusing a single persistent client following best practices for communication.
- Improved SMIA PE graphical interface: added toggle switch for workflow management to configure iterative vs. single execution, and fixed retrieving of negotiation criteria for CNP requests.
- Improved SMIA Operator graphical interface: Added a selection option for the negotiation criteria only if the user selects multiple SMIA instances. 
  - Additionally, if the selected instances do not share the same negotiation criteria, the user is notified in the interface that the negotiation may fail.
- Added ``asyncua`` as a dependency for SMIA, due to the new communication protocol.
  - It has been added to ``pyproject.toml`` so that it is generated in the SMIA package on PyPI.

### Fixed errors

- Fixed bug in SMIA-I KB when generating (POST) and returning (GET) capabilities: it did not take the ``Agent/AssetCapability`` category into account and returned the capability name instead of the category. Now instances are correctly generated and categorized.
  - Previously, when SMIA instances were registered, ontological instances were always generated from the ``Capability`` class; now they are generated from the correct class, ``Agent/AssetCapability``.
  - Previously, when capabilities were obtained, they all displayed their category using the same name as the capability; now they are displayed with their correct ``Agent/AssetCapability`` category.
- Fixed template for the ``AssetInterfacesDescription`` submodel: removed ``{0:00}`` entries which caused a parsing error in SMIA.
- Added error message when an ``AssetConnectionError`` occurs during CSS capability execution in ``HandleCapabilityBehaviour``.
- Added compatibility comment in ``extended_aas_model``: if ``basyx-python-sdk`` is updated to v2.1.0 an ``if`` statement must be removed.
  - This compatibility issue has been verified through testing with different versions of ``basyx-python-sdk``.
- Fixed minor errors in communication guide and simulated assets tutorial guide.

## v0.3.5

This release of Self-configurable Manufacturing Industrial Agents (SMIA) includes some improvements to additional tools of the SMIA ecocystem, as well as fixes for some bugs and errors throughout the project.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Added new aCSS-enriched AAS models: in this case for industrial robot as simulated asset via HTTP.
- Improvements to SMIA additional tool: assets simulator for HTTP-based assets. 
  - Added Docker files for the generation and deployment of its container.
  - Graphical interface improvements: Added options to minimize and maximize the sidebar, and fixed the display of asset status (it is now responsive).
  - Now the battery for automated assets is distinguished from stamina for humans, with ``recharge`` for the former and ``recovery`` for the latter.
- Improvements to SMIA Environment Builder tool within ReadTheDocs platform. 
  - Asset simulators have been included in the environment generation process (currently, the only one developed is HTTP).
  - Improved Asset simulators within local environments (now the specified assets IDs are included in the source code).


### Major Changes

- Improved SMIA additional tool: assets simulator for HTTP-based assets. 
  - Now the assets can be charged (``charge``) without a body within the HTTP request (they are fully charged).
  - Improved animations for mobile robots and added transportation task also for human.
- Removed old code (related to performance tests) from SMIA PE additional tool (extended agent) source code.


### Fixed errors

- Fixed errors in SMIA additional tool: assets simulator for HTTP-based assets. 
  - An issue with retrieving the assetID has been fixed. Since it is retrieved from the URL, it has been added as a path to retrieve it in its entirety.
- Fixed bugs and errors in SMIA asset connection classes: 
  - The URI for the asset interface was obtained without cleaning the URi. Now it is used ``strip`` to remove leading and tralining spaces to allow semi-valid URIs.
  - Fixed an error in HTTP asset connection within SMIA source code: request params and body were not reset with each request (the value from the previous request was retained).
- Fixed an error obtaining the response content from a message from the asset after executing an asset service. Now if ``dataQuery`` element in defined but with empty value, it is not considered to extract the information from the response.
- Fixed Docker container generation of SMIA PE additional tool. Due to the previous generic modification to the import of the ``smia_pe`` package, the Dockerfile had to be modified to specify the PYTHONPATH.
- Fixed error in ``get_safe_env_var()`` within ``DockerUtils`` of SMIA: with boolean environment variables it always returns True because the variable value is obtained in string, so ``bool(string)=True``.
- Fixed SMIA Environment Builder tool within ReadTheDocs platform. 
  - Fixed error when saving agent JID for each SMIA agent defined in Step 3.
  - Fixed error when saving agent JID for each SMIA agent defined in Step 3 (a ``smia-`` prefix was added in JID, now it is only added in container name).

## v0.3.4

This release of Self-configurable Manufacturing Industrial Agents (SMIA) comes with an significant upgrade of ... en la plataforma de documentación alojada en la plataforma ReadTheDocs, especificamente en relacion con los componentes del ecosistema SMIA. It also includes improvements to the source code's efficiency by removing obsolete code and comments.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Added GNU GPL V3 license file to the source code of SMIA Environment Builder tool of SMIA documentation platform in ReadTheDocs.
- Progress with SMIA ReadTheDocs documentation platform
  - Added ecosystem infrastructure pages and improved page for SMIA Operator tool as extended agent.
  - A new page has been added to the ``API Documentation`` section to allow for the inclusion of source code for additional tools within the ecosystem.
    - API of SMIA PE source code extended agent.
    - API of SMIA Operator source code extended agent.
    - API of SMIA HI source code extended agent.
    - API of SMIA ISM source code extended agent as infrastructure component.
  - Significantly improved SMIA Operator page, e.g., detailing the usage of its graphical interface and added link to the video showing its usage.
  - Significantly improved SMIA PE page, e.g., detailing the implementation, and how to deploy and use this extended agent. It is also added link to the video showing its usage.
  - Created and added page for SMIA-I KB:  its complete API has been detailed using tables (specifying the HTTP methods available and required schemas and parameters), an usage section (for HTTPrequests and FIPA-SMIACL requests through SMIA ISM), how to deploy it
  - Created and added page for SMIA HI: 
  - Created and added page for SMIA ISM: explanation of the internal logic, "Architecture and implementation" section (schemas for valid FIPA-SMIACL messages, and list of available infrastructure services exposed), "Execution example" section (some usage scenarios which involve SMIA ISM and added also some example codes)
  - Created and added page for Camunda Modeler plugin
  - Added 'Quick start' in 'Getting started' page within ReadTheDocs SMIA documentation platform to guide new users'
  - Added page of the use case of flexible small-scale manufacturing developed in CeDRI.
    - Improved page of the use case of flexible small-scale manufacturing developed in CeDRI: added link to Camunda Modeler plugin, used to design the BPMN production plans for the case study.
- First version of the new SMIA additional tool: assets simulator for HTTP-based assets.

### Major Changes

- Updated ``docs/requirements.txt`` file with dependencies for SMIA (updated some versions and added missing dependencies such as aiomqtt).
- Source code cleanup. Completed ``TODO`` tasks have been removed, and obsolete code has been removed from ``ACLHandlingBehaviour``, ``HandleAASRelatedSvcBehaviour``, ``InitAASModelBehaviour``, and ``NegotiatingBehaviour``.
  

### Fixed errors

- Grammatical corrections added to the step-by-step tutorial for the SMIA documentation platform on ReadTheDocs.
- Added SMIA Environment builder link in 'getting_started' page within the ReadTheDocs documentation platform.
- Fixed SMIA Operator source code (OperatorRequestBehaviour):
  - Requesting FIPA-CNP distributed negotiation protocol with new version of the algorithm within SMIA.
  - Obtaining the winner of a FIPA-CNP distributed negotiation protocol with the new version of the algorithm within SMIA.
- Fixed bug requesting distributed negotiations when multiple SMIA instances selected in SMIA Operator and fixed SMIA version in its HTML pages (now the latest version is shown).
- Fixed docker-compose.yml file of SMIA Operator with its new Docker image within "smia-tools" repository.
- Fixed SMIA Environment Builder source code when generating YAML deployment file for SMIA Operator (Docker image was not properly defined).
- Fixed name of the GCIS research group (which is the group in which the PhD thesis that develops the SMIA approach is being conducted) in all the required files.

## v0.3.3

This release of Self-configurable Manufacturing Industrial Agents (SMIA) includes new features and improvements to the software's inherent functionality, information updates, and bug fixes.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Added new communication protocol to SMIA: ``MQTT``
  - Created the file for the source code of the new communication protocol (MQTT): ``MQTTAssetConnection``. 
  - The file has been added alongside the source code (not yet tested). 
- Added latest source code of ``SMIA environment builder`` tool within ReadTheDocs documentation platform.
- Added SMIA software performance-related dataset link to README files (GitHub and PyPI) and ReadTheDocs documentation platform (getting started).

### Major Changes

- Added generation of ``MQTTAssetConnection`` class for each MQTT interface defined in AAS model dynamically within ``InitAASModelBehaviour``.
- Added ``aiomqtt`` as dependencies for SMIA in ``pyproject.toml`` file.
- Improved ``SMIA environment builder`` tool within ReadTheDocs documentation platform.
  - Modified displayed text, added third-party icons trademarks and acknowledgments, and added footer icons with links to SMIA official support resources (GitHub, DockerHub, etc.).
- Update of PyPI development status classifier and version from ``2-Pre-Alpha`` to ``3-Alpha`` status.
- Improved source code from the results of the Codacy analysis.
  

### Fixed errors

- Fixed AASX file for SMIA Operator additional tool
  - Added valid AASX file from SMIA approach scientific paper to SMIA Operator additional tool. 
  - It is also modified its launcher to improve the configurability between local and Docker execution enviroments.
- Fixed an issue in the SMIA Operator tool when receiving an ACL response with a body that was not in JSON format. The body is now parsed correctly.
- Minor corrections have also been made to the comments in the HTTP protocol file.
- Fixed an error in version specification in pyproject aiomqtt dependency and minor error in MQTT asset connection class regarding configuration from AAS model.
- Fixed problems when generating Kubernetes environment with SMIA environment builder tool within ReadTheDocs documentation platform.
- Fixed errors in CapabilityRequestExecutionError instantiations in ``HandleCapabilityBehaviour`` (thread argument was not added).
- Fixed an error assigning arguments in ``logic.services_utils``.


## v0.3.2

This release of Self-configurable Manufacturing Industrial Agents (SMIA) includes an update to the solution in terms of distributed negotiation logic as an inherent agent capability (``AgentCapability``) and an increase in support resources for using the approach (guided tutorials).

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Added a reference to the published article presenting SMIA software contribution: added citation block on RTD and GitHub and links as buttons in README.
  - [An open-source reference framework for the implementation of type 3 Asset Administration Shells](https://doi.org/10.1016/j.simpa.2025.100807)
- Added new agent service for all SMIA instances ``get_random_float_value``: generation of float numbers between 0 and 100.
- Added negotiation value as data to be stored in the SMIA log, to have more information about each negotiation.
- Added new method to obtain time in nanoseconds in SMIA general utils: ``get_current_timer_nanosecs``.
- New step-by-step tutorial for SMIA extension and validation on ReadTheDocs platform
  - Files added from the first step-by-step tutorial: both useful files and README.md files have been added to detail all the steps to follow.
- Added latest version of SMIA NR (Negotiation Requester) source code: the agent that initializes the negotiations for performance evaluation.
  - Cleaned and improved source code: removed debugging console prints, added SMIA utilities, improved the efficiency of the code...
  - Modified source code with new design of experiments and new CSV structure.

### Major Changes

- Improved SMIA negotiation algorithm:
  - Now the algorithm is capable of managing desynchronization cases in which not all proposal messages have been received.
  - Now the algorithm requests negotiation values in case they are not received, to fix the cases where some messages are missing.
  - Now the algorithm distributes the processing load. All messages are exchanged within the run method (sent and received).
  - Dynamic calculation of waiting time between sent messages and waiting time for recoveries (retries).
  - Code efficiency has been improved by using global variables for reusable data.
- Added new global variable for the SMIA agent so that specific behaviors can reserve messages from a specific thread (so that the generic ACLHandling behavior does not process them)
  - The new version of negotiation algorithm behaviour reserves the messages for its thread so that the generic behavior ``ACLHandlingBehavior`` never processes those messages (until the negotiation is complete).
- Now the SMIA PyPI package also enables the ``aas_model`` module.

  

### Fixed errors

- Fixed the handling of negotiation behaviours when a negotiation request is received (the ACL template was not specified, now the thread is used to only obtain messages for the specific negotiation).
- Fixed a bug obtaining the SMIA-I KB registration configuration in SMIA agents (capital letters were not taken into account, corrected in booting state).
- Fixed a bug in CSS-SMIA ontology submodel plugin for AASX Package Explorer (semantic identifiers for ``accessibleThrough`` relationships were incorrectly defined).
- Fixed EHU acronym in ReadTheDocs and GitHub.
- Fixed bug in SMIA PE starter (added first the SMIAPEGUIBehaviour before the BPMNPerformerBehaviour, since the latter uses variables established by the former).
- Fixed missing concepts in SMIA CSS qualifiers presets for AASX Package Explorer resources (``additional_resources/aasx_package_explorer_resources/SMIA-css-qualifier-presets.json``).



## v0.3.1

This release of Self-configurable Manufacturing Industrial Agents (SMIA) comes with an upgrade of the solution in terms of the organization of related developments within the GitHub project and fixes for some bugs in the software startup. 

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- Added published article reference proposing the SMIA approach in GitHub README and ReadTheDocs documentation.
  - [Self-configurable Manufacturing Industrial Agents (SMIA): a standardized approach for digitizing manufacturing assets](https://doi.org/10.1016/j.jii.2025.100915)
- Added last version of SMIA Operator code as ``additional tool``.
- Added all files of SMIA use case for CeDRI demonstrator in ``use_cases`` folder.
- Added option in properties file to specify whether or not to register with the SMIA-I KB.
  - Added also Docker option via environmental variable to specify it.
- Developed scripts for SMIA performance tests (scaling, AAS and CSS complexity, negotiation and benchmarking tests)

### Major Changes

- Restructured additional developments related to the SMIA approach within the GitHub repository:
  - Restructured ``additional_tools``, distinguishing between extended agents and infrastructure components.
    - The extended agents include SMIA PE, SMIA HI, and SMIA Operator.
    - The infrastructure components include SMIA-I KB and SMIA ISM.
    - The Camunda Modeler plugin is also added as an additional tool.
  - The ``additional_resources`` folder maintains the remaining SMIA-related developments: visual resources, CSS-SMIA ontology with the OWL file, AASX Package Explorer resources...
- Cleaned code from the analysis of Codacy.
- Improved self-configuration processing time x4, by reducing waiting time to show the progress bar increase.
  

### Fixed errors

- Updated SMIA dependencies versions in README and RTD documentation.
- Fixed and completed description of project structure in README file.
- Fixed SMIA startup via the CLI launcher (the AAS ID argument was not being obtained). 
- Fixed the obtaining of the OWL ontology from the AASX during SMIA startup, if so defined in the properties file.


## v0.3.0

This release of Self-configurable Manufacturing Industrial Agents (SMIA) comes with a significant upgrade of the solution in terms of flexible manufacturing automation using the SMIA approach. Version 0.2.x of SMIA focused on asset integration, and version 0.3.x will focus on autonomy and flexible manufacturing (where the interaction of multiple SMIA instances and the need for new infrastructure arise).

This specific release introduces new components within the SMIA ecosystem that enable flexible manufacturing automation. These new components are:
- ``SMIA KB``: This is an infrastructure component for a Knowledge Base (KB). It is an OWL ontology instance management database based on the CSS model. This infrastructure provides HTTP access following the OpenAPI standard specification.
- ``SMIA ISM``: This is a "special" SMIA agent in charge of managing all the infrastructure services that may be requested by SMIA instances. In other words, it offers the possibility of receiving requests for infrastructure services via FIPA-ACL, executing them and returning the response. In the validated case study it is used for the interaction between the ACL environment (SMIA instances) and HTTP-OpenAPI (SMIA KB and AAS Repository).
- ``SMIA PE``: This is a "special" SMIA agent able to collect a flexible production plan serialized in BPMN and carry it out by performing the necessary interactions with the other SMIA instances or with the infrastructure services (through the SMIA ISM).
- ``SMIA HI``: This is an extension of SMIA agent that provides a human interface (HI) so that a human can be an additional production asset. It is capable of submitting CSS requests and picking up completed ones via web GUI.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- All the code of the newly developed components has been added
  - SMIA KB, SMIA ISM, SMIA PE, SMIA HI.
  - Their developments have been done in individual branches, which have been integrated into the main at the end of their development.
  - All of them have been added inside the ``additional_tools`` folder.
- The SMIA plugin code for the Camunda Modeler software has been added.
  - This plugin is able to collect the CSS ontology information from the SMIA KB and present it to the user during the design of the BPMN flow (which will represent the flexible production plan).
- Added option to set the AAS ID (instead of the path to the AAS model file)
  - Added option as CLI, environment variable (Docker) and via code (``smia.load_aas_id``).
  - If the ID is set, and not the model file, the AAS model is obtained through an infrastructure service to SMIA ISM (it will obtain the whole AAS model from the AAS Repository)
- Added more precision in saved timestamps for SMIA performance evaluation (new method ``get_current_timestamp_microsecs`` in GeneralUtils)
- Added code to generate JSON objects from ontology instances for CSS elements. Added also the method to use this JSONs to register all the CSS elements extracted in the self-configuration in the SMIA KB

### Major Changes

- The additional software within the SMIA ecosystem has been divided into two folders
  - ``additional_resources``: several additional static resources will be grouped here, such as the CSS-SMIA ontology OWL file, visual resources, etc.
  - ``additional_tools``: several software programs developed within the SMIA ecosystem will be grouped here: SMIA KB, ISM, PE, HI, Camunda plugin...
- The versions of some SMIA dependencies have been upgraded (regarding SPADE, other versions have had to be adapted for the software to function correctly)
  - SPADE from v3.3.3 to v4.0.3
  - Basyx-python-sdk to v1.2.1
  - Owlready2 to v0.48
- Added explanation in SMIA RTD ``Extension guide`` on how to correctly add agent services that are defined inside Python classes (need to be added with the "self" included in the executable method)
- Added adaptation of complex parameters in ``get_adapted_service_parameters`` for services_utils

### Fixed errors

- Ontology file loading bug fixed: before if the properties file was not set, it always looked for the ontology inside the AASX, now it looks for it in the SMIA Archive.
- Added ServerConnectionError handling during HTTP requests (connection with HTTP-based assets)
  - For cases, e.g., in which the server suddenly is disconnected
- Fixed an error obtaining the agent identifier from the agent JID with SPADE version >4.x.x (now the ``acl_smia_messages_utils.get_agent_id_from_jid`` method is used)
- Fixed some circular imports error when creating SMIA documentation with Sphinx (for ReadTheDocs)

## v0.2.4

This release of Self-Configurable Manufacturing Industrial Agents (SMIA) comes with an upgrade of the solution in terms of interaction between different SMIA instances.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- A class for AAS services information (``aas_services_info``) has been added.
- The possible interactions between SMIA instances have been analyzed and a new ACL message structure for the SMIA approach has been proposed.
  - This proposal will be used for all SMIA instances.
  - The proposal is based on FIPA-ACL, integrating the FIPA performatives and proposing ontologies based on the different AAS services defined in the Functional View of AAS.
- JSON schemas have been added within SMIA for the new structures of ACL messages.
  - These schemas will be used to both validate incoming messages and create new ones to be sent.
  - Added a method to check ACL-SMIA messages with the new JSONSchemas in ``inter_aas_interactions_utils``.
  - Added util code to interactions between SMIA instances: create message from received ones, create message body using JSONSchemas...
- Improved JSONSchema for AAS ModelReferences. Now it can be defined in object (as defined in the AAS meta-model) or in String (e.g., as copied from the AASX Package Explorer).
- Added code into ``HTTPAssetConnection`` to send POST requests with the service data in the body, serialized by the specified content type.
- Added method to register the SMIA instance itself in the SMIA KB using by requesting an AAS infrastructure service.
- Improved distributed negotiation algorithm in FIPA-CNP management of SMIA (situations whit negotiation value tie).
A seeded randomization process is now performed to manage the tie and obtain a random winner (the same for all instances managing the same specific tie).

### Major Changes

- Changed ``inter_aas_interactions_utils`` to ``inter_smia_interactions_utils``
- The additional resource ``GUI Agent`` has been improved by adding the new structure for ACL message for interactions between SMIA instances
- Added possibility to determine the affected element in ServiceRequestExecutionErrors
- Modified all the ACL receiving methods and behaviours (ACLHandling, Negotiation…) with the new structure of ACL-SMIA message and the new approach to handle the interactions (depending on the ontology, its associated behaviour is added)
- Modified the handling of AAS related services with the new approach and new ACL-SMIA message schemas: to handle asset-/agent-related services and AAS Services (discovery)
- Modified the handling of CSS related services with the new approach and new ACL-SMIA message schemas: received JSON validation, capability checking and capability execution
- Modified SMIA negotiation code (management of FIPA-CNP protocol) with the new structures of FIPA-SMIA-ACL messages
Added ``CapabilityChecking`` in the FIPA-CNP management. In case it failed, SMIA instance returns Refuse message and it will have -1.0 negotiation value to lose against all the participants

### Fixed errors

- Fixed a bug during the self-configuration of an AAS without agent capabilities
  - SMIA was trying to add non-existing elements
- Fixed an error in the method to serialize service input data into HTTP request body
- Fixed an error in HTTPAssetConnection by adding body content to the HTTP POST requests
- Fixed error during saving information in log files (now the ontology values are used to determine the log file for each type of service)
- Fixed error when receiving ACL message with non JSON body (e.g. in an Inform message)
- Modified ``simple_human_in_the_mesh`` and ``cooperative_transport_logistics`` use cases deployment files to set v0.2.2 of SMIA as base Docker image
  - To avoid errors due to future developments of the source code
- Fixed README files regarding the links to SMIA ReadTheDocs project
- Fixed error executing agent services defined both as asynchronous and as static methods
- Fixed a problem in capability checking (constraints were checked although the capability did not have them)

## v0.2.3

This release of Self-Configurable Manufacturing Industrial Agents (SMIA) comes with an upgrade of the solution in terms of validation and accesibility. 

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- All relevant tests have been conducted with the first case study (SMIA operator and transport robots within the “Cooperative transport logistics” case).
- The tutorials for SMIA (AAS development, SMIA extension and deployment of the “Cooperative transport logistics” case study) have been completed.
- CSS-SMIA ontology has been published in w3id: now using the IRIs in the browser you can access the SMIA GitHub.
- Improved RTD glossary:
  - Added more terms.
  - Improved explanations of each term.
- Added SMIA approach PDF and demo video as additional resource.
- Created branches for additional infrastructure services development: SMIA KB (``smia_kb_development``) and Camunda plugin (``camunda_plugin_development``).

### Major Changes

- Renamed ``additional_tools`` folder to ``additional_resources``.
- Renamed additional resources folder ``capability_skill_ontology`` to ``css_smia_ontology``.
- Changed I4.0 SMIA to SMIA:
  - Both on GitHub and on ReadTheDocs.
  - Updated all files that contain the old name (PyPI configuration files, READMEs…).
- Modified SMIA banner style. 
- Upgraded “basyx-python-sdk” dependency to its latest version (1.2.0).

### Fixed errors
- Fixed bugs during testing of CSS-based AAS development tutorial
- Removed old Kubernetes test files (YAML deployment files in “examples” folder)
- Removed tests with CSS-SMIA ontology from “additional_resources/css_smia_ontology/tests” folder
- Removed code from old SMIA approach: folder with the different AAS Cores
- Removed ``deploy`` folder: contained deployment files of the old SMIA approach
- Modified README file to improve the important message in the “Usage” section mentioning the validations being conducted with the use cases.

## v0.2.2

This release of Self-Configurable Manufacturing Industrial Agent (SMIA) comes with an upgrade of the solution. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- SMIA now is available as pip package in PyPI and TestPyPI 
  - In the previous version the package was generated and uploaded manually 
  - In this version it is automatically created with GitHub Actions and uploaded to both PyPI and TestPyPI. 
- The first use case for SMIA with the new approach (from ``v0.2.0``) has been started its development 
  - An SMIA operator has been developed taking advantage of the SMIA extension methods. 
    - The related resources (code for the new capability, HTMLs for the operator dashboard) have been developed. 
  - Some SMIAs for transport robot assets have been deployed. 
  - The required AASs for the different types of assets (operator and transport robot) have been developed.  
  - First tests with transport requests and negotiations in case of multiple robot options have been performed. 
- The SMIA ReadTheDocs documentation project has been improved 
  - New guides developed such as SMIA Extension  
- A new SMIA launcher for SMIA deployments based on Docker containers (``smia_docker_starter.py``)

### Major Changes 

- The SMIA ReadTheDocs documentation project file have been improved 
  - Improved guides such as start-up SMIA 
  - The glossary has been considerably improved by adding multiple terms useful for understanding the SMIA approach 
- Removed all old code related to the AAS Manager-Core approach (prior to ``v0.2.0``) 
  - Removed unused objects like interaction_id, all related methods only used in the old approach... 
- The README for PyPI has been improved:  
  - Added some examples  
  - Added explanations of the modules  
  - Added explanations of the extension methods  

### Fixed errors

- Added OWL ontology file for the CSS model in Docker SMIA images in case the user does not add it in AASX (AAS model associated to SMIA).  
- Fixed problem with displaying AAS model analysis results with no parsed CSS model elements. 
- Fixed bugs with tests with invalid AAS models. 
- Fixed bugs with invalid ontology tests. 
- Fixed an error when SubmodelService with ExternalReference is requested. 

## v0.2.1

This release of I4.0 Self-Configurable Manufacturing Industrial Agent comes with an upgrade of the new approach added in version 0.2.0 of the solution. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes two launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_ and _smia_starter.py_.

### Features

- Information about the software during runtime is now stored in the Archive.  
  - The log has been structured to store different types of information (status of executions and errors).  
  - The status of completed requests for services and capabilities is also stored. 
    - Information about errors occurred during requests is also stored with the type of the error. 
- There are new ways to run the software  
  - PyPI package to install SMIA and run it directly (accessible on TestPyPI) 
  - Docker container with SMIA installed to run it passing only the AAS model as environment variable. 
    - Los Dockerfiles con los que se han generado están disponibles en la carpeta ``docker`` 
    - Two types of images are provided: a lightweight image based on Python Alpine (``smia/alpine-*``) and a full image based on generic Python (``smia/full-*``).   
  - Docker Compose for efficient deployment with all required infrastructure 
    - Comes with an XMPP server that can be used to communicate with different SMIAs  
- Now it is possible to extend the software through extension methods that allow you to add your own code to the SMIA base.  
  - It is offered through a new agent called ``ExtensibleSMIAAgent``.  
  - It is accessible through the PyPI package or by downloading the source code.  
- New guides have been added to the associated ReadTheDocs documentation platform to help developers and users get integrated into the SMIA ecosystem  
  - A SMIA start-up guide has been developed. 

### Major Changes 

- The code of the negotiation capability has been modified with the new approach (the one added in version ``v0.2.0``). 
  - Negotiation is now an agent capability and is managed as such. 
- The open source project has been completed with the remaining files such as contributing, release notes, about the project, code of conduct or templates for issues. 
  - Both on GitHub and on ReadTheDocs 
- Progress has been made in the removal of old code related to the AAS Manager-Core approach (prior to version ``v0.2.0``). 	

### Fixed errors

- Changed library for HTTPAssetConnection from ``requests`` to ``aiohttp``. 
  - Requests is a library for synchronous program, so it was blocking all software waiting for server response. 
  - With aiohttp now software is able to perform other tasks while waiting for HTTP server response (e.g. pick up other ACL requests) 
- Fixed a bug in the ``load_aas_model`` method of the smia package: it did not use the file passed, now it copies the file into the archive to use it as AAS model 
  - Did not allow to start correctly the code 
- Fixed problem with ``capability_skill_module`` module during Sphinx documentation generation due to ontology Python object 
  - A condition has been added to fix the problem during Sphinx generation. 
- Fixed problem with inheritance of SMIA extended classes from Basyx AAS classes


## v0.2.0

This release of I4.0 Self-Configurable Manufacturing Industrial Agent comes with a new approach for the solution. That is the reason why the software has been upgraded to version 0.2.x. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes two launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_ and _smia_starter.py_.

### Features

- New additional tools:
  - A reader capable of parsing an AAS model based on a given OWL ontology.
  - The JSON files to extend the AASX Package Explorer software with the Capability-Skill-Service (CSS) model.
  - The ontology for the Capability-Skill-Service (CSS) model in an OWL file. Some ExtendedClasses implemented in Python are also provided.
  - A SPADE agent with an easy-to-use graphical interface. This agent provides several useful functionalities for SMIA usage and execution.
- SMIA can be run with several launchers offered with the source code.
  - smia_cli_starter.py: SMIA can be run with a simple configuration by setting the AAS model with "-m" or "--model" attribute and the SPADE configuration with "-c" or "--config"
  - smia_starter.py: provides some methods to load the AAS model or the SPADE configuration file by passing the path.
- This new approach focuses on the integration of the Capablity-Skill-Service (CSS) model, implemented as an OWL ontology.
- SMIA now self-configures using an AAS model based on an OWL ontology that represents the CSS model.
  - It can create ontology instances with the CSS model information added in the AAS model.
  - So now the structure of the AAS model is not constrained, only the CSS model concepts need to be added using semantic identifiers.
- SMIA can handle two types of interactions:
  - Service requests, with new kinds such as submodel services.with new kinds such as submodel services.
  - Capability requests, related to the CSS model.
- SMIA now integrates assets with communication protocol utility logic within its source code.
  - An abstract "AssetConnection" class has been defined, with some general methods to extend it with the necessary communication protocols.
  - Asset integration for HTTP has been developed in this version.


### Major Changes 

- The name of the approach has changed from "I4.0 Standardized Microservice-based Industrial Agent" to "I4.0 Self-Configurable Manufacturing Industrial Agent". The acronym of SMIA is retained.
- The AAS Core disappears. The logic for asset integration and connection has been added in the AAS Manager.
  - Now the asset connection is defined within SMIA by extending a common abstract class.
- With the removal of AAS Core, the Intra AAS interactions through Kafka have also disappeared.
- The AAS Manager as a concept disappears. In the new approach, the software is AAS-compliant, so there is now only SMIA as software solution.
  - The approach is also based on the CSS model implemented as an OWL ontology.
- The software can now entirely self-configure by using only a valid AASX Package.
  - The structure of the AAS model within the AASX is now unconstrained, only the required CSS model semantic identifiers need to be added.
- The management of FIPA-ACL request messages has been changed, as there are now two types: service requests (i.e. submodel service) and capability requests (i.e. execute a capability through a specific skill and skill interface).

### Fixed errors

- Fixed Sphinx code autodocumentation with some modules.
- Fixed errors during the execution of the software with the development of exception to manage them.
  - AAS model reading errors, asset connection errors…

## v0.1.3

Fourth release of I4.0 Standardized Microservice-based Industrial Agent (I4.0 SMIA) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Cores: The source code of the three AAS Cores developed for this release: Numerical AAS Core (developed in Java, so the JAR file (`Numerical_AAS_Core.jar`) is provided), OPC UA AAS Core (Python modules, including the `main.py`) and ROS AAS Core (Python modules, including the `main.py`).

### Features

- New additional tools:  
  - A reader capable of transforming an AAS definition in XML (following the RAMI 4.0 meta-model) into structured Python objects. 
  - A reader capable of reading AASX files and getting the submodels fromt the AAS definition. 
- The AAS Manager and the AAS Core can be run individually, as the interaction between them has been changed to be done through Kafka. 
- The AAS Manager can handle service request from the AAS Core. 
- The AAS Manager can handle negotiation requests. 
  - The AASs can participate in negotiation with different criteria using a distributed algorithm. 
- The AAS Core for physical assets has been improved: for ROS transport robots and a Warehouse managed by a PLC with OPC UA server. 
- First proactive AAS with logical asset to perform a production management application. 
  - The AAS Core defines the relation between the AASs of the I4.0 System in order to produce an industrial application. 
  - The first developed application has been in a use case of a transport process to store product to a warehouse using transport robots. 


### Major Changes 

- Changed GitHub repository name from "Component_I4.0" to "I4.0 SMIA".
- The interaction between the AAS Manager and the AAS Core is perform through Kafka. 

### Fixed errors

- Fixed ReadTheDocs project with the new name of the GitHub repository (I4.0 SMIA).
- Fixed AAS Manager managing some service requests with unsupported format.

## v0.1.2

Third release of I4.0 Standardized Microservice-based Industrial Agent (I4.0 SMIA) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Cores: The source code of the three AAS Cores developed for this release: Numerical AAS Core (developed in Java, so the JAR file (`Numerical_AAS_Core.jar`) is provided), OPC UA AAS Core (Python modules, including the `main.py`) and ROS AAS Core (Python modules, including the `main.py`).

### Features

- AAS Manager is a SPADE agent parameterized with physical or logical assets. 
- AAS Manager has a Finite State Machine (FSM) to add behaviours in each state of the agent. 
   - This FSM depends on the type of the asset. 
- AAS Manager is capable of managing FIPA-ACL requests for executing asset related services and for negotiating (for latter the algorithm is not yet integrated ). 
- AAS Manager and AAS Core are able to interact and synchronized between them. 
- Two new AAS Cores have been developed and added in this version 
   - An AAS Core to work with ROS: able to interact with ROS nodes and to communicate with physical robots. In the tested use case a simulation of a Turtlebot 3 has been used. 
   - An AAS Core to work with OPC UA: able to interact with a OPC Servers. It has been tested with a server running on a Siemens PLC that manages a warehouse simulated in Factory I/O. 

### Major Changes 

- The AAS Manager gets its ID form the associated configmap
   - Due to the deployment of multiple AASs 
- AAS Manager and AAS Core have FSMs to synchronize with each other. 

### Fixed errors

- AAS Manager can handle ACL messages using template with multiple options 
   - For example, to negotiation requests different performative can be used 
- AAS Manager and AAS Core initialization fixed: bugs with status JSON file 
- Fixed some links a content related to the documentation

## v0.1.1

Second release of I4.0 Standardized Manufacturing Component (I4.0 SMC) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Core: Example of AAS Core for for the numerical services functionality. Developed in Java, so the JAR file (`AAS_Core.jar`) is provided.

### Features

- AAS Manager is a SPADE agent.
- AAS Manager has a Finite State Machine (FSM) to add behaviours in each state of the agent.
- AAS Manager is able to initialize all required files to allow interaction with the AAS Core.
- AAS Manager is capable of managing FIPA-ACL requests.
- AAS Manager and AAS Core are able to interact between them.
- AAS Manager and AAS Core are synchronized at startup.
- AAS Manager can request services from AAS Core.
- AAS Core is able to offer services related to numbers.

## v0.1.0

First release of I4.0 Standardized Manufacturing Component (I4.0 SMC) with the source code in a ZIP file. Content of ZIP file:

### Source code

> AAS Manager: Python main file (`main.py`) and required files (inside `utilities` folder).
> AAS Core: Example of AAS Core for for the numerical services functionality. Developed in Java, so the JAR file (`AAS_Core.jar`) is provided.

### Features

- AAS Manager is capable of managing HTTP requests.
- AAS Manager and AAS Core are able to interact between them.
- AAS Manager can request services from AAS Core.
- AAS Core is able to offer services to work with numbers.

