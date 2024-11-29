import calendar
import json
import os
import time
from collections import OrderedDict
from os import getcwd
from urllib.parse import parse_qs

import spade
from aiohttp import web
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

# XMPP_SERVER = 'worker4'
XMPP_SERVER = 'ejabberd'


class GUIAgent(Agent):
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
                msg_body_json = {'serviceID': data_json['serviceID'],
                                 'serviceType': data_json['serviceType'],
                                 'serviceData': {
                                     'serviceCategory': data_json['serviceCategory']
                                 }
                                 }
                if 'serviceParams' in data_json:
                    msg_body_json['serviceData']['serviceParams'] = json.loads(data_json['serviceParams'])
                # '", "serviceParams": ' + data_json['serviceParams'] + '}}
                print(json.dumps(msg_body_json))
                msg.body = json.dumps(msg_body_json)
            print(msg)

            print("Sending the message...")
            await self.send(msg)
            print("Message sent!")

    class NegBehaviour(OneShotBehaviour):

        async def run(self):
            # Prepare the ACL message
            data_json = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(self.msg_data).items()}
            print(data_json)

            # Create the Message object
            # TODO mirar como se envian las negociaciones
            if ',' in data_json['receiver']:
                receivers_jid = data_json['receiver'].split(',')
            else:
                receivers_jid = [data_json['receiver']]

            for i in range(0, len(receivers_jid)):
                receivers_jid[i] = receivers_jid[i] + '@' + data_json['server']
            print("targets updated with XMPP server")


            for jid in receivers_jid:
                print("Building the negotiation message to send to the agent with JID: " + jid)
                msg = Message(to=jid, thread=data_json['thread'])
                msg.set_metadata('performative', data_json['performative'])
                msg.set_metadata('ontology', data_json['ontology'])
                # msg.set_metadata('neg_requester_jid', str(self.agent.jid))
                # msg.set_metadata('targets', str(receivers_jid))
                # msg.body = data_json['criteria']

                # TODO Msg structure of I4.0 SMIA
                msg_body_json = {
                    'serviceID': 'startNegotiation',
                    'serviceType': 'AssetRelatedService',   # TODO pensar que tipo de servicio es el de negociacion
                    'serviceData': {
                        'serviceCategory': 'service-request',
                        'timestamp': calendar.timegm(time.gmtime()),
                        'serviceParams': {
                            'neg_requester_jid': str(self.agent.jid),
                            'criteria': data_json['criteria'],
                            'targets': ','.join(receivers_jid)
                        }
                    }
                }
                msg.body = json.dumps(msg_body_json)

                print(msg)

                print("Sending the message...")
                await self.send(msg)
                print("Message sent!")

            print("All negotiation messages sent!")

    class ReceiverBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for a message for 10 seconds
            if msg:
                msg_body_json = json.loads(msg.body)
                msg_body_json['sender'] = msg.sender
                msg_body_json['thread'] = msg.thread
                msg_body_json['performative'] = msg.get_metadata('performative')
                self.agent.acl_msg_log.append(msg_body_json)
                print(f"Message received: {msg.body}")
            # else:
            #     print("No msg")

    async def setup(self):
        print("Hello World! I'm sender agent {}".format(str(self.jid)))
        print("GUIAgent started")
        self.acl_sent = False  # se inicializa en False
        self.neg_sent = False  # se inicializa en False
        self.acl_msg_log = []  # se inicializa el array de mensajes ACL
        self.web_menu_entries = OrderedDict()  # se inicializa el diccionario para añadir las entradas del menu

        receiver_behav = self.ReceiverBehaviour()
        self.add_behaviour(receiver_behav)

    # TODO PENSAR SI MOVERLOS A UN MODULO SOLAMENTE PARA LOS METODOS DEL GUI
    async def add_new_menu_entry(self, entry_name, entry_url, entry_icon):
        # Primero, se crea la entrada del menu con el metodo de SPADE
        self.web.add_menu_entry(entry_name, entry_url, entry_icon)

        # Despues, se añade la informacion al atributo con el diccionario en el agente, para que este accesible cuando
        self.web_menu_entries[entry_name] = {"url": entry_url, "icon": entry_icon}

    @staticmethod
    async def handle_favicon(request):
        print(getcwd())
        favicon_path = os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico')
        return web.FileResponse(favicon_path)

    @staticmethod
    def build_avatar_url(jid: str) -> str:
        # TODO CUIDADO, este metodo se esta sobrescribiendo por el de SPADE
        return "https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/main/images/I4_0_SMIA_logo_negative.png"

    async def acl_post_controller(self, request):

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
        print("Behaviour added to the agent")
        await self.b.join()
        self.acl_sent = True

        return {"status": "OK"}

    async def neg_post_controller(self, request):

        self.neg_sent = False  # se inicializa en False
        print("HA LLEGADO AL POST DEL AGENTE: " + str(self.jid))
        print(request)
        data_bytes = b''
        async for line in request.content:
            data_bytes = data_bytes + line
        data_str = data_bytes.decode('utf-8')
        print(data_str)

        self.b = self.NegBehaviour()
        self.b.msg_data = data_str
        self.add_behaviour(self.b)
        print("Behaviour added to the agent")
        await self.b.join()
        self.neg_sent = True

        return {"status": "OK"}


