import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils

from smia_pe.behaviours.smia_pe_gui_behaviour import SMIAPEGUIBehaviour
from smia_pe.behaviours.bpmn_performer_behaviour import BPMNPerformerBehaviour
from smia_pe.behaviours.receive_acl_behaviour import ReceiveACLBehaviour

_logger = logging.getLogger(__name__)

# This is the starter file to launch the SMIA (Self-configurable Manufacturing Industrial Agents Production Execution)

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA PE ...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PSSWD')

    # Create the agent object
    smia_pe_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    # The behavior to receive all ACL messages and check if they are replies to previous SMIA PE messages is added
    receive_acl_behaviour = ReceiveACLBehaviour(smia_pe_agent)
    smia_pe_agent.add_new_agent_capability(receive_acl_behaviour)

    # The graphical web user interface is also added in order to manage the BPMN workflow
    smia_pe_gui_behaviour = SMIAPEGUIBehaviour()
    smia_pe_agent.add_new_agent_capability(smia_pe_gui_behaviour)

    # The behaviour for executing the CSS-driven BPMN production plan is added
    bpmn_performer_behaviour = BPMNPerformerBehaviour(smia_pe_agent)
    smia_pe_agent.add_new_agent_capability(bpmn_performer_behaviour)

    smia.run(smia_pe_agent)


if __name__ == '__main__':

    # Run main program with SMIA PE
    main()