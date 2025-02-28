import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent
from my_extended_logic import MyExtendedCapability, my_extended_agent_service, MyExtendedAssetConnection

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()

    # The AAS model is added to SMIA
    aas_model_path = smia.utilities.general_utils.DockerUtils.get_aas_model_from_env_var()
    smia.load_aas_model(aas_model_path)

    # Create and run the extensible agent object
    my_extensible_smia_agent = ExtensibleSMIAAgent('myextendedsmia001@ejabberd', 'smia1234')

    # Add a new capability
    my_extended_cap = MyExtendedCapability(agent_object=my_extensible_smia_agent)
    my_extensible_smia_agent.add_new_agent_capability(my_extended_cap)

    # Add a new agent service
    my_extensible_smia_agent.add_new_agent_service('MyExtendedAgentService', my_extended_agent_service)

    # Add a new AssetConnection
    my_asset_conn = MyExtendedAssetConnection()
    my_extensible_smia_agent.add_new_asset_connection('MyExtendedInterface', my_asset_conn)

    smia.run(my_extensible_smia_agent)

if __name__ == '__main__':
    main()