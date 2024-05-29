"""This class contains some utils methods related to ROS."""
def callback(data):
    # Este método se ejecutará cada vez que se publiquen datos por el tópico /status
    print("[TURTLEBOT3 - NEW STATE] :" + str(data.data))

    # Actualiza el estado del transporte
    self.myAgent.state = str(data.data) # TODO, revisar si en el codigo de Ane y Maite utilizan el state
    print("")