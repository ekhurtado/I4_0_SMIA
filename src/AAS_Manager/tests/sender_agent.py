import codecs
import json
from urllib.parse import parse_qs
import os
import time

import spade
from aioxmpp import stream
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

# XMPP_SERVER = 'worker4'
XMPP_SERVER = 'ejabberd'


class SenderAgent(Agent):
    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            # Prepare the ACL message
            data_json = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(self.msg_data).items()}
            print(data_json)

            # Create the Message object
            print("Building the message to send to the agent with JID: " + str(data_json['receiver']))
            receiver = data_json['receiver'] + '@' + data_json['server']
            msg = Message(to=receiver, thread=data_json['thread'])
            msg.set_metadata('performative', data_json['performative'])
            msg.set_metadata('ontology', data_json['ontology'])

            if data_json['messageType'] == 'normal':  # message body with normal format
                msg.body = data_json['normalMessage']
            elif len(data_json['messageType']) == 2:
                body = '{"serviceID": "' + data_json['serviceID'] + \
                       '", "serviceType": "' + data_json['serviceType'] + \
                       '", "serviceData": "', data_json['serviceData'] + '"}'
                msg.body = str(body)
            print(msg)

            print("Sending the message...")
            await self.send(msg)

            # set exit_code for the behaviour
            self.agent.acl_sent = True

            # stop agent from behaviour
            # await self.agent.stop()

    async def setup(self):
        print("Hello World! I'm sender agent {}".format(str(self.jid)))
        print("SenderAgent started")

    async def post_controller(self, request):

        self.acl_sent = False  # se inicializa en False
        print("HA LLEGADO AL POST DEL AGENTE: " + str(self.jid))
        print(request)
        data_bytes = b''
        async for line in request.content:
            data_bytes = data_bytes + line
        data_str = data_bytes.decode('utf-8')
        print(data_str)

        self.b = self.SendBehaviour()
        self.b.msg_data = data_str
        self.add_behaviour(self.b)

        return "OK"


async def hello_controller(request):
    print(request)
    return {"number": 42}


async def main():
    aas_id = 'senderagent'  # For testing
    # Build the agent jid and password
    agent_jid = aas_id + '@' + XMPP_SERVER
    passwd = '123'

    agent_jid = "gcis3@anonym.im"
    passwd = "gcis1234"
    sender_agent = SenderAgent(agent_jid, passwd)

    # Add customized webpage
    # sender_agent.web.add_get("/hello", hello_controller, "/hello.html")
    sender_agent.web.add_get("/acl_message", hello_controller, "/send_acl.html")
    sender_agent.web.add_post("/acl_message/submit", sender_agent.post_controller, "/send_acl_submit.html")
    sender_agent.web.add_get("/editor", hello_controller, "/own_programming_language_editor.html")
    sender_agent.web.add_post("/editor/submit", sender_agent.post_controller, "/own_programming_language_editor.html")
    sender_agent.web.add_get("/aas_library", hello_controller, "/aas_library.html")
    print("Hello HTML added")

    # Since the agent object has already been created, the agent will start
    await sender_agent.start()
    sender_agent.web.start(hostname="0.0.0.0", port="10000")  # https://spade-mas.readthedocs.io/en/latest/web.html#
    sender_agent.web.add_menu_entry("Send ACL message", "/acl_message",
                                    "fa fa-envelope")  # https://github.com/javipalanca/spade/blob/master/docs/web.rst#menu-entries
    sender_agent.web.add_menu_entry("Programming language editor", "/editor", "fa fa-code")
    sender_agent.web.add_menu_entry("AAS Library", "/aas_library", "fa fa-book")
    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(sender_agent)


if __name__ == '__main__':
    print("Initializing AAS Manager program...")

    # Run main program with SPADE
    spade.run(main())
