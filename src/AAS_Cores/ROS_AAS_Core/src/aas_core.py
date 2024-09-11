#!/usr/bin/env python
import logging
import time
from threading import Thread

import rospy
from std_msgs.msg import String

import assetRelatedMethods
from utilities import Interactions_utils
from utilities.AASArchive_utils import file_to_json
from utilities.Interactions_utils import make_gateway_request, create_response_json_object
from utilities.KafkaInfo import KafkaInfo


class AASCore:
    """
    This class contains all the information about the AAS Core
    """

    state = None
    ready = False
    WIP = False
    processed_services = {}
    manager_status = None
    interaction_id_num = 0

    # ROS nodes
    pub = None
    pubCoord = None


    def __init__(self):
        print("Init method of AAS Core")
        self.state = 'IDLE'
        self.ready = False
        self.WIP = False
        self.processed_services = {}
        self.manager_status = 'Unknown'

        # ROS nodes
        self.pub = None
        self.pubCoord = None

        self.interaction_id_num = 0

    def increase_interaction_id_num(self):
        self.interaction_id_num += 1

    def get_interaction_id(self):
        return 'core-' + str(self.interaction_id_num)

    def initialize_aas_core(self):
        """This method executes the required tasks to initialize the AAS Core. In this case, create the connection and
        execute a necessary ROS nodes."""

        print("Initializing the AAS Core...")

        # A ROS node corresponding to the AAS Core is executed.
        rospy.init_node('AAS_Core', anonymous=True)
        print("ROS node initiated.")

        # Se crean además dos nodos:
        #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
        self.pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
        #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
        #   Utiliza para ello el tópico /coordinate
        self.pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)

        print("ROS publishers initiated.")

    def run_aas_core(self):

        self.send_status_change_to_manager('Running')

        # Each function will have its own thread of execution
        thread_func1 = Thread(target=self.handle_data_to_transport, args=())
        thread_func2 = Thread(target=self.handle_data_from_transport, args=())

        thread_func1.start()
        thread_func2.start()

    def handle_data_to_transport(self):
        """This method handles the message and data to the transport. Thus, it obtains the interaction requests by the
        AAS Manager and send to necessary command to the asset."""

        kafka_consumer_manager_partition = Interactions_utils.create_interaction_kafka_consumer('i4-0-smia-manager')

        print("Listening for manager messages in topic " + KafkaInfo.KAFKA_TOPIC)
        for msg in kafka_consumer_manager_partition:
            print("El consumidor del manager (partition 0) de Kafka ha recibido algo!")
            print("   |__ msg: " + str(msg))

            msg_key = msg.key.decode("utf-8")
            msg_json_value = msg.value

            if msg_key == 'manager-status':
                print("The AAS Core has received an update of the AAS Manager status.")
                self.manager_status = msg_json_value['status']
                if self.manager_status != 'Initializing':
                    print("AAS Manager has initialized, so the AAS Core can go to running state.")
            if msg_key == 'manager-service-request':
                if self.manager_status != 'Initializing' and self.manager_status != 'idle':
                    # Only if the AAS Manager is ready the AAS Core will work
                    if msg_json_value['interactionID'] in self.processed_services:
                        print("The request with interaction_id [" + msg_json_value['interactionID'] +
                              "] has already been performed")
                        break
                    else:
                        if msg_json_value['serviceType'] == "AssetRelatedService":
                            print("The AAS Core has received an asset related service request")
                            # TODO, si ha llegado alguna peticion, enviar el comando a traves del pub y pubCoord

                            if not self.WIP:
                                if msg_json_value['serviceID'] == "collection" or \
                                        msg_json_value['serviceID'] == "delivery":
                                    # TODO pensar como se llamaria al metodo (Ane y Maite lo hicieron con el thread
                                    #  del mensaje ACL, yo lo he hecho con el serviceID)
                                    # Se configura la información de logging: Imprime líneas con información
                                    # sobre la conexión
                                    logging.basicConfig(level=logging.INFO)

                                    # Marcar el flag para indicar trabajo en proceso
                                    self.WIP = True
                                    print("---> State: " + str(self.state))
                                    print(self.pub)

                                    if self.state == "IDLE":
                                        self.pub.publish("GO")
                                        time.sleep(1)

                                        # PRUEBA CON GATEWAY
                                        make_gateway_request('/coordinateIDLE', 'GO')

                                    # Se le ordena a un publicista que publique las coordenadas objetivo
                                    # Para este ejemplo, son coordenadas estáticas, que representan la
                                    # posición fija e invariable del almacén
                                    self.pubCoord.publish("1.43,0.59")
                                    print("AAS Core send warehouse coordinates")
                                    print("AAS Core wait while moving to warehouse")

                                    # PRUEBA CON GATEWAY
                                    make_gateway_request('/coordinate', '1.43,0.59')

                                    # TODO Pensar como hacer para no bloquear el hilo
                                    time.sleep(1)
                                    while not self.state == "ACTIVE":  # wait until the robot has reached the target coordinates
                                        time.sleep(1)

                                    # TODO: para pruebas, eliminamos la peticion de servicio, como que ya se ha ofrecido
                                    self.processed_services[msg_json_value['interactionID']] = msg_json_value

                                    # Write the response in svResponses.json of the AAS Core
                                    response_json = create_response_json_object(msg_json_value)
                                    result = Interactions_utils.send_interaction_msg_to_manager(
                                        client_id='i4-0-smia-core',
                                        msg_key='core-service-response',
                                        msg_data=response_json)
                                    if result != "OK":
                                        print("The AAS Manager-Core interaction is not working: " + str(result))
                                    else:
                                        print(
                                            "The AAS Core has notified the AAS Manager that the service has been"
                                            " completed.")

                                    # Once it is in the active state and has reached the target (has completed the service), the robot
                                    # will proceed to return to the home position.
                                    time.sleep(2)
                                    #    Coordenadas estáticas, que representan la posición de ORIGEN del turtlebot3
                                    self.pubCoord.publish("-1.65,-0.56")

                                    # PRUEBA CON GATEWAY
                                    make_gateway_request('/coordinate', '-1.65,-0.56')

                                    print("AAS Core send collection/delivery point coordinates")
                                    print("AAS Core wait while moving to collection/delivery point")

                                    time.sleep(1)
                                    while not self.state == "ACTIVE":  # wait until the robot has reached the target coordinates
                                        time.sleep(1)

                                    # Se "apaga" el flag 'WIP'
                                    self.WIP = False

                                elif msg_json_value['serviceID'] == "getNegotiationValue":
                                    if msg_json_value['serviceData']['serviceParams']['criteria'] == "battery":

                                        self.WIP = True
                                        # TODO habria que analizar como conseguir el valor real de la bateria, de momento
                                        #  se genera un numero random
                                        battery_value = assetRelatedMethods.get_battery()

                                        # TODO: para pruebas, eliminamos la peticion de servicio, como que ya se ha ofrecido
                                        self.processed_services[msg_json_value['interactionID']] = msg_json_value

                                        svc_response_params = {'value': battery_value}

                                        # Write the response in svResponses.json of the AAS Core
                                        response_json = create_response_json_object(msg_json_value,
                                                                                    svc_params=svc_response_params)
                                        result = Interactions_utils.send_interaction_msg_to_manager(
                                            client_id='i4-0-smia-core',
                                            msg_key='core-service-response',
                                            msg_data=response_json)
                                        if result != "OK":
                                            print("The AAS Manager-Core interaction is not working: " + str(result))
                                        else:
                                            print(
                                                "The AAS Core has notified the AAS Manager that the service has been"
                                                " completed.")

                                        self.WIP = False

                        elif msg_json_value['serviceType'] == "SubmodelService":
                            print("The AAS Core has received a submodel service request")
                        else:
                            print("Service type not available")

            if msg_key == 'manager-service-response':
                print("The AAS Core has received a response from the AAS Manager")
                # TODO
            else:
                print("Option not available")

    def handle_data_from_transport(self):
        """This method handles the message and data from the transport. Thus, it obtains the data from the asset with a ROS
        Subscriber node and send the necessary interaction command or response to the AAS Manager."""

        # Crea un nodo SUBSCRIBER, que se quedará a la escucha por el tópico /status
        # y notificará al agente del estado del transporte
        # rospy.Subscriber('/status', String, callback)

        # PRUEBA GATEWAY
        while True:
            time.sleep(2)
            status_json = file_to_json('/ros_aas_core_archive/status.json')
            self.state = status_json['status']
            print("Current state in file: " + self.state)

    def send_status_change_to_manager(self, new_status):
        """
        This method sends the status message to the Manager to notify that the state of the AAS Core has changed.
        """

        result = Interactions_utils.send_interaction_msg_to_manager(client_id='i4-0-smia-core',
                                                                    msg_key='core-status',
                                                                    msg_data={
                                                                        'interactionID': self.get_interaction_id(),
                                                                        'status': new_status})
        if result != "OK":
            print("The AAS Manager-Core interaction is not working: " + str(result))
        else:
            print("The AAS Core has notified the AAS Manager that its initialization has been completed.")

