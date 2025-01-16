SMIA Start-up Guide
===================

.. _SMIA Start-up Guide:

The aim of this guide is to assist in the start-up of SMIA through the different methods offered. In order to make the explanations clearer, it has been decided to describe each method in detail.

Running with the source code
----------------------------

As an open source project, the source code of SMIA can be downloaded and executed using the command line interface (CLI). The source code is located inside the ``src`` folder in the :octicon:`mark-github;1em` `offical GitHub repository <https://github.com/ekhurtado/I4_0_SMIA>`_, and there are two launchers to run the software easily.

f the folder where the launchers are located is accessed, it is possible to run SMIA using a unique command:

.. code:: bash

    python3 smia_cli_starter.py --model "<path to AASX package>"

.. code:: bash

    python3 smia_starter.py

.. note::

    The launcher ``smia_starter.py`` specifies the AAS model manually, so the code must be modified. Just change the line that specifies the path to the AASX package that contains the AAS model.

.. button-link:: https://github.com/ekhurtado/I4_0_SMIA
    :color: primary
    :outline:

    :octicon:`package;1em` Official SMIA GitHub repository.

Running via PyPI package
------------------------

The SMIA approach is also available as Python package in PyPI. It can be easily installed using [pip](https://pip.pypa.io/en/stable/):

.. code:: bash

    pip install smia

The PyPI SMIA package contains all the source code and there are determined the necessary dependencies, so they can be automatically installed by pip, so it can run SMIA directly by:

.. code:: bash

    python3 -m smia.launchers.smia_cli_starter --model "<path to AASX package>"

.. button-link:: https://test.pypi.org/project/smia/
    :color: primary
    :outline:

    :octicon:`mark-github;1em` Official SMIA PyPI project.

Running via Docker container
----------------------------

The SMIA approach is also available as Docker image in DockerHub. To run SMIA software the AAS model should be passed as environmental variable:

.. code:: bash

    docker run -e model=<path to AASX package> ehu-gcis/smia:alpine-latest

.. tip::

    As explained in the official SMIA Docker Hub repository, there are two types of Docker images for SMIA. Those with the tag ``*-base-*`` can be used to build your own Docker image using SMIA as a base.

.. button-link:: https://hub.docker.com/r/ekhurtado/smia
    :color: primary
    :outline:

    :octicon:`container;1em` Official SMIA Docker Hub repository.


.. TODO FALTA POR REPASAR
