import logging
import spade.behaviour

from smia.agents.smia_agent import SMIAAgent

_logger = logging.getLogger(__name__)

class ExtensibleSMIAAgent(SMIAAgent):
    """
    This agent offers some extension mechanisms to add own code to the base SMIA agent.
    """
    # TODO The features that shall be offered are:
    #  1. define and add new connections to the asset (i.e., new communication protocols)
    #  2. define and add new agent capabilities to increase its intelligence and autonomy.
    #  3. define and add new agent services

    def add_new_agent_capability(self, new_capability_behaviour):
        # TODO por ahora simplemente se añade con la clase behaviour del agente. Mas adelante podriamos pensar ofrecer
        #  la posibilidad de añadir el código a ejecutar (el que iria en el 'run') y el tipo de behaviour
        if isinstance(new_capability_behaviour, spade.behaviour.CyclicBehaviour):
            self.add_behaviour(new_capability_behaviour)
        else:
            _logger.warning("The new agent capability [] cannot be added because it is not a SPADE behavior "
                            "class.".format(new_capability_behaviour))

    # TODO QUEDA PROBAR EL RESTO

