#!/usr/bin/env python
import rospy
from std_msgs.msg import String

import logging
import time
from threading import Thread

from aas_core import AASCore
from utilities import AASArchive_utils, Interactions_utils
from utilities.AASArchive_utils import file_to_json
from utilities.Interactions_utils import get_next_svc_request, add_new_svc_response, create_response_json_object, \
    make_gateway_request
from utilities.KafkaInfo import KafkaInfo

# Some variables needed by this AAS Core
state = 'IDLE'
ready = False
WIP = False
processed_services = {}
manager_status = None

# ROS nodes
pub = None
pubCoord = None

def main():

    # rospy.init_node('PruebaROS2', anonymous=True)
    # # Se crean además dos nodos:
    # #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
    # pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
    # #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
    # #   Utiliza para ello el tópico /coordinate
    # pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)
    # time.sleep(2)
    # pub.publish("GO")
    # time.sleep(4)
    # # Se le ordena a un publicista que publique las coordenadas objetivo
    # # Para este ejemplo, son coordenadas estáticas, que representan la
    # # posición fija e invariable del almacén
    # pubCoord.publish("1.43,0.59")
    # # pubCoord.publish("-1.65,-0.56")
    # print(" send warehouse coordinates")
    # print("wait while moving to warehouse")
    # print("FINALIZADA PRUEBA A MANO")

    #############################

    # Create the AAS Core object
    aas_core = AASCore()
    # initialize_aas_archive()
    aas_core.send_status_change_to_manager('Initializing')

    # Then, the initialization tasks are performed
    aas_core.initialize_aas_core()

    # AASArchive_utils.change_status('InitializationReady')   #  Previous
    aas_core.send_status_change_to_manager('InitializationReady')

    # The AAS Core can start running
    aas_core.run_aas_core()

def initialize_aas_archive():
    """These tasks are in charge of AAS Manager, but for testing, they will be performed by the Core"""

    # First, the status file is created
    AASArchive_utils.create_status_file()

    # initial_status_info = {'name': 'AAS_Core', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}
    # f = open('/aas_archive/status/aas_core.json', 'x')
    # json.dump(initial_status_info, f)
    # f.close()


# def initialize_aas_core():
#     """This method executes the required tasks to initialize the AAS Core. In this case, create the connection and
#     execute a necessary ROS nodes."""
#
#     print("Initializing the AAS Core...")
#
#     # A ROS node corresponding to the AAS Core is executed.
#     rospy.init_node('AAS_Core', anonymous=True)
#     print("ROS node initiated.")
#
#     # Se crean además dos nodos:
#     #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
#     global pub
#     pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
#     #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
#     #   Utiliza para ello el tópico /coordinate
#     global pubCoord
#     pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)
#
#     print("ROS publishers initiated.")


def run_aas_core():
    print("AAS Core running...")
    # AASArchive_utils.change_status('Running')
    result = Interactions_utils.send_interaction_msg_to_manager(client_id='i4-0-smia-core',
                                                                msg_key='core-status',
                                                                msg_data={'status': 'Running'})
    if result != "OK":
        print("The AAS Manager-Core interaction is not working: " + str(result))
    else:
        print("The AAS Core has notified the AAS Manager that it is in running state.")

    # Each function will have its own thread of execution
    thread_func1 = Thread(target=handle_data_to_transport, args=())
    thread_func2 = Thread(target=handle_data_from_transport, args=())

    thread_func1.start()
    thread_func2.start()


