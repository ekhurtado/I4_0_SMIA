import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template



class ReceiverAgent(Agent):
    class RecvBehav(OneShotBehaviour):

        async def run(self):
            # self.presence.set_available()
            print("RecvBehav running")

            msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()

        # presenceBehav = PresenceBehav.PresenceBehav2()
        # self.add_behaviour(presenceBehav)

        template = Template()
        # template.set_metadata("performative", "inform")
        # template.set_metadata("conversationid", "1234")
        # template.set_metadata("ontology", "sys_mngt")
        self.add_behaviour(b, template)


async def main():
    recv_jid = "admin@localhost"
    passwd = "gcis"

    sender_jid = "gcis1@anonym.im"
    recv_jid = "gcis3@anonym.im"
    passwd = "gcis1234"

    # DATOS DE PROSODY
    # sender_jid = "sender@ubuntu.min.vm"
    # recv_jid = "recv@ubuntu.min.vm"
    # passwd = "gcis"

    receiveragent = ReceiverAgent(recv_jid, passwd)
    # receiveragent.jid2 = "gcis@localhost"
    receiveragent.jid2 = "sender@ubuntu.min.vm"

    await receiveragent.start(auto_register=True)
    # await receiveragent.web.start(hostname="127.0.0.1", port="10000")  # si se quiere lanzarlo con interfaz web
    print("Receiver started")

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())
