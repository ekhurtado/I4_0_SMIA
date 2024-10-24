import json
import logging

from spade.behaviour import CyclicBehaviour

from behaviours.HandleSvcRequestBehaviour import HandleSvcRequestBehaviour
from behaviours.HandleSvcResponseBehaviour import HandleSvcResponseBehaviour
from logic import InterAASInteractions_utils

_logger = logging.getLogger(__name__)


class SvcACLHandlingBehaviour(CyclicBehaviour):
    """
    This class implements the behaviour that handles all the ACL messages that the AAS Manager will receive from the
    others standardized AAS Manager in the I4.0 System.
    """

    # TODO pensar cambiarle el nombre, tanto a esta clase como a InteractionHandlingBehaviour, y pasarlas a tipo de
    #  interaccion, es decir: InteractionHandlingBehaviour -> IntraAASInteractionsHandlingBehaviour y
    #  SvcACLHandlingBehaviour -> InterAASInteractionsHandlingBehaviour

    def __init__(self, agent_object):
        """
        The constructor method is rewritten to add the object of the agent
        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The constructor of the inherited class is executed.
        super().__init__()

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

    async def on_start(self):
        """
        This method implements the initialization process of this behaviour.
        """
        _logger.info("SvcACLHandlingBehaviour starting...")

    async def run(self):
        """
        This method implements the logic of the behaviour.
        """

        # Wait for a message with the standard ACL template to arrive.
        msg = await self.receive(
            timeout=10)  # Timeout set to 10 seconds so as not to continuously execute the behavior.
        if msg:
            # TODO modificar el concepto de como gestionar los servicios. En este behaviour (llamemosle a partir de ahora
            #  SvcRequestsHanldingBehaviour) se gestionarán todas las peticiones de servicios via ACL, pero no gestionará
            #  cada servicio individualmente. Por cada servicio añadira otro behaviour al agente (llamemosle
            #  'SvcHandlingBehaviour') y este sí será el encargado de gestionar ese servicio en concreto. De esta forma,
            #  conseguimos que los servicios se gestionen "en paralelo" (aunque no es 100% paralelo según van llegando
            #  peticiones de servicios se van generando behaviours, así que se van gestionando todos a la vez). Gracias
            #  a esta forma cada behaviour individual es capaz de gestionar mas facilmente su servicio (analizar si
            #  tarda mucho en realizarse, guardar en el log cuando finalice toda la informacion que la tendra en su
            #  propia clase, etc.). Cada behaviour individual será el que se eliminará del agente en cuanto el servicio
            #  se haya completado (self.kill())

            # TODO ACTUALIZACION: de momento se va a seguir esta idea, y por cada peticion de servicio se va a crear un
            #  behaviour (SvcRequestHandlingBehaviour). Este se creará tanto con peticiones via ACL como peticiones via
            #  Interaction (solicitadas por el AAS Core), ya que en ambos casos es una solicitud de un servicio al AAS
            #  Manager. Este dentro del behaviour decidirá los pasos a seguir para llevar a cabo ese servicio (solicitar
            #  algo por interaccion, o por ACL a otro Manager...). Para respuestas a peticiones de servicio se generará
            #  otro behaviour diferente

            # An ACL message has been received by the agent
            _logger.aclinfo("         + Message received on AAS Manager Agent (ACLHandlingBehaviour)"
                            " from {}".format(msg.sender))
            _logger.aclinfo("                 |___ Message received with content: {}".format(msg.body))

            # The msg body will be parsed to a JSON object
            msg_json_body = json.loads(msg.body)

            # TODO por ACL entiendo que también pueden llegar respuestas de servicios, no solo solicitudes,
            #  asi que habria que modificar esto
            service_category = msg_json_body['serviceData']['serviceCategory']

            if service_category == 'service-request':
                # The new service request is looked up in the agent's global ACL request dictionary.
                if await self.myagent.get_acl_svc_request(thread=msg.thread) is not None:
                    _logger.error("A request has been made for an ACL service that already exists.")
                else:
                    # The thread is the identifier of the conversation, so all the information will be saved using it
                    msg_json_body['performative'] = msg.get_metadata('performative')
                    msg_json_body['ontology'] = msg.get_metadata('ontology')

                    if '/' in str(msg.sender):  # XMPP server can add a random string to differentiate the agent JID
                        msg_json_body['sender'] = str(msg.sender).split('/')[0]
                    else:
                        msg_json_body['sender'] = str(msg.sender)
                    await self.myagent.save_new_acl_svc_request(thread=msg.thread, request_data=msg_json_body)
                    _logger.aclinfo("acl_svc_requests shared object updated by " + str(self.__class__.__name__)
                                    + " responsible for thread [" + msg.thread + "]. Action: request data added")

                    svc_req_data = InterAASInteractions_utils.create_svc_json_data_from_acl_msg(msg)

                    # A new behaviour is added to the SPADE agent to handle this specific service request
                    svc_req_handling_behav = HandleSvcRequestBehaviour(self.agent,
                                                                       'Inter AAS interaction',
                                                                       svc_req_data)
                    self.myagent.add_behaviour(svc_req_handling_behav)

            elif service_category == 'service-response':
                _logger.aclinfo("The agent has received the response of a service with thread [" + msg.thread + "].")

                # As it is a response to a previous request, a new HandleSvcResponseBehaviour to handle this service
                # response will be added to the agent
                svc_resp_data = InterAASInteractions_utils.create_svc_json_data_from_acl_msg(msg)
                svc_resp_handling_behav = HandleSvcResponseBehaviour(self.agent,
                                                                     'Inter AAS interaction',
                                                                     svc_resp_data)
                self.myagent.add_behaviour(svc_resp_handling_behav)


        else:
            _logger.info("         - No message received within 10 seconds on AAS Manager Agent (ACLHandlingBehaviour)")