def handle_data_to_transport():
    """This method handles the message and data to the transport. Thus, it obtains the interaction requests by the AAS
    Manager and send to necessary command to the asset."""

    kafka_consumer_manager_partition = Interactions_utils.create_interaction_kafka_consumer(
        'i4-0-smia-manager')

    print("Listening for manager messages in topic " + KafkaInfo.KAFKA_TOPIC)
    for msg in kafka_consumer_manager_partition:
    # while True:
    #     # TODO analizar los mensajes de peticiones del AAS Manager
    #     msgReceived = get_next_svc_request()
        print("El consumidor del manager (partition 0) de Kafka ha recibido algo!")
        print("   |__ msg: " + str(msg))

        msg_key = msg.key.decode("utf-8")
        msg_json_value = msg.value

        global manager_status
        if msg_key == 'manager-status':
            print("The AAS Core has received an update of the AAS Manager status.")
            manager_status = msg_json_value['status']
            if manager_status != 'Initializing':
                print("AAS Manager has initialized, so the AAS Core can go to running state.")
        if msg_key == 'manager-service-request':
            if manager_status != 'Initializing' and manager_status != 'idle':
                # Only if the AAS Manager is ready the AAS Core will work
                global processed_services
                if msg_json_value['interactionID'] in processed_services:
                    print("The request with interaction_id [" + msg_json_value['interactionID'] +
                          "] has already been performed")
                    break
                else:
                    if msg_json_value['serviceType'] == "AssetRelatedService":
                        print("The AAS Core has received a asset related service request")
                        # TODO, si ha llegado alguna peticion, enviar el comando a traves del pub y pubCoord
                        global WIP
                        if not WIP:
                            if msg_json_value['serviceID'] == "collection" or \
                                    msg_json_value['serviceID'] == "delivery":
                                # TODO pensar como se llamaria al metodo (Ane y Maite lo hicieron con el thread
                                #  del mensaje ACL, yo lo he hecho con el serviceID)
                                # Se configura la información de logging: Imprime líneas con información
                                # sobre la conexión
                                logging.basicConfig(level=logging.INFO)

                                # Marcar el flag para indicar trabajo en proceso
                                WIP = True

                                global pub
                                global pubCoord
                                global state
                                print("---> State: " + str(state))
                                print(pub)

                                if state == "IDLE":
                                    pub.publish("GO")
                                    time.sleep(1)

                                    # PRUEBA CON GATEWAY
                                    make_gateway_request('/coordinateIDLE', 'GO')

                                # Se le ordena a un publicista que publique las coordenadas objetivo
                                # Para este ejemplo, son coordenadas estáticas, que representan la
                                # posición fija e invariable del almacén
                                pubCoord.publish("1.43,0.59")
                                print("AAS Core send warehouse coordinates")
                                print("AAS Core wait while moving to warehouse")

                                # PRUEBA CON GATEWAY
                                make_gateway_request('/coordinate', '1.43,0.59')

                                time.sleep(1)
                                while not state == "ACTIVE":  # wait until the robot has reached the target coordinates
                                    time.sleep(1)

                                # TODO: para pruebas, eliminamos la peticion de servicio, como que ya se ha ofrecido
                                # delete_svc_request(msgReceived)
                                processed_services[msg_json_value['interactionID']] = msg_json_value
                                # processed_services.append(msg_json_value['interactionID'])

                                # Write the response in svResponses.json of the AAS Core
                                response_json = create_response_json_object(msg_json_value)
                                # add_new_svc_response(response_json)
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
                                pubCoord.publish("-1.65,-0.56")

                                # PRUEBA CON GATEWAY
                                make_gateway_request('/coordinate', '-1.65,-0.56')

                                print("AAS Core send collection/delivery point coordinates")
                                print("AAS Core wait while moving to collection/delivery point")

                                time.sleep(1)
                                while not state == "ACTIVE":  # wait until the robot has reached the target coordinates
                                    time.sleep(1)

                                # Se "apaga" el flag 'WIP'
                                WIP = False

                    elif msg_json_value['serviceType'] == "SubmodelService":
                        print("The AAS Core has received a submodel service request")
                    else:
                        print("Service type not available")

        if msg_key == 'manager-service-response':
            print("The AAS Core has received a response from the AAS Manager")
            # TODO
        else:
            print("Option not available")


def handle_data_from_transport():
    """This method handles the message and data from the transport. Thus, it obtains the data from the asset with a ROS
    Subscriber node and send the necessary interaction command or response to the AAS Manager."""

    # Crea un nodo SUBSCRIBER, que se quedará a la escucha por el tópico /status
    # y notificará al agente del estado del transporte
    # rospy.Subscriber('/status', String, callback)

    # PRUEBA GATEWAY
    while True:
        time.sleep(2)
        status_json = file_to_json('/ros_aas_core_archive/status.json')
        global state
        state = status_json['status']
        print("Current state in file: " + state)

def callback(data):
    # Este método se ejecutará cada vez que se publiquen datos por el tópico /status
    print("[TURTLEBOT3 - NEW STATE] :" + str(data.data))

    # Actualiza el estado del transporte
    global state
    state = str(data.data)
    print("")

if __name__ == '__main__':
    print('AAS Core to work with ROS')
    print('AAS Core starting...')
    main()
    print('AAS ending...')

