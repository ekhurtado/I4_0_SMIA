SMIA Extension Guide
====================

.. _SMIA Extension Guide:

The objective of this guide is to assist in the extension of SMIA through the different extension mechanisms offered. The goal of SMIA extensibility, understood as the introduction of new functionalities without modifying the underlying base, is to provide future enhancements in the form of increased autonomy and intelligence and greater adaptability to new use cases.

To this end, the different SMIA extension mechanisms try to offer extensibility in three key aspects of the approach:

- Defining and adding **new connections to the asset** (i.e., new communication protocols): in order to be able to integrate as many assets as possible.
- Define and add **new agent capabilities**: in order to be able to increase the autonomy and intelligence of SMIA as an industrial agent.
- Define and add **new agent services**: since the execution of capabilities based on the CSS model is performed by an asset or agent service in the last instance, and agent services are SMIA's own functional code, it is possible to add new functionalities in the form of agent services.

Each mechanism will be detailed individually below with the addition of source code examples for clarity of concepts.

Before being able to use the SMIA extension mechanisms, it is necessary to use a special agent called ``ExtensibleSMIAAgent``. The following code represents a ``launcher`` for a SMIA extension case.

.. code:: python

    import smia
    from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent

    def main():
        # First, the initial configuration must be executed
        smia.initial_self_configuration()

        # The AAS model is added to SMIA
        smia.load_aas_model(<path to the AAS model>)

        # Create and run the extensible agent object
        my_extensible_smia_agent = ExtensibleSMIAAgent(<jid of SMIA SPADE agent>, <password of SMIA SPADE agent>)
        smia.run(my_extensible_smia_agent)

    if __name__ == '__main__':
        main()

.. seealso::

    The ExtensibleSMIAAgent source code is available within the API documentation section: :py:mod:`smia.agents.extensible_smia_agent.ExtensibleSMIAAgent`.

Adding new asset connections
----------------------------

SMIA can be extended to integrate assets with new communication protocols by adding new asset connections using the :bdg-primary-line:`add_new_asset_connection()` method (see in :py:mod:`API documentation <smia.agents.extensible_smia_agent.ExtensibleSMIAAgent.add_new_asset_connection>`). This method presents the following parameters in order to properly extend SMIA:

