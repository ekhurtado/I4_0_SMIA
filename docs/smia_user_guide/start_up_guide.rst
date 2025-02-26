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

    docker run -v ./aas:/smia_archive/config/aas -e model=<path to AASX package> ekhurtado/smia:latest-alpine

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

In all the previous methods it is necessary to have the XMPP server accessible, as it is required because SMIA integrates the SPADE development platform, based on this protocol. In the case of not wanting to worry about the infrastructure, there are possibilities of generating a shared environment in which both SMIA and the necessary infrastructure can be deployed. The most efficient options for self-contained deployments are always related to containerized virtualization.

Docker containerization technology offers us a tool that we can use for this need: `Docker Compose <https://docs.docker.com/compose/>`_. It allows to define in a single file different Docker containers, running all of them in a shared environment and accessible through a single command.

As for the minimum infrastructure for SMIA, only an XMPP server is needed. There are several options, so in this example the `Ejabberd <https://www.ejabberd.im/>`_ server will be presented. The file that is required to be developed for Docker Compose is named ``docker-compose.yml``. Therefore, as shown below, both the SMIA Docker container and the Ejabberd XMPP server container have been added.

.. code:: yaml

    services:

      smia:
        image: ekhurtado/smia:latest-alpine
        container_name: smia
        environment:
          - AAS_MODEL_NAME=<path_to_AASX_package>
          - AGENT_ID=<agent-id>@ejabberd
          - AGENT_PSSWD=<agent-password>
        depends_on:
          xmpp-server:
            condition: service_healthy
        volumes:
          - ./aas:/smia_archive/config/aas

      xmpp-server:
        image: ghcr.io/processone/ejabberd
        container_name: ejabberd
        environment:
          - ERLANG_NODE_ARG=admin@ejabberd
          - ERLANG_COOKIE=dummycookie123
          - CTL_ON_CREATE=! register admin localhost asd
        ports:
          - "5222:5222"
          - "5269:5269"
          - "5280:5280"
          - "5443:5443"
        volumes:
          - ./xmpp_server/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml
        healthcheck:
          test: netstat -nl | grep -q 5222
          start_period: 5s
          interval: 5s
          timeout: 5s
          retries: 10

.. dropdown:: Explanation of ``docker-compose.yml``
    :octicon:`file-code;1em;sd-text-primary`

    The explanation of the ``docker-compose.yml`` file is shown in order of element appearance:

        - ``image``: where the Docker image is set. For SMIA the alpine image has been added.
        - ``depends_on``: here it is set that SMIA should not start until the XMPP server container has been successfully started.
        - ``volumes``: links the host folder to the SMIA container folder, because this is the way SMIA is made accessible for its associated AAS model.
            - Therefore, remember to copy the required AAS models into the *./aas* folder in the same location as this file.
        - ``xmpp-server``: the definition provided by the official Ejabberd page for deployment via Docker container has been added.
            - The official Ejabberd page recommends to provide the configuration file through a ``volume``, so the ``ejabberd.yml`` file is required. This file is accessible in the following link (remember to create the file with the exact name and to copy it into the *./xmpp_server* folder in the same location as the Docker Compose file):

            .. button-link:: https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/main/examples/docker_compose_deployment/xmpp_server/ejabberd.yml
                :color: primary
                :outline:

                :octicon:`mark-github;1em` Link to *ejabberd.yml* within the SMIA GitHub repository.

.. note::

    Within the examples in the SMIA GitHub repository, there is a `folder <https://github.com/ekhurtado/I4_0_SMIA/tree/main/examples/docker_compose_deployment>`_ with all the files for SMIA deployment via Docker Compose.

Once this file is defined and stored, both SMIA and the XMPP server can be deployed using a single command executed in the same directory as the ``docker-compose.yml`` file.

.. code:: bash

    docker-compose up

To stop the execution you can execute ``Ctrl+C`` and to delete the environment and the containers inside it you can execute the following command:

.. code:: bash

    docker-compose down

