import sys
from random import randint

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class ReceiverAgent(Agent):
    class RecvBehav(CyclicBehaviour):

        async def run(self):
            # self.presence.set_available()
            print("RecvBehav running")

            msg = await self.receive(timeout=5)  # wait for a message for 10 seconds
            if msg:
                print("Message received in RecvBehav from {}".format(msg.sender))
                print("   with content: {}".format(msg.body))
            else:
                print("Did not received any message after 5 seconds in RecvBehav")

    class NegBehav(CyclicBehaviour):

        # 1) Paso de la negociación
        step = 0
        # 2) Número de respuestas recibidas
        replyNum = 0

        NEG_LOST = 0
        NEG_PARTIAL_WON = 1
        NEG_WON = 2
        NEG_RETRY = -1
        NEG_FAIL = -2

        async def run(self):
            print("NegBehav running")
            msg = await self.receive(timeout=5)  # wait for a message for 10 seconds
            if msg:
                print("Message received in NegBehav from {}".format(msg.sender))
                print("   with content: {}".format(msg.body))

                # Get the data from the msg
                targets = msg.get_metadata('targets')
                criteria = msg.body

                if len(targets) == 1:
                    # Sólo hay un target disponible (por lo tanto, es el único y es el winner)
                    print("     =>>>  THE WINNER OF THE NEGOTIATION IS: " + str(self.agent.jid))
                    print(" Faltaria contestar al que ha pedido la negociacion")
                    response_msg = Message(to=msg.get_metadata('neg_request_jid'), body='WINNER')
                    # await self.send(response_msg)
                else:
                    if msg.get_metadata('performative') == 'CFP':


                if criteria == "battery":
                    my_value = self.agent.battery


            else:
                print("Did not received any message after 5 seconds in NegBehav")

    async def setup(self):
        print("ReceiverAgent started")

        self.battery = int(randint(1, 100))

        b = self.RecvBehav()

        # presenceBehav = PresenceBehav.PresenceBehav2()
        # self.add_behaviour(presenceBehav)

        # template = Template()
        # template.set_metadata("performative", "inform")
        # template.set_metadata("conversationid", "1234")
        # template.set_metadata("ontology", "negotiation")
        self.add_behaviour(b)
        # self.add_behaviour(b, template)

        neg = self.NegBehav()
        t1 = Template()
        t1.set_metadata("performative", "CFP")
        t1.set_metadata("ontology", "negotiation")

        t2 = Template()
        t2.set_metadata("performative", "ACCEPT")
        t2.set_metadata("ontology", "negotiation")

        t3 = Template()
        t3.set_metadata("performative", "REJECT")
        t3.set_metadata("ontology", "negotiation")
        self.add_behaviour(neg, t1 | t2 | t3)


async def main():
    recv_jid = sys.argv[1] + "@anonym.im"
    passwd = "gcis1234"

    receiveragent = ReceiverAgent(recv_jid, passwd)
    # receiveragent.jid2 = "gcis@localhost"
    # receiveragent.jid2 = "sender@ubuntu.min.vm"

    await receiveragent.start(auto_register=True)
    # await receiveragent.web.start(hostname="127.0.0.1", port="10000")  # si se quiere lanzarlo con interfaz web
    print("Receiver started with jid: {}".format(recv_jid))

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())
