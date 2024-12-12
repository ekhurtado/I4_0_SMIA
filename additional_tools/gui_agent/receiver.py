import asyncio
import calendar
import json
import sys
import time
from random import randint
import psutil

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

from smia.utilities import FIPAACLInfo

XMPP_SERVER = 'anonym.im'


class ReceiverAgent(Agent):
    class SleepingBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("SleepingBehaviour starting...")
            self.neg_value = None
            self.event = asyncio.Event()

        async def run(self):
            print("SleepingBehaviour running...")
            print("---> Neg value before waits: " + str(self.neg_value))
            await self.event.wait()  # Wait until the neg value is added in the behaviour
            self.event.clear()  # neg value added
            print("---> Neg value after waits: " + str(self.neg_value))

    class RecvBehav(CyclicBehaviour):

        async def run(self):
            # self.presence.set_available()
            print("RecvBehav running")

            # for behav in self.agent.behaviours:
            #     behav_class_name = str(behav.__class__.__name__)
            #     if behav_class_name == 'HandleNegBehav':
            #         behav.neg_value = 99999999
            #         print(behav)

            msg = await self.receive(timeout=5)  # wait for a message for 10 seconds
            if msg:
                print("Message received in RecvBehav from {}".format(msg.sender))
                print("   with content: {}".format(msg.body))

                print("The negotiations that this agent has been a participant are: " +
                      str(self.agent.negotiations_data))
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
                        response_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM)
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
                        propose_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE)
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
                elif msg.get_metadata('performative') == FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE:
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
                        response_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM)
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

    class NegBehav_v2(CyclicBehaviour):
        async def on_start(self):
            if self.presence.is_available():
                print("[" + str(self.agent.jid) + "]" + " [RUNNING THE NEGOTIATION BEHAVIOUR]")

        async def run(self):
            print("NegBehav_v2 running")
            msg = await self.receive(timeout=5)  # wait for a message for 10 seconds
            if msg:
                # These messages are only with ontology 'negotiation' and performative 'CFP'
                print("CFP message received in NegBehav_v2 from {}".format(msg.sender))
                print("   with content: {}".format(msg.body))

                # Get the data from the msg
                # targets_list = eval(msg.get_metadata('targets'))
                msg_body_json = json.loads(msg.body)
                targets_list = eval(
                    msg_body_json['serviceData']['serviceParams']['targets'])  # With msg structure of I4.0 SMIA

                # Si el servidor XMPP le ha puesto un random para diferenciar al agente, lo quitamos (lo introduce
                # despues de '/')
                if '/' in str(msg.sender):
                    msg.sender = str(msg.sender).split('/')[0]

                print("Como ha llegado un CFP al agente {} quiere decir que se ha comenzado una negociacion".format(
                    self.agent.jid))
                print("Comienza la negociacion con ID: " + str(msg.thread))
                if len(targets_list) == 1:
                    # Sólo hay un target disponible (por lo tanto, es el único y es el winner)
                    print("En este caso es el unico agente que es parte de esta negociacion, asi que es el ganador")
                    print("     =>>>  THE WINNER OF THE NEGOTIATION IS: " + str(self.agent.jid))
                    print(" Faltaria contestar al que ha pedido la negociacion")
                    # response_msg = Message(to=msg.get_metadata('neg_request_jid'), thread=msg.thread, body='WINNER')
                    response_msg = Message(to=str(msg.sender),
                                           thread=msg.thread)  # With msg structure of I4.0 SMIA
                    response_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM)
                    response_msg.set_metadata('ontology', 'negotiation')

                    # TODO With msg structure of I4.0 SMIA
                    svc_response_json = {
                        'serviceID': msg_body_json['serviceID'],
                        'serviceType': msg_body_json['serviceType'],
                        'serviceData': {
                            'serviceCategory': 'service-response',
                            'serviceStatus': 'Completed',
                            'timestamp': calendar.timegm(time.gmtime()),
                            'serviceParams': {
                                'winner': str(self.agent.jid)
                            }
                        }
                    }
                    response_msg.body = json.dumps(svc_response_json)
                    await self.send(response_msg)  # TODO AL AÑADIRLO EN EL AAS_MANAGER QUITAR EL COMENTARIO

                    # Actualizo la informacion de esta negociacion para informar de que el agente es el ganador
                    # Las negociaciones se diferencian por el thread
                    # self.agent.negotiations_data[msg.thread] = {'winner': self.agent.jid,
                    #                                             'participants': msg.get_metadata('targets')}
                    # TODO With msg structure of I4.0 SMIA
                    self.agent.negotiations_data[msg.thread] = {'winner': str(self.agent.jid),
                                                                'participants':
                                                                    msg_body_json['serviceData']['serviceParams'][
                                                                        'targets']}
                else:
                    # Si hay mas targets, se añade un comportamiento de gestion de esta negociacion en concreto,
                    # que se encargara de enviar a cada uno un mensaje PROPOSE con mi valor del criterio,
                    # recibir respuestas, etc.

                    # Creo el objeto con la informacion de la negociacion para luego almacenarlo en el comportamiento
                    # negotiation_info = {
                    #     'thread': msg.thread,
                    #     'neg_requester_jid': msg.get_metadata('neg_requester_jid'),
                    #     'targets': msg.get_metadata('targets'),
                    #     'neg_criteria': msg.body,
                    #     'neg_value': await self.get_value_with_criteria(msg.body)  # El valor del criterio se genera
                    #     # justo antes de comenzar a gestionar la negociacion (para a la hora de enviar el PROPOSE y
                    #     # recibir lo de los demas sea el mismo valor)
                    # }

                    # TODO With msg structure of I4.0 SMIA
                    neg_criteria = msg_body_json['serviceData']['serviceParams']['criteria']
                    negotiation_info = {
                        'thread': msg.thread,
                        'neg_requester_jid': str(msg.sender),
                        'targets': msg_body_json['serviceData']['serviceParams']['targets'],
                        'neg_criteria': neg_criteria,
                        'neg_value': await self.get_value_with_criteria(neg_criteria)  # El valor del criterio se genera
                        # justo antes de comenzar a gestionar la negociacion (para a la hora de enviar el PROPOSE y
                        # recibir lo de los demas sea el mismo valor)
                    }

                    # Añado el comportamiento al agente (la plantilla asegura de solo recibir mensajes PROPOSE pero
                    # ademas solo con el thread de esa negociacion en concreto) Consigo mi valor dependiendo el criterio
                    handle_neg_template = Template()
                    handle_neg_template.set_metadata("performative", FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE)
                    handle_neg_template.set_metadata("ontology", "negotiation")
                    handle_neg_template.thread = msg.thread
                    handle_neg_behav = self.agent.HandleNegBehav(negotiation_info)
                    self.agent.add_behaviour(handle_neg_behav, handle_neg_template)

            else:
                print("Did not received any message after 5 seconds in NegBehav_v2")

        async def get_value_with_criteria(self, criteria):
            if criteria == "battery":
                agent_neg_value = self.agent.battery
            elif criteria == "mem":
                agent_neg_value = psutil.virtual_memory().available - randint(0, 1024)
            else:
                agent_neg_value = ''
            return agent_neg_value

    class HandleNegBehav(CyclicBehaviour):

        def __init__(self, negotiation_info):
            super().__init__()  # Heredamos el init de la clase super

            self.thread = negotiation_info['thread']
            self.neg_requester_jid = negotiation_info['neg_requester_jid']
            self.targets = negotiation_info['targets']
            self.neg_criteria = negotiation_info['neg_criteria']
            self.neg_value = negotiation_info['neg_value']
            # self.targets_processed = []
            self.targets_processed = set()  # TODO pensar si cambiarlo a un set para evitar valores repetidos

        async def on_start(self):
            print("[" + str(self.agent.jid) + "]" + " [RUNNING THE HANDLE NEGOTIATION BEHAVIOUR]")

            # Al comenzar con la gestion de la negociacion, el primer paso es enviar el mensaje PROPOSE con el valor
            # propio a los demas participantes de la negociacion. Al ser el primer paso, se realizara en el metodo on_start

            # Genero el mensaje PROPOSE
            # propose_msg = Message(thread=self.thread, body=self.neg_criteria + ',' + str(self.neg_value))
            propose_msg = Message(thread=self.thread)
            propose_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE)
            propose_msg.set_metadata('ontology', 'negotiation')
            # propose_msg.set_metadata('targets', self.targets)
            # propose_msg.set_metadata('neg_requester_jid', self.neg_requester_jid)
            # TODO With msg structure of I4.0 SMIA
            propose_msg_body_json = {
                'serviceID': 'proposeNegotiation',
                'serviceType': 'AssetRelatedService',
                'serviceData': {
                    'serviceCategory': 'service-request',
                    'timestamp': calendar.timegm(time.gmtime()),
                    'serviceParams': {
                        'targets': self.targets,
                        'neg_requester_jid': self.neg_requester_jid,
                        'criteria': self.neg_criteria,
                        'neg_value': str(self.neg_value)
                    }
                }
            }
            propose_msg.body = json.dumps(propose_msg_body_json)

            targets_list = eval(self.targets)
            for jid_target in targets_list:
                # Envio el mensaje a cada uno de los targets (excepto al propio agente)
                if jid_target + '@' + XMPP_SERVER != str(self.agent.jid):
                # if jid_target != str(self.agent.jid):
                    propose_msg.to = jid_target + '@' + XMPP_SERVER
                    await self.send(propose_msg)
                    print("[" + str(self.agent.jid) + "]" + " [NEGOTIATION " + self.thread + "] PROPOSE message" \
                          + " sent to " + jid_target)

        async def run(self):
            print("HandleNegBehav running")
            msg = await self.receive(timeout=5)  # wait for a message for 10 seconds
            if msg:
                # These messages are only with ontology 'negotiation' and performative 'PROPOSE' and exactly the thread
                # with which this behavior has been created
                print("PROPOSE message received in NegBehav_v2 from {}".format(msg.sender))
                print("   with content: {}".format(msg.body))

                # Si el servidor XMPP le ha puesto un random para diferenciar al agente, lo quitamos (lo introduce
                # despues de '/')
                if '/' in str(msg.sender):
                    msg.sender = str(msg.sender).split('/')[0]

                print("En este caso es un PROPOSE, asi que el agente {} esta en medio de una negociacion".format(
                    self.agent.jid))
                print("El agente " + str(self.agent.jid) + " ha recibido una propuesta de " + str(msg.sender))
                # Se obtiene el criterio de esta negociacion
                # criteria = msg.body.split(',')[0]
                # sender_agent_neg_value = msg.body.split(',')[1]
                # TODO With msg structure of I4.0 SMIA
                msg_body_json = json.loads(msg.body)
                criteria = msg_body_json['serviceData']['serviceParams']['criteria']
                sender_agent_neg_value = msg_body_json['serviceData']['serviceParams']['neg_value']

                print("El valor del agente " + str(self.agent.jid) + " es " + str(self.neg_value))
                print("El valor del agente sender " + str(msg.sender) + " es " + sender_agent_neg_value)

                # Se comparan los valores
                if int(sender_agent_neg_value) > self.neg_value:
                    # Como el valor del agente sender es mayor, este agente debe salir de la negociacion
                    await self.exit_negotiation(is_winner=False)
                    return None  # killing a behaviour does not cancel its current run loop
                if (int(sender_agent_neg_value) == self.neg_value) and not self.agent.tie_break:
                    # empata negocicación pero no es quien fija desempate
                    await self.exit_negotiation(is_winner=False)
                    return None  # killing a behaviour does not cancel its current run loop
                # if str(msg.sender) not in self.targets_processed:
                #     # Solo añado si no se ha procesado antes, para evitar errores con mensajes duplicados
                #     self.targets_processed.append(str(msg.sender))
                self.targets_processed.add(str(msg.sender))
                if len(self.targets_processed) == len(eval(self.targets)) - 1:
                    # En este caso ya se han recibido todos los mensajes, por lo que el valor del agente es el mejor
                    print("     =>>>  THE WINNER OF THE NEGOTIATION IS: " + str(self.agent.jid))
                    print(" Faltaria contestar al que ha pedido la negociacion")
                    # response_msg = Message(to=msg.get_metadata('neg_request_jid'), thread=msg.thread, body='WINNER')
                    response_msg = Message(to=msg_body_json['serviceData']['serviceParams']['neg_requester_jid'],
                                           thread=msg.thread)
                    response_msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM)
                    response_msg.set_metadata('ontology', 'negotiation')

                    # TODO With msg structure of I4.0 SMIA
                    svc_response_json = {
                        'serviceID': 'startNegotiation',
                        'serviceType': msg_body_json['serviceType'],
                        'serviceData': {
                            'serviceCategory': 'service-response',
                            'serviceStatus': 'Completed',
                            'timestamp': calendar.timegm(time.gmtime()),
                            'serviceParams': {
                                'winner': str(self.agent.jid)
                            }
                        }
                    }
                    response_msg.body = json.dumps(svc_response_json)
                    await self.send(response_msg)  # TODO AL AÑADIRLO EN EL AAS_MANAGER QUITAR EL COMENTARIO

                    # Una vez tenemos ganador, se puede dar por finalizada la negociacion, por lo que eliminamos el
                    # behaviour del agente
                    await self.exit_negotiation(is_winner=True)

            else:
                print("Did not received any message after 5 seconds in HandleNegBehav")

        async def exit_negotiation(self, is_winner):
            # Este metodo se ejecuta cuando la negociacion ha finalizado, ya sea siendo ganador o perdedor. En cualquier
            # caso, se añade toda la informacion de la negociacion al agente, para que tenga la informacion de todas las
            # negociaciones en las que ha partipado. Utilizamos el thread para diferenciar la informacion de cada
            # negociacion, ya que este es el identificador de cada una de ellas
            print(str(self.agent.jid) + " agent exiting the negotiation " +
                  str(self.thread) + " as winner=" + str(is_winner))
            self.agent.negotiations_data[self.thread] = {
                'targets': self.targets,
                'neg_requester_jid': self.neg_requester_jid,
                'neg_criteria': self.neg_criteria,
                'is_winner': str(is_winner),
            }

            # TODO prueba para añadir variable en behaviour a la espera para que continue su ejecucion
            for behav in self.agent.behaviours:
                behav_class_name = str(behav.__class__.__name__)
                if behav_class_name == 'SleepingBehaviour':
                    behav.neg_value = self.neg_value
                    behav.event.set()

            # Para finalizar la negociacion se elimina este behaviour del agente
            self.kill(exit_code=10)

    class SendBehaviour(OneShotBehaviour):
        async def run(self):
            # Create the Message object
            print("Building the message to send to the agent with JID: gui_agent")
            receiver = 'gui_agent' + '@' + XMPP_SERVER
            msg = Message(to=receiver, thread='pruebaMsg')
            msg.set_metadata('performative', FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP)
            msg.set_metadata('ontology', FIPAACLInfo.FIPA_ACL_ONTOLOGY_SVC_REQUEST)

            msg.body = '{"serviceID": "getAssetData' + \
                       '", "serviceType": "AssetRelatedService' + \
                       '", "serviceData": {' + \
                       '"serviceCategory": "service-request' + \
                       '", "timestamp": "100212569682' + \
                       '", "serviceParams": {"requestedData": "battery"}' + '}}'
            print(msg)

            print("Sending the message... ")
            await self.send(msg)
            print("Message sent!")

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
        template.set_metadata("performative", FIPAACLInfo.FIPA_ACL_PERFORMATIVE_INFORM)
        # template.set_metadata("conversationid", "1234")
        # template.set_metadata("ontology", "negotiation")
        # self.add_behaviour(b)
        self.add_behaviour(b, template)

        t1 = Template()
        t1.set_metadata("performative", FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP)
        t1.set_metadata("ontology", "negotiation")

        t2 = Template()
        t2.set_metadata("performative", FIPAACLInfo.FIPA_ACL_PERFORMATIVE_PROPOSE)
        t2.set_metadata("ontology", "negotiation")

        t3 = Template()
        t3.set_metadata("performative", "ACCEPT")
        t3.set_metadata("ontology", "negotiation")

        t4 = Template()
        t4.set_metadata("performative", "REJECT")
        t4.set_metadata("ontology", "negotiation")
        # neg = self.NegBehav()
        # self.add_behaviour(neg, t1 | t2 | t3 | t4)

        # Negotiation behaviour v2.0 (get from Oskar's code)
        t = Template()
        t.set_metadata("performative", FIPAACLInfo.FIPA_ACL_PERFORMATIVE_CFP)
        t.set_metadata("ontology", "negotiation")
        neg_behav = self.NegBehav_v2()
        self.add_behaviour(neg_behav, t)

        # Behaviour that sends ACL messages for tests
        send_behav = self.SendBehaviour()
        self.add_behaviour(send_behav)

        # Behavior that waits for one of its attributes to change
        sleeping_behav = self.SleepingBehaviour()
        self.add_behaviour(sleeping_behav)


async def main():
    recv_jid = sys.argv[1] + "@" + XMPP_SERVER
    passwd = "gcis1234"

    # recv_jid = "gcis1@xmpp.jp"

    receiveragent = ReceiverAgent(recv_jid, passwd)
    # receiveragent.jid2 = "gcis@localhost"
    # receiveragent.jid2 = "sender@ubuntu.min.vm"

    await receiveragent.start(auto_register=True)
    await receiveragent.web.start(hostname="127.0.0.1", port="10001")  # si se quiere lanzarlo con interfaz web
    print("Receiver started with jid: {}".format(recv_jid))

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())
