import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent

def main():
    # First, the initial configuration must be executed
    smia.initial_self_configuration()

    # The AAS model is added to SMIA
    smia.load_aas_model(<path to the AAS model>)

    # Create and run the extensible agent object
    my_extensible_smia_agent = ExtensibleSMIAAgent(<jid of SMIA SPADE agent>, <password of SMIA SPADE agent>)
    smia.run(my_extensible_smia_agent)

if __name__ == '__main__':
    main()