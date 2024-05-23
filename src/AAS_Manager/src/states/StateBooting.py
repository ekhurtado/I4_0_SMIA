from spade.behaviour import State

from behaviours.InitAASarchiveBehaviour import InitAASarchiveBehaviour
from behaviours.InitSubmodelsBehaviour import InitSubmodelsBehaviour
from utilities.AASmanagerInfo import AASmanagerInfo


class StateBooting(State):
    """
    This class contains the Boot state of the common AAS Manager.
    """

    async def run(self):
        """
        This method implements the boot state of the common AAS Manager. Here all the required initialization tasks are performed.
        """
        print("\n---------------------------------------\n")
        print("## STATE 1: BOOTING ##  (Initial state)")

        # First, the interactionId is reset
        self.agent.interaction_id = 0

        # Then the AAS Archive is initialized. To do so, the associated behaviour is added to the agent
        init_aas_archive_behav = InitAASarchiveBehaviour(self.agent)
        self.agent.add_behaviour(init_aas_archive_behav)

        # The submodels also have to be initalized, so its behaviour is also added
        init_submodels_behav = InitSubmodelsBehaviour(self.agent)
        self.agent.add_behaviour(init_submodels_behav)

        # Wait until the behaviour has finished because the AAS Archive has to be initialized to pass to running state.
        await init_aas_archive_behav.join()
        await init_submodels_behav.join()

        # Finished the Boot State the agent can move to the next state
        print(f"{self.agent.jid} agent has finished it Boot state.")
        self.set_next_state(AASmanagerInfo.RUNNING_STATE_NAME)