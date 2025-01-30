import logging


import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.agents.smia_agent import SMIAAgent
from smia.assetconnection.asset_connection import AssetConnection

_logger = logging.getLogger(__name__)

"""
This is the launch file of the SMIA, which runs the logic of the program.
"""

class NewConn(AssetConnection):

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        pass

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_skill_by_asset_service(self, interaction_metadata, skill_params_exposure_elems,
                                             skill_input_params=None, skill_output_params=None):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        pass

    async def receive_msg_from_asset(self):
        pass

    def __init__(self):
        pass



def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # Then, the AASX model is added
    smia.load_aas_model('../examples/SMIA_TransportRobot_with_OWL.aasx')
    # smia.load_aas_model('../smia_archive/config/SMIA_TransportRobot_with_OWL.aasx')

    # Create the agent object
    # smia_agent = SMIAAgent("gcis2@xmpp.jp", "gcis1234")
    # smia_agent = SMIAAgent()
    smia_agent = ExtensibleSMIAAgent()

    new_conn = NewConn()
    smia_agent.add_new_asset_connection('InterfaceForHTTP', new_conn)
    # smia_agent.add_new_asset_connection('a', new_conn)

    smia.run(smia_agent)

if __name__ == '__main__':

    # Run main program with SMIA
    main()