- *aas_interface_id_short* (string): this is the identifier of the new interface within the AAS model. Because all asset connections are grouped in the “AssetInterfacesDescription” Submodel, they are distinguished by the ``id_short`` attribute.
- *asset_connetion_class* (Python class instance): this parameter represents the class instance of the new asset connection. Like all asset connection classes, it must be inherited from the ``AssetConnection`` class and implement all its abstract methods (see in :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection>`).

Once the values for these two parameters are achieved, it is possible to add a new asset connection using the following code (it has been assumed that the class that inherits AssetConnection and implements all its methods is defined in an external module).

.. dropdown:: Source code example for adding a new asset connection
    :octicon:`code;1em;sd-text-primary`

    .. code:: python

        import smia
        from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
        from my_asset_connections import NewAssetConnection

        def main():
            smia.initial_self_configuration()
            smia.load_aas_model(<path to the AAS model>)
            my_extensible_smia_agent = ExtensibleSMIAAgent(<jid of SMIA SPADE agent>, <password of SMIA SPADE agent>)

            # The instance of the new asset connection class is created and added to SMIA
            new_asset_connection_class = NewAssetConnection()
            my_extensible_smia_agent.add_new_asset_connection('new_aas_interface_id_short', new_asset_connection_class)

            smia.run(my_extensible_smia_agent)

        if __name__ == '__main__':
            main()

Creating new AssetConnection class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the above example it is assumed that the new AssetConnection class has already been developed. Since the new class instance to be added must inherit from the ``AssetConnection`` class and implement all its abstract methods, the following source code is shown in order to clear the necessary methods to be implemented. The source code is explained below.

.. dropdown:: Source code example for new AssetConnections
    :octicon:`code;1em;sd-text-primary`

    .. code:: python

        from smia.assetconnection.asset_connection import AssetConnection

        class NewAssetConnection(AssetConnection):

            def __init__(self):
                # If the constructor will be overridden remember to add 'super().__init__()'.
                pass

            async def configure_connection_by_aas_model(self, interface_aas_elem):
                pass

            async def check_asset_connection(self):
                pass

            async def connect_with_asset(self):
                pass

            async def execute_asset_service(self, interaction_metadata, service_input_data=None):
                pass

            async def receive_msg_from_asset(self):
                pass

    - ``__init__()``: The constructor of the new class can be added. For instance, the type of ``ArchitectureStyle`` (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.ArchitectureStyle>`) can be determined to be used at runtime.
    - ``configure_connection_by_aas_model()``: within this method you can add the necessary code to correctly configure the asset connection from the data in the AAS model (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.configure_connection_by_aas_model>`).
    - ``check_asset_connection()``: within this method you can add the necessary code to check the asset connection with the asset (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.check_asset_connection>`).
    - ``connect_with_asset()``: within this method you can add the necessary code to correctly connect with the asset through this asset connection (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.connect_with_asset>`).
    - ``execute_asset_service()``: within this method you can add the necessary code to correctly execute an asset service through this the asset connection from the data in the AAS model and the optional data of a CSS-related request such as the values of input parameters (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.execute_asset_service>`).
    - ``receive_msg_from_asset()``: within this method you can add the necessary code to correctly obtain a message from the asset through this asset connection (see :py:mod:`API documentation <smia.assetconnection.asset_connection.AssetConnection.receive_msg_from_asset>`).

Adding new agent capabilities
-----------------------------

SMIA can be extended to increased the autonomy and intelligence of the software by adding new agent capabilities using the :bdg-primary-line:`add_new_agent_capability()` method (see in :py:mod:`API documentation <smia.agents.extensible_smia_agent.ExtensibleSMIAAgent.add_new_agent_capability>`). This method presents one parameter in order to properly extend SMIA:

- *behaviour_class* (Python class instance): this parameter represents the SPADE behavior that will be added to SMIA and executed simultaneously with the other behaviors.

The autonomy of the industrial agents is provided by the so-called *behaviors*. SPADE presents different classes for different types of behaviors, depending on the type of execution (i.e. cyclic, unique...): ``CyclicBehaviour``, ``PeriodicBehaviour``, ``OneShotBehaviour``, ``TimeoutBehaviour``, ``FSMBehaviour``. All of them are detailed in the `official SPADE documentation <https://spade-mas.readthedocs.io/en/latest/behaviours.html>`_.

Once the desired behaviour classes for new agent capabilities are developed, it is possible to add them using the following code (it has been assumed that the behaviour classes are defined in an external module).

.. dropdown:: Source code example for adding a new agent capability
    :octicon:`code;1em;sd-text-primary`

    .. code:: python

        import smia
        from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
        from my_agent_capabilities import NewCyclicBehaviour, NewOneShotBehaviour

        def main():
            smia.initial_self_configuration()
            smia.load_aas_model(<path to the AAS model>)
            my_extensible_smia_agent = ExtensibleSMIAAgent(<jid of SMIA SPADE agent>, <password of SMIA SPADE agent>)

            # The instance of the new agent capability classes are created and added to SMIA
            new_cyclic_agent_capability = NewCyclicBehaviour()
            new_oneshot_agent_capability = NewOneShotBehaviour()
            my_extensible_smia_agent.add_new_agent_capability(new_cyclic_agent_capability)
            my_extensible_smia_agent.add_new_agent_capability(new_oneshot_agent_capability)

            smia.run(my_extensible_smia_agent)

        if __name__ == '__main__':
            main()

Adding new agent services
-------------------------

