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


