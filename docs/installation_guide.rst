Installation guide
==================

This guide is a comprehensive utility to properly install and configure the necessary tools for the :term:`SMIA` software. For a better understanding of the software, the guide is divided into several subsections, each showing one of the tools.


AASX Package Explorer
---------------------

.. _AASX Package Explorer:

The `AASX Package Explorer <https://github.com/eclipse-aaspe/package-explorer>`_ is is a viewer and editor for the Asset Administration Shell (:term:`AAS`). It is licensed under the Apache License 2.0 and it is available for Windows 10+ based systems.

.. image:: _static/images/AASX_Package_Explorer_1.png
  :align: center
  :width: 400
  :alt: AASX Package Explorer initialization window

Software installation
~~~~~~~~~~~~~~~~~~~~~

For installing the AASX Package Explorer the binaries are provided in the project `releases <https://github.com/eclipse-aaspe/package-explorer/releases>`_ section of GitHub.

.. tip::

    Up to now, the latest version of the software is the `v2024-06-10.alpha <https://github.com/eclipse-aaspe/package-explorer/releases/tag/v2024-06-10.alpha>`_. The ZIP file with all necessary files can be downloaded from the `aasx-package-explorer.2024-06-10.alpha.zip <https://github.com/eclipse-aaspe/package-explorer/releases/download/v2024-06-10.alpha/aasx-package-explorer.2024-06-10.alpha.zip>`_.

Software configuration
~~~~~~~~~~~~~~~~~~~~~~

Once the AASX Package Explorer is installed, it is necessary to update some configuration files to add the necessary resources for the correct operation of SMIA.

Adding the custom submodel templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AASX Package Explorer allows adding custom submodel templates in the form of plugins. With this feature, submodels can be easily created automatically. All new submodel templates must be added as ``AasxPluginGenericForms``.

In the case of the SMIA approach, a submodel has been developed with all necessary semantic identifiers to easily import all ConceptDescriptions with semantic identifiers related to the Capability-Skill-Service ontology used at runtime.

To do so, first the JSON object with the submodel template definition will be collected, available in the `GitHub as additional tool link <"https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/capabilityskill_tests/additional_tools/aasx_package_explorer_resources/SMIA-css-semantic-ids-sm.add-options.json>`_.

.. TODO CUIDADO, CUANDO SE PASE ESTE BRANCH AL MAIN ACTUALIZAR LOS LINKS AL GITHUB

When the JSON object is obtained, it is necessary to copy it to the following path, relative to where the AASX Package Explorer has been installed:

    * <path to AASX Package Installation>/plugins/AasxPluginGenericForms/

Once the file is copied there, the next time the program is initialized, the submodel can be easily created from the options: ``Workspace > Create ... > New Submodel from plugin``, or by pressing ``Ctrl + Shift + M``.

Adding the qualifier templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Another useful feature is to add presets to Qualifier elements, in order to use them easily without the need to add information from the user. To do this, in this case another JSON file will be added to an existing program configuration file. The JSON objects with the qualifier presets for SMIA are available as `GitHub additional tool <https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/capabilityskill_tests/additional_tools/aasx_package_explorer_resources/SMIA-css-qualifier-presets.json>`_.

In this case, the content of the JSON file should be copied and pasted to the end of the ``qualifier-presets.json`` configuration file available in the same installation folder as the program executable.

.. warning::

    Be careful, the JSON must be valid, so consider that this configuration file is a JSON Array, and that is why the JSON content starts with ','.


Python
------

Python is the base programming language of SMIA. In order to install Python environment it is available at the `official web page <https://www.python.org/downloads/>`_.

.. tip::

    SMIA works with Python 3.7, 3.8 and 3.9, but `version 3.10 <https://www.python.org/downloads/release/python-31011/>`_ is recommended.

Python modules
~~~~~~~~~~~~~~

SMIA is built in top of some required Python modules. ``Pip``, as the package installer for Python, can be used to install them.

BaSyx Python SDK
^^^^^^^^^^^^^^^^

BaSyx SDK is used by SMIA to manage the AAS model in Python. It can be installed using pip, executing ``pip install basyx-python-sdk``.

SPADE
^^^^^

SPADE is a multi-agent system platform on which the SMIA software has been built. An official installation guide is available at `<https://spade-mas.readthedocs.io/en/latest/installation.html>`_.

OWLReady2
^^^^^

OWLReady2 is used by SMIA to manage the OWL-based CSS ontology in Python. An official installation guide is available at `<https://owlready2.readthedocs.io/en/v0.47/install.html>`_.

