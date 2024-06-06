import calendar
import json
import logging
import os
import time
from threading import Thread

import rospy
from std_msgs.msg import String

from utilities import AASArchive_utils
from utilities.Interactions_utils import get_next_svc_request, delete_svc_request

# Some variables needed by this AAS Core
state = 'IDLE'
ready = False
WIP = False
processed_services = []

# ROS nodes
pub = None
pubCoord = None

def main():

    initialize_aas_archive()

    # Then, the initialization tasks are performed
    initialize_aas_core()

    AASArchive_utils.change_status('InitializationReady')

    # The AAS Core can start running
    run_aas_core()

def initialize_aas_archive():
    """These tasks are in charge of AAS Manager, but for testing, they will be performed by the Core"""

    # First, the status file is created
    AASArchive_utils.create_status_file()

    # initial_status_info = {'name': 'AAS_Core', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}
    # f = open('/aas_archive/status/aas_core.json', 'x')
    # json.dump(initial_status_info, f)
    # f.close()


def initialize_aas_core():
    """This method executes the required tasks to initialize the AAS Core. In this case, create the connection and
    execute a necessary ROS nodes."""

    print("Initializing the AAS Core...")

    # A ROS node corresponding to the AAS Core is executed.
    rospy.init_node('AAS_Core', anonymous=True)
    print("ROS node initiated.")

    # Se crean además dos nodos:
    #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
    global pub
    pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
    #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
    #   Utiliza para ello el tópico /coordinate
    global pubCoord
    pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)

    print("ROS publishers initiated.")


def run_aas_core():
    print("AAS Core running...")
    AASArchive_utils.change_status('Running')

    # Each function will have its own thread of execution
    thread_func1 = Thread(target=handle_data_to_transport(), args=())
    thread_func2 = Thread(target=handle_data_from_transport(), args=())

    thread_func1.start()
    thread_func2.start()


def handle_data_to_transport():
    """This method handles the message and data to the transport. Thus, it obtains the interaction requests by the AAS
    Manager and send to necessary command to the asset."""

    while True:
        # TODO analizar los mensajes de peticiones del AAS Manager
        msgReceived = get_next_svc_request()
        global processed_services

        print("Processed svc: " + str(processed_services))

        if (msgReceived is not None) and (msgReceived['interactionID'] not in processed_services):
            print("    NOW")
            print(msgReceived)
            print("InteractionID: " + str(msgReceived['interactionID']))

            # TODO, si ha llegado alguna peticion, enviar el comando a traves del pub y pubCoord
            global WIP
            global state
            if state == "IDLE" and not WIP:
                # Marcar el flag para indicar trabajo en proceso
                WIP = True

                # Si el thread del mensaje recibido es INTRODUCE o DELIVERY
                if msgReceived['serviceData']['thread'] == "INTRODUCE" or msgReceived['serviceData']['thread'] == "DELIVERY":
                    # Se configura la información de logging: Imprime líneas con información sobre la conexión
                    logging.basicConfig(level=logging.INFO)

                    global pub
                    global pubCoord

                    print("         + Notify ROS nodes for service   [GO]")
                    # Se le ordena a un publicista que notifique al transporte de que se requiere un servicio
                    pub.publish("GO")
                    # Hacer tiempo mientras el transporte alcanza el estado 'LOCALIZATION'
                    while state == "LOCALIZATION":
                        pass;
                    print("transport in state LOCALIZATION")

                    # Se le ordena a un publicista que publique las coordenadas objetivo
                    # Para este ejemplo, son coordenadas estáticas, que representan la
                    # posición fija e invariable del almacén
                    time.sleep(10)
                    pubCoord.publish("1.43,0.59")

                    # Hacer tiempo mientras el transporte alcanza el estado 'ACTIVE'
                    while state == "ACTIVE":
                        pass
                    print("transport in state ACTIVE")

                    # Hacer tiempo mientras el transporte alcanza el estado 'OPERATIVE'
                    while state == "OPERATIVE":
                        pass
                    print("transport in state OPERATIVE")

                if WIP:
                    # Se "apaga" el flag 'WIP'
                    WIP = None
                    # Ahora el turtlebot3 se ha transladado hasta la máquina y vuelve al estado ACTIVE
                    # En este punto realiza dos acciones:

                    # 1) Avisar a TransportAgent de que el robot ya ha llegado a la máquina.
                    msg2 = {'thread': 'READY'} #TODO escribir la respuesta en svcResponses del Core con body="ALREADY IN WAREHOUSE"
                    # msg2.thread = "READY"

                    # Envía al mensaje a TransportAgent
                    # TODO
                    print(
                        "         + Message sent to AAS Manager from AAS Core  (interactions/Core/svcResponses.json)")

                    time.sleep(15)
                    # 2) Devolver célula de transporte a su punto de partida
                    print("           |____Returning transport to base!")

                    #    Coordenadas estáticas, que representan la posición de ORIGEN del turtlebot3
                    pubCoord.publish("-1.65,-0.56")

                    # Hacer tiempo mientras el transporte alcanza el estado 'ACTIVE'
                    while state == "ACTIVE":
                        pass
                    # Hacer tiempo mientras el transporte alcanza el estado 'OPERATIVE'
                    while state == "OPERATIVE":
                        pass

                    # TODO: para pruebas, eliminamos la peticion de servicio, como que ya se ha ofrecido
                    # delete_svc_request(msgReceived)
                    processed_services.append(msgReceived['interactionID'])
        else:
            print("No service requests yet.")
            time.sleep(2)

def handle_data_from_transport():
    """This method handles the message and data from the transport. Thus, it obtains the data from the asset with a ROS
    Subscriber node and send the necessary interaction command or response to the AAS Manager."""

    # Crea un nodo SUBSCRIBER, que se quedará a la escucha por el tópico /status
    # y notificará al agente del estado del transporte
    rospy.Subscriber('/status', String, callback)


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

