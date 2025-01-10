# Release Notes

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

