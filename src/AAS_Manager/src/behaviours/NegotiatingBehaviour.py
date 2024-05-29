import json
import logging

from spade.behaviour import CyclicBehaviour

_logger = logging.getLogger(__name__)

# TODO analizar clase NegotiatingBehaviour de Alejandro para ver como manejaba las negociaciones entre agentes


class NegotiatingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles the negotiation requests made by other standardized AAS Managers
    through ACL messages in the I4.0 System.
    """

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object


    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("NegotiationBehaviour starting...")


    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template for negotiating to arrive.
        msg = await self.receive(timeout=5) # Timeout set to 5 seconds so as not to continuously execute the behavior.
        if msg:
            # An ACL message has been received by the agent
            _logger.info("         + Message received on AAS Manager Agent (NegotiatingBehaviour)")
            _logger.info("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # Depending on the performative of the message, the agent will have to perform some actions or others
            match msg.get_metadata('performative'):
                # TODO esta hecho asi para pruebas, pero hay que pensar el procedimiento a seguir a la hora de gestionar los mensajes ACL
                case "CallForProposal":
                    _logger.info("The agent has received a request to participate in a negotiation: CFP")
                    # TODO analizar como lo ha hecho Alejandro para desarrollarlo mas

                case "Inform":
                    _logger.info("The agent has received a request to participate in a negotiation: Inform")
                    # TODO analizar como lo ha hecho Alejandro para desarrollarlo mas
                case "Propose":
                    _logger.info("The agent has received a response in a negotiation: Propose")
                    # TODO analizar como lo ha hecho Alejandro para desarrollarlo mas
                case "Failure":
                    _logger.info("The agent has received a response in a negotiation: Failure")
                    # TODO analizar como lo ha hecho Alejandro para desarrollarlo mas
                case _:
                    _logger.error("ACL performative type not available.")
        else:
            _logger.info("         - No message received within 5 seconds on AAS Manager Agent (NegotiatingBehaviour)")
