import random
import time

import rospy
from std_msgs.msg import String

from AssetServicesInfo import AssetServicesInfo


class AssetServices:

    def __init__(self):
        self.properties = AssetServicesInfo.PROPERTIES_DATA
        self.actions = AssetServicesInfo.ACTIONS_DATA
        self.battery = 100
        self.location = '-1.65,-0.56'   # starting coordinate of the robot

        # ROS-related attributes
        self.state = 'IDLE'
        self.ready = False
        self.WIP = False
        self.pub = None
        self.pubCoord = None

    def initialize_ros_node(self):
        rospy.init_node('AssetIntegration', anonymous=True)

    def initialize_publishers(self):
        # Se crean además dos nodos:
        #   1) Un PUBLISHER, que dará la señal de comienzo del servicio por el tópico (coordinateIDLE)
        self.pub = rospy.Publisher('/coordinateIDLE', String, queue_size=10)
        #   2) Otro PUBLISHER, que comunicará el destino o coordenada a la que debe desplazarse el transporte.
        #   Utiliza para ello el tópico /coordinate
        self.pubCoord = rospy.Publisher('/coordinate', String, queue_size=10)  # Coordinate, queue_size=10)

    def initialize_status_subscriber(self):
        rospy.Subscriber('/status', String, self.status_callback)

    def status_callback(self, data):
        # Este método se ejecutará cada vez que se publiquen datos por el tópico /status
        print("[TURTLEBOT3 - NEW STATE] :" + str(data.data))

        # Actualiza el estado del transporte
        self.state = str(data.data)

    def get_battery(self):
        self.battery = random.uniform(0.0, 100.0)
        return self.battery

    def get_property(self, property_name):
        if property_name == 'battery':
            return self.get_battery()
        elif property_name == 'location':
            return self.location
        else:
            print("This property does not exist.")
            return None

    def perform_action(self, action_name, parameters):
        if action_name == 'move':
            return self.perform_action_move(parameters['destinationcoordinates'])
        else:
            return 'FAILED'

    def perform_action_move(self, coordinates):
        # Create the ros node
        # rospy.init_node('AssetIntegration', anonymous=True)

        # Publish the message
        print("Sending message...")
        self.pub.publish("GO")
        print("Message sent")
        time.sleep(1)

        print("Sending coordinates...")
        self.pubCoord.publish(coordinates)
        print("Coordinates sent")
        time.sleep(1)
        while not self.state == "ACTIVE":  # wait until the robot has reached the target coordinates
            time.sleep(1)

        # Shutdown the ros node
        # rospy.signal_shutdown("node completed")
        print(" --> Move service completed!")
        self.location = coordinates
        return 'SUCCESS'
