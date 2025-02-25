"""
This is the SMIA launch file for CLI, which executes the program logic from the command and gets the AAS model from the
arguments.
"""

import logging
import os
import sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))    # To run in CLI (executing in 'src' folder)

import smia
from smia.agents.smia_agent import SMIAAgent
from smia.agents.smia_app_agent import SMIAAppAgent
from smia.agents.smia_resource_agent import SMIAResourceAgent
from smia.utilities import smia_archive_utils
from smia.utilities import properties_file_utils
from smia.utilities.general_utils import CLIUtils

# XMPP_SERVER = 'worker4'
# XMPP_SERVER = 'ejabberd'

_logger = logging.getLogger(__name__)

def main():
    # First, the command line arguments are obtained
    init_config, aas_model = CLIUtils.get_information_from_cli(sys.argv[1:])
    smia_archive_utils.save_cli_added_files(init_config, aas_model)

    # It is checked and saved the command line arguments
    CLIUtils.check_and_save_cli_information(init_config, aas_model)

    # The AAS_ID will be set in the associated ConfigMap, within the general-information of the AAS
    aas_id = properties_file_utils.get_dt_general_property('agentID')
    passwd = properties_file_utils.get_dt_general_property('password')

    # The XMPP server of the MAS will also be set in the associated ConfiMap
    xmpp_server = properties_file_utils.get_dt_general_property('xmpp-server')

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
