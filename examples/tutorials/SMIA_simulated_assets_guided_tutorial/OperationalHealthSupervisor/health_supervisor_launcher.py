import os

import smia

from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from internal_logic import HealthSupervisorBehaviour

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()

    # The AAS model is added to SMIA
    aas_model_path = smia.utilities.general_utils.DockerUtils.get_aas_model_from_env_var()
    smia.load_aas_model(aas_model_path)
    # smia.load_aas_model('../SimulatedAssets_OperationalHealthSupervisor.aasx')

    # The jid and password can also be set as environmental variables. In case they are not set, the values are obtained
    # from the initialization properties file
    smia_jid = os.environ.get('AGENT_ID')
    smia_psswd = os.environ.get('AGENT_PSSWD')

    # Create the agent object
    ohs_extensible_smia_agent = ExtensibleSMIAAgent(smia_jid, smia_psswd)
    # ohs_extensible_smia_agent = ExtensibleSMIAAgent('gcis1@xmpp.jp', 'gcis1234')

    # Add its extended capability
    ohs_extended_cap = HealthSupervisorBehaviour(agent_object=ohs_extensible_smia_agent)
    ohs_extensible_smia_agent.add_new_agent_capability(ohs_extended_cap)

    smia.run(ohs_extensible_smia_agent)

if __name__ == '__main__':
    main()