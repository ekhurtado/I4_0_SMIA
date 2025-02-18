SMIA Start-up Guide
===================

.. _SMIA Start-up Guide:

The aim of this guide is to assist in the start-up of SMIA through the different methods offered. In order to make the explanations clearer, it has been decided to describe each method in detail.

Running with the source code
----------------------------

As an open source project, the source code of SMIA can be downloaded and executed using the command line interface (CLI). The source code is located inside the ``src`` folder in the :octicon:`mark-github;1em` `offical GitHub repository <https://github.com/ekhurtado/I4_0_SMIA>`_, and there are two launchers to easily run the software by executing commands.

When the folder where the launchers are located is accessed, it is possible to run SMIA using a unique command. There are two possibilities.

.. attention::

    Make sure that the XMPP server set for SMIA is accessible from where the command is executed.

Running with CLI launcher
~~~~~~~~~~~~~~~~~~~~~~~~~

.. _SMIA_CLI_launcher:

In case you want to run SMIA using the CLI launcher, it is possible to do so using a single command if it contains the appropriate arguments. The possible arguments to add are the following:

===============  ===============  ===============   ===============
    Argument         Short              Type           Description
===============  ===============  ===============   ===============
   ``--model``       ``-m``          Mandatory         Path to the AAS model to self-configure SMIA (i.e. AASX Package).
   ``--config``       ``-c``          Optional         Path to the initial properties configuration file.
===============  ===============  ===============   ===============

So, with these arguments, SMIA can be run by simply executing the following command.

.. code:: bash

    python3 smia_cli_starter.py --model "<path to AASX package>"

Running with custom coding launcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _SMIA_coding_launcher:

The other option is to use the custom coding launcher. This option is the closest to the launcher that can be developed in the SMIA extension (a guide on this aspect is available at LINK).

To start SMIA, you can modify the ``smia_starter.py`` file to add the path to the AAS model associated with SMIA.

.. dropdown:: Source code example of ``smia_starter.py``
    :octicon:`code;1em;sd-text-primary`

    .. code:: python

        import smia
        from smia.agents.smia_agent import SMIAAgent

        def main():
            # First, the initial configuration must be executed
            smia.initial_self_configuration()

            # Then, the AASX model is added
            smia.load_aas_model('<path to AASX package>')

            # Create and run the SMIA agent object
            smia_agent = SMIAAgent()
            smia.run(smia_agent)

        if __name__ == '__main__':
            # Run main program with SMIA
            main()

    .. note::

        The launcher ``smia_starter.py`` specifies the AAS model manually, so the code must be modified. Just change the line that specifies the path to the AASX package that contains the AAS model.

Once modified and the appropriate AAS model is added, it is possible to run SMIA by simply running the Python program.

.. code:: bash

    python3 smia_starter.py

.. button-link:: https://github.com/ekhurtado/I4_0_SMIA
    :color: primary
    :outline:

    :octicon:`package;1em` Official SMIA GitHub repository.

Running via PyPI package
------------------------

The SMIA approach is also available as Python package in PyPI. It can be easily installed using `pip <https://pip.pypa.io/en/stable/>`_:

.. code:: bash

    pip install smia

The PyPI SMIA package contains all the source code and the necessary dependencies are already determined, so everything needed can be installed automatically by pip. Afterwards, SMIA can be executed by the same mechanisms as explained above with the source code (:ref:`Running with CLI launcher <SMIA_CLI_launcher>` or :ref:`Running with custom coding launcher <SMIA_coding_launcher>`). For instance, with CLI launcher:

.. code:: bash

    python3 -m smia.launchers.smia_cli_starter --model "<path to AASX package>"

.. attention::

    Make sure that the XMPP server set for SMIA is accessible from where the command is executed.

.. button-link:: https://test.pypi.org/project/smia/
    :color: primary
    :outline:

    :octicon:`mark-github;1em` Official SMIA PyPI project.

Running via Docker container
----------------------------

The SMIA approach is also available as Docker image in DockerHub. To run SMIA software the AAS model should be passed as environmental variable. There are some options as variables in order to customize the SMIA Docker containers:

==============================  ===============
    Environmental Variable         Description
==============================  ===============
      ``AAS_MODEL_NAME``            Path to the AAS model to self-configure SMIA (i.e. AASX Package): inside the given ``volume``.
      ``AGENT_ID``                  Identifier of the SMIA SPADE agent (incluyendo el servidor XMPP ``<id>@<xmpp_server>``).
      ``AGENT_PASSWD``              Password of the SMIA SPADE agent to connect with the XMPP server.
==============================  ===============

In addition, for the SMIA container to have the AAS model accessible, it must be offered through the ``volume`` resource provided by Docker. This way, we can link a folder on the host to a folder in the container.

In this case, we link the ``aas`` folder located on the same desktop where the command is executed and copy the AAS model (AASX package) into this folder. Once finished, it is possible to run SMIA by a single command:

.. code:: bash

    docker run -v ./aas:/smia_archive/config/aas -e model=<path to AASX package> ekhurtado/smia:alpine-latest

.. tip::

    As explained in the official SMIA Docker Hub repository, there are two types of Docker images for SMIA. Those with the tag ``*-base-*`` can be used to build your own Docker image using SMIA as a base.

.. attention::

    Make sure that the XMPP server established for SMIA is accessible from the Docker container.

.. button-link:: https://hub.docker.com/r/ekhurtado/smia
    :color: primary
    :outline:

    :octicon:`container;1em` Official SMIA Docker Hub repository.

Running with Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~

En el caso de no querer que preocuparse por la infraestructura, es posible utilizar la herramienta `Docker Compose <https://docs.docker.com/compose/>`_, añadiendo todo lo necesario en un único archivo y ejecutando SMIA mediante un único comando.

.. TODO FALTA POR EXPLICAR COMO ARRANCAR CON DOCKER COMPOSE (añadiendo xmpp server)


.. TODO FALTA POR REPASAR
