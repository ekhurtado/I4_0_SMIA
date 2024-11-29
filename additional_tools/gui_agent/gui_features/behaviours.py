import calendar
import json
import time
from urllib.parse import parse_qs

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message


class GUIAgentBehaviours:

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