SMIA can be extended by adding new functionalities in the form of new agent services using the :bdg-primary-line:`add_new_agent_service()` method (see in :py:mod:`API documentation <smia.agents.extensible_smia_agent.ExtensibleSMIAAgent.add_new_agent_service>`). This method presents the following parameters in order to properly extend SMIA:

- service_id* (string): in this parameter you have to add the identifier of the SubmodelElement inside the AAS model. Depending on the type of element it will be the ``id`` or ``id_short`` (generally this one because the agent services are simple SubmodelElement). This identifier will be used when executing a skill of a capability implemented by this service.
- service_method* (Python method): in this parameter you have to add the Python method which will be executed when the skill of the capability implemented by the agent service is requested. It is preferable to offer the executable method and it also allows adding the type of parameter values, so that SMIA automatically performs a check during its execution.

Once the desired Python methods for new agent services are developed, it is possible to add them using the following code.

.. dropdown:: Source code example for adding a new agent service
    :octicon:`code;1em;sd-text-primary`

    .. code:: python

        import smia
        from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
        from my_agent_capabilities import NewCyclicBehaviour, NewOneShotBehaviour

        async def new_asset_service_async():
            print("New asynchronous asset service without parameters.")

        def new_asset_service_with_params(param1, param2):
            print("New synchronous asset service with params: {}, {}".format(param1, param2))

        def main():
            smia.initial_self_configuration()
            smia.load_aas_model(<path to the AAS model>)
            my_extensible_smia_agent = ExtensibleSMIAAgent(<jid of SMIA SPADE agent>, <password of SMIA SPADE agent>)

            # The methods of the new agent services are added to SMIA
            my_extensible_smia_agent.add_new_agent_service('new_service_async_id_short', new_asset_service_async)
            my_extensible_smia_agent.add_new_agent_service('new_service_params_id_short', new_asset_service_with_params)

            smia.run(my_extensible_smia_agent)

        if __name__ == '__main__':
            main()

Starting-up an extended SMIA
----------------------------

As in the case of extending SMIA a new launcher is generated, it must have all the necessary resources accessible (e.g. the CSS ontology file either in the SMIA Archive or within the AASX package of the asset's AAS model). Among the different SMIA deployment methods the Docker container-based ones offer all the necessary self-contained infrastructure.

However, in the case of extending SMIA it is necessary to generate a new Docker image from the SMIA base. As the simplest method of deployment is through Docker Compose, this section will detail how to generate the Docker container for the extended SMIA and how to deploy it with Docker Compose.

Generation of the extended SMIA Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Taking advantage of the fact that the SMIA DockerHub repository offers a Docker image to be used as the basis for solutions based on the SMIA approach, this image will be collected and the generated source code files will be added.

Let's say that a Python file has been generated with the launcher named ``extended_smia_launcher.py`` and the internal logic of the extended code has been stored in ``extended_logic.py``. Using the following Dockerfile the base SMIA image (the latest release of the *alpine* type) is collected, the developed files and the necessary execution command are added.

.. code:: Dockerfile

    FROM ekhurtado/smia:latest-alpine-base

    COPY extended_logic.py /
    COPY extended_smia_launcher.py /

    CMD ["python3", "-u", "/extended_smia_launcher.py"]

.. note::

    Within the examples in the SMIA GitHub repository, there is a `folder <https://github.com/ekhurtado/I4_0_SMIA/tree/main/examples/smia_extended>`_ with all the files to generate the extended SMIA Docker image.

Starting-up the extended SMIA Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the file has been developed and stored with the name ``Dockerfile`` together with the source code files, it is possible to generate the new Docker image by executing the following command in the same directory as the files:

.. code:: bash

    docker build -t <your DockerHub user>/<your repository>:<your tag for extended SMIA> .

With the Docker image created, it is possible to upload it to DockerHub (``> docker push <image tag>``) or deploy it via Docker Compose following the process detailed in the :octicon:`repo;1em` :ref:`SMIA Start-up Guide <SMIA run Docker Compose>`.