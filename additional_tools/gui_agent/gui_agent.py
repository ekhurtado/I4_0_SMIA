import os
from collections import OrderedDict

import spade
from spade.agent import Agent

from gui_features.behaviours import GUIAgentBehaviours
from gui_features.general_features import GeneralGUIFeatures

# XMPP_SERVER = 'worker4'
XMPP_SERVER = 'ejabberd'


class GUIAgent(Agent):

    async def setup(self):
        print("Hello World! I'm sender agent {}".format(str(self.jid)))
        print("GUIAgent started")
        self.acl_sent = False  # se inicializa en False
        self.neg_sent = False  # se inicializa en False
        self.acl_msg_log = []  # se inicializa el array de mensajes ACL
        self.web_menu_entries = OrderedDict()  # se inicializa el diccionario para añadir las entradas del menu

        self.general_features = GeneralGUIFeatures(self)

        receiver_behav = GUIAgentBehaviours.ReceiverBehaviour()
        self.add_behaviour(receiver_behav)

        # TODO BORRAR
        file1 = {'capabilities': {'capability': {'type': 'agentcap', 'skills': {'type': 'operation',
                 'interfaces': {'type': 'HTTPinterface', 'protocol': 'HTTP', 'endpoint': 'http://localhost:5000'}}}}}
        file2 = {'capabilities': {'capability': {'type': 'assetcap', 'skills': {'type': 'event',
                 'interfaces': {'type': 'MQTTinterface', 'protocol': 'MQTT', 'endpoint': 'http://localhost:5000'}}}}}
        self.files = [file1, file2]

    @staticmethod
    def build_avatar_url(jid: str) -> str:
        # TODO CUIDADO, este metodo se esta sobrescribiendo por el de SPADE
        return ("https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/capabilityskill_tests/images/SMIA_logo_vertical"
                ".png")      # TODO HACER AHORA: modificarlo cuando se una al main branch (ahora esta con la imagen de la rama de pruebas)
        # return "https://raw.githubusercontent.com/ekhurtado/I4_0_SMIA/main/images/I4_0_SMIA_logo_negative.png"


async def main():
    aas_id = 'guiagent'  # For testing
    # Build the agent jid and password
    agent_jid = aas_id + '@' + XMPP_SERVER
    passwd = '123'

    # DATOS PARA PRUEBAS CON ANONYM.IM
    if 'KUBERNETES_PORT' not in os.environ:
        agent_jid = os.environ.get('AGENT_ID')
        passwd = os.environ.get('AGENT_PASSWD')

        if agent_jid is None:
            # agent_jid = "gui_agent@anonym.im"
            agent_jid = "gui_agent@xmpp.jp"
            # agent_jid = "gui_agent@localhost"
        if passwd is None:
            passwd = "gcis1234"

    gui_agent = GUIAgent(agent_jid, passwd)
    gui_agent.agent_name = 'gui_agent'

    # Since the agent object has already been created, the agent will start
    await gui_agent.start()

    # Add customized webpages
    gui_agent.web.add_get("/acl_message", GeneralGUIFeatures.hello_controller, "/htmls/send_acl.html")
    gui_agent.web.add_post("/acl_message/submit", gui_agent.general_features.acl_post_controller, "/htmls/send_acl_submit.html")

    gui_agent.web.add_get("/receive_acl_msgs", GeneralGUIFeatures.hello_controller, "/htmls/receive_acl.html")

    gui_agent.web.add_get("/negotiation", GeneralGUIFeatures.hello_controller, "/htmls/negotiation.html")
    gui_agent.web.add_post("/negotiation/submit", gui_agent.general_features.neg_post_controller, "/htmls/negotiation_submit.html")

    gui_agent.web.add_get("/editor", GeneralGUIFeatures.hello_controller, "/htmls/own_programming_language_editor.html")
    gui_agent.web.add_post("/editor/submit", gui_agent.general_features.acl_post_controller,
                           "/htmls/own_programming_language_editor.html")

    gui_agent.web.add_get("/aas_library", GeneralGUIFeatures.hello_controller, "/htmls/aas_library.html")
    gui_agent.web.add_post("/capability_request", gui_agent.general_features.capability_request_controller,
                           "/htmls/aas_library.html")

    gui_agent.web.add_get("/aas_loader", GeneralGUIFeatures.hello_controller, "/htmls/aas_loader.html")
    gui_agent.web.add_post("/aas_loader/submit", gui_agent.general_features.aas_upload_controller,
                           "/htmls/aas_loader_submit.html")

    print("All HTMLs added.")

    # Codigo para añadir el Favicon (logo pequeño en la pestaña): si no presenta error de que no lo encuentra
    gui_agent.web.app.router.add_get('/favicon.ico', GeneralGUIFeatures.handle_favicon)
    gui_agent.web.app.router.add_static('/static/', path=str(os.path.join(os.path.dirname(__file__), 'static')))

    # gui_agent.web.add_menu_entry("Send ACL message", "/acl_message",
    #                              "fa fa-envelope")  # https://github.com/javipalanca/spade/blob/master/docs/web.rst#menu-entries
    # gui_agent.web.add_menu_entry("Received ACL messages", "/receive_acl_msgs", "fa fa-inbox")
    # gui_agent.web.add_menu_entry("Negotiation", "/negotiation", "fa fa-comments")
    # gui_agent.web.add_menu_entry("Programming language editor", "/editor", "fa fa-code")
    # gui_agent.web.add_menu_entry("AAS Library", "/aas_library", "fa fa-book")

    await gui_agent.general_features.add_new_menu_entry("Send ACL message", "/acl_message", "fa fa-envelope")
    await gui_agent.general_features.add_new_menu_entry("Received ACL messages", "/receive_acl_msgs", "fa fa-inbox")
    await gui_agent.general_features.add_new_menu_entry("Negotiation", "/negotiation", "fa fa-comments")
    await gui_agent.general_features.add_new_menu_entry("Programming language editor", "/editor", "fa fa-code")
    await gui_agent.general_features.add_new_menu_entry("AAS Library", "/aas_library", "fa fa-book")
    await gui_agent.general_features.add_new_menu_entry("AAS Loader", "/aas_loader", "fa fa-file-import")

    gui_agent.web.start(hostname="0.0.0.0", port="10000")  # https://spade-mas.readthedocs.io/en/latest/web.html#
    print("GUI started.")

    # The main thread will be waiting until the agent has finished
    await spade.wait_until_finished(gui_agent)


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    spade.run(main())
