from pade.misc.utility import display_message, start_loop, call_later
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from sys import argv


class Remetente(Agent):
    def __init__(self, aid):
        super(Remetente, self).__init__(aid=aid, debug=False)

    def on_start(self):
        super(Remetente, self).on_start()
        display_message(self.aid.localname, 'Remetente started...')
        call_later(8.0, self.sending_message)

    def sending_message(self):
        display_message(self.aid.localname, 'Sending message...')
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(AID('destinatario'))
        message.set_content('Ola')
        self.send(message)

    def react(self, message):
        super(Remetente, self).react(message)
        display_message(self.aid.localname, 'Mensagem recebida from {}'.format(message.sender.name))


class Destinatario(Agent):
    def __init__(self, aid):
        super(Destinatario, self).__init__(aid=aid, debug=False)

    def on_start(self):
        display_message(self.aid.localname, 'Destinatario started.')

    def react(self, message):
        super(Destinatario, self).react(message)
        display_message(self.aid.localname, 'Mensagem recebida from {}'.format(message.sender.name))


if __name__ == '__main__':

    agents = list()
    port = int(argv[1])
    destinatario_agent = Destinatario(AID(name='destinatario@localhost:{}'.format(port)))
    agents.append(destinatario_agent)

    port += 1
    remetente_agent = Remetente(AID(name='remetente@localhost:{}'.format(port)))
    agents.append(remetente_agent)

    start_loop(agents)