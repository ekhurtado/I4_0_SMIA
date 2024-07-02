import sys
from random import randint

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

XMPP_SERVER = 'anonym.im'


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
                targets = eval(msg.get_metadata('targets'))

                # Si el servidor XMPP le ha puesto un random para diferenciar al agente, lo quitamos (lo introduce despues de '/')
                if '/' in str(msg.sender):
                    print(str(msg.sender))
                    print(str(msg.sender).split('/')[0])
                    msg.sender = str(msg.sender).split('/')[0]

                if msg.get_metadata('performative') == 'CFP':
                    print("Como ha llegado un CFP al agente {} quiere decir que se ha comenzado una negociacion".format(
                        self.agent.jid))
                    print("Comienza la negociacion con ID: " + str(msg.thread))
                    if len(targets) == 1:
                        # Sólo hay un target disponible (por lo tanto, es el único y es el winner)
                        print("En este caso es el unico agente que es parte de esta negociacion, asi que es el ganador")
                        print("     =>>>  THE WINNER OF THE NEGOTIATION IS: " + str(self.agent.jid))
                        print(" Faltaria contestar al que ha pedido la negociacion")
                        response_msg = Message(to=msg.get_metadata('neg_request_jid'), thread=msg.thread, body='WINNER')
                        response_msg.set_metadata('performative', 'INFORM')
                        response_msg.set_metadata('ontology', 'negotiation')
                        # await self.send(response_msg)

                        # Actualizo la informacion de esta negociacion para informar de que el agente es el ganador
                        # Las negociaciones se diferencian por el thread
                        self.agent.negotiations_data[msg.thread] = {'winner': self.agent.jid,
                                                                    'participants': msg.get_metadata('targets')}
                    else:
                        # Si hay mas targets, envio a cada uno un mensaje PROPOSE con mi valor del criterio
                        # Consigo mi valor dependiendo el criterio
                        criteria = msg.body
                        agent_neg_value = await self.get_value_with_criteria(criteria)
                        # Genero el mensaje sin el receiver (es lo unico que cambia)
                        propose_msg = Message(thread=msg.thread, body=criteria + ',' + str(agent_neg_value))
                        propose_msg.set_metadata('performative', 'PROPOSE')
                        propose_msg.set_metadata('ontology', 'negotiation')
                        propose_msg.set_metadata('targets', msg.get_metadata('targets'))
                        propose_msg.set_metadata('neg_request_jid', msg.get_metadata('neg_request_jid'))
                        for jid_target in targets:
                            # Envio el mensaje a cada uno de los targets (excepto al propio agente)
                            if jid_target + '@' + XMPP_SERVER != str(self.agent.jid):
                                propose_msg.to = jid_target + '@' + XMPP_SERVER
                                await self.send(propose_msg)

                        # Actualizo la informacion de esta negociacion. Las negociaciones (conversaciones) se
                        # diferencian por el thread asi que toda esta negociacion sera con el mismo thread. Se añade una
                        # lista vacia para ir rellenando segun se vaya procesando valores recibidos de los targets
                        self.agent.negotiations_data[msg.thread] = {'targets': targets,
                                                                    'targets_processed': []}
                elif msg.get_metadata('performative') == 'PROPOSE':
                    print("En este caso es un PROPOSE, asi que el agente {} esta en medio de una negociacion".format(
                        self.agent.jid))
                    print("El agente " + str(self.agent.jid) + " ha recibido una propuesta de " + str(msg.sender))
                    # Se obtiene el criterio de esta negociacion
                    criteria = msg.body.split(',')[0]
                    sender_agent_neg_value = msg.body.split(',')[1]

                    # Se logra el valor del agente con el criterio
                    agent_neg_value = await self.get_value_with_criteria(criteria)
                    print("El valor del agente " + str(self.agent.jid) + " es " + str(agent_neg_value))
                    print("El valor del agente sender " + str(msg.sender) + " es " + sender_agent_neg_value)

                    # Se comparan los valores
                    if int(sender_agent_neg_value) > agent_neg_value:
                        # Como el valor del agente sender es mayor, este agente debe salir de la negociacion
                        return None
                    if (
                            int(sender_agent_neg_value) == agent_neg_value) and not self.agent.tie_break:  # empata negocicación pero no es quien fija desempate
                        return None
                    if str(msg.sender) not in self.agent.negotiations_data[msg.thread]['targets_processed']:
                        # Solo añado si no se ha procesado antes, para evitar errores con mensajes duplicados
                        self.agent.negotiations_data[msg.thread]['targets_processed'].append(str(msg.sender))
                    if len(self.agent.negotiations_data[msg.thread]['targets_processed']) == len(
                            self.agent.negotiations_data[msg.thread]['targets']) - 1:
                        # En este caso ya se han recibido todos los mensajes, por lo que el valor del agente es el mejor
                        print("     =>>>  THE WINNER OF THE NEGOTIATION IS: " + str(self.agent.jid))
                        print(" Faltaria contestar al que ha pedido la negociacion")
                        response_msg = Message(to=msg.get_metadata('neg_request_jid'), thread=msg.thread, body='WINNER')
                        response_msg.set_metadata('performative', 'INFORM')
                        response_msg.set_metadata('ontology', 'negotiation')
                        # await self.send(response_msg)

                        # Actualizo la informacion de esta negociacion para informar de que el agente es el ganador
                        # Las negociaciones se diferencian por el thread
                        self.agent.negotiations_data[msg.thread] = {'winner': self.agent.jid}


            else:
                print("Did not received any message after 5 seconds in NegBehav")

        async def get_value_with_criteria(self, criteria):
            if criteria == "battery":
                agent_neg_value = self.agent.battery
            else:
                agent_neg_value = ''
            return agent_neg_value

    async def setup(self):
        print("ReceiverAgent started")

        # Inicializo variables relacionadas con la negociacion
        self.battery = int(randint(1, 100))
        self.negotiations_data = {}
        self.tie_break = True

        b = self.RecvBehav()

        # presenceBehav = PresenceBehav.PresenceBehav2()
        # self.add_behaviour(presenceBehav)

        template = Template()
        template.set_metadata("performative", "inform")
        # template.set_metadata("conversationid", "1234")
        # template.set_metadata("ontology", "negotiation")
        # self.add_behaviour(b)
        self.add_behaviour(b, template)

        neg = self.NegBehav()
        t1 = Template()
        t1.set_metadata("performative", "CFP")
        t1.set_metadata("ontology", "negotiation")

        t2 = Template()
        t2.set_metadata("performative", "PROPOSE")
        t2.set_metadata("ontology", "negotiation")

        t3 = Template()
        t3.set_metadata("performative", "ACCEPT")
        t3.set_metadata("ontology", "negotiation")

        t4 = Template()
        t4.set_metadata("performative", "REJECT")
        t4.set_metadata("ontology", "negotiation")
        self.add_behaviour(neg, t1 | t2 | t3 | t4)


async def main():
    recv_jid = sys.argv[1] + "@" + XMPP_SERVER
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
