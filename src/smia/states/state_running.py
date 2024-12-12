import logging
from spade.behaviour import State

from smia.behaviours.negotiating_behaviour import NegotiatingBehaviour
from smia.behaviours.acl_handling_behaviour import ACLHandlingBehaviour
from smia.utilities import smia_archive_utils
from smia.utilities.general_utils import SMIAGeneralInfo
from smia.utilities.smia_info import SMIAInteractionInfo
from smia.css_ontology.css_ontology_utils import CapabilitySkillOntologyUtils

_logger = logging.getLogger(__name__)


class StateRunning(State):
    """
    This class contains the Running state of the common AAS Manager.
    """

    async def run(self):
        """
        This method implements the running state of the common AAS Manager. Here all requests services are handled,
        both from ACL of another AAS Manager or from the AAS Core.
        """

        _logger.info("## STATE 2: RUNNING ##  (Initial state)")

        # SMIA is in the Running status
        smia_archive_utils.update_status('Running')

        # On the one hand, a behaviour is required to handle ACL messages
        acl_handling_behav = ACLHandlingBehaviour(self.agent)
        self.agent.add_behaviour(acl_handling_behav, SMIAInteractionInfo.SVC_STANDARD_ACL_TEMPLATE)

        # On the other hand, a behaviour is required to handle interaction messages
        # TODO revisar, ya que en el nuevo enfoque no hay AAS Core
        # interaction_handling_behav = InteractionHandlingBehaviour(self.agent)
        # self.agent.add_behaviour(interaction_handling_behav)

        # Besides, the negotiation behaviour has to be added to the agent
        agent_behaviours_classes = await self.add_agent_capabilities_behaviours()

        # Wait until the behaviour has finished. Is a CyclicBehaviour, so it will not end until an error occurs or, if
        # desired, it can be terminated manually using "behaviour.kill()".
        await acl_handling_behav.join()
        # await interaction_handling_behav.join()
        if agent_behaviours_classes:
            # TODO revisar si esto se quiere hacer asi (pensar en las transciones entre estados)
            for behav_class in agent_behaviours_classes:
                await behav_class.join()

        # If the Execution Running State has been completed, the agent can move to the next state
        _logger.info(f"{self.agent.jid} agent has finished it Running state.")
        self.set_next_state(SMIAGeneralInfo.STOPPING_STATE_NAME)

    async def add_agent_capabilities_behaviours(self):
        behaviours_objects = []
        agent_capabilities = await self.agent.aas_model.get_capability_dict_by_type(
            CapabilitySkillOntologyUtils.AGENT_CAPABILITY_TYPE)
        for capability in agent_capabilities.keys():
            if capability.id_short == 'Negotiation':
                # The negotiation behaviour has to be added to the agent
                _logger.info("This DT has negotiation capability.")
                negotiation_behav = NegotiatingBehaviour(self.agent)
                self.agent.add_behaviour(negotiation_behav, SMIAInteractionInfo.NEG_STANDARD_ACL_TEMPLATE)
                behaviours_objects.append(negotiation_behav)
            elif capability.id_short == 'OtherAgentCapability':
                # TODO pensarlo
                pass
        return behaviours_objects
