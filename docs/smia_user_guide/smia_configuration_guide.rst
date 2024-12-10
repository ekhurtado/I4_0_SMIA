SMIA Configuration Guide
========================

.. _SMIA Configuration Guide:

This guide is focused on the configuration of  :term:`SMIA` software. The configuration changes minimally depending on the deployment technology.

Properties file configuration
-----------------------------

This file will be used to define the entire SMIA configuration. For example, in order to run the SMIA software correctly, it is necessary to specify certain information about the infrastructure. The properties file is divided into several sections to clarify the configuration.

===============  ===============
     Section         Details
===============  ===============
    DT               Information about the software
    AAS              Information about the AAS model
    ONTOLOGY         Information about the CSS ontology
===============  ===============

The attributes of each section will be detailed in the following subsections.

Properties file: DT section
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of DT section.

===============  ===============   ===============
    Attribute         Type              Details
===============  ===============   ===============
    agentID          Mandatory         Identifier of the SPADE agent within SMIA to connect with XMPP server.
    password         Mandatory         Password of the SPADE agent within SMIA to connect with XMPP server.
    xmpp-server      Mandatory         XMPP server as required infrastructure for SPADE agent within SMIA.
===============  ===============   ===============

Properties file: AAS section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of AAS section.

=====================   ===============   ===============
    Attribute               Type              Details
=====================   ===============   ===============
meta-model.version          Optional         Version of the AAS meta-model.
model.serialization         Optional         Serialization format of the AAS meta-model ("AASX", "XML" or "JSON").
    model.folder            Optional*        Path of the folder where the AAS model can be accessed.
    model.file              Optional*        File name of the AAS model.
=====================   ===============   ===============

.. important::
    *\*:If the AAS model is not specified at the start of the SMIA software, they are mandatory. The AAS model must be defined either at software start-up or in this attribute of the properties file.*

Properties file: ONTOLOGY section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of ONTOLOGY section.

=====================   ===============   ===============
    Attribute               Type              Details
=====================   ===============   ===============
    ontology.folder          Optional*         Path of the folder where the ontology OWL file can be accessed.
    ontology.file            Optional*         File name of the OWL ontology.
=====================   ===============   ===============

.. important::
    *\*:If the ontology has not been added within the AASX package at start-up of the SMIA software, it is mandatory.*

AAS model configuration
-----------------------

The AAS model can be defined following the :octicon:`link;1em` :ref:`AAS Development Guide`. If it is decided to use AASX as the serialisation format, both the ontology file and the properties file can be added to the package.

.. TODO falta la guia de como añadir los ficheros dentro del AASX






