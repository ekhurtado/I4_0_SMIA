import getpass
import os
import time

import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template


class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to=self.agent.recv_jid)  # Instantiate the message
            msg.set_metadata(
                "performative", "inform"
            )  # Set the "inform" FIPA performative

            msg.set_metadata("conversationid", "1234")
            msg.set_metadata("ontology", "sys_mngt")
            msg.body = "Hello World {}".format(
                self.agent.recv_jid
            )  # Set the message content

            await self.send(msg)
            print("Message sent!")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)

    def __init__(self, recv_jid, *args, **kwargs):
        self.recv_jid = recv_jid
        super().__init__(*args, **kwargs)


class ReceiverAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        template.set_metadata("conversationid", "1234")
        template.set_metadata("ontology", "sys_mngt")
        self.add_behaviour(b, template)


async def main():
    # DATOS DE OPENFIRE
    recv_jid = "admin@localhost"
    # passwd1 = getpass.getpass()
    passwd = "gcis"

    sender_jid = "gcis@localhost"

    # DATOS DE https://anonym.im:5281/conversejs
    sender_jid = "gcis1@anonym.im"
    recv_jid = "gcis3@anonym.im"
    passwd = "gcis1234"

    # DATOS DE PROSODY K8s
    sender_jid = "sender@ubuntu.min.vm"
    recv_jid = "recv@ubuntu.min.vm"
    passwd = "gcis"
    # sender_jid = "sender@192.168.1.1:30522"
    # recv_jid = "recv@192.168.1.1:30522"
    # passwd = "gcis"

    # DATOS DE RECOGIDOS DE VARIABLES DE ENTORNO PARA PRUEBAS CON PROSODY K8s
    # sender_jid = os.environ.get('SENDER_JID')
    # recv_jid = os.environ.get('RECEIVER_JID')
    # passwd = "gcis1234"

    # time.sleep(10)  # espera de 10s para contenedor Docker

    receiveragent = ReceiverAgent(recv_jid, passwd)
    await receiveragent.start(auto_register=True)
    print("Receiver started")

    senderagent = SenderAgent(recv_jid, sender_jid, passwd)
    await senderagent.start(auto_register=True)
    print("Sender started")

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())
