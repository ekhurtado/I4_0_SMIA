import logging
import sys

import smia
from agents.smia_agent import SMIAAgent
from agents.smia_app_agent import SMIAAppAgent
from agents.smia_resource_agent import SMIAResourceAgent
from utilities import configmap_utils, smia_archive_utils
from utilities.general_utils import CLIUtils

# XMPP_SERVER = 'worker4'
# XMPP_SERVER = 'ejabberd'

_logger = logging.getLogger(__name__)

"""
This is the launch file of the SMIA, which runs the logic of the program.
"""


def main():
    # First, the command line arguments are obtained
    init_config, aas_model = CLIUtils.get_information_from_cli(sys.argv[1:])
    smia_archive_utils.save_cli_added_files(init_config, aas_model)

    # It is checked and saved the command line arguments
    CLIUtils.check_and_save_cli_information(init_config, aas_model)

    # The AAS_ID will be set in the associated ConfigMap, within the general-information of the AAS
    aas_id = configmap_utils.get_dt_general_property('agentID')
    passwd = configmap_utils.get_dt_general_property('password')

    # The XMPP server of the MAS will also be set in the associated ConfiMap
    xmpp_server = configmap_utils.get_dt_general_property('xmpp-server')

    # Build the agent jid and password
    agent_jid = aas_id + '@' + xmpp_server

    # Depending on the asset type, the associated SPADE agent will be created
    aas_type = ''  # For testing (TODO Get the type of the asset)
    match aas_type:
        case "physical":
            _logger.info("The asset is physical")
            smia_agent = SMIAResourceAgent(agent_jid, passwd)
        case "digital":
            _logger.info("The asset is logical")
            smia_agent = SMIAAppAgent(agent_jid, passwd)
        case _:
            _logger.info("The asset is not defined, so it is a generic SMIA")
            # Create the agent object
            smia_agent = SMIAAgent(agent_jid, passwd)

    smia.run(smia_agent)

if __name__ == '__main__':

    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # Run main program with SPADE
    main()
