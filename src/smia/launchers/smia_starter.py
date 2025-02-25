"""
This is the SMIA launch file, which executes the program logic from the command and gets the AAS model by the provided
Python methods.
"""

import logging

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.agents.smia_agent import SMIAAgent
from smia.assetconnection.asset_connection import AssetConnection

_logger = logging.getLogger(__name__)


def nuevo_svc():
    print("dsfsdffsd")

async def nuevo_svc_params(param1, param2):
    print("{}, {}".format(param1, param2))



def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # Then, the AASX model is added
    # smia.load_aas_model('../examples/SMIA_Operator_article.aasx')
    smia.load_aas_model('../examples/SMIA_TransportRobot_article_1.aasx')
    # smia.load_aas_model('../examples/SMIA_TransportRobot_without_OWL.aasx')
    # smia.load_aas_model('../examples/SMIA_tutorial_1.aasx')
    # smia.load_aas_model('../smia_archive/config/SMIA_TransportRobot_with_OWL.aasx')

    # Create the agent object
    smia_agent = SMIAAgent("gcis2@xmpp.jp", "gcis1234")
    # smia_agent = SMIAAgent()

    # smia_agent = ExtensibleSMIAAgent()
    # smia_agent.add_new_agent_service('newSvc', nuevo_svc_params)

    smia.run(smia_agent)


if __name__ == '__main__':

    # Run main program with SMIA
    main()
