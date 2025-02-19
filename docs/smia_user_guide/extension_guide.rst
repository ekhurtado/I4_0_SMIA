SMIA Extension Guide
===================

.. _SMIA Extension Guide:

TODO

Test with Python code:

.. code:: python

    import smia
    from smia.agents.smia_agent import SMIAAgent

    smia.load_aas_model('<path to the AASX package containing the AAS model>')
    my_agent = SMIAAgent()

    smia.run(my_agent)