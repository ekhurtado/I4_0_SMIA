import logging
import os

import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from smia.utilities.general_utils import DockerUtils

from request_acl_neg_behaviour import RequestACLNegBehaviour
from receive_acl_neg_behaviour import ReceiveACLNegBehaviour

_logger = logging.getLogger(__name__)

# This is the starter file to launch the SMIA (Self-configurable Manufacturing Industrial Agents) instance to request negotiations

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()
    _logger.info("Initializing SMIA Negotiation Requester ...")

    # The AAS model is obtained from the environmental variables
    aas_model_path = DockerUtils.get_aas_model_from_env_var()

    # When the AAS model path has been obtained, it is added to SMIA
    smia.load_aas_model(aas_model_path)

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PSSWD')

    # Create the agent object
    smia_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)

    # The behavior to request all ACL negotiations
    req_acl_behaviour = RequestACLNegBehaviour(smia_agent)
    smia_agent.add_new_agent_capability(req_acl_behaviour)

    recv_acl_behaviour = ReceiveACLNegBehaviour(smia_agent)
    smia_agent.add_new_agent_capability(recv_acl_behaviour)

    smia.run(smia_agent)


if __name__ == '__main__':

    # Run main program with SMIA PE
    main()