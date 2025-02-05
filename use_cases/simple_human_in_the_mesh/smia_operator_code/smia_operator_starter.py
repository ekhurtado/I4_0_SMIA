import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils
from gui_logic import OperatorGUIBehaviour

_logger = logging.getLogger(__name__)


def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA software...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PASSWD')

    # Create the agent object
    smia_extensible_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    operator_behaviour = OperatorGUIBehaviour()
    smia_extensible_agent.add_new_agent_capability(operator_behaviour)

    smia.run(smia_extensible_agent)

if __name__ == '__main__':

    # Run main program with SMIA
    main()
