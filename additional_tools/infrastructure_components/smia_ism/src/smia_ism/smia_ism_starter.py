import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils

from smia_ism.behaviours.acl_openapi_handling_behaviour import ACLOpenAPIHandlingBehaviour
from smia_ism.utilities import general_utils

_logger = logging.getLogger(__name__)

# This is the starter file to launch the SMIA Infrastructure Services Manager software

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA ISM (Infrastructure Services Manager)...")

    # The main banner of SMIA will be replaced for the SMIA ISM banner
    smia.utilities.general_utils.GeneralUtils.print_smia_banner = general_utils.print_smia_ism_banner

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PSSWD')

    # # TODO BORRAR (para pruebas)
    # smia_jid = "gcis1@xmpp.jp"
    # smia_psswd = "gcis1234"
    # smia.load_aas_model('../smia_archive/config/aas/SMIA_InfrastructureServicesManager.aasx')

    # Create the agent object
    smia_extensible_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    operator_behaviour = ACLOpenAPIHandlingBehaviour(smia_extensible_agent)

    smia_extensible_agent.add_new_agent_capability(operator_behaviour)

    smia.run(smia_extensible_agent)


if __name__ == '__main__':

    # Run main program with SMIA
    main()
