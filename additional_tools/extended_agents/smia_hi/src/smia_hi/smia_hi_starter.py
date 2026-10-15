import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils

from smia_hi.behaviours.receive_acl_behaviour import ReceiveACLBehaviour
from smia_hi.behaviours.smia_hi_gui_behaviour import SMIAHIGUIBehaviour
from smia_hi.logic.smia_hi_agent_services import SMIAHIAgentServices

_logger = logging.getLogger(__name__)

# This is the starter file to launch the SMIA HI (Human Interface)

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA HI ...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PSSWD')

    # TODO BORRAR (para pruebas)
    # smia_jid = "gcis1@xmpp.jp"
    # smia_psswd = "gcis1234"
    # smia.load_aas_model('../smia_archive/config/aas/CeDRI_Operator_instance.aasx')

    # Create the agent object
    smia_hi_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    # The behavior to receive all ACL messages and set available them for the web interface
    receive_acl_behaviour = ReceiveACLBehaviour(smia_hi_agent)
    smia_hi_agent.add_new_agent_capability(receive_acl_behaviour)

    # The graphical web user interface is also added in order to manage the web Human Interface
    spia_gui_behaviour = SMIAHIGUIBehaviour()
    smia_hi_agent.add_new_agent_capability(spia_gui_behaviour)

    # Let's add all Agent Services for SMIA HI
    smia_hi_agent_services = SMIAHIAgentServices(smia_hi_agent)
    for service_id, service_method in smia_hi_agent_services.services_map.items():
        smia_hi_agent.add_new_agent_service(service_id, service_method)

    smia.run(smia_hi_agent)


if __name__ == '__main__':

    # Run main program with SMIA
    main()