async def hello_controller(request):
    print(request)
    return {"status": "OK"}


async def main():
    aas_id = 'guiagent'  # For testing
    # Build the agent jid and password
    agent_jid = aas_id + '@' + XMPP_SERVER
    passwd = '123'

    # DATOS PARA PRUEBAS CON ANONYM.IM
    if 'KUBERNETES_PORT' not in os.environ:
        # agent_jid = "gui_agent@anonym.im"
        agent_jid = "gui_agent@xmpp.jp"
        passwd = "gcis1234"

    gui_agent = GUIAgent(agent_jid, passwd)
    gui_agent.agent_name = 'gui_agent'

    # Add customized webpages
    gui_agent.web.add_get("/acl_message", hello_controller, "/htmls/send_acl.html")
    gui_agent.web.add_post("/acl_message/submit", gui_agent.acl_post_controller, "/htmls/send_acl_submit.html")

    gui_agent.web.add_get("/receive_acl_msgs", hello_controller, "/htmls/receive_acl.html")

    gui_agent.web.add_get("/negotiation", hello_controller, "/htmls/negotiation.html")
    gui_agent.web.add_post("/negotiation/submit", gui_agent.neg_post_controller, "/htmls/negotiation_submit.html")

    gui_agent.web.add_get("/editor", hello_controller, "/htmls/own_programming_language_editor.html")
    gui_agent.web.add_post("/editor/submit", gui_agent.acl_post_controller,
                           "/htmls/own_programming_language_editor.html")

    gui_agent.web.add_get("/aas_library", hello_controller, "/htmls/aas_library.html")

    gui_agent.web.add_get("/aas_loader", hello_controller, "/htmls/aas_loader.html")
    print("All HTMLs added.")

    # Since the agent object has already been created, the agent will start
    await gui_agent.start()

    # Codigo para añadir el Favicon (logo pequeño en la pestaña): si no presenta error de que no lo encuentra
    gui_agent.web.app.router.add_get('/favicon.ico', GUIAgent.handle_favicon)
    gui_agent.web.app.router.add_static('/static/', path=str(os.path.join(os.path.dirname(__file__), 'static')))

    gui_agent.web.start(hostname="0.0.0.0", port="10000")  # https://spade-mas.readthedocs.io/en/latest/web.html#
    # gui_agent.web.add_menu_entry("Send ACL message", "/acl_message",
    #                              "fa fa-envelope")  # https://github.com/javipalanca/spade/blob/master/docs/web.rst#menu-entries
    # gui_agent.web.add_menu_entry("Received ACL messages", "/receive_acl_msgs", "fa fa-inbox")
    # gui_agent.web.add_menu_entry("Negotiation", "/negotiation", "fa fa-comments")
    # gui_agent.web.add_menu_entry("Programming language editor", "/editor", "fa fa-code")
    # gui_agent.web.add_menu_entry("AAS Library", "/aas_library", "fa fa-book")

    await gui_agent.add_new_menu_entry("Send ACL message", "/acl_message", "fa fa-envelope")
    await gui_agent.add_new_menu_entry("Received ACL messages", "/receive_acl_msgs", "fa fa-inbox")
    await gui_agent.add_new_menu_entry("Negotiation", "/negotiation", "fa fa-comments")
    await gui_agent.add_new_menu_entry("Programming language editor", "/editor", "fa fa-code")
    await gui_agent.add_new_menu_entry("AAS Library", "/aas_library", "fa fa-book")
    await gui_agent.add_new_menu_entry("AAS Loader", "/aas_loader", "fa fa-file-import")

    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(gui_agent)


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    spade.run(main())
