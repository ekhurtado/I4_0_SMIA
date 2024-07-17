"""
This class contains methods related to the communication with the asset, in this case, a transport robot in ROS.
"""


def rcvDataFromAsset(self, behav, myAgent):
    # Evalúa el valor de un flag de “trabajo en proceso”(WIP) para determinar
    # si un recurso físico está disponible.
    print("rcvDataFromAsset")