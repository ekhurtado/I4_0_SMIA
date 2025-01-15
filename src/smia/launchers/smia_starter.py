import logging

import smia
from smia.agents.smia_agent import SMIAAgent


_logger = logging.getLogger(__name__)

"""
This is the launch file of the SMIA, which runs the logic of the program.
"""


def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # Then, the AASX model is added
    smia.load_aas_model('../examples/SMIA_TransportRobot_with_OWL.aasx')
    # smia.load_aas_model('../smia_archive/config/SMIA_TransportRobot_with_OWL.aasx')

    # Create the agent object
    # smia_agent = SMIAAgent("gcis2@xmpp.jp", "gcis1234")
    smia_agent = SMIAAgent()
    smia.run(smia_agent)

if __name__ == '__main__':

    # Run main program with SMIA
    main()
