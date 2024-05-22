import logging

from spade.behaviour import CyclicBehaviour


class ACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the AAS Manager will receive from the others standardized AAS Manager in the I4.0 System.
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
        This method implements the initialization process of this behaviour. Here the template of the ACL message that will be received by the agent is set.
        """
        logging.basicConfig(level=logging.INFO)



    async def run(self):
        """
        This method implements the logic of the behaviour.
        """
        print("ACLHandlingBehaviour running...")

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive()
        if msg:
            # Se configura la información de logging: Imprime líneas con información sobre la conexión
            print("         + Message received on GWAgent: GW AGENT (RcvBehaviour)")
            print("                 |___ Message received with content: {}".format(msg.body))