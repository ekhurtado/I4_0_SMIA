from threading import Thread

import rospy
from std_msgs.msg import String

from utilities import AASArchive_utils, ROS_utils

# Some variables needed by this AAS Core
state = 'IDLE'
ready = False

# ROS nodes
pub = None
pubCoord = None

def main():

    # First, the status file is created
    AASArchive_utils.create_status_file()

    # Then, the initialization tasks are performed
    initialize_aas_core()

def initialize_aas_core():
    """This method executes the required tasks to initialize the AAS Core. In this case, create the connection and
    execute a necessary ROS nodes."""

    # A ROS node corresponding to the AAS Core is executed.
    rospy.init_node('AAS_Core', anonymous=True)

    # Se crean además dos nodos:
    #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
    pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
    #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
    #   Utiliza para ello el tópico /coordinate
    pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)

    # Each function will have its own thread of execution
    thread_func1 = Thread(target=handle_data_to_transport(), args=())
    thread_func2 = Thread(target=handle_data_from_transport(), args=())

    thread_func1.start()
    thread_func2.start()


def handle_data_to_transport():
    """This method handles the message and data to the transport. Thus, it obtains the interaction requests by the AAS
    Manager and send to necessary command to the asset."""

    # TODO analizar los mensajes de peticiones del AAS Manager

    # TODO, si ha llegado alguna peticion, enviar el comando a trabes del pub y pubCoord

def handle_data_from_transport():
    """This method handles the message and data from the transport. Thus, it obtains the data from the asset with a ROS
    Subscriber node and send the necessary interaction command or response to the AAS Manager."""

    # Crea un nodo SUBSCRIBER, que se quedará a la escucha por el tópico /status
    # y notificará al agente del estado del transporte
    rospy.Subscriber('/status', String, ROS_utils.callback)


if __name__ == '__main__':
    print('AAS Core starting...')
    main()
    print('AAS Core to work with ROS